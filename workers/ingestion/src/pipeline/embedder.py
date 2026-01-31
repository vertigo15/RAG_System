import logging
from typing import List, Dict, Any
from openai import AsyncAzureOpenAI

logger = logging.getLogger(__name__)

class Embedder:
    """Generate embeddings using Azure OpenAI text-embedding-3-large"""
    
    def __init__(self, endpoint: str, api_key: str, deployment: str, api_version: str):
        self.client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self.deployment = deployment
        self.dimension = 3072  # text-embedding-3-large dimension
    
    async def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for all chunks
        
        Args:
            chunks: List of chunks from Chunker
        
        Returns:
            chunks with added "embedding" field
        """
        logger.info(f"Generating embeddings for {len(chunks)} chunks")
        
        # Extract texts
        texts = [chunk.get("text", "") for chunk in chunks]
        
        # Generate embeddings in batches
        batch_size = 50
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = await self._embed_batch(batch)
            all_embeddings.extend(embeddings)
        
        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, all_embeddings):
            chunk["embedding"] = embedding
        
        logger.info(f"Generated {len(all_embeddings)} embeddings")
        return chunks
    
    async def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        try:
            response = await self.client.embeddings.create(
                model=self.deployment,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            return embeddings
        
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            # Return zero vectors as fallback
            return [[0.0] * self.dimension for _ in texts]
