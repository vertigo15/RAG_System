"""
Test language detection functionality.
"""
import sys
import os

# Add workers to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'workers', 'ingestion', 'src'))

from pipeline.language_detector import LanguageDetector

def test_language_detection():
    """Test language detection with various text samples."""
    
    detector = LanguageDetector()
    
    # Test cases
    test_cases = [
        {
            "name": "Hebrew only",
            "text": "שלום עולם זה טקסט בעברית",
            "expected_primary": "he"
        },
        {
            "name": "English only",
            "text": "Hello world this is English text",
            "expected_primary": "en"
        },
        {
            "name": "Mixed Hebrew-English",
            "text": "שלום my name is דוד and I live in ירושלים",
            "expected_primary": None,  # Could be either
            "expected_multilingual": True
        },
        {
            "name": "Mostly Hebrew with English words",
            "text": "זה מסמך בעברית עם כמה מילים ב-English כמו technology ו-computer",
            "expected_primary": "he",
            "expected_multilingual": True
        },
        {
            "name": "Arabic text",
            "text": "مرحبا بك في العالم العربي",
            "expected_primary": "ar"
        },
        {
            "name": "Numbers and punctuation",
            "text": "123 456 !!! ??? ...",
            "expected_primary": "unknown"
        }
    ]
    
    print("=" * 80)
    print("Language Detection Test Results")
    print("=" * 80)
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print(f"Text: {test_case['text']}")
        print("-" * 80)
        
        # Word-level analysis
        word_result = detector.detect_language_per_word(test_case['text'])
        print(f"\nWord-level detection:")
        for word_info in word_result['words'][:10]:  # Show first 10 words
            print(f"  {word_info['word']:20s} -> {word_info['language']:10s} (conf: {word_info['confidence']:.2f})")
        
        print(f"\nLanguage counts: {word_result['language_distribution']}")
        print(f"Primary language: {word_result['primary_language']}")
        
        # Chunk-level analysis
        chunk_result = detector.analyze_chunk_language(test_case['text'])
        print(f"\nChunk-level analysis:")
        print(f"  Primary: {chunk_result['primary_language']}")
        print(f"  Is multilingual: {chunk_result['is_multilingual']}")
        print(f"  Languages: {chunk_result['languages']}")
        print(f"  Distribution: {chunk_result['distribution']}")
        
        # Validate expectations
        print(f"\nValidation:")
        if 'expected_primary' in test_case and test_case['expected_primary']:
            if chunk_result['primary_language'] == test_case['expected_primary']:
                print(f"  ✓ Primary language matches expected: {test_case['expected_primary']}")
            else:
                print(f"  ✗ Expected {test_case['expected_primary']}, got {chunk_result['primary_language']}")
        
        if 'expected_multilingual' in test_case:
            if chunk_result['is_multilingual'] == test_case['expected_multilingual']:
                print(f"  ✓ Multilingual flag matches expected: {test_case['expected_multilingual']}")
            else:
                print(f"  ✗ Expected multilingual={test_case['expected_multilingual']}, got {chunk_result['is_multilingual']}")
        
        print("=" * 80)
    
    print("\n✓ Language detection test completed")

if __name__ == "__main__":
    test_language_detection()
