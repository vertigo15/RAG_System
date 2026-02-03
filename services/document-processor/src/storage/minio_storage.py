"""
MinIO Storage Wrapper
Wraps shared MinIO client with document-specific operations.
"""

import logging
import sys
from pathlib import Path

# Add shared modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "shared"))

from shared.storage.minio_client import create_minio_client, MinIOClient

logger = logging.getLogger(__name__)


class MinIOStorage:
    """MinIO storage operations for Document Processor."""
    
    def __init__(self, client: MinIOClient):
        self.client = client
    
    def store_document_files(
        self,
        doc_id: str,
        original_file_path: str,
        markdown: str,
        metadata: dict,
        summary: str,
        qa_pairs: list
    ) -> str:
        """
        Store all document files in MinIO.
        
        Args:
            doc_id: Document UUID
            original_file_path: Path to original uploaded file
            markdown: Converted markdown
            metadata: Document metadata
            summary: Generated summary
            qa_pairs: Generated Q&A pairs
        
        Returns:
            MinIO path (prefix) for the document
        """
        minio_path = f"{doc_id}/"
        
        logger.info(f"Storing document files to MinIO: {minio_path}")
        
        try:
            # 1. Store original file
            original_ext = Path(original_file_path).suffix
            with open(original_file_path, 'rb') as f:
                self.client.store_file(
                    object_name=f"{minio_path}original{original_ext}",
                    data=f,
                    content_type=metadata.get("mime_type", "application/octet-stream")
                )
            
            # 2. Store markdown
            self.client.store_file(
                object_name=f"{minio_path}document.md",
                data=markdown,
                content_type="text/markdown"
            )
            
            # 3. Store metadata
            self.client.store_json(
                object_name=f"{minio_path}metadata.json",
                data=metadata
            )
            
            # 4. Store summary
            self.client.store_file(
                object_name=f"{minio_path}summary.md",
                data=summary,
                content_type="text/markdown"
            )
            
            # 5. Store Q&A pairs
            self.client.store_json(
                object_name=f"{minio_path}qa_pairs.json",
                data={"qa_pairs": qa_pairs}
            )
            
            logger.info(f"Successfully stored all files to MinIO: {minio_path}")
            return minio_path
            
        except Exception as e:
            logger.error(f"Failed to store files to MinIO: {e}")
            raise


def create_minio_storage(
    host: str,
    port: int,
    access_key: str,
    secret_key: str,
    bucket_name: str,
    secure: bool = False
) -> MinIOStorage:
    """Create MinIOStorage instance."""
    client = create_minio_client(
        host=host,
        port=port,
        access_key=access_key,
        secret_key=secret_key,
        bucket_name=bucket_name,
        secure=secure
    )
    return MinIOStorage(client)
