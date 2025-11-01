"""File content cache service for avoiding redundant file processing."""

import logging
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
from .bigquery_client import bq_client

logger = logging.getLogger(__name__)


class FileContentCacheService:
    """Service for caching processed file contents in BigQuery."""
    
    def __init__(self):
        """Initialize the file content cache service."""
        self.table_name = "file_content_cache"
        self._ensure_cache_table_exists()
    
    def _ensure_cache_table_exists(self):
        """Ensure the file content cache table exists in BigQuery."""
        if not bq_client or not bq_client.is_available:
            logger.warning("BigQuery client not available, cache table creation skipped")
            return
        
        try:
            from google.cloud import bigquery
            
            table_id = f"{bq_client.project_id}.{bq_client.dataset_id}.{self.table_name}"
            
            # Check if table exists
            try:
                bq_client.client.get_table(table_id)
                logger.info(f"File content cache table already exists: {table_id}")
                return
            except Exception:
                logger.info(f"Creating file content cache table: {table_id}")
            
            # Define schema for file content cache
            schema = [
                bigquery.SchemaField("file_hash", "STRING", mode="REQUIRED", description="SHA256 hash of file content"),
                bigquery.SchemaField("gcs_uri", "STRING", mode="REQUIRED", description="GCS URI of the file"),
                bigquery.SchemaField("filename", "STRING", mode="REQUIRED", description="Original filename"),
                bigquery.SchemaField("content_type", "STRING", mode="REQUIRED", description="MIME type of the file"),
                bigquery.SchemaField("extracted_text", "STRING", mode="NULLABLE", description="Extracted text content"),
                bigquery.SchemaField("text_length", "INTEGER", mode="NULLABLE", description="Length of extracted text"),
                bigquery.SchemaField("processing_status", "STRING", mode="REQUIRED", description="Status: success, failed, empty"),
                bigquery.SchemaField("error_message", "STRING", mode="NULLABLE", description="Error message if processing failed"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED", description="When the cache entry was created"),
                bigquery.SchemaField("last_accessed_at", "TIMESTAMP", mode="REQUIRED", description="When the cache entry was last accessed"),
                bigquery.SchemaField("access_count", "INTEGER", mode="REQUIRED", description="Number of times this cache entry was accessed"),
            ]
            
            # Create table
            table = bigquery.Table(table_id, schema=schema)
            table = bq_client.client.create_table(table)
            logger.info(f"Successfully created file content cache table: {table_id}")
            
        except Exception as e:
            logger.error(f"Failed to create file content cache table: {e}")
    
    @staticmethod
    def _compute_file_hash(gcs_uri: str, filename: str, content_type: str) -> str:
        """
        Compute a unique hash for a file based on its GCS URI, filename, and content type.
        
        Args:
            gcs_uri: GCS URI of the file
            filename: Original filename
            content_type: MIME type
            
        Returns:
            SHA256 hash string
        """
        # Combine GCS URI, filename, and content type for hash
        # This ensures we cache based on the actual file location
        hash_input = f"{gcs_uri}|{filename}|{content_type}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def get_cached_content(self, gcs_uri: str, filename: str, content_type: str) -> Optional[Dict]:
        """
        Retrieve cached file content if it exists.
        
        Args:
            gcs_uri: GCS URI of the file
            filename: Original filename
            content_type: MIME type
            
        Returns:
            Dict with cached content or None if not found
        """
        if not bq_client or not bq_client.is_available:
            logger.debug("BigQuery not available, skipping cache lookup")
            return None
        
        try:
            file_hash = self._compute_file_hash(gcs_uri, filename, content_type)
            
            # Query for cached content
            query = f"""
                SELECT 
                    file_hash,
                    filename,
                    content_type,
                    extracted_text,
                    text_length,
                    processing_status,
                    error_message,
                    created_at,
                    access_count
                FROM `{bq_client.project_id}.{bq_client.dataset_id}.{self.table_name}`
                WHERE file_hash = @file_hash
                LIMIT 1
            """
            
            from google.cloud import bigquery
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("file_hash", "STRING", file_hash)
                ]
            )
            
            query_job = bq_client.client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if results:
                row = results[0]
                logger.info(f"Cache HIT for {filename} (hash: {file_hash[:16]}...)")
                
                # Update last_accessed_at and access_count
                self._update_access_stats(file_hash)
                
                return {
                    "filename": row.filename,
                    "content_type": row.content_type,
                    "extracted_text": row.extracted_text,
                    "text_length": row.text_length or 0,
                    "processing_status": row.processing_status,
                    "error_message": row.error_message,
                    "cached": True,
                    "cache_created_at": row.created_at.isoformat() if row.created_at else None,
                    "cache_access_count": row.access_count
                }
            else:
                logger.info(f"Cache MISS for {filename} (hash: {file_hash[:16]}...)")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving cached content for {filename}: {e}")
            return None
    
    def _update_access_stats(self, file_hash: str):
        """Update last_accessed_at and increment access_count for a cache entry."""
        try:
            update_query = f"""
                UPDATE `{bq_client.project_id}.{bq_client.dataset_id}.{self.table_name}`
                SET 
                    last_accessed_at = CURRENT_TIMESTAMP(),
                    access_count = access_count + 1
                WHERE file_hash = @file_hash
            """
            
            from google.cloud import bigquery
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("file_hash", "STRING", file_hash)
                ]
            )
            
            bq_client.client.query(update_query, job_config=job_config).result()
            logger.debug(f"Updated access stats for file hash: {file_hash[:16]}...")
            
        except Exception as e:
            logger.warning(f"Failed to update access stats: {e}")
    
    def cache_file_content(
        self, 
        gcs_uri: str, 
        filename: str, 
        content_type: str, 
        extracted_text: Optional[str] = None,
        processing_status: str = "success",
        error_message: Optional[str] = None
    ) -> bool:
        """
        Cache processed file content in BigQuery.
        
        Args:
            gcs_uri: GCS URI of the file
            filename: Original filename
            content_type: MIME type
            extracted_text: Extracted text content (None if processing failed)
            processing_status: Status of processing (success, failed, empty)
            error_message: Error message if processing failed
            
        Returns:
            True if caching succeeded, False otherwise
        """
        if not bq_client or not bq_client.is_available:
            logger.debug("BigQuery not available, skipping cache storage")
            return False
        
        try:
            file_hash = self._compute_file_hash(gcs_uri, filename, content_type)
            
            # Check if entry already exists
            existing = self.get_cached_content(gcs_uri, filename, content_type)
            if existing:
                logger.info(f"Cache entry already exists for {filename}, skipping insert")
                return True
            
            # Prepare cache entry
            now = datetime.utcnow()
            cache_entry = {
                "file_hash": file_hash,
                "gcs_uri": gcs_uri,
                "filename": filename,
                "content_type": content_type,
                "extracted_text": extracted_text,
                "text_length": len(extracted_text) if extracted_text else 0,
                "processing_status": processing_status,
                "error_message": error_message,
                "created_at": now.isoformat(),
                "last_accessed_at": now.isoformat(),
                "access_count": 1
            }
            
            # Insert into BigQuery
            bq_client.insert_rows(self.table_name, [cache_entry])
            logger.info(f"Successfully cached content for {filename} (hash: {file_hash[:16]}...)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache file content for {filename}: {e}")
            return False
    
    def get_cache_stats(self) -> Dict:
        """Get statistics about the file content cache."""
        if not bq_client or not bq_client.is_available:
            return {"error": "BigQuery not available"}
        
        try:
            query = f"""
                SELECT 
                    COUNT(*) as total_entries,
                    SUM(CASE WHEN processing_status = 'success' THEN 1 ELSE 0 END) as successful_entries,
                    SUM(CASE WHEN processing_status = 'failed' THEN 1 ELSE 0 END) as failed_entries,
                    SUM(CASE WHEN processing_status = 'empty' THEN 1 ELSE 0 END) as empty_entries,
                    SUM(access_count) as total_accesses,
                    AVG(access_count) as avg_accesses_per_file,
                    SUM(text_length) as total_cached_text_bytes
                FROM `{bq_client.project_id}.{bq_client.dataset_id}.{self.table_name}`
            """
            
            query_job = bq_client.client.query(query)
            results = list(query_job.result())
            
            if results:
                row = results[0]
                return {
                    "total_entries": row.total_entries,
                    "successful_entries": row.successful_entries,
                    "failed_entries": row.failed_entries,
                    "empty_entries": row.empty_entries,
                    "total_accesses": row.total_accesses,
                    "avg_accesses_per_file": float(row.avg_accesses_per_file) if row.avg_accesses_per_file else 0,
                    "total_cached_text_bytes": row.total_cached_text_bytes
                }
            
            return {"error": "No data available"}
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e)}


# Global service instance
file_content_cache_service = FileContentCacheService()
