"""
Semantic Chunker
Chunks by document sections/paragraphs with size constraints.

Features:
- Splits by markdown headers and paragraphs
- Merges small sections, splits oversized sections
- Adds overlap between chunks (configurable)
- Tracks hierarchy path from document structure
"""

import logging
import re
from typing import List, Dict, Any, Tuple, Optional

from .base import BaseChunker
from ..models.config import ChunkingConfig
from ..utils.tokenizer import Tokenizer
from ..utils.markdown_parser import MarkdownParser, Section
from ..utils.hierarchy_builder import HierarchyBuilder

logger = logging.getLogger(__name__)


class SemanticChunker(BaseChunker):
    """
    Semantic chunking based on document structure.
    
    Features:
    - Splits by markdown headers
    - Merges small sections
    - Splits oversized sections by sentences
    - Adds overlap between chunks (NEW)
    - Tracks hierarchy path (NEW)
    """
    
    def __init__(self, config: ChunkingConfig = None):
        """
        Initialize semantic chunker.
        
        Args:
            config: Chunking configuration
        """
        super().__init__(config)
        self.markdown_parser = MarkdownParser()
        self.hierarchy_builder = HierarchyBuilder()
    
    @property
    def strategy_name(self) -> str:
        return "semantic"
    
    def chunk(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, Any]]:
        """
        Chunk text by sections/paragraphs with size constraints.
        
        Args:
            text: Document text (markdown format)
            chunk_size: Target max size in tokens
            chunk_overlap: Overlap size in tokens
        
        Returns:
            List of chunks with metadata
        """
        self._log_chunking_start(text)
        
        # Step 1: Parse markdown structure
        logger.debug("Parsing markdown structure")
        sections = self.markdown_parser.parse(text)
        header_levels = self.markdown_parser.get_header_levels(text)
        logger.debug(f"Found {len(sections)} sections, header_levels={header_levels}")
        
        # Step 2: Create chunks from sections
        logger.debug("Creating chunks from sections")
        chunks = self._create_chunks_from_sections(sections, chunk_size)
        
        # Step 3: Apply overlap between chunks (NEW)
        if self.config.semantic_overlap_enabled and len(chunks) > 1:
            logger.debug(f"Applying overlap ({self.config.semantic_overlap_tokens} tokens)")
            chunks = self._apply_overlap(chunks)
        
        # Step 4: Finalize chunks with metadata
        for i, chunk in enumerate(chunks):
            chunk['chunk_index'] = i
            chunk['token_count'] = self._count_tokens(chunk['text'])
            
            # Log chunk creation
            self._log_chunk_created(
                chunk_index=i,
                token_count=chunk['token_count'],
                hierarchy_path=chunk.get('hierarchy_path'),
                has_overlap=chunk.get('metadata', {}).get('has_overlap', False)
            )
            
            # Warn if chunk size outside range
            self._log_warning_chunk_size(i, chunk['token_count'])
        
        self._log_chunking_complete(chunks)
        return chunks
    
    def _create_chunks_from_sections(
        self,
        sections: List[Section],
        chunk_size: int
    ) -> List[Dict[str, Any]]:
        """
        Create chunks from parsed sections.
        
        Args:
            sections: List of parsed Section objects
            chunk_size: Target chunk size in tokens
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        current_chunk_parts: List[Tuple[str, str]] = []  # (content, hierarchy_path)
        current_tokens = 0
        
        for section in sections:
            # Build full section text (title + content)
            section_text = ""
            if section.title and section.level > 0:
                section_text = f"{'#' * section.level} {section.title}\n\n"
            section_text += section.content
            
            section_tokens = self._count_tokens(section_text)
            
            # If section is too large, split it
            if section_tokens > chunk_size:
                # Save current chunk first
                if current_chunk_parts:
                    chunks.append(self._build_chunk_dict(current_chunk_parts))
                    current_chunk_parts = []
                    current_tokens = 0
                
                # Split large section into sub-chunks
                sub_chunks = self._split_large_section(section, chunk_size)
                chunks.extend(sub_chunks)
            
            # If adding section exceeds limit, save current chunk
            elif current_tokens + section_tokens > chunk_size:
                if current_chunk_parts:
                    chunks.append(self._build_chunk_dict(current_chunk_parts))
                
                # Start new chunk with this section
                current_chunk_parts = [(section_text, section.hierarchy_path)]
                current_tokens = section_tokens
            
            # Add to current chunk
            else:
                current_chunk_parts.append((section_text, section.hierarchy_path))
                current_tokens += section_tokens
        
        # Add remaining chunk
        if current_chunk_parts:
            chunks.append(self._build_chunk_dict(current_chunk_parts))
        
        return chunks
    
    def _build_chunk_dict(
        self,
        parts: List[Tuple[str, str]]
    ) -> Dict[str, Any]:
        """
        Build chunk dictionary from content parts.
        
        Args:
            parts: List of (content, hierarchy_path) tuples
            
        Returns:
            Chunk dictionary
        """
        text = "\n\n".join(content for content, _ in parts)
        
        # Use first non-empty hierarchy path
        hierarchy_path = next(
            (path for _, path in parts if path),
            None
        )
        
        # Extract section title from hierarchy path
        section_title = None
        if hierarchy_path:
            section_title = HierarchyBuilder.extract_section_title(hierarchy_path)
        
        return {
            "text": text,
            "chunk_index": 0,  # Will be set later
            "token_count": 0,  # Will be set later
            "hierarchy_path": hierarchy_path,
            "section_title": section_title,
            "metadata": {
                "chunking_strategy": "semantic",
                "chunk_size": self.config.chunk_size,
                "chunk_overlap": self.config.chunk_overlap,
                "has_overlap": False,
                "overlap_tokens": 0
            }
        }
    
    def _split_large_section(
        self,
        section: Section,
        chunk_size: int
    ) -> List[Dict[str, Any]]:
        """
        Split a large section into smaller chunks.
        
        Args:
            section: Section to split
            chunk_size: Target chunk size
            
        Returns:
            List of chunk dictionaries
        """
        # Build full section text
        text = ""
        if section.title and section.level > 0:
            text = f"{'#' * section.level} {section.title}\n\n"
        text += section.content
        
        # Split by sentences
        sentences = re.split(r'([.!?]+\s+)', text)
        
        chunks = []
        current_chunk = ""
        
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            if i + 1 < len(sentences):
                sentence += sentences[i + 1]  # Include punctuation
            
            test_chunk = current_chunk + sentence
            if self._count_tokens(test_chunk) > chunk_size:
                if current_chunk:
                    chunks.append({
                        "text": current_chunk.strip(),
                        "chunk_index": 0,
                        "token_count": 0,
                        "hierarchy_path": section.hierarchy_path,
                        "section_title": section.title,
                        "metadata": {
                            "chunking_strategy": "semantic",
                            "chunk_size": self.config.chunk_size,
                            "chunk_overlap": self.config.chunk_overlap,
                            "has_overlap": False,
                            "overlap_tokens": 0,
                            "split_from_large_section": True
                        }
                    })
                current_chunk = sentence
            else:
                current_chunk = test_chunk
        
        # Add remaining
        if current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "chunk_index": 0,
                "token_count": 0,
                "hierarchy_path": section.hierarchy_path,
                "section_title": section.title,
                "metadata": {
                    "chunking_strategy": "semantic",
                    "chunk_size": self.config.chunk_size,
                    "chunk_overlap": self.config.chunk_overlap,
                    "has_overlap": False,
                    "overlap_tokens": 0,
                    "split_from_large_section": True
                }
            })
        
        return chunks if chunks else [{
            "text": text,
            "chunk_index": 0,
            "token_count": 0,
            "hierarchy_path": section.hierarchy_path,
            "section_title": section.title,
            "metadata": {
                "chunking_strategy": "semantic",
                "chunk_size": self.config.chunk_size,
                "chunk_overlap": self.config.chunk_overlap,
                "has_overlap": False,
                "overlap_tokens": 0
            }
        }]
    
    def _apply_overlap(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Add overlap from previous chunk to current chunk.
        
        Only applies overlap when chunks come from split sections,
        not at natural section boundaries.
        
        Args:
            chunks: List of chunks
            
        Returns:
            Chunks with overlap applied
        """
        if len(chunks) <= 1:
            return chunks
        
        overlap_tokens = self.config.semantic_overlap_tokens
        result = [chunks[0]]  # First chunk has no overlap
        
        for i in range(1, len(chunks)):
            prev_chunk = chunks[i - 1]
            current_chunk = chunks[i].copy()
            
            # Get overlap text from previous chunk
            prev_text = prev_chunk['text']
            overlap_text = self.tokenizer.get_last_n_tokens(prev_text, overlap_tokens)
            
            # Prepend overlap to current chunk
            current_chunk['text'] = f"...{overlap_text}\n\n{current_chunk['text']}"
            current_chunk['metadata'] = current_chunk.get('metadata', {}).copy()
            current_chunk['metadata']['has_overlap'] = True
            current_chunk['metadata']['overlap_tokens'] = overlap_tokens
            
            logger.debug(f"Added {overlap_tokens} token overlap to chunk {i}")
            result.append(current_chunk)
        
        return result
