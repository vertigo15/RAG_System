"""
Chunker Orchestrator
Routes to appropriate chunking strategy.

Features:
- Auto-selection based on document structure and size
- Configurable via ChunkingConfig
- Detailed logging for strategy selection
"""

import logging
from typing import List, Dict, Any, Optional

from .strategies.simple_chunker import SimpleChunker
from .strategies.semantic_chunker import SemanticChunker
from .strategies.hierarchical_chunker import HierarchicalChunker
from .models.config import ChunkingConfig
from .utils.markdown_parser import MarkdownParser

logger = logging.getLogger(__name__)


class Chunker:
    """
    Orchestrator for chunking strategies.
    
    Features:
    - Routes to appropriate strategy based on configuration
    - Auto-selection considers document structure quality
    - Passes configuration to all strategies
    """
    
    def __init__(self, config: ChunkingConfig = None):
        """
        Initialize chunker with configuration.
        
        Args:
            config: Chunking configuration (uses defaults if not provided)
        """
        self.config = config or ChunkingConfig()
        self.markdown_parser = MarkdownParser()
        
        # Initialize strategies with config
        self.simple_chunker = SimpleChunker(self.config)
        self.semantic_chunker = SemanticChunker(self.config)
        self.hierarchical_chunker = HierarchicalChunker(self.config)
        
        logger.debug("Chunker orchestrator initialized")
    
    def chunk(
        self,
        text: str,
        strategy: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, Any]]:
        """
        Chunk text using specified strategy.
        
        Args:
            text: Document text (markdown)
            strategy: "simple", "semantic", "hierarchical", or "auto"
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap size in tokens
        
        Returns:
            List of chunks with metadata
        """
        # Auto-select strategy if needed
        if strategy == "auto":
            strategy = self._auto_select_strategy(text)
        
        logger.info(
            f"Chunking with strategy='{strategy}', "
            f"chunk_size={chunk_size}, chunk_overlap={chunk_overlap}"
        )
        
        # Route to appropriate chunker
        if strategy == "simple":
            return self.simple_chunker.chunk(text, chunk_size, chunk_overlap)
        elif strategy == "semantic":
            return self.semantic_chunker.chunk(text, chunk_size, chunk_overlap)
        elif strategy == "hierarchical":
            return self.hierarchical_chunker.chunk(text, chunk_size, chunk_overlap)
        else:
            logger.warning(f"Unknown strategy: {strategy}, falling back to simple")
            return self.simple_chunker.chunk(text, chunk_size, chunk_overlap)
    
    def _auto_select_strategy(self, text: str) -> str:
        """
        Auto-select chunking strategy based on text characteristics.
        
        Improved logic:
        1. Check document structure quality (header count)
        2. Check document size (character count)
        3. Select appropriate strategy
        
        Returns:
            Strategy name: "simple", "semantic", or "hierarchical"
        """
        text_length = len(text)
        
        # Count markdown headers for structure quality
        header_count = self.markdown_parser.count_headers(text)
        has_good_structure = header_count >= self.config.min_headers_for_semantic
        
        # Get header levels for logging
        header_levels = self.markdown_parser.get_header_levels(text)
        
        # Selection logic
        if text_length > self.config.hierarchical_threshold_chars:
            selected = "hierarchical"
            reason = f"document_size ({text_length} chars) > threshold ({self.config.hierarchical_threshold_chars})"
        elif has_good_structure and text_length > self.config.semantic_threshold_chars:
            selected = "semantic"
            reason = f"good_structure ({header_count} headers) AND size > {self.config.semantic_threshold_chars}"
        elif has_good_structure and text_length > 3000:
            selected = "semantic"
            reason = f"good_structure ({header_count} headers) AND medium size ({text_length} chars)"
        else:
            selected = "simple"
            reason = "small_document OR no_clear_structure"
        
        logger.info(
            f"Auto-selected strategy: '{selected}' "
            f"(reason: {reason}, headers={header_count}, levels={header_levels})"
        )
        
        return selected
    
    def update_config(self, config: ChunkingConfig) -> None:
        """
        Update configuration for all strategies.
        
        Args:
            config: New chunking configuration
        """
        self.config = config
        self.simple_chunker = SimpleChunker(config)
        self.semantic_chunker = SemanticChunker(config)
        self.hierarchical_chunker = HierarchicalChunker(config)
        logger.debug("Chunker configuration updated")
