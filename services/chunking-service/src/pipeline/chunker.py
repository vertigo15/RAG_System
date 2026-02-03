"""
Chunker Orchestrator
Routes to appropriate chunking strategy.
"""

import logging
from typing import List, Dict

from .strategies.simple_chunker import SimpleChunker
from .strategies.semantic_chunker import SemanticChunker
from .strategies.hierarchical_chunker import HierarchicalChunker

logger = logging.getLogger(__name__)


class Chunker:
    """Orchestrator for chunking strategies."""
    
    def __init__(self):
        self.simple_chunker = SimpleChunker()
        self.semantic_chunker = SemanticChunker()
        self.hierarchical_chunker = HierarchicalChunker()
    
    def chunk(
        self,
        text: str,
        strategy: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, any]]:
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
            logger.info(f"Auto-selected strategy: {strategy}")
        
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
        
        Logic:
        - If text has clear sections (markdown headers), use semantic
        - If text is very long (>60k tokens estimated), use hierarchical
        - Otherwise, use simple
        """
        # Estimate token count (rough: 4 chars per token)
        estimated_tokens = len(text) / 4
        
        # Check for markdown headers
        has_sections = "# " in text or "## " in text
        
        if estimated_tokens > 15000:  # ~60k chars
            return "hierarchical"
        elif has_sections and estimated_tokens > 3000:
            return "semantic"
        else:
            return "simple"
