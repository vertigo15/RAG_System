"""
Token Counter
Counts tokens in document text with exact or estimation strategies.
"""

import logging
from typing import Dict
import tiktoken

logger = logging.getLogger(__name__)


class TokenCounter:
    """Count tokens in document text."""
    
    def __init__(self, encoding_name: str = "cl100k_base"):
        """
        Initialize token counter.
        
        Args:
            encoding_name: Tiktoken encoding name (default: cl100k_base for GPT-4)
        """
        try:
            self.encoding = tiktoken.get_encoding(encoding_name)
            logger.info(f"Initialized token counter with encoding: {encoding_name}")
        except Exception as e:
            logger.error(f"Failed to load encoding: {e}")
            self.encoding = None
    
    def count(
        self,
        text: str,
        estimate_threshold: int = 100000  # chars
    ) -> Dict[str, any]:
        """
        Count tokens in text with automatic method selection.
        
        Args:
            text: Document text
            estimate_threshold: Character count above which to use estimation
        
        Returns:
            {
                "token_count": 1234,
                "char_count": 5678,
                "method": "exact" | "estimated"
            }
        """
        if not text:
            return {
                "token_count": 0,
                "char_count": 0,
                "method": "exact"
            }
        
        char_count = len(text)
        
        # Use estimation for very large documents
        if char_count > estimate_threshold:
            return self._estimate_tokens(text, char_count)
        
        # Use exact counting for smaller documents
        return self._count_exact(text, char_count)
    
    def _count_exact(self, text: str, char_count: int) -> Dict[str, any]:
        """Count tokens exactly using tiktoken."""
        try:
            if self.encoding is None:
                # Fallback to estimation if encoding failed
                return self._estimate_tokens(text, char_count)
            
            tokens = self.encoding.encode(text)
            token_count = len(tokens)
            
            logger.info(f"Exact token count: {token_count} ({char_count} chars)")
            
            return {
                "token_count": token_count,
                "char_count": char_count,
                "method": "exact"
            }
            
        except Exception as e:
            logger.error(f"Exact counting failed: {e}")
            return self._estimate_tokens(text, char_count)
    
    def _estimate_tokens(self, text: str, char_count: int) -> Dict[str, any]:
        """
        Estimate token count using sampling or ratio.
        
        For English text, average ratio is ~4 chars per token.
        We'll sample the first 10K characters for better accuracy.
        """
        try:
            # Sample first 10K chars for ratio calculation
            sample_size = min(10000, char_count)
            sample = text[:sample_size]
            
            if self.encoding:
                # Calculate ratio from sample
                sample_tokens = len(self.encoding.encode(sample))
                ratio = sample_size / sample_tokens if sample_tokens > 0 else 4.0
            else:
                # Default ratio
                ratio = 4.0
            
            # Estimate total tokens
            estimated_tokens = int(char_count / ratio)
            
            logger.info(
                f"Estimated token count: {estimated_tokens} ({char_count} chars, "
                f"ratio: {ratio:.2f})"
            )
            
            return {
                "token_count": estimated_tokens,
                "char_count": char_count,
                "method": "estimated"
            }
            
        except Exception as e:
            logger.error(f"Estimation failed: {e}")
            # Fallback to simple ratio
            return {
                "token_count": int(char_count / 4),
                "char_count": char_count,
                "method": "estimated"
            }
    
    def categorize_size(self, token_count: int) -> str:
        """
        Categorize document size based on token count.
        
        Args:
            token_count: Number of tokens
        
        Returns:
            "small", "medium", "large", or "very_large"
        """
        if token_count < 3000:
            return "small"
        elif token_count < 20000:
            return "medium"
        elif token_count < 60000:
            return "large"
        else:
            return "very_large"
