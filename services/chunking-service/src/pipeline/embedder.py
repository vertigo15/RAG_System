"""
Embedder
Generate embeddings with batching for efficiency.
"""

import logging
from typing import List, Dict
from openai import AzureOpenAI
import time

logger = logging.getLogger(__name__)


class Embedder:
    """Generate embeddings using Azure OpenAI with batching."""
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        api_version: str,
        deployment_name: str,
        batch_size: int = 20
    ):
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self.deployment_name = deployment_name
        self.batch_size = batch_size
        
        logger.info(f"Embedder initialized with batch size: {batch_size}")
    
    def embed_chunks(
        self,
        chunks: List[Dict[str, any]]
    ) -> List[Dict[str, any]]:
        """
        Generate embeddings for chunks with batching.
        
        Args:
            chunks: List of chunk dictionaries
        
        Returns:
            List of chunks with added 'embedding' field
        """
        total_chunks = len(chunks)
        logger.info(f"Embedding {total_chunks} chunks")
        
        # Process in batches
        embedded_chunks = []
        
        for i in range(0, total_chunks, self.batch_size):
            batch = chunks[i:i + self.batch_size]
            batch_texts = [chunk["text"] for chunk in batch]
            
            logger.info(f"Embedding batch {i // self.batch_size + 1}/{(total_chunks + self.batch_size - 1) // self.batch_size}")
            
            try:
                # Generate embeddings for batch
                embeddings = self._embed_batch(batch_texts)
                
                # Add embeddings to chunks
                for chunk, embedding in zip(batch, embeddings):
                    chunk["embedding"] = embedding
                    embedded_chunks.append(chunk)
                
                # Small delay to avoid rate limits
                if i + self.batch_size < total_chunks:
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error embedding batch at index {i}: {e}")
                raise
        
        logger.info(f"Successfully embedded {len(embedded_chunks)} chunks")
        return embedded_chunks
    
    def embed_single(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model=self.deployment_name,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating single embedding: {e}")
            raise
    
    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embedding vectors
        """
        try:
            # Truncate very long texts (embedding models have limits)
            max_length = 8000  # Conservative limit for text-embedding-3-large
            truncated_texts = [
                text[:max_length] if len(text) > max_length else text
                for text in texts
            ]
            
            response = self.client.embeddings.create(
                model=self.deployment_name,
                input=truncated_texts
            )
            
            # Extract embeddings in order
            embeddings = [item.embedding for item in response.data]
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error in batch embedding: {e}")
            raise
    
    def embed_summary_and_qa(
        self,
        summary: str,
        qa_pairs: List[Dict[str, str]]
    ) -> tuple[List[float], List[Dict[str, any]]]:
        """
        Generate embeddings for summary and Q&A pairs.
        
        Args:
            summary: Document summary text
            qa_pairs: List of Q&A pair dictionaries
        
        Returns:
            Tuple of (summary_embedding, qa_pairs_with_embeddings)
        """
        logger.info(f"Embedding summary and {len(qa_pairs)} Q&A pairs")
        
        try:
            # Embed summary
            summary_embedding = self.embed_single(summary)
            
            # Embed Q&A pairs (both questions and answers)
            qa_with_embeddings = []
            
            for qa in qa_pairs:
                question = qa.get("question", "")
                answer = qa.get("answer", "")
                
                # Embed question and answer separately
                question_embedding = self.embed_single(question)
                answer_embedding = self.embed_single(answer)
                
                qa_with_embeddings.append({
                    **qa,
                    "question_embedding": question_embedding,
                    "answer_embedding": answer_embedding
                })
                
                # Small delay
                time.sleep(0.05)
            
            logger.info("Summary and Q&A embeddings complete")
            return summary_embedding, qa_with_embeddings
            
        except Exception as e:
            logger.error(f"Error embedding summary/Q&A: {e}")
            raise
