import logging
from typing import List
from openai import AsyncAzureOpenAI

logger = logging.getLogger(__name__)

class QueryEmbedder:
    """Generate query embeddings"""
    
    def __init__(self, endpoint: str, api_key: str, deployment: str, api_version: str):
        self.client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self.deployment = deployment
    
    async def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query"""
        try:
            response = await self.client.embeddings.create(
                model=self.deployment,
                input=[query]
            )
            
            return response.data[0].embedding
        
        except Exception as e:
            logger.error(f"Query embedding failed: {e}")
            raise
