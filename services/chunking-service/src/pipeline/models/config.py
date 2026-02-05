"""
Chunking Configuration Model
Dataclass containing all chunking configuration parameters.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ChunkingConfig:
    """
    Configuration for chunking operations.
    
    All parameters can be overridden via settings or message payload.
    """
    
    # Basic chunking parameters
    chunk_size: int = 500
    chunk_overlap: int = 50
    min_chunk_size: int = 100
    max_chunk_size: int = 1000
    
    # Semantic chunker specific
    semantic_overlap_enabled: bool = True
    semantic_overlap_tokens: int = 50
    
    # Hierarchical chunker specific
    parent_chunk_multiplier: float = 2.0
    use_llm_for_parent_summary: bool = False
    parent_summary_max_length: int = 300
    
    # Auto-selection thresholds
    hierarchical_threshold_chars: int = 60000
    semantic_threshold_chars: int = 12000
    min_headers_for_semantic: int = 3
    
    # Tokenizer settings
    encoding_name: str = "cl100k_base"
    
    @classmethod
    def from_dict(cls, data: dict) -> "ChunkingConfig":
        """
        Create config from dictionary.
        
        Args:
            data: Dictionary with config values
            
        Returns:
            ChunkingConfig instance
        """
        # Filter to only known fields
        known_fields = {
            'chunk_size', 'chunk_overlap', 'min_chunk_size', 'max_chunk_size',
            'semantic_overlap_enabled', 'semantic_overlap_tokens',
            'parent_chunk_multiplier', 'use_llm_for_parent_summary',
            'parent_summary_max_length', 'hierarchical_threshold_chars',
            'semantic_threshold_chars', 'min_headers_for_semantic',
            'encoding_name'
        }
        
        filtered = {k: v for k, v in data.items() if k in known_fields and v is not None}
        return cls(**filtered)
    
    @classmethod
    def from_message(cls, message: dict) -> "ChunkingConfig":
        """
        Create config from RabbitMQ message payload.
        
        Args:
            message: Message dictionary from queue
            
        Returns:
            ChunkingConfig instance
        """
        config_data = {}
        
        # Map message fields to config fields
        if 'chunk_size' in message:
            config_data['chunk_size'] = message['chunk_size']
        if 'chunk_overlap' in message:
            config_data['chunk_overlap'] = message['chunk_overlap']
        if 'semantic_overlap_enabled' in message:
            config_data['semantic_overlap_enabled'] = message['semantic_overlap_enabled']
        if 'semantic_overlap_tokens' in message:
            config_data['semantic_overlap_tokens'] = message['semantic_overlap_tokens']
        if 'parent_chunk_multiplier' in message:
            config_data['parent_chunk_multiplier'] = message['parent_chunk_multiplier']
        if 'use_llm_for_parent_summary' in message:
            config_data['use_llm_for_parent_summary'] = message['use_llm_for_parent_summary']
        if 'parent_summary_max_length' in message:
            config_data['parent_summary_max_length'] = message['parent_summary_max_length']
        if 'hierarchical_threshold_chars' in message:
            config_data['hierarchical_threshold_chars'] = message['hierarchical_threshold_chars']
        if 'semantic_threshold_chars' in message:
            config_data['semantic_threshold_chars'] = message['semantic_threshold_chars']
        if 'min_headers_for_semantic' in message:
            config_data['min_headers_for_semantic'] = message['min_headers_for_semantic']
        
        return cls.from_dict(config_data)
    
    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'min_chunk_size': self.min_chunk_size,
            'max_chunk_size': self.max_chunk_size,
            'semantic_overlap_enabled': self.semantic_overlap_enabled,
            'semantic_overlap_tokens': self.semantic_overlap_tokens,
            'parent_chunk_multiplier': self.parent_chunk_multiplier,
            'use_llm_for_parent_summary': self.use_llm_for_parent_summary,
            'parent_summary_max_length': self.parent_summary_max_length,
            'hierarchical_threshold_chars': self.hierarchical_threshold_chars,
            'semantic_threshold_chars': self.semantic_threshold_chars,
            'min_headers_for_semantic': self.min_headers_for_semantic,
            'encoding_name': self.encoding_name
        }
    
    @property
    def parent_chunk_size(self) -> int:
        """Calculate parent chunk size based on multiplier."""
        return int(self.chunk_size * self.parent_chunk_multiplier)
