"""
Strategy Selector
Selects appropriate processing strategies based on document characteristics.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class StrategySelector:
    """Select processing strategies based on document size and characteristics."""
    
    def select_strategies(self, metadata: Dict[str, Any]) -> Dict[str, str]:
        """
        Select appropriate processing strategies.
        
        Args:
            metadata: Document metadata with size_category
        
        Returns:
            {
                "summary_method": "single" | "map_reduce",
                "qa_method": "single" | "per_section",
                "language_detection_method": "direct" | "sampling",
                "chunking_strategy": "simple" | "semantic" | "hierarchical"
            }
        """
        size_category = metadata["document"]["size_category"]
        
        strategies = {
            "summary_method": self._select_summary_method(size_category),
            "qa_method": self._select_qa_method(size_category),
            "language_detection_method": metadata["language"]["detection_method"],
            "chunking_strategy": metadata["chunking"]["recommended_strategy"]
        }
        
        logger.info(
            f"Selected strategies for {size_category} document: "
            f"summary={strategies['summary_method']}, "
            f"qa={strategies['qa_method']}, "
            f"chunking={strategies['chunking_strategy']}"
        )
        
        return strategies
    
    def _select_summary_method(self, size_category: str) -> str:
        """Select summarization method based on size."""
        if size_category in ["small", "medium"]:
            return "single"
        else:  # large, very_large
            return "map_reduce"
    
    def _select_qa_method(self, size_category: str) -> str:
        """Select Q&A generation method based on size."""
        if size_category in ["small", "medium"]:
            return "single"
        else:  # large, very_large
            return "per_section"
    
    def get_num_qa_pairs(self, size_category: str) -> int:
        """Get recommended number of Q&A pairs based on size."""
        if size_category == "small":
            return 8
        elif size_category == "medium":
            return 12
        else:  # large, very_large
            return 15
