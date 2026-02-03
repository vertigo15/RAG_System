"""
MinIO Storage Wrapper
Wraps shared MinIO client for Chunking Service operations.
"""

import logging
import sys
from pathlib import Path

# Add shared modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "shared"))

from shared.storage.minio_client import create_minio_client

logger = logging.getLogger(__name__)


def create_minio_storage(
    host: str,
    port: int,
    access_key: str,
    secret_key: str,
    bucket_name: str,
    secure: bool = False
):
    """Create MinIO client for Chunking Service."""
    return create_minio_client(
        host=host,
        port=port,
        access_key=access_key,
        secret_key=secret_key,
        bucket_name=bucket_name,
        secure=secure
    )
