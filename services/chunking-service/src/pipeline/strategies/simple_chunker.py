"""
Simple Chunker
Fixed-size chunking by token count with overlap.
"""

import logging
from typing import List, Dict
import tiktoken

logger = logging.getLogger(__name__)


class SimpleChunker:
    """Simple fixed-size chunking strategy."""
    
    def __init__(self, encoding_name: str = "cl100k_base"):
        self.encoding = tiktoken.get_encoding(encoding_name)
    
    def chunk(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, any]]:
        """
        Chunk text into fixed-size pieces with overlap.
        
        Args:
            text: Document text
            chunk_size: Target size in tokens
            chunk_overlap: Overlap size in tokens
        
        Returns:
            List of chunks with metadata
        """
        logger.info(f"Simple chunking: size={chunk_size}, overlap={chunk_overlap}")
        
        # Tokenize the entire text
        tokens = self.encoding.encode(text)
        total_tokens = len(tokens)
        
        logger.info(f"Total tokens: {total_tokens}")
        
        chunks = []
        start_idx = 0
        chunk_index = 0
        
        while start_idx < total_tokens:
            # Define end index
            end_idx = min(start_idx + chunk_size, total_tokens)
            
            # Get chunk tokens
            chunk_tokens = tokens[start_idx:end_idx]
            
            # Decode back to text
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Create chunk metadata
            chunk = {
                "text": chunk_text,
                "chunk_index": chunk_index,
                "token_count": len(chunk_tokens),
                "start_token": start_idx,
                "end_token": end_idx,
                "metadata": {
                    "chunking_strategy": "simple",
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap
                }
            }
            
            chunks.append(chunk)
            chunk_index += 1
            
            # Move start index (with overlap)
            start_idx += chunk_size - chunk_overlap
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
