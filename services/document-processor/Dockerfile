FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY services/document-processor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY shared /app/shared

# Copy application code
COPY services/document-processor/src /app/src

# Set Python path to include shared modules
ENV PYTHONPATH=/app:$PYTHONPATH

CMD ["python", "src/main.py"]
