import logging
from typing import List, Dict, Any
from openai import AsyncAzureOpenAI

logger = logging.getLogger(__name__)

class Reranker:
    """Rerank retrieved chunks using LLM-based relevance scoring"""
    
    def __init__(self, endpoint: str, api_key: str, deployment: str, api_version: str):
        self.client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self.deployment = deployment
    
    async def rerank(self, query: str, chunks: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Rerank chunks by relevance to query using LLM
        
        Args:
            query: User query
            chunks: Retrieved chunks
            top_k: Number of top chunks to return
        
        Returns:
            Top K reranked chunks
        """
        logger.info(f"Reranking {len(chunks)} chunks to top {top_k}")
        
        if not chunks:
            return []
        
        try:
            # Create prompt for reranking
            chunks_text = "\n\n".join([
                f"[{i}] {chunk.get('text', '')[:500]}"
                for i, chunk in enumerate(chunks)
            ])
            
            prompt = f"""Given the query and document chunks below, rank the chunks by relevance to the query.
Output only the indices of the top {top_k} most relevant chunks, in order, separated by commas.

Query: {query}

Chunks:
{chunks_text}

Top {top_k} most relevant chunk indices (comma-separated):"""
            
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are a relevance ranking assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0
            )
            
            # Parse indices
            result_text = response.choices[0].message.content.strip()
            indices_str = result_text.split(",")
            
            reranked = []
            for idx_str in indices_str:
                try:
                    idx = int(idx_str.strip())
                    if 0 <= idx < len(chunks):
                        chunk = chunks[idx].copy()
                        chunk["rerank_position"] = len(reranked) + 1
                        reranked.append(chunk)
                except ValueError:
                    continue
            
            # Fallback: if reranking failed, return top K by original score
            if not reranked:
                logger.warning("Reranking failed, falling back to original order")
                reranked = chunks[:top_k]
            
            logger.info(f"Reranked to {len(reranked)} chunks")
            return reranked[:top_k]
        
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            # Fallback to original order
            return chunks[:top_k]
