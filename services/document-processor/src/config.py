"""
Configuration module for Document Processor Service.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Document Processor service settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application
    app_env: str = "development"
    log_level: str = "INFO"
    log_json: bool = True
    
    # PostgreSQL
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
    azure_llm_deployment: str = "gpt-4"
    
    # Processing Configuration
    small_doc_threshold: int = 3000  # tokens
    medium_doc_threshold: int = 20000  # tokens
    large_doc_threshold: int = 60000  # tokens
    
    # Language detection sampling
    lang_sample_points_small: int = 1  # Direct full text
    lang_sample_points_medium: int = 3  # Beginning, middle, end
    lang_sample_points_large: int = 5  # More sampling points
    
    # Summary generation
    summary_num_questions_small: int = 8
    summary_num_questions_medium: int = 12
    summary_num_questions_large: int = 15
    
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


# Global settings instance
settings = Settings()
