"""
Hierarchical Chunker
Parent-child chunking with context preservation.
"""

import logging
from typing import List, Dict
import tiktoken

logger = logging.getLogger(__name__)


class HierarchicalChunker:
    """Hierarchical parent-child chunking strategy."""
    
    def __init__(self, encoding_name: str = "cl100k_base"):
        self.encoding = tiktoken.get_encoding(encoding_name)
    
    def chunk(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, any]]:
        """
        Create hierarchical parent-child chunks.
        
        Parent chunks: Larger context (2x chunk_size)
        Child chunks: Regular size with parent reference
        
        Args:
            text: Document text
            chunk_size: Target size for child chunks
            chunk_overlap: Overlap size in tokens
        
        Returns:
            List of chunks with parent-child relationships
        """
        logger.info(f"Hierarchical chunking: size={chunk_size}, overlap={chunk_overlap}")
        
        # Parent chunk size is 2x child size
        parent_size = chunk_size * 2
        
        # Create parent chunks first
        parent_chunks = self._create_parent_chunks(text, parent_size, chunk_overlap)
        
        logger.info(f"Created {len(parent_chunks)} parent chunks")
        
        # Create child chunks within each parent
        all_chunks = []
        global_chunk_index = 0
        
        for parent_idx, parent_chunk in enumerate(parent_chunks):
            parent_text = parent_chunk["text"]
            
            # Create child chunks from parent text
            child_chunks = self._create_child_chunks(
                parent_text,
                chunk_size,
                chunk_overlap,
                parent_idx,
                global_chunk_index
            )
            
            # Add parent chunk (marked as parent)
            parent_chunk["chunk_type"] = "parent"
            parent_chunk["parent_id"] = None
            parent_chunk["chunk_index"] = f"parent_{parent_idx}"
            all_chunks.append(parent_chunk)
            
            # Add child chunks
            for child in child_chunks:
                child["chunk_type"] = "child"
                child["parent_id"] = f"parent_{parent_idx}"
                all_chunks.append(child)
                global_chunk_index += 1
        
        logger.info(
            f"Created {len(all_chunks)} total chunks "
            f"({len(parent_chunks)} parents, {len(all_chunks) - len(parent_chunks)} children)"
        )
        
        return all_chunks
    
    def _create_parent_chunks(
        self,
        text: str,
        parent_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, any]]:
        """Create parent chunks (larger context)."""
        tokens = self.encoding.encode(text)
        total_tokens = len(tokens)
        
        chunks = []
        start_idx = 0
        
        while start_idx < total_tokens:
            end_idx = min(start_idx + parent_size, total_tokens)
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            chunk = {
                "text": chunk_text,
                "token_count": len(chunk_tokens),
                "start_token": start_idx,
                "end_token": end_idx,
                "metadata": {
                    "chunking_strategy": "hierarchical",
                    "chunk_size": parent_size,
                    "chunk_overlap": chunk_overlap
                }
            }
            
            chunks.append(chunk)
            start_idx += parent_size - chunk_overlap
        
        return chunks
    
    def _create_child_chunks(
        self,
        parent_text: str,
        chunk_size: int,
        chunk_overlap: int,
        parent_idx: int,
        start_global_idx: int
    ) -> List[Dict[str, any]]:
        """Create child chunks within a parent."""
        tokens = self.encoding.encode(parent_text)
        total_tokens = len(tokens)
        
        chunks = []
        start_idx = 0
        local_chunk_idx = 0
        
        while start_idx < total_tokens:
            end_idx = min(start_idx + chunk_size, total_tokens)
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            chunk = {
                "text": chunk_text,
                "chunk_index": start_global_idx + local_chunk_idx,
                "token_count": len(chunk_tokens),
                "start_token": start_idx,
                "end_token": end_idx,
                "metadata": {
                    "chunking_strategy": "hierarchical",
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                    "parent_index": parent_idx,
                    "local_index": local_chunk_idx
                }
            }
            
            chunks.append(chunk)
            local_chunk_idx += 1
            start_idx += chunk_size - chunk_overlap
        
        return chunks
