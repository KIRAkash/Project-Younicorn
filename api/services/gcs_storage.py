"""Google Cloud Storage service for Project Younicorn."""

import os
import logging
from typing import Optional, List, Dict, Any
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError

logger = logging.getLogger(__name__)


class GCSStorageService:
    """Service for managing file uploads to Google Cloud Storage."""
    
    def __init__(self, bucket_name: Optional[str] = None):
        """Initialize GCS storage service.
        
        Args:
            bucket_name: Name of the GCS bucket. If not provided, uses environment variable.
        """
        self.bucket_name = bucket_name or os.environ.get("GCS_BUCKET_NAME", "younicorns-uploads")
        self.is_available = False
        self.client = None
        self.bucket = None
        
        try:
            self.client = storage.Client()
            # Try to get or create bucket
            try:
                self.bucket = self.client.get_bucket(self.bucket_name)
                logger.info(f"Connected to GCS bucket: {self.bucket_name}")
            except Exception as e:
                logger.warning(f"Bucket {self.bucket_name} not found, attempting to create: {e}")
                try:
                    self.bucket = self.client.create_bucket(self.bucket_name)
                    logger.info(f"Created GCS bucket: {self.bucket_name}")
                except Exception as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    raise
            
            self.is_available = True
        except Exception as e:
            logger.error(f"Failed to initialize GCS storage: {e}")
            self.is_available = False
    
    def upload_file(
        self,
        file_content: bytes,
        destination_path: str,
        content_type: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """Upload a file to GCS.
        
        Args:
            file_content: File content as bytes
            destination_path: Destination path in GCS (e.g., "startups/startup-id/file.pdf")
            content_type: MIME type of the file
            metadata: Optional metadata dictionary
            
        Returns:
            GCS path (gs://bucket/path) if successful, None otherwise
        """
        if not self.is_available:
            logger.error("GCS storage is not available")
            return None
        
        try:
            blob = self.bucket.blob(destination_path)
            blob.content_type = content_type
            
            if metadata:
                blob.metadata = metadata
            
            blob.upload_from_string(file_content, content_type=content_type)
            
            gcs_path = f"gs://{self.bucket_name}/{destination_path}"
            logger.info(f"Uploaded file to: {gcs_path}")
            return gcs_path
            
        except GoogleCloudError as e:
            logger.error(f"Failed to upload file to GCS: {e}")
            return None
    
    def upload_base64_file(
        self,
        base64_content: str,
        destination_path: str,
        content_type: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """Upload a base64-encoded file to GCS.
        
        Args:
            base64_content: Base64-encoded file content
            destination_path: Destination path in GCS
            content_type: MIME type of the file
            metadata: Optional metadata dictionary
            
        Returns:
            GCS path if successful, None otherwise
        """
        import base64
        
        try:
            file_content = base64.b64decode(base64_content)
            return self.upload_file(file_content, destination_path, content_type, metadata)
        except Exception as e:
            logger.error(f"Failed to decode and upload base64 file: {e}")
            return None
    
    def delete_file(self, gcs_path: str) -> bool:
        """Delete a file from GCS.
        
        Args:
            gcs_path: Full GCS path (gs://bucket/path)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            logger.error("GCS storage is not available")
            return False
        
        try:
            # Extract blob path from GCS path
            if gcs_path.startswith(f"gs://{self.bucket_name}/"):
                blob_path = gcs_path.replace(f"gs://{self.bucket_name}/", "")
                blob = self.bucket.blob(blob_path)
                blob.delete()
                logger.info(f"Deleted file: {gcs_path}")
                return True
            else:
                logger.error(f"Invalid GCS path: {gcs_path}")
                return False
        except GoogleCloudError as e:
            logger.error(f"Failed to delete file from GCS: {e}")
            return False
    
    def delete_folder(self, folder_path: str) -> bool:
        """Delete all files in a folder from GCS.
        
        Args:
            folder_path: Folder path in GCS (e.g., "startups/startup-id/")
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            logger.error("GCS storage is not available")
            return False
        
        try:
            blobs = self.bucket.list_blobs(prefix=folder_path)
            for blob in blobs:
                blob.delete()
            logger.info(f"Deleted folder: {folder_path}")
            return True
        except GoogleCloudError as e:
            logger.error(f"Failed to delete folder from GCS: {e}")
            return False
    
    def get_signed_url(self, gcs_path: str, expiration_minutes: int = 60) -> Optional[str]:
        """Generate a signed URL for temporary access to a file.
        
        Args:
            gcs_path: Full GCS path (gs://bucket/path)
            expiration_minutes: URL expiration time in minutes
            
        Returns:
            Signed URL if successful, None otherwise
        """
        if not self.is_available:
            logger.error("GCS storage is not available")
            return None
        
        try:
            from datetime import timedelta
            
            # Extract blob path from GCS path
            if gcs_path.startswith(f"gs://{self.bucket_name}/"):
                blob_path = gcs_path.replace(f"gs://{self.bucket_name}/", "")
                blob = self.bucket.blob(blob_path)
                
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=timedelta(minutes=expiration_minutes),
                    method="GET"
                )
                return url
            else:
                logger.error(f"Invalid GCS path: {gcs_path}")
                return None
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {e}")
            return None
    
    def list_files(self, prefix: str) -> List[Dict[str, Any]]:
        """List files in a GCS folder.
        
        Args:
            prefix: Folder prefix (e.g., "startups/startup-id/")
            
        Returns:
            List of file information dictionaries
        """
        if not self.is_available:
            logger.error("GCS storage is not available")
            return []
        
        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            files = []
            for blob in blobs:
                files.append({
                    "name": blob.name,
                    "size": blob.size,
                    "content_type": blob.content_type,
                    "created": blob.time_created.isoformat() if blob.time_created else None,
                    "updated": blob.updated.isoformat() if blob.updated else None,
                    "gcs_path": f"gs://{self.bucket_name}/{blob.name}",
                    "metadata": blob.metadata or {}
                })
            return files
        except GoogleCloudError as e:
            logger.error(f"Failed to list files from GCS: {e}")
            return []
    
    def upload_image(
        self,
        image_content: bytes,
        destination_path: str,
        max_size_mb: int = 5
    ) -> Optional[str]:
        """Upload image with validation.
        
        Args:
            image_content: Image content as bytes
            destination_path: Destination path in GCS
            max_size_mb: Maximum file size in MB (default: 5MB)
            
        Returns:
            GCS path if successful, None otherwise
        """
        # Size check
        size_mb = len(image_content) / (1024 * 1024)
        if size_mb > max_size_mb:
            logger.error(f"Image size {size_mb:.2f}MB exceeds limit of {max_size_mb}MB")
            return None
        
        # Format check using magic bytes
        import imghdr
        image_type = imghdr.what(None, h=image_content)
        if not image_type:
            # Fallback to checking magic bytes for common formats
            if image_content.startswith(b'\x89PNG'):
                image_type = 'png'
            elif image_content.startswith(b'\xff\xd8\xff'):
                image_type = 'jpeg'
            elif image_content.startswith(b'GIF'):
                image_type = 'gif'
            elif image_content.startswith(b'RIFF') and b'WEBP' in image_content[:20]:
                image_type = 'webp'
            elif b'<svg' in image_content[:1000]:
                image_type = 'svg+xml'
        
        if not image_type:
            logger.error("Unable to determine image type")
            return None
        
        content_type = f"image/{image_type}"
        return self.upload_file(image_content, destination_path, content_type)
    
    def upload_profile_icon(
        self,
        user_id: str,
        image_content: bytes
    ) -> Optional[str]:
        """Upload user profile icon (2MB max).
        
        Args:
            user_id: User ID (Firebase UID)
            image_content: Image content as bytes
            
        Returns:
            GCS path if successful, None otherwise
        """
        from datetime import datetime
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        destination_path = f"users/{user_id}/profile_icon_{timestamp}.jpg"
        return self.upload_image(image_content, destination_path, max_size_mb=2)
    
    def upload_startup_logo(
        self,
        startup_id: str,
        image_content: bytes
    ) -> Optional[str]:
        """Upload startup logo (5MB max).
        
        Args:
            startup_id: Startup ID
            image_content: Image content as bytes
            
        Returns:
            GCS path if successful, None otherwise
        """
        from datetime import datetime
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        destination_path = f"startups/{startup_id}/logo_{timestamp}.jpg"
        return self.upload_image(image_content, destination_path, max_size_mb=5)
    
    def get_latest_image(self, prefix: str) -> Optional[Dict[str, Any]]:
        """Get the most recent image from a folder.
        
        Args:
            prefix: Folder prefix (e.g., "users/{user_id}/profile_icon_")
            
        Returns:
            Latest file info dict or None
        """
        files = self.list_files(prefix)
        if not files:
            return None
        
        # Sort by creation time, newest first
        files.sort(key=lambda x: x['created'] or '', reverse=True)
        return files[0]


# Global GCS storage service instance
gcs_storage = GCSStorageService()
