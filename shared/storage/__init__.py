"""Shared storage clients for the RAG system."""

from .minio_client import MinIOClient, create_minio_client

__all__ = ["MinIOClient", "create_minio_client"]
