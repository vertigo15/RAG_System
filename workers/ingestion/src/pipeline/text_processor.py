import logging
import json
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class TextProcessor:
    """Process plain text files (TXT, MD, JSON)"""
    
    def __init__(self):
        pass
    
    async def process(self, file_path: str) -> Dict[str, Any]:
        """
        Extract content from text files
        
        Returns:
            {
                "text": str,  # Full text content
                "pages": List[Dict],  # Single page
                "tables": List[Dict],  # Empty for text files
                "paragraphs": List[Dict],  # Text split into paragraphs
                "styles": List[Dict]  # Empty for text files
            }
        """
        logger.info(f"Processing text file: {file_path}")
        
        file_ext = Path(file_path).suffix.lower()
        
        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Special handling for JSON
            if file_ext == ".json":
                content = self._format_json(content)
            
            # Split into paragraphs
            paragraphs = self._extract_paragraphs(content, file_ext)
            
            logger.info(f"Extracted {len(paragraphs)} paragraphs from text file")
            
            return {
                "text": content,
                "pages": [{
                    "page_number": 1,
                    "width": None,
                    "height": None,
                    "unit": None,
                    "lines": [{"text": line, "polygon": None} for line in content.split('\n') if line.strip()]
                }],
                "tables": [],
                "paragraphs": paragraphs,
                "styles": []
            }
            
        except UnicodeDecodeError:
            # Try with different encoding
            logger.warning(f"UTF-8 decoding failed, trying latin-1")
            with open(file_path, "r", encoding="latin-1") as f:
                content = f.read()
            
            if file_ext == ".json":
                content = self._format_json(content)
            
            paragraphs = self._extract_paragraphs(content, file_ext)
            
            return {
                "text": content,
                "pages": [{
                    "page_number": 1,
                    "width": None,
                    "height": None,
                    "unit": None,
                    "lines": [{"text": line, "polygon": None} for line in content.split('\n') if line.strip()]
                }],
                "tables": [],
                "paragraphs": paragraphs,
                "styles": []
            }
            
        except Exception as e:
            logger.error(f"Text file processing failed: {e}")
            raise
    
    def _format_json(self, content: str) -> str:
        """Format JSON content for better readability"""
        try:
            # Parse and pretty-print JSON
            data = json.loads(content)
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            return formatted
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON, using raw content: {e}")
            return content
    
    def _extract_paragraphs(self, content: str, file_ext: str) -> list:
        """Extract paragraphs from text content"""
        paragraphs = []
        
        if file_ext == ".md":
            # For Markdown, treat headers and text blocks separately
            lines = content.split('\n')
            current_para = []
            
            for line in lines:
                stripped = line.strip()
                
                if not stripped:
                    # Empty line - end current paragraph
                    if current_para:
                        para_text = '\n'.join(current_para)
                        role = "title" if para_text.startswith('#') else None
                        paragraphs.append({
                            "content": para_text,
                            "role": role,
                            "bounding_regions": []
                        })
                        current_para = []
                elif stripped.startswith('#'):
                    # Heading - save previous paragraph and start new one
                    if current_para:
                        para_text = '\n'.join(current_para)
                        paragraphs.append({
                            "content": para_text,
                            "role": None,
                            "bounding_regions": []
                        })
                        current_para = []
                    
                    # Add heading as its own paragraph
                    paragraphs.append({
                        "content": stripped,
                        "role": "title",
                        "bounding_regions": []
                    })
                else:
                    current_para.append(line)
            
            # Add remaining paragraph
            if current_para:
                para_text = '\n'.join(current_para)
                paragraphs.append({
                    "content": para_text,
                    "role": None,
                    "bounding_regions": []
                })
        
        else:
            # For TXT and JSON, split by double newlines
            blocks = content.split('\n\n')
            for block in blocks:
                stripped = block.strip()
                if stripped:
                    paragraphs.append({
                        "content": stripped,
                        "role": None,
                        "bounding_regions": []
                    })
        
        return paragraphs
