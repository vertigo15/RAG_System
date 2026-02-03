#!/bin/bash
# MinIO Bucket Initialization Script
# This script creates the required buckets for the RAG system

set -e

echo "Waiting for MinIO to be ready..."
sleep 5

# Configure MinIO client (mc)
mc alias set local http://localhost:9000 ${MINIO_ROOT_USER:-minioadmin} ${MINIO_ROOT_PASSWORD:-minioadmin}

# Create documents bucket if it doesn't exist
if ! mc ls local/documents > /dev/null 2>&1; then
    echo "Creating 'documents' bucket..."
    mc mb local/documents
    echo "Setting bucket policy to allow read/write..."
    mc anonymous set download local/documents
    echo "Bucket 'documents' created successfully!"
else
    echo "Bucket 'documents' already exists."
fi

echo "MinIO initialization complete!"
