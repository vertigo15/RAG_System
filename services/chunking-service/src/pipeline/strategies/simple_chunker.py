"""
Simple Chunker
Fixed-size chunking by token count with overlap.

Features:
- Fixed-size token-based chunking
- Configurable overlap between chunks
- Detailed logging for debugging
"""

import logging
from typing import List, Dict, Any

from .base import BaseChunker
from ..models.config import ChunkingConfig
from ..models.chunk import ChunkType

logger = logging.getLogger(__name__)


class SimpleChunker(BaseChunker):
    """
    Simple fixed-size chunking strategy.
    
    Features:
    - Fixed-size token-based chunking
    - Configurable overlap between chunks
    - hierarchy_path set to None (no structure tracking)
    """
    
    def __init__(self, config: ChunkingConfig = None):
        """
        Initialize simple chunker.
        
        Args:
            config: Chunking configuration
        """
        super().__init__(config)
    
    @property
    def strategy_name(self) -> str:
        return "simple"
    
    def chunk(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, Any]]:
        """
        Chunk text into fixed-size pieces with overlap.
        
        Args:
            text: Document text
            chunk_size: Target size in tokens
            chunk_overlap: Overlap size in tokens
        
        Returns:
            List of chunks with metadata
        """
        self._log_chunking_start(text)
        
        # Tokenize the entire text
        tokens = self._encode(text)
        total_tokens = len(tokens)
        
        logger.debug(f"Total tokens to chunk: {total_tokens}")
        
        chunks = []
        start_idx = 0
        chunk_index = 0
        
        while start_idx < total_tokens:
            # Define end index
            end_idx = min(start_idx + chunk_size, total_tokens)
            
            # Get chunk tokens
            chunk_tokens = tokens[start_idx:end_idx]
            
            # Decode back to text
            chunk_text = self._decode(chunk_tokens)
            
            # Create chunk with metadata
            chunk = {
                "text": chunk_text,
                "chunk_index": chunk_index,
                "token_count": len(chunk_tokens),
                "hierarchy_path": None,  # Simple chunker doesn't track structure
                "section_title": None,
                "metadata": {
                    "chunking_strategy": "simple",
                    "chunk_type": ChunkType.STANDALONE.value,
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                    "start_token": start_idx,
                    "end_token": end_idx,
                    "has_overlap": chunk_index > 0 and chunk_overlap > 0,
                    "overlap_tokens": chunk_overlap if chunk_index > 0 else 0
                }
            }
            
            # Log chunk creation
            self._log_chunk_created(
                chunk_index=chunk_index,
                token_count=len(chunk_tokens),
                hierarchy_path=None,
                has_overlap=chunk_index > 0 and chunk_overlap > 0
            )
            
            # Warn if chunk size outside optimal range
            self._log_warning_chunk_size(chunk_index, len(chunk_tokens))
            
            chunks.append(chunk)
            chunk_index += 1
            
            # Move start index (with overlap)
            start_idx += chunk_size - chunk_overlap
            
            # Prevent infinite loop
            if chunk_size <= chunk_overlap:
                logger.warning("Chunk size <= overlap, stopping to prevent infinite loop")
                break
        
        self._log_chunking_complete(chunks)
        return chunks
