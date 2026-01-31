import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class TreeBuilder:
    """Build hierarchical document structure"""
    
    def build_tree(self, extracted_data: Dict[str, Any], image_descriptions: List[Dict]) -> Dict[str, Any]:
        """
        Create hierarchical document tree with sections and subsections
        
        Args:
            extracted_data: Output from DocumentIntelligenceProcessor
            image_descriptions: Output from VisionProcessor
        
        Returns:
            {
                "text": str,  # Full text
                "structure": {
                    "sections": List[Dict],  # Hierarchical sections
                    "tables": List[Dict],
                    "images": List[Dict]
                },
                "metadata": Dict
            }
        """
        logger.info("Building document tree structure")
        
        paragraphs = extracted_data.get("paragraphs", [])
        tables = extracted_data.get("tables", [])
        pages = extracted_data.get("pages", [])
        
        # Build sections based on paragraph roles and structure
        sections = self._build_sections(paragraphs)
        
        # Integrate image descriptions
        images = self._integrate_images(image_descriptions, pages)
        
        tree = {
            "text": extracted_data.get("text", ""),
            "structure": {
                "sections": sections,
                "tables": tables,
                "images": images
            },
            "metadata": {
                "total_pages": len(pages),
                "total_sections": len(sections),
                "total_tables": len(tables),
                "total_images": len(images)
            }
        }
        
        logger.info(f"Built tree with {len(sections)} sections, {len(tables)} tables, {len(images)} images")
        return tree
    
    def _build_sections(self, paragraphs: List[Dict]) -> List[Dict]:
        """
        Build hierarchical sections from paragraphs
        
        Uses paragraph roles (title, sectionHeading, etc.) to create hierarchy
        """
        sections = []
        current_section = None
        
        for para in paragraphs:
            role = para.get("role")
            content = para.get("content", "")
            
            if role in ["title", "sectionHeading"]:
                # Start a new section
                if current_section:
                    sections.append(current_section)
                
                current_section = {
                    "title": content,
                    "level": 1 if role == "title" else 2,
                    "content": "",
                    "subsections": []
                }
            elif current_section:
                # Add content to current section
                current_section["content"] += f"\n{content}"
            else:
                # No section yet, create a default one
                current_section = {
                    "title": "Main Content",
                    "level": 1,
                    "content": content,
                    "subsections": []
                }
        
        # Add final section
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _integrate_images(self, image_descriptions: List[Dict], pages: List[Dict]) -> List[Dict]:
        """Integrate image descriptions with page information"""
        images = []
        
        for img_desc in image_descriptions:
            images.append({
                "page_number": img_desc.get("page_number"),
                "description": img_desc.get("description", ""),
                "type": "chart_or_diagram"
            })
        
        return images
