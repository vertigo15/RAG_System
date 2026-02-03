"""
Semantic Chunker
Chunks by document sections/paragraphs with size constraints.
"""

import logging
from typing import List, Dict
import tiktoken
import re

logger = logging.getLogger(__name__)


class SemanticChunker:
    """Semantic chunking based on document structure."""
    
    def __init__(self, encoding_name: str = "cl100k_base"):
        self.encoding = tiktoken.get_encoding(encoding_name)
    
    def chunk(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, any]]:
        """
        Chunk text by sections/paragraphs with size constraints.
        
        Args:
            text: Document text (markdown format)
            chunk_size: Target max size in tokens
            chunk_overlap: Overlap size in tokens
        
        Returns:
            List of chunks with metadata
        """
        logger.info(f"Semantic chunking: size={chunk_size}, overlap={chunk_overlap}")
        
        # Split by markdown headers and paragraphs
        sections = self._split_by_sections(text)
        
        logger.info(f"Found {len(sections)} sections")
        
        # Merge small sections and split large ones
        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_index = 0
        
        for section in sections:
            section_tokens = len(self.encoding.encode(section))
            
            # If section is too large, split it
            if section_tokens > chunk_size:
                # Save current chunk if not empty
                if current_chunk:
                    chunk_text = "\n\n".join(current_chunk)
                    chunks.append(self._create_chunk(chunk_text, chunk_index, chunk_size, chunk_overlap))
                    chunk_index += 1
                    current_chunk = []
                    current_tokens = 0
                
                # Split large section
                sub_chunks = self._split_large_section(section, chunk_size, chunk_overlap)
                for sub_chunk_text in sub_chunks:
                    chunks.append(self._create_chunk(sub_chunk_text, chunk_index, chunk_size, chunk_overlap))
                    chunk_index += 1
            
            # If adding this section exceeds chunk_size, save current chunk
            elif current_tokens + section_tokens > chunk_size:
                if current_chunk:
                    chunk_text = "\n\n".join(current_chunk)
                    chunks.append(self._create_chunk(chunk_text, chunk_index, chunk_size, chunk_overlap))
                    chunk_index += 1
                
                # Start new chunk with this section
                current_chunk = [section]
                current_tokens = section_tokens
            
            # Otherwise, add to current chunk
            else:
                current_chunk.append(section)
                current_tokens += section_tokens
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            chunks.append(self._create_chunk(chunk_text, chunk_index, chunk_size, chunk_overlap))
        
        logger.info(f"Created {len(chunks)} semantic chunks")
        return chunks
    
    def _split_by_sections(self, text: str) -> List[str]:
        """Split text by markdown headers and paragraphs."""
        # Split by headers (# or ##) and double newlines
        sections = []
        
        # Split by headers first
        header_pattern = r'(^#{1,2}\s+.+$)'
        parts = re.split(header_pattern, text, flags=re.MULTILINE)
        
        current_section = ""
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # If it's a header, start new section
            if re.match(r'^#{1,2}\s+', part):
                if current_section:
                    sections.append(current_section)
                current_section = part
            else:
                # Split by double newlines (paragraphs)
                paragraphs = [p.strip() for p in part.split('\n\n') if p.strip()]
                for para in paragraphs:
                    if current_section:
                        current_section += "\n\n" + para
                    else:
                        current_section = para
                    
                    # If section is getting long, save it
                    if len(self.encoding.encode(current_section)) > 300:
                        sections.append(current_section)
                        current_section = ""
        
        # Add final section
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _split_large_section(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[str]:
        """Split a large section into smaller chunks."""
        # Use sentence splitting for better boundaries
        sentences = re.split(r'([.!?]+\s+)', text)
        
        chunks = []
        current_chunk = ""
        
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            if i + 1 < len(sentences):
                sentence += sentences[i + 1]  # Include punctuation
            
            test_chunk = current_chunk + sentence
            if len(self.encoding.encode(test_chunk)) > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk = test_chunk
        
        # Add remaining
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text]
    
    def _create_chunk(
        self,
        text: str,
        chunk_index: int,
        chunk_size: int,
        chunk_overlap: int
    ) -> Dict[str, any]:
        """Create chunk dictionary."""
        tokens = self.encoding.encode(text)
        
        return {
            "text": text,
            "chunk_index": chunk_index,
            "token_count": len(tokens),
            "metadata": {
                "chunking_strategy": "semantic",
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap
            }
        }
