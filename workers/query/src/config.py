import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuration for query worker"""
    
    # RabbitMQ
    rabbitmq_host: str = os.getenv("RABBITMQ_HOST", "rabbitmq")
    rabbitmq_port: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    rabbitmq_user: str = os.getenv("RABBITMQ_USER", "guest")
    rabbitmq_password: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    
    # PostgreSQL
    postgres_host: str = os.getenv("POSTGRES_HOST", "postgres")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5433"))
    postgres_db: str = os.getenv("POSTGRES_DB", "rag_system")
    postgres_user: str = os.getenv("POSTGRES_USER", "admin")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "admin")
    
    # Qdrant
    qdrant_host: str = os.getenv("QDRANT_HOST", "qdrant")
    qdrant_port: int = int(os.getenv("QDRANT_PORT", "6333"))
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "documents")
    
    # Azure OpenAI
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_key: str = os.getenv("AZURE_OPENAI_KEY", "")
    azure_openai_deployment_gpt4: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_GPT4", "gpt-4")
    azure_openai_deployment_embed: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_EMBED", "text-embedding-3-large")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    
    # RAG Settings
    retrieval_top_k: int = int(os.getenv("RETRIEVAL_TOP_K", "20"))
    reranking_top_k: int = int(os.getenv("RERANKING_TOP_K", "5"))
    rrf_k: int = int(os.getenv("RRF_K", "60"))
    agent_max_iterations: int = int(os.getenv("AGENT_MAX_ITERATIONS", "3"))
    
    @property
    def postgres_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def rabbitmq_url(self) -> str:
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@{self.rabbitmq_host}:{self.rabbitmq_port}/"
    
    class Config:
        env_file = ".env"

settings = Settings()
