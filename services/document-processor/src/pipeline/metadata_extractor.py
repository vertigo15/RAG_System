"""
Metadata Extractor
Extracts comprehensive metadata from document and markdown.
"""

import logging
from typing import Dict, Any
from datetime import datetime

from .language_detector import LanguageDetector
from .token_counter import TokenCounter

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extract document metadata including language, tokens, and structure."""
    
    def __init__(self):
        self.language_detector = LanguageDetector()
        self.token_counter = TokenCounter()
    
    def extract(
        self,
        doc_id: str,
        original_filename: str,
        file_size_bytes: int,
        mime_type: str,
        markdown: str,
        doc_intelligence_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from document.
        
        Args:
            doc_id: Document UUID
            original_filename: Original file name
            file_size_bytes: File size in bytes
            mime_type: MIME type
            markdown: Converted markdown content
            doc_intelligence_result: Azure Doc Intelligence output
        
        Returns:
            Complete metadata dictionary matching schema in design doc
        """
        logger.info(f"Extracting metadata for document: {doc_id}")
        
        # Token counting
        token_info = self.token_counter.count(markdown)
        token_count = token_info["token_count"]
        char_count = token_info["char_count"]
        token_count_method = token_info["method"]
        
        # Size categorization
        size_category = self.token_counter.categorize_size(token_count)
        
        # Structure analysis
        pages = doc_intelligence_result.get("pages", [])
        tables = doc_intelligence_result.get("tables", [])
        paragraphs = doc_intelligence_result.get("paragraphs", [])
        
        # Count sections (paragraphs with "sectionHeading" role)
        section_count = sum(
            1 for p in paragraphs
            if p.get("role") == "sectionHeading"
        )
        
        # Language detection (with sampling based on size)
        sample_points = self._get_sample_points(size_category)
        language_info = self.language_detector.detect(
            markdown,
            size_category,
            sample_points
        )
        
        # Build metadata
        metadata = {
            "doc_id": doc_id,
            "original_filename": original_filename,
            "mime_type": mime_type,
            "file_size_bytes": file_size_bytes,
            
            "processing": {
                "started_at": datetime.utcnow().isoformat() + "Z",
                "completed_at": None,  # Will be set after processing
                "duration_seconds": None
            },
            
            "document": {
                "page_count": len(pages),
                "token_count": token_count,
                "token_count_method": token_count_method,
                "char_count": char_count,
                "size_category": size_category
            },
            
            "language": {
                "primary": language_info["primary"],
                "confidence": language_info["confidence"],
                "is_multilingual": language_info["is_multilingual"],
                "all_languages": language_info["all_languages"],
                "distribution": language_info["distribution"],
                "detection_method": language_info["detection_method"]
            },
            
            "structure": {
                "has_sections": section_count > 0,
                "section_count": section_count,
                "has_tables": len(tables) > 0,
                "table_count": len(tables),
                "has_images": False,  # Will be set by vision processor if implemented
                "image_count": 0
            },
            
            "enrichment": {
                "summary_method": None,  # Will be set by summarizer
                "summary_sections_count": None,
                "qa_method": None,  # Will be set by Q&A generator
                "qa_pairs_count": None
            },
            
            "chunking": {
                "recommended_strategy": self._recommend_chunking_strategy(size_category),
                "recommended_chunk_size": 500,
                "recommended_overlap": 50
            },
            
            "tags": [],  # Can be set from user input
            "user_id": None  # Can be set from user context
        }
        
        logger.info(
            f"Metadata extracted: {size_category} document with {token_count} tokens, "
            f"language: {language_info['primary']}"
        )
        
        return metadata
    
    def _get_sample_points(self, size_category: str) -> int:
        """Get number of sample points for language detection based on size."""
        if size_category == "small":
            return 1  # Direct full text
        elif size_category == "medium":
            return 3  # Beginning, middle, end
        elif size_category == "large":
            return 5  # More sampling points
        else:  # very_large
            return 5
    
    def _recommend_chunking_strategy(self, size_category: str) -> str:
        """Recommend chunking strategy based on document size."""
        if size_category == "small":
            return "simple"
        elif size_category == "medium":
            return "semantic"
        else:  # large or very_large
            return "hierarchical"
    
    def update_enrichment(
        self,
        metadata: Dict[str, Any],
        summary_method: str,
        summary_sections_count: int,
        qa_method: str,
        qa_pairs_count: int
    ) -> Dict[str, Any]:
        """
        Update metadata with enrichment information.
        
        Args:
            metadata: Existing metadata dictionary
            summary_method: "single" or "map_reduce"
            summary_sections_count: Number of sections for map-reduce
            qa_method: "single" or "per_section"
            qa_pairs_count: Number of Q&A pairs generated
        
        Returns:
            Updated metadata
        """
        metadata["enrichment"] = {
            "summary_method": summary_method,
            "summary_sections_count": summary_sections_count,
            "qa_method": qa_method,
            "qa_pairs_count": qa_pairs_count
        }
        
        return metadata
    
    def finalize(
        self,
        metadata: Dict[str, Any],
        started_at: datetime
    ) -> Dict[str, Any]:
        """
        Finalize metadata with completion time.
        
        Args:
            metadata: Existing metadata
            started_at: Processing start time
        
        Returns:
            Finalized metadata
        """
        completed_at = datetime.utcnow()
        duration = (completed_at - started_at).total_seconds()
        
        metadata["processing"]["completed_at"] = completed_at.isoformat() + "Z"
        metadata["processing"]["duration_seconds"] = round(duration, 2)
        
        return metadata
