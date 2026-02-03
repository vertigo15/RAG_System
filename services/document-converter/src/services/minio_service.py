"""
MinIO service for document storage.
"""

import logging
import io
from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)


class MinIOService:
    """MinIO operations for document converter."""
    
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        secure: bool = False
    ):
        """
        Initialize MinIO service.
        
        Args:
            endpoint: MinIO endpoint (host:port)
            access_key: Access key
            secret_key: Secret key
            bucket_name: Bucket name
            secure: Whether to use HTTPS
        """
        self.bucket_name = bucket_name
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        self.ensure_bucket_exists()
    
    def ensure_bucket_exists(self):
        """Ensure the bucket exists, create if not."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                logger.debug(f"Bucket exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error checking/creating bucket: {e}")
            raise
    
    def upload_markdown(self, document_id: str, markdown_content: str) -> str:
        """
        Upload markdown content to MinIO.
        
        Args:
            document_id: Document UUID
            markdown_content: Markdown text
            
        Returns:
            MinIO object path
        """
        object_name = f"markdown/{document_id}.md"
        
        try:
            content_bytes = markdown_content.encode('utf-8')
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=io.BytesIO(content_bytes),
                length=len(content_bytes),
                content_type="text/markdown"
            )
            logger.info(f"Uploaded markdown: {object_name}")
            return object_name
        except S3Error as e:
            logger.error(f"Failed to upload markdown: {e}")
            raise
    
    def upload_image(self, document_id: str, image_id: str, image_bytes: bytes) -> str:
        """
        Upload image to MinIO.
        
        Args:
            document_id: Document UUID
            image_id: Image identifier
            image_bytes: Image binary data
            
        Returns:
            MinIO object path
        """
        object_name = f"images/{document_id}/{image_id}.png"
        
        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=io.BytesIO(image_bytes),
                length=len(image_bytes),
                content_type="image/png"
            )
            logger.debug(f"Uploaded image: {object_name}")
            return object_name
        except S3Error as e:
            logger.error(f"Failed to upload image: {e}")
            raise
    
    def upload_file(self, object_name: str, file_path: str, content_type: str = "application/octet-stream"):
        """
        Upload a file from filesystem to MinIO.
        
        Args:
            object_name: Destination object name
            file_path: Source file path
            content_type: MIME type
        """
        try:
            self.client.fput_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                file_path=file_path,
                content_type=content_type
            )
            logger.debug(f"Uploaded file: {object_name}")
        except S3Error as e:
            logger.error(f"Failed to upload file: {e}")
            raise
