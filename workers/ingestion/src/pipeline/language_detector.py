import logging
import re
from typing import Dict, List, Optional
from collections import Counter

logger = logging.getLogger(__name__)

class LanguageDetector:
    """Detect languages at word level for multilingual documents."""
    
    def __init__(self):
        """Initialize language detector with optional fasttext model."""
        self.fasttext_model = None
        self._load_fasttext_model()
    
    def _load_fasttext_model(self):
        """Load fasttext model if available, fallback to character-based detection."""
        try:
            import fasttext
            # Try to load pre-trained model
            # Download from: https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
            model_path = '/app/models/lid.176.bin'
            self.fasttext_model = fasttext.load_model(model_path)
            logger.info("Fasttext language detection model loaded")
        except Exception as e:
            logger.warning(f"Fasttext model not available, using character-based detection only: {e}")
            self.fasttext_model = None
    
    def detect_language_per_word(self, text: str) -> Dict:
        """
        Detect language at word level.
        Good for heavily mixed text.
        
        Returns:
            {
                'words': List[Dict],
                'language_distribution': Dict[str, int],
                'primary_language': str
            }
        """
        # Split by spaces, keep punctuation with words
        words = text.split()
        
        results = []
        for word in words:
            # Skip short words and numbers
            clean_word = re.sub(r'[^\w]', '', word)
            if len(clean_word) < 2 or clean_word.isdigit():
                results.append({'word': word, 'language': 'neutral', 'confidence': 1.0})
                continue
            
            # Detect by character set first (fast)
            if re.search(r'[\u0590-\u05FF]', word):  # Hebrew chars
                results.append({'word': word, 'language': 'he', 'confidence': 0.99})
            elif re.search(r'[\u0600-\u06FF]', word):  # Arabic chars
                results.append({'word': word, 'language': 'ar', 'confidence': 0.99})
            elif re.search(r'[a-zA-Z]', word):  # Latin chars
                # Could be English, Spanish, French, etc.
                if self.fasttext_model:
                    try:
                        pred = self.fasttext_model.predict(word, k=1)
                        lang = pred[0][0].replace('__label__', '')
                        conf = float(pred[1][0])
                        results.append({'word': word, 'language': lang, 'confidence': conf})
                    except Exception as e:
                        logger.debug(f"Fasttext prediction failed for '{word}': {e}")
                        # Fallback to English for Latin chars
                        results.append({'word': word, 'language': 'en', 'confidence': 0.7})
                else:
                    # No fasttext - assume English for Latin characters
                    results.append({'word': word, 'language': 'en', 'confidence': 0.7})
            else:
                results.append({'word': word, 'language': 'unknown', 'confidence': 0.0})
        
        # Summarize
        lang_counts = {}
        for r in results:
            lang = r['language']
            if lang not in ['neutral', 'unknown']:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
        return {
            'words': results,
            'language_distribution': lang_counts,
            'primary_language': max(lang_counts, key=lang_counts.get) if lang_counts else 'unknown'
        }
    
    def detect_languages_per_segment(self, text: str) -> Dict:
        """
        Detect languages in text and provide distribution.
        
        Returns:
            {
                'language_distribution': Dict[str, float],  # Percentage per language
                'languages_found': List[str],
                'is_multilingual': bool,
                'primary_language': str
            }
        """
        word_analysis = self.detect_language_per_word(text)
        
        # Calculate percentages
        total_words = sum(word_analysis['language_distribution'].values())
        language_percentages = {}
        
        if total_words > 0:
            for lang, count in word_analysis['language_distribution'].items():
                language_percentages[lang] = round(count / total_words, 2)
        
        languages_found = list(word_analysis['language_distribution'].keys())
        is_multilingual = len(languages_found) > 1
        primary_language = word_analysis['primary_language']
        
        return {
            'language_distribution': language_percentages,
            'languages_found': languages_found,
            'is_multilingual': is_multilingual,
            'primary_language': primary_language
        }
    
    def analyze_chunk_language(self, content: str) -> Dict:
        """
        Analyze language composition of a chunk.
        
        Returns:
            {
                'primary_language': str,
                'is_multilingual': bool,
                'languages': List[str],
                'distribution': Dict[str, float]
            }
        """
        result = self.detect_languages_per_segment(content)
        
        return {
            'primary_language': result['primary_language'],
            'is_multilingual': result['is_multilingual'],
            'languages': result['languages_found'],
            'distribution': result['language_distribution']
        }
