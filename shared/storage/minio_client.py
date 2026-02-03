"""
MinIO Client Library
Shared library for interacting with MinIO object storage across services.
"""

import io
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, BinaryIO
from datetime import timedelta

from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)


class MinIOClient:
    """Client for interacting with MinIO object storage."""
    
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        secure: bool = False
    ):
        """
        Initialize MinIO client.
        
        Args:
            endpoint: MinIO server endpoint (e.g., 'minio:9000')
            access_key: MinIO access key
            secret_key: MinIO secret key
            bucket_name: Default bucket name
            secure: Whether to use HTTPS
        """
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        
        # Ensure bucket exists
        self._ensure_bucket_exists()
        
        logger.info(f"MinIO client initialized for bucket: {bucket_name}")
    
    def _ensure_bucket_exists(self) -> None:
        """Create bucket if it doesn't exist."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                logger.debug(f"Bucket already exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise
    
    def store_file(
        self,
        object_name: str,
        data: bytes | str | BinaryIO,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Store a file in MinIO.
        
        Args:
            object_name: Path/name of object in bucket (e.g., 'doc_id/document.md')
            data: File data as bytes, string, or file-like object
            content_type: MIME type of the content
            metadata: Optional metadata dictionary
            
        Returns:
            True if successful
        """
        try:
            # Convert string to bytes
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Convert bytes to BytesIO
            if isinstance(data, bytes):
                data = io.BytesIO(data)
                length = len(data.getvalue())
            else:
                # For file-like objects, get the length
                data.seek(0, 2)  # Seek to end
                length = data.tell()
                data.seek(0)  # Reset to beginning
            
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=data,
                length=length,
                content_type=content_type,
                metadata=metadata or {}
            )
            
            logger.info(f"Stored file: {object_name} ({length} bytes)")
            return True
            
        except S3Error as e:
            logger.error(f"Error storing file {object_name}: {e}")
            raise
    
    def store_json(
        self,
        object_name: str,
        data: Dict[str, Any] | List[Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Store JSON data in MinIO.
        
        Args:
            object_name: Path/name of object in bucket
            data: Dictionary or list to store as JSON
            metadata: Optional metadata dictionary
            
        Returns:
            True if successful
        """
        try:
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            return self.store_file(
                object_name=object_name,
                data=json_str,
                content_type="application/json",
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Error storing JSON {object_name}: {e}")
            raise
    
    def retrieve_file(self, object_name: str) -> bytes:
        """
        Retrieve a file from MinIO.
        
        Args:
            object_name: Path/name of object in bucket
            
        Returns:
            File content as bytes
        """
        try:
            response = self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=object_name
            )
            data = response.read()
            response.close()
            response.release_conn()
            
            logger.info(f"Retrieved file: {object_name} ({len(data)} bytes)")
            return data
            
        except S3Error as e:
            logger.error(f"Error retrieving file {object_name}: {e}")
            raise
    
    def retrieve_text(self, object_name: str, encoding: str = 'utf-8') -> str:
        """
        Retrieve a text file from MinIO.
        
        Args:
            object_name: Path/name of object in bucket
            encoding: Text encoding (default: utf-8)
            
        Returns:
            File content as string
        """
        data = self.retrieve_file(object_name)
        return data.decode(encoding)
    
    def retrieve_json(self, object_name: str) -> Dict[str, Any] | List[Any]:
        """
        Retrieve JSON data from MinIO.
        
        Args:
            object_name: Path/name of object in bucket
            
        Returns:
            Parsed JSON data
        """
        try:
            text = self.retrieve_text(object_name)
            return json.loads(text)
        except Exception as e:
            logger.error(f"Error retrieving JSON {object_name}: {e}")
            raise
    
    def list_files(self, prefix: str = "") -> List[str]:
        """
        List files in bucket with given prefix.
        
        Args:
            prefix: Object name prefix to filter by (e.g., 'doc_id/')
            
        Returns:
            List of object names
        """
        try:
            objects = self.client.list_objects(
                bucket_name=self.bucket_name,
                prefix=prefix,
                recursive=True
            )
            
            file_list = [obj.object_name for obj in objects]
            logger.info(f"Listed {len(file_list)} files with prefix: {prefix}")
            return file_list
            
        except S3Error as e:
            logger.error(f"Error listing files with prefix {prefix}: {e}")
            raise
    
    def file_exists(self, object_name: str) -> bool:
        """
        Check if a file exists in MinIO.
        
        Args:
            object_name: Path/name of object in bucket
            
        Returns:
            True if file exists
        """
        try:
            self.client.stat_object(
                bucket_name=self.bucket_name,
                object_name=object_name
            )
            return True
        except S3Error:
            return False
    
    def delete_file(self, object_name: str) -> bool:
        """
        Delete a file from MinIO.
        
        Args:
            object_name: Path/name of object in bucket
            
        Returns:
            True if successful
        """
        try:
            self.client.remove_object(
                bucket_name=self.bucket_name,
                object_name=object_name
            )
            logger.info(f"Deleted file: {object_name}")
            return True
            
        except S3Error as e:
            logger.error(f"Error deleting file {object_name}: {e}")
            raise
    
    def delete_folder(self, prefix: str) -> int:
        """
        Delete all files in a folder (prefix).
        
        Args:
            prefix: Folder prefix to delete (e.g., 'doc_id/')
            
        Returns:
            Number of files deleted
        """
        try:
            # List all objects with prefix
            objects = self.client.list_objects(
                bucket_name=self.bucket_name,
                prefix=prefix,
                recursive=True
            )
            
            # Delete all objects
            count = 0
            for obj in objects:
                self.client.remove_object(
                    bucket_name=self.bucket_name,
                    object_name=obj.object_name
                )
                count += 1
            
            logger.info(f"Deleted {count} files with prefix: {prefix}")
            return count
            
        except S3Error as e:
            logger.error(f"Error deleting folder {prefix}: {e}")
            raise
    
    def get_presigned_url(
        self,
        object_name: str,
        expires: timedelta = timedelta(hours=1)
    ) -> str:
        """
        Get a presigned URL for temporary access to a file.
        
        Args:
            object_name: Path/name of object in bucket
            expires: URL expiration time (default: 1 hour)
            
        Returns:
            Presigned URL
        """
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                expires=expires
            )
            logger.debug(f"Generated presigned URL for: {object_name}")
            return url
            
        except S3Error as e:
            logger.error(f"Error generating presigned URL for {object_name}: {e}")
            raise
    
    def get_file_metadata(self, object_name: str) -> Dict[str, Any]:
        """
        Get metadata for a file.
        
        Args:
            object_name: Path/name of object in bucket
            
        Returns:
            Dictionary with metadata (size, content_type, last_modified, etc.)
        """
        try:
            stat = self.client.stat_object(
                bucket_name=self.bucket_name,
                object_name=object_name
            )
            
            metadata = {
                "object_name": stat.object_name,
                "size": stat.size,
                "content_type": stat.content_type,
                "last_modified": stat.last_modified.isoformat() if stat.last_modified else None,
                "etag": stat.etag,
                "metadata": stat.metadata or {}
            }
            
            return metadata
            
        except S3Error as e:
            logger.error(f"Error getting metadata for {object_name}: {e}")
            raise


def create_minio_client(
    host: str,
    port: int,
    access_key: str,
    secret_key: str,
    bucket_name: str,
    secure: bool = False
) -> MinIOClient:
    """
    Factory function to create MinIO client.
    
    Args:
        host: MinIO server host
        port: MinIO server port
        access_key: Access key
        secret_key: Secret key
        bucket_name: Bucket name
        secure: Use HTTPS
        
    Returns:
        Configured MinIOClient instance
    """
    endpoint = f"{host}:{port}"
    return MinIOClient(
        endpoint=endpoint,
        access_key=access_key,
        secret_key=secret_key,
        bucket_name=bucket_name,
        secure=secure
    )
