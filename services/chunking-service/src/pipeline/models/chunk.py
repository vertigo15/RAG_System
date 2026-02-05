"""
Chunk Model
Dataclass representing a document chunk with metadata.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum


class ChunkType(str, Enum):
    """Type of chunk in hierarchical chunking."""
    PARENT = "parent"
    CHILD = "child"
    STANDALONE = "standalone"  # For simple/semantic chunking


@dataclass
class Chunk:
    """
    Represents a document chunk with all metadata.
    
    Attributes:
        text: The chunk content
        chunk_index: Index of chunk within document
        token_count: Number of tokens in chunk
        hierarchy_path: Document hierarchy path (e.g., "Chapter 1 > Section 1.1")
        section_title: Title of the section this chunk belongs to
        strategy: Chunking strategy used ("simple", "semantic", "hierarchical")
        chunk_type: Type of chunk (parent, child, standalone)
        parent_id: ID of parent chunk (for hierarchical chunking)
        parent_summary: Summary of parent section (for child chunks)
        has_overlap: Whether chunk has overlap from previous chunk
        overlap_tokens: Number of overlap tokens if has_overlap
        start_token: Starting token index in original document
        end_token: Ending token index in original document
        metadata: Additional metadata dictionary
    """
    
    text: str
    chunk_index: int
    token_count: int = 0
    
    # Hierarchy information
    hierarchy_path: Optional[str] = None
    section_title: Optional[str] = None
    
    # Chunking metadata
    strategy: str = "simple"
    chunk_type: ChunkType = ChunkType.STANDALONE
    
    # Parent-child relationships (hierarchical)
    parent_id: Optional[str] = None
    parent_summary: Optional[str] = None
    
    # Overlap information
    has_overlap: bool = False
    overlap_tokens: int = 0
    
    # Position information
    start_token: Optional[int] = None
    end_token: Optional[int] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert chunk to dictionary format.
        
        Returns:
            Dictionary representation of chunk
        """
        return {
            "text": self.text,
            "chunk_index": self.chunk_index,
            "token_count": self.token_count,
            "hierarchy_path": self.hierarchy_path,
            "section_title": self.section_title,
            "metadata": {
                "chunking_strategy": self.strategy,
                "chunk_type": self.chunk_type.value if isinstance(self.chunk_type, ChunkType) else self.chunk_type,
                "parent_id": self.parent_id,
                "parent_summary": self.parent_summary,
                "has_overlap": self.has_overlap,
                "overlap_tokens": self.overlap_tokens,
                "start_token": self.start_token,
                "end_token": self.end_token,
                **self.metadata
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Chunk":
        """
        Create Chunk from dictionary.
        
        Args:
            data: Dictionary with chunk data
            
        Returns:
            Chunk instance
        """
        metadata = data.get("metadata", {})
        
        return cls(
            text=data.get("text", ""),
            chunk_index=data.get("chunk_index", 0),
            token_count=data.get("token_count", 0),
            hierarchy_path=data.get("hierarchy_path"),
            section_title=data.get("section_title"),
            strategy=metadata.get("chunking_strategy", "simple"),
            chunk_type=ChunkType(metadata.get("chunk_type", "standalone")),
            parent_id=metadata.get("parent_id"),
            parent_summary=metadata.get("parent_summary"),
            has_overlap=metadata.get("has_overlap", False),
            overlap_tokens=metadata.get("overlap_tokens", 0),
            start_token=metadata.get("start_token"),
            end_token=metadata.get("end_token"),
            metadata={k: v for k, v in metadata.items() 
                     if k not in {'chunking_strategy', 'chunk_type', 'parent_id', 
                                  'parent_summary', 'has_overlap', 'overlap_tokens',
                                  'start_token', 'end_token'}}
        )
