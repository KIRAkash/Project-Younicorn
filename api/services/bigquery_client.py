"""BigQuery client and operations for Project Minerva API."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..config import settings

logger = logging.getLogger(__name__)

class BigQueryClient:
    """BigQuery client wrapper for Project Minerva operations."""
    
    def __init__(self):
        self.client = None
        self.project_id = None
        self.dataset_id = settings.bigquery_dataset_id
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize BigQuery client."""
        try:
            from google.cloud import bigquery
            self.client = bigquery.Client()
            self.project_id = self.client.project
            logger.info(f"BigQuery client initialized for project: {self.project_id}")
            
            # Ensure tables exist with updated schema
            self._ensure_analyses_table_updated()
        except Exception as e:
            logger.warning(f"Could not initialize BigQuery client: {e}")
            self.client = None
    
    def _ensure_analyses_table_updated(self):
        """Ensure analyses table has the new schema with individual agent columns."""
        if not self.is_available:
            return
        
        try:
            from google.cloud import bigquery
            table_id = f"{self.project_id}.{self.dataset_id}.analyses"
            
            # Get current table schema
            try:
                table = self.client.get_table(table_id)
                current_fields = {field.name for field in table.schema}
                
                # Check if new columns exist
                new_columns = {
                    'team_analysis', 'market_analysis', 'product_analysis', 
                    'competition_analysis', 'synthesis_analysis'
                }
                
                missing_columns = new_columns - current_fields
                
                if missing_columns:
                    logger.info(f"Adding missing columns to analyses table: {missing_columns}")
                    
                    # Create new schema with additional columns
                    new_schema = list(table.schema)
                    
                    # Add missing columns before the existing agent_analyses column
                    insert_index = None
                    for i, field in enumerate(new_schema):
                        if field.name == 'agent_analyses':
                            insert_index = i
                            break
                    
                    if insert_index is not None:
                        for col in ['team_analysis', 'market_analysis', 'product_analysis', 'competition_analysis', 'synthesis_analysis']:
                            if col in missing_columns:
                                new_schema.insert(insert_index, bigquery.SchemaField(col, "JSON", mode="NULLABLE"))
                                insert_index += 1
                    
                    # Update table schema
                    table.schema = new_schema
                    table = self.client.update_table(table, ["schema"])
                    logger.info("Successfully updated analyses table schema")
                else:
                    logger.info("Analyses table already has the updated schema")
                    
            except Exception as schema_error:
                logger.warning(f"Could not update analyses table schema: {schema_error}")
                
        except Exception as e:
            logger.warning(f"Error ensuring analyses table schema: {e}")
    
    @property
    def is_available(self) -> bool:
        """Check if BigQuery client is available."""
        return self.client is not None
    
    def query(self, sql: str, parameters: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a BigQuery query."""
        if not self.is_available:
            raise RuntimeError("BigQuery client not available")
        
        job_config = None
        if parameters:
            from google.cloud import bigquery
            job_config = bigquery.QueryJobConfig()
            for key, value in parameters.items():
                job_config.query_parameters.append(
                    bigquery.ScalarQueryParameter(key, "STRING", value)
                )
        
        query_job = self.client.query(sql, job_config=job_config)
        return query_job.result()
    
    def insert_rows(self, table_name: str, rows: List[Dict[str, Any]]) -> None:
        """Insert rows into a BigQuery table."""
        if not self.is_available:
            raise RuntimeError("BigQuery client not available")
        
        try:
            table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
            table = self.client.get_table(table_id)
            
            # Process rows for BigQuery compatibility
            processed_rows = []
            for row in rows:
                processed_row = {}
                for key, value in row.items():
                    if value is None:
                        processed_row[key] = None
                    elif isinstance(value, (dict, list)):
                        # Convert dict/list to JSON string for BigQuery JSON fields
                        processed_row[key] = value  # BigQuery handles JSON natively
                    else:
                        processed_row[key] = value
                processed_rows.append(processed_row)
            
            errors = self.client.insert_rows_json(table, processed_rows)
            if errors:
                raise RuntimeError(f"BigQuery insert failed: {errors}")
            
            logger.info(f"Successfully inserted {len(rows)} rows into {table_name}")
        except Exception as e:
            # Handle VPC Service Controls and other BigQuery access issues
            if "VPC Service Controls" in str(e) or "403" in str(e):
                logger.warning(f"BigQuery access restricted by VPC Service Controls: {e}")
                raise RuntimeError("BigQuery access temporarily restricted")
            else:
                logger.error(f"BigQuery insert error: {e}")
                raise

# Global BigQuery client instance
bq_client = BigQueryClient() if settings.google_cloud_project else None
