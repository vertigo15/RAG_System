"""
Tokenizer Utility
Wrapper around tiktoken for token counting and encoding.
"""

import logging
from typing import List

import tiktoken

logger = logging.getLogger(__name__)


class Tokenizer:
    """Utility class for token operations using tiktoken."""
    
    def __init__(self, encoding_name: str = "cl100k_base"):
        """
        Initialize tokenizer.
        
        Args:
            encoding_name: Tiktoken encoding name (default: cl100k_base for GPT-4)
        """
        self.encoding_name = encoding_name
        self.encoding = tiktoken.get_encoding(encoding_name)
        logger.debug(f"Tokenizer initialized with encoding: {encoding_name}")
    
    def encode(self, text: str) -> List[int]:
        """
        Encode text to tokens.
        
        Args:
            text: Text to encode
            
        Returns:
            List of token IDs
        """
        return self.encoding.encode(text)
    
    def decode(self, tokens: List[int]) -> str:
        """
        Decode tokens back to text.
        
        Args:
            tokens: List of token IDs
            
        Returns:
            Decoded text
        """
        return self.encoding.decode(tokens)
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        return len(self.encode(text))
    
    def truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to specified number of tokens.
        
        Args:
            text: Text to truncate
            max_tokens: Maximum number of tokens
            
        Returns:
            Truncated text
        """
        tokens = self.encode(text)
        if len(tokens) <= max_tokens:
            return text
        return self.decode(tokens[:max_tokens])
    
    def get_last_n_tokens(self, text: str, n: int) -> str:
        """
        Get last N tokens of text as string.
        
        Args:
            text: Source text
            n: Number of tokens to get from end
            
        Returns:
            Text containing last N tokens
        """
        tokens = self.encode(text)
        if len(tokens) <= n:
            return text
        return self.decode(tokens[-n:])
    
    def split_by_tokens(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[str]:
        """
        Split text into chunks by token count with overlap.
        
        Args:
            text: Text to split
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap size in tokens
            
        Returns:
            List of text chunks
        """
        tokens = self.encode(text)
        total_tokens = len(tokens)
        
        if total_tokens == 0:
            return []
        
        chunks = []
        start_idx = 0
        
        while start_idx < total_tokens:
            end_idx = min(start_idx + chunk_size, total_tokens)
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            # Move start with overlap
            start_idx += chunk_size - chunk_overlap
            
            # Prevent infinite loop for small documents
            if start_idx >= total_tokens:
                break
        
        return chunks
