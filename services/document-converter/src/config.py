"""
Configuration module for Document Converter Service.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Document Converter service settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application
    app_env: str = "development"
    log_level: str = "INFO"
    log_json: bool = True
    
    # PostgreSQL (for status updates)
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "rag_system"
    postgres_user: str
    postgres_password: str
    
    # RabbitMQ
    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    document_processing_queue: str = "ingestion_queue"
    chunking_queue: str = "chunking_queue"
    
    # MinIO
    minio_host: str = "minio"
    minio_port: int = 9000
    minio_root_user: str = "minioadmin"
    minio_root_password: str = "minioadmin"
    minio_bucket: str = "documents"
    minio_secure: bool = False
    
    # Azure Document Intelligence
    azure_doc_intelligence_endpoint: str
    azure_doc_intelligence_key: str
    
    # Azure OpenAI
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_api_version: str = "2024-02-01"
    azure_openai_vision_deployment: Optional[str] = None  # Defaults to LLM deployment
    azure_llm_deployment: str = "gpt-4"
    
    # Feature flags
    enable_image_descriptions: bool = True
    enable_table_summaries: bool = True
    
    # Limits
    max_file_size_mb: int = 100
    table_summary_threshold_rows: int = 50
    
    # Timeouts (seconds)
    doc_intelligence_timeout: int = 120
    openai_timeout: int = 30
    conversion_timeout: int = 300
    
    # Concurrency
    max_concurrent_image_processing: int = 5
    
    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    @property
    def rabbitmq_url(self) -> str:
        """Get RabbitMQ connection URL."""
        return (
            f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}"
            f"@{self.rabbitmq_host}:{self.rabbitmq_port}/"
        )
    
    @property
    def vision_deployment(self) -> str:
        """Get vision deployment name, defaults to LLM deployment."""
        return self.azure_openai_vision_deployment or self.azure_llm_deployment


# Global settings instance
settings = Settings()
