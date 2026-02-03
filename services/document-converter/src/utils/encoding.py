"""
Text encoding detection utilities.
"""

import logging
from charset_normalizer import detect

logger = logging.getLogger(__name__)


def detect_encoding(file_bytes: bytes) -> str:
    """
    Detect the encoding of a byte string.
    
    Args:
        file_bytes: Byte content to analyze
        
    Returns:
        Encoding name (e.g., 'utf-8', 'latin-1')
    """
    try:
        result = detect(file_bytes)
        if result and result.get('encoding'):
            encoding = result['encoding']
            logger.debug(f"Detected encoding: {encoding}")
            return encoding
    except Exception as e:
        logger.warning(f"Encoding detection failed: {e}")
    
    # Default fallback
    return 'utf-8'


def decode_text(file_bytes: bytes) -> str:
    """
    Decode bytes to string with automatic encoding detection and fallbacks.
    
    Args:
        file_bytes: Byte content to decode
        
    Returns:
        Decoded text string
        
    Raises:
        ValueError: If decoding fails with all known encodings
    """
    # First, try detected encoding
    encoding = detect_encoding(file_bytes)
    try:
        text = file_bytes.decode(encoding)
        logger.info(f"Successfully decoded text with {encoding}")
        return text
    except UnicodeDecodeError:
        logger.warning(f"Failed to decode with detected encoding: {encoding}")
    
    # Fallback chain
    fallback_encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for enc in fallback_encodings:
        try:
            text = file_bytes.decode(enc)
            logger.info(f"Successfully decoded text with fallback encoding: {enc}")
            return text
        except UnicodeDecodeError:
            continue
    
    # Last resort: decode with errors='replace'
    try:
        text = file_bytes.decode('utf-8', errors='replace')
        logger.warning("Decoded with errors='replace', some characters may be corrupted")
        return text
    except Exception as e:
        raise ValueError(f"Could not decode file with any known encoding: {e}")


def is_binary(file_bytes: bytes, sample_size: int = 8192) -> bool:
    """
    Check if the file appears to be binary.
    
    Args:
        file_bytes: Byte content to check
        sample_size: Number of bytes to sample
        
    Returns:
        True if file appears to be binary
    """
    # Check for null bytes (common in binary files)
    sample = file_bytes[:sample_size]
    
    # If null bytes are present, likely binary
    if b'\x00' in sample:
        return True
    
    # Check ratio of non-printable characters
    non_printable = sum(1 for byte in sample if byte < 32 and byte not in (9, 10, 13))
    ratio = non_printable / len(sample) if sample else 0
    
    # If more than 30% non-printable, likely binary
    return ratio > 0.3
