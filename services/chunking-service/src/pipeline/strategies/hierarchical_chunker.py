"""
Hierarchical Chunker
Parent-child chunking with context preservation.

Features:
- Parent chunks contain SUMMARIES (not raw content) for context
- Child chunks contain actual content with parent reference
- Hierarchy path tracking for document structure
- Parent summary attached to each child for retrieval context
"""

import logging
import re
from typing import List, Dict, Any, Optional

from .base import BaseChunker
from ..models.config import ChunkingConfig
from ..models.chunk import ChunkType
from ..utils.markdown_parser import MarkdownParser, Section
from ..utils.hierarchy_builder import HierarchyBuilder

logger = logging.getLogger(__name__)


class HierarchicalChunker(BaseChunker):
    """
    Hierarchical parent-child chunking strategy.
    
    Features:
    - Parent chunks: SUMMARIES of sections (first paragraph, not raw content)
    - Child chunks: Actual content with parent_id and parent_summary
    - Hierarchy path tracking from document structure
    - Configurable parent summary length
    """
    
    def __init__(self, config: ChunkingConfig = None):
        """
        Initialize hierarchical chunker.
        
        Args:
            config: Chunking configuration
        """
        super().__init__(config)
        self.markdown_parser = MarkdownParser()
        self.hierarchy_builder = HierarchyBuilder()
    
    @property
    def strategy_name(self) -> str:
        return "hierarchical"
    
    def chunk(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, Any]]:
        """
        Create hierarchical parent-child chunks.
        
        Parent chunks: Summaries of sections (provides context)
        Child chunks: Actual content with parent reference
        
        Args:
            text: Document text
            chunk_size: Target size for child chunks
            chunk_overlap: Overlap size in tokens
        
        Returns:
            List of chunks with parent-child relationships
        """
        self._log_chunking_start(text)
        
        # Parse document structure
        logger.debug("Parsing markdown structure for hierarchical chunking")
        sections = self.markdown_parser.parse(text)
        logger.debug(f"Found {len(sections)} sections")
        
        all_chunks = []
        global_child_index = 0
        
        # Process each major section
        for section_idx, section in enumerate(sections):
            # Build full section text
            section_text = ""
            if section.title and section.level > 0:
                section_text = f"{'#' * section.level} {section.title}\n\n"
            section_text += section.content
            
            section_tokens = self._count_tokens(section_text)
            
            # Skip very small sections
            if section_tokens < self.config.min_chunk_size:
                logger.debug(f"Skipping small section: {section.title} ({section_tokens} tokens)")
                continue
            
            # Create parent (summary) chunk
            parent_id = f"parent_{section_idx}"
            parent_summary = self._create_parent_summary(section)
            
            parent_chunk = {
                "text": parent_summary,
                "chunk_index": parent_id,
                "token_count": self._count_tokens(parent_summary),
                "hierarchy_path": section.hierarchy_path,
                "section_title": section.title,
                "metadata": {
                    "chunking_strategy": "hierarchical",
                    "chunk_type": ChunkType.PARENT.value,
                    "chunk_size": self.config.parent_chunk_size,
                    "chunk_overlap": chunk_overlap,
                    "parent_id": None,
                    "parent_summary": None,
                    "is_summary": True,
                    "original_section_tokens": section_tokens
                }
            }
            
            all_chunks.append(parent_chunk)
            logger.debug(
                f"Parent created: section='{section.title}', "
                f"summary_length={len(parent_summary)}, method='first_paragraph'"
            )
            
            # Create child chunks from section content
            child_chunks = self._create_child_chunks(
                section=section,
                parent_id=parent_id,
                parent_summary=parent_summary,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                start_index=global_child_index
            )
            
            for child in child_chunks:
                all_chunks.append(child)
                self._log_chunk_created(
                    chunk_index=child['chunk_index'],
                    token_count=child['token_count'],
                    hierarchy_path=child.get('hierarchy_path'),
                    has_overlap=False
                )
                global_child_index += 1
        
        # Log completion stats
        parent_count = sum(1 for c in all_chunks if c.get('metadata', {}).get('chunk_type') == 'parent')
        child_count = len(all_chunks) - parent_count
        
        logger.info(
            f"Hierarchical chunking complete: "
            f"{len(all_chunks)} total ({parent_count} parents, {child_count} children)"
        )
        
        self._log_chunking_complete(all_chunks)
        return all_chunks
    
    def _create_parent_summary(
        self,
        section: Section
    ) -> str:
        """
        Create a summary for the parent chunk.
        
        Extracts first meaningful paragraph as summary.
        If LLM summary is enabled (future), would call LLM here.
        
        Args:
            section: Section to summarize
            
        Returns:
            Summary text for parent chunk
        """
        max_length = self.config.parent_summary_max_length
        
        # Option 1: Use LLM for summary (if configured - future feature)
        if self.config.use_llm_for_parent_summary:
            # TODO: Implement LLM-based summarization
            logger.debug("LLM summary not implemented, using first paragraph")
        
        # Option 2: Extract first meaningful paragraph
        summary = self.markdown_parser.extract_first_paragraph(
            section.content,
            max_chars=max_length,
            skip_headers=True
        )
        
        # Add section title context
        if section.title:
            summary = f"**{section.title}**: {summary}"
        
        return summary
    
    def _create_child_chunks(
        self,
        section: Section,
        parent_id: str,
        parent_summary: str,
        chunk_size: int,
        chunk_overlap: int,
        start_index: int
    ) -> List[Dict[str, Any]]:
        """
        Create child chunks from a section.
        
        Args:
            section: Source section
            parent_id: ID of parent chunk
            parent_summary: Summary from parent for context
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks
            start_index: Starting global index
            
        Returns:
            List of child chunk dictionaries
        """
        # Build section content (with title for context)
        content = ""
        if section.title and section.level > 0:
            content = f"{'#' * section.level} {section.title}\n\n"
        content += section.content
        
        # Split into token-based chunks
        tokens = self._encode(content)
        total_tokens = len(tokens)
        
        if total_tokens == 0:
            return []
        
        chunks = []
        start_idx = 0
        local_idx = 0
        
        while start_idx < total_tokens:
            end_idx = min(start_idx + chunk_size, total_tokens)
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self._decode(chunk_tokens)
            
            chunk = {
                "text": chunk_text,
                "chunk_index": start_index + local_idx,
                "token_count": len(chunk_tokens),
                "hierarchy_path": section.hierarchy_path,
                "section_title": section.title,
                "metadata": {
                    "chunking_strategy": "hierarchical",
                    "chunk_type": ChunkType.CHILD.value,
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                    "parent_id": parent_id,
                    "parent_summary": parent_summary,
                    "local_index": local_idx,
                    "start_token": start_idx,
                    "end_token": end_idx
                }
            }
            
            chunks.append(chunk)
            local_idx += 1
            
            # Move with overlap
            start_idx += chunk_size - chunk_overlap
            
            # Prevent infinite loop
            if chunk_size <= chunk_overlap:
                break
        
        logger.debug(
            f"Created {len(chunks)} child chunks for section '{section.title}'"
        )
        
        return chunks
