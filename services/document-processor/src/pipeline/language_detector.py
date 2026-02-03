"""
Language Detector
Detects document language with sampling strategy for large documents.
"""

import logging
from typing import Dict, List, Tuple
from langdetect import detect, detect_langs, LangDetectException
from collections import Counter

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Detect language(s) in document text."""
    
    def detect(
        self,
        text: str,
        size_category: str,
        sample_points: int = 3
    ) -> Dict[str, any]:
        """
        Detect language(s) in text based on document size.
        
        Args:
            text: Document text
            size_category: "small", "medium", "large", "very_large"
            sample_points: Number of sampling points for large docs
        
        Returns:
            {
                "primary": "en",  # Primary language code
                "confidence": 0.95,
                "is_multilingual": False,
                "all_languages": ["en"],
                "distribution": {"en": 1.0},
                "detection_method": "direct" | "sampling"
            }
        """
        logger.info(f"Detecting language (size: {size_category})")
        
        if not text or not text.strip():
            return self._empty_result()
        
        try:
            # For small documents, analyze full text
            if size_category == "small":
                return self._detect_direct(text)
            
            # For larger documents, use sampling
            return self._detect_sampling(text, sample_points)
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return self._empty_result()
    
    def _detect_direct(self, text: str) -> Dict[str, any]:
        """Direct language detection on full text."""
        try:
            # Detect all languages with probabilities
            lang_probs = detect_langs(text)
            
            # Primary language
            primary_lang = lang_probs[0].lang
            primary_confidence = lang_probs[0].prob
            
            # Check if multilingual (second language has significant probability)
            is_multilingual = (
                len(lang_probs) > 1 and
                lang_probs[1].prob > 0.2
            )
            
            # Build distribution
            distribution = {
                lang.lang: round(lang.prob, 3)
                for lang in lang_probs
                if lang.prob > 0.1
            }
            
            all_languages = list(distribution.keys())
            
            return {
                "primary": primary_lang,
                "confidence": round(primary_confidence, 3),
                "is_multilingual": is_multilingual,
                "all_languages": all_languages,
                "distribution": distribution,
                "detection_method": "direct"
            }
            
        except LangDetectException as e:
            logger.warning(f"Direct detection failed: {e}")
            return self._empty_result()
    
    def _detect_sampling(
        self,
        text: str,
        sample_points: int
    ) -> Dict[str, any]:
        """Language detection using sampling strategy."""
        try:
            # Split text into chunks
            text_length = len(text)
            samples = []
            
            # Calculate sample positions
            positions = self._calculate_sample_positions(
                text_length,
                sample_points
            )
            
            # Extract samples (1000 chars each)
            sample_size = 1000
            for pos in positions:
                start = max(0, pos - sample_size // 2)
                end = min(text_length, pos + sample_size // 2)
                sample = text[start:end]
                if sample.strip():
                    samples.append(sample)
            
            # Detect language in each sample
            detected_languages = []
            for sample in samples:
                try:
                    lang = detect(sample)
                    detected_languages.append(lang)
                except LangDetectException:
                    continue
            
            if not detected_languages:
                return self._empty_result()
            
            # Count occurrences
            lang_counter = Counter(detected_languages)
            total_samples = len(detected_languages)
            
            # Calculate distribution
            distribution = {
                lang: round(count / total_samples, 3)
                for lang, count in lang_counter.items()
            }
            
            # Primary language (most common)
            primary_lang = lang_counter.most_common(1)[0][0]
            primary_confidence = distribution[primary_lang]
            
            # Check multilingual
            is_multilingual = len(distribution) > 1
            all_languages = list(distribution.keys())
            
            logger.info(
                f"Detected {len(all_languages)} language(s) from "
                f"{len(samples)} samples: {distribution}"
            )
            
            return {
                "primary": primary_lang,
                "confidence": primary_confidence,
                "is_multilingual": is_multilingual,
                "all_languages": all_languages,
                "distribution": distribution,
                "detection_method": "sampling"
            }
            
        except Exception as e:
            logger.error(f"Sampling detection failed: {e}")
            return self._empty_result()
    
    def _calculate_sample_positions(
        self,
        text_length: int,
        num_samples: int
    ) -> List[int]:
        """
        Calculate evenly distributed sample positions.
        
        Args:
            text_length: Total text length
            num_samples: Number of samples to take
        
        Returns:
            List of character positions
        """
        if num_samples <= 1:
            return [text_length // 2]
        
        # Evenly distributed positions
        positions = []
        step = text_length / (num_samples + 1)
        
        for i in range(1, num_samples + 1):
            pos = int(step * i)
            positions.append(pos)
        
        return positions
    
    def _empty_result(self) -> Dict[str, any]:
        """Return empty/unknown language result."""
        return {
            "primary": "unknown",
            "confidence": 0.0,
            "is_multilingual": False,
            "all_languages": ["unknown"],
            "distribution": {"unknown": 1.0},
            "detection_method": "failed"
        }
