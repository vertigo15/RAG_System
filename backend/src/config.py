"""
Application configuration using Pydantic settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "RAG System"
    app_env: str = Field(default="development")
    debug: bool = False
    log_level: str = Field(default="INFO")
    log_json: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # PostgreSQL
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "rag_system"
    postgres_user: str
    postgres_password: str
    
    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    # Qdrant
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    
    # RabbitMQ
    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    
    @property
    def rabbitmq_url(self) -> str:
        """Get RabbitMQ connection URL."""
        return (
            f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}"
            f"@{self.rabbitmq_host}:{self.rabbitmq_port}/"
        )
    
    # Azure OpenAI
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_embedding_deployment: str = "text-embedding-3-large"
    azure_llm_deployment: str = "gpt-4"
    
    # Azure Document Intelligence
    azure_doc_intelligence_endpoint: str
    azure_doc_intelligence_key: str
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # RAG Settings
    default_top_k: int = 10
    default_rerank_top: int = 5
    max_agent_iterations: int = 3
    chunk_size: int = 512
    chunk_overlap: int = 50
    enable_hybrid_search: bool = True
    enable_qa_matching: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings instance
    """
    return Settings()
