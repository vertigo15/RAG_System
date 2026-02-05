"""
Text Splitter Utility
Handles text splitting with overlap and sentence-aware boundaries.
"""

import logging
import re
from typing import List, Tuple

from .tokenizer import Tokenizer

logger = logging.getLogger(__name__)


class TextSplitter:
    """Utility for splitting text with overlap and smart boundaries."""
    
    # Sentence ending patterns
    SENTENCE_ENDINGS = re.compile(r'([.!?]+[\s]+)')
    
    def __init__(self, tokenizer: Tokenizer = None):
        """
        Initialize text splitter.
        
        Args:
            tokenizer: Tokenizer instance (creates default if not provided)
        """
        self.tokenizer = tokenizer or Tokenizer()
        logger.debug("TextSplitter initialized")
    
    def split_by_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Split by sentence endings, keeping the punctuation
        parts = self.SENTENCE_ENDINGS.split(text)
        
        sentences = []
        for i in range(0, len(parts) - 1, 2):
            sentence = parts[i]
            if i + 1 < len(parts):
                sentence += parts[i + 1]  # Add punctuation back
            sentences.append(sentence.strip())
        
        # Add any remaining text
        if len(parts) % 2 == 1 and parts[-1].strip():
            sentences.append(parts[-1].strip())
        
        return [s for s in sentences if s]
    
    def split_with_sentence_boundary(
        self,
        text: str,
        max_tokens: int
    ) -> List[str]:
        """
        Split text at sentence boundaries within token limit.
        
        Args:
            text: Text to split
            max_tokens: Maximum tokens per chunk
            
        Returns:
            List of text chunks respecting sentence boundaries
        """
        sentences = self.split_by_sentences(text)
        
        if not sentences:
            return [text] if text.strip() else []
        
        chunks = []
        current_chunk: List[str] = []
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = self.tokenizer.count_tokens(sentence)
            
            # If single sentence exceeds limit, add it as own chunk
            if sentence_tokens > max_tokens:
                # Save current chunk first
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                
                # Split long sentence by tokens
                token_chunks = self.tokenizer.split_by_tokens(
                    sentence, max_tokens, overlap=0
                ) if hasattr(self.tokenizer, 'split_by_tokens') else [sentence]
                chunks.extend(token_chunks)
                continue
            
            # Check if adding sentence exceeds limit
            if current_tokens + sentence_tokens > max_tokens:
                # Save current chunk
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                
                # Start new chunk with this sentence
                current_chunk = [sentence]
                current_tokens = sentence_tokens
            else:
                # Add to current chunk
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def add_overlap_to_chunks(
        self,
        chunks: List[dict],
        overlap_tokens: int
    ) -> List[dict]:
        """
        Add overlap from previous chunk to each chunk's content.
        
        Args:
            chunks: List of chunk dictionaries with 'text' or 'content' key
            overlap_tokens: Number of tokens to overlap
            
        Returns:
            Chunks with overlap added to content
        """
        if not chunks or overlap_tokens <= 0:
            return chunks
        
        result = []
        
        for i, chunk in enumerate(chunks):
            # Get content key (support both 'text' and 'content')
            content_key = 'text' if 'text' in chunk else 'content'
            chunk_copy = chunk.copy()
            
            if i == 0:
                # First chunk - no overlap to add
                chunk_copy['has_overlap'] = False
                chunk_copy['overlap_tokens'] = 0
            else:
                # Get overlap from previous chunk
                prev_content = chunks[i - 1].get(content_key, '')
                overlap_text = self.tokenizer.get_last_n_tokens(prev_content, overlap_tokens)
                
                # Prepend overlap to current chunk
                current_content = chunk.get(content_key, '')
                chunk_copy[content_key] = overlap_text + "\n" + current_content
                chunk_copy['has_overlap'] = True
                chunk_copy['overlap_tokens'] = overlap_tokens
                
                logger.debug(f"Added {overlap_tokens} token overlap to chunk {i}")
            
            result.append(chunk_copy)
        
        return result
    
    def merge_small_chunks(
        self,
        chunks: List[str],
        min_tokens: int,
        max_tokens: int
    ) -> List[str]:
        """
        Merge consecutive small chunks together.
        
        Args:
            chunks: List of text chunks
            min_tokens: Minimum tokens per chunk
            max_tokens: Maximum tokens per merged chunk
            
        Returns:
            Merged chunks
        """
        if not chunks:
            return chunks
        
        result = []
        current_merged: List[str] = []
        current_tokens = 0
        
        for chunk in chunks:
            chunk_tokens = self.tokenizer.count_tokens(chunk)
            
            # If chunk alone exceeds max, save current and add as-is
            if chunk_tokens > max_tokens:
                if current_merged:
                    result.append('\n\n'.join(current_merged))
                    current_merged = []
                    current_tokens = 0
                result.append(chunk)
                continue
            
            # Check if we can merge
            if current_tokens + chunk_tokens <= max_tokens:
                current_merged.append(chunk)
                current_tokens += chunk_tokens
            else:
                # Save current merged chunk
                if current_merged:
                    result.append('\n\n'.join(current_merged))
                
                # Start new merged chunk
                current_merged = [chunk]
                current_tokens = chunk_tokens
        
        # Add remaining
        if current_merged:
            result.append('\n\n'.join(current_merged))
        
        return result
