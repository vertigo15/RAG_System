"""
Base Chunker
Abstract base class for all chunking strategies.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from ..models.config import ChunkingConfig
from ..utils.tokenizer import Tokenizer

logger = logging.getLogger(__name__)


class BaseChunker(ABC):
    """
    Abstract base class for chunking strategies.
    
    Provides shared utilities and logging methods for all chunkers.
    """
    
    def __init__(self, config: ChunkingConfig = None):
        """
        Initialize base chunker.
        
        Args:
            config: Chunking configuration (uses defaults if not provided)
        """
        self.config = config or ChunkingConfig()
        self.tokenizer = Tokenizer(self.config.encoding_name)
        self._start_time: Optional[float] = None
    
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Return the strategy name for logging."""
        pass
    
    @abstractmethod
    def chunk(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, Any]]:
        """
        Chunk text into pieces.
        
        Args:
            text: Document text to chunk
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap size in tokens
            
        Returns:
            List of chunk dictionaries
        """
        pass
    
    def _log_chunking_start(self, text: str, doc_id: str = None) -> None:
        """
        Log start of chunking process.
        
        Args:
            text: Document text being chunked
            doc_id: Optional document ID for correlation
        """
        self._start_time = time.time()
        
        log_data = {
            "strategy": self.strategy_name,
            "text_length": len(text),
            "text_tokens": self.tokenizer.count_tokens(text),
            "config": {
                "chunk_size": self.config.chunk_size,
                "chunk_overlap": self.config.chunk_overlap
            }
        }
        
        if doc_id:
            log_data["doc_id"] = doc_id
        
        logger.info(
            f"Chunking started: strategy={self.strategy_name}, "
            f"text_length={len(text)}, text_tokens={log_data['text_tokens']}"
        )
        logger.debug(f"Chunking config: {log_data['config']}")
    
    def _log_chunking_complete(
        self,
        chunks: List[Dict[str, Any]],
        doc_id: str = None
    ) -> None:
        """
        Log completion of chunking process.
        
        Args:
            chunks: List of generated chunks
            doc_id: Optional document ID for correlation
        """
        duration_ms = int((time.time() - self._start_time) * 1000) if self._start_time else 0
        
        total_tokens = sum(c.get('token_count', 0) for c in chunks)
        chunk_sizes = [c.get('token_count', 0) for c in chunks]
        
        log_data = {
            "strategy": self.strategy_name,
            "total_chunks": len(chunks),
            "total_tokens": total_tokens,
            "avg_chunk_tokens": total_tokens // len(chunks) if chunks else 0,
            "min_chunk_tokens": min(chunk_sizes) if chunk_sizes else 0,
            "max_chunk_tokens": max(chunk_sizes) if chunk_sizes else 0,
            "duration_ms": duration_ms
        }
        
        if doc_id:
            log_data["doc_id"] = doc_id
        
        # Count chunks with overlap
        chunks_with_overlap = sum(1 for c in chunks if c.get('metadata', {}).get('has_overlap', False))
        if chunks_with_overlap > 0:
            log_data["chunks_with_overlap"] = chunks_with_overlap
        
        logger.info(
            f"Chunking completed: strategy={self.strategy_name}, "
            f"chunks={len(chunks)}, total_tokens={total_tokens}, "
            f"avg_tokens={log_data['avg_chunk_tokens']}, duration_ms={duration_ms}"
        )
    
    def _log_chunk_created(
        self,
        chunk_index: int,
        token_count: int,
        hierarchy_path: str = None,
        has_overlap: bool = False
    ) -> None:
        """
        Log creation of individual chunk.
        
        Args:
            chunk_index: Index of the chunk
            token_count: Number of tokens in chunk
            hierarchy_path: Optional hierarchy path
            has_overlap: Whether chunk has overlap
        """
        logger.debug(
            f"Chunk created: index={chunk_index}, tokens={token_count}, "
            f"hierarchy_path='{hierarchy_path or ''}', has_overlap={has_overlap}"
        )
    
    def _log_warning_chunk_size(
        self,
        chunk_index: int,
        actual_size: int
    ) -> None:
        """
        Log warning when chunk size is outside optimal range.
        
        Args:
            chunk_index: Index of the chunk
            actual_size: Actual chunk size in tokens
        """
        if actual_size < self.config.min_chunk_size:
            logger.warning(
                f"Chunk {chunk_index} below minimum size: "
                f"actual={actual_size}, min={self.config.min_chunk_size}"
            )
        elif actual_size > self.config.max_chunk_size:
            logger.warning(
                f"Chunk {chunk_index} above maximum size: "
                f"actual={actual_size}, max={self.config.max_chunk_size}"
            )
    
    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        return self.tokenizer.count_tokens(text)
    
    def _encode(self, text: str) -> List[int]:
        """
        Encode text to tokens.
        
        Args:
            text: Text to encode
            
        Returns:
            List of token IDs
        """
        return self.tokenizer.encode(text)
    
    def _decode(self, tokens: List[int]) -> str:
        """
        Decode tokens to text.
        
        Args:
            tokens: List of token IDs
            
        Returns:
            Decoded text
        """
        return self.tokenizer.decode(tokens)
