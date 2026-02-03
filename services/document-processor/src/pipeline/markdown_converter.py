"""
Markdown Converter
Converts Azure Document Intelligence output to unified Markdown format.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class MarkdownConverter:
    """Convert Azure Document Intelligence output to Markdown."""
    
    def convert(self, doc_intelligence_result: Dict[str, Any]) -> str:
        """
        Convert Document Intelligence result to Markdown.
        
        Args:
            doc_intelligence_result: Output from Azure Document Intelligence
                {
                    "text": str,
                    "pages": List[Dict],
                    "tables": List[Dict],
                    "paragraphs": List[Dict],
                    "styles": List[Dict]
                }
        
        Returns:
            Markdown-formatted document
        """
        logger.info("Converting document to Markdown")
        
        markdown_parts = []
        
        # Extract components
        paragraphs = doc_intelligence_result.get("paragraphs", [])
        tables = doc_intelligence_result.get("tables", [])
        pages = doc_intelligence_result.get("pages", [])
        
        # Build markdown from paragraphs and tables
        # We'll process paragraphs sequentially and insert tables where appropriate
        
        if paragraphs:
            markdown_parts.extend(self._convert_paragraphs(paragraphs))
        
        # If no paragraph structure, fall back to full text
        if not markdown_parts:
            full_text = doc_intelligence_result.get("text", "")
            if full_text:
                markdown_parts.append(full_text)
        
        # Append tables at the end if they exist
        if tables:
            markdown_parts.append("\n\n## Tables\n")
            for i, table in enumerate(tables, 1):
                markdown_parts.append(f"\n### Table {i}\n")
                markdown_parts.append(self._convert_table(table))
        
        # Add page count metadata
        if pages:
            markdown_parts.insert(0, f"*Document with {len(pages)} pages*\n\n---\n\n")
        
        markdown = "\n\n".join(markdown_parts)
        
        logger.info(f"Converted to Markdown ({len(markdown)} characters)")
        return markdown
    
    def _convert_paragraphs(self, paragraphs: List[Dict[str, Any]]) -> List[str]:
        """
        Convert paragraphs to Markdown sections.
        
        Args:
            paragraphs: List of paragraph dictionaries
        
        Returns:
            List of Markdown strings
        """
        markdown_parts = []
        
        for para in paragraphs:
            content = para.get("content", "").strip()
            if not content:
                continue
            
            role = para.get("role")
            
            # Format based on role
            if role == "title":
                markdown_parts.append(f"# {content}")
            elif role == "sectionHeading":
                markdown_parts.append(f"## {content}")
            elif role == "pageHeader":
                markdown_parts.append(f"*{content}*")
            elif role == "pageFooter":
                markdown_parts.append(f"*{content}*")
            elif role == "pageNumber":
                # Skip page numbers in markdown
                continue
            else:
                # Regular paragraph
                markdown_parts.append(content)
        
        return markdown_parts
    
    def _convert_table(self, table: Dict[str, Any]) -> str:
        """
        Convert table to Markdown table format.
        
        Args:
            table: Table dictionary with cells
        
        Returns:
            Markdown table string
        """
        row_count = table.get("row_count", 0)
        col_count = table.get("column_count", 0)
        cells = table.get("cells", [])
        
        if not cells or row_count == 0 or col_count == 0:
            return ""
        
        # Build 2D grid
        grid = [[""  for _ in range(col_count)] for _ in range(row_count)]
        
        for cell in cells:
            row_idx = cell.get("row_index", 0)
            col_idx = cell.get("column_index", 0)
            content = cell.get("content", "").replace("\n", " ").strip()
            
            if row_idx < row_count and col_idx < col_count:
                grid[row_idx][col_idx] = content
        
        # Convert to Markdown table
        markdown_lines = []
        
        # Header row
        if row_count > 0:
            header = "| " + " | ".join(grid[0]) + " |"
            markdown_lines.append(header)
            
            # Separator
            separator = "| " + " | ".join(["---"] * col_count) + " |"
            markdown_lines.append(separator)
            
            # Data rows
            for row in grid[1:]:
                data_row = "| " + " | ".join(row) + " |"
                markdown_lines.append(data_row)
        
        return "\n".join(markdown_lines)
    
    def extract_sections(self, markdown: str) -> List[Dict[str, str]]:
        """
        Extract sections from markdown for map-reduce processing.
        
        Args:
            markdown: Markdown document
        
        Returns:
            List of sections with title and content
        """
        sections = []
        lines = markdown.split("\n")
        
        current_section = {"title": "Introduction", "content": []}
        
        for line in lines:
            # Check if it's a header
            if line.startswith("# ") or line.startswith("## "):
                # Save current section if it has content
                if current_section["content"]:
                    current_section["content"] = "\n".join(current_section["content"])
                    sections.append(current_section)
                
                # Start new section
                title = line.lstrip("#").strip()
                current_section = {"title": title, "content": []}
            else:
                # Add line to current section
                if line.strip():
                    current_section["content"].append(line)
        
        # Add final section
        if current_section["content"]:
            current_section["content"] = "\n".join(current_section["content"])
            sections.append(current_section)
        
        logger.info(f"Extracted {len(sections)} sections from Markdown")
        return sections
