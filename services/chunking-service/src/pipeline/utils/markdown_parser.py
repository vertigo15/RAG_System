"""
Markdown Parser Utility
Parses markdown documents to extract structure, headers, and sections.
"""

import logging
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Section:
    """Represents a markdown section."""
    title: str
    level: int  # Header level (1 for #, 2 for ##, etc.)
    content: str
    start_line: int
    hierarchy_path: str  # e.g., "Introduction > Overview"


class MarkdownParser:
    """Parser for markdown documents with structure extraction."""
    
    # Regex patterns
    HEADER_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    
    def __init__(self):
        """Initialize markdown parser."""
        logger.debug("MarkdownParser initialized")
    
    def parse(self, text: str) -> List[Section]:
        """
        Parse markdown text into sections.
        
        Args:
            text: Markdown text
            
        Returns:
            List of Section objects
        """
        sections = []
        lines = text.split('\n')
        
        # Track header stack for hierarchy path
        header_stack: List[Tuple[int, str]] = []  # (level, title)
        
        current_section_title = ""
        current_section_level = 0
        current_section_content: List[str] = []
        current_section_start = 0
        
        for line_num, line in enumerate(lines):
            header_match = self.HEADER_PATTERN.match(line)
            
            if header_match:
                # Save previous section if exists
                if current_section_content or current_section_title:
                    hierarchy_path = self._build_hierarchy_path(header_stack, current_section_level, current_section_title)
                    sections.append(Section(
                        title=current_section_title,
                        level=current_section_level,
                        content='\n'.join(current_section_content).strip(),
                        start_line=current_section_start,
                        hierarchy_path=hierarchy_path
                    ))
                
                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                
                # Update header stack
                header_stack = self._update_header_stack(header_stack, level, title)
                
                current_section_title = title
                current_section_level = level
                current_section_content = []
                current_section_start = line_num
            else:
                current_section_content.append(line)
        
        # Add final section
        if current_section_content or current_section_title:
            hierarchy_path = self._build_hierarchy_path(header_stack, current_section_level, current_section_title)
            sections.append(Section(
                title=current_section_title,
                level=current_section_level,
                content='\n'.join(current_section_content).strip(),
                start_line=current_section_start,
                hierarchy_path=hierarchy_path
            ))
        
        # Handle documents with no headers
        if not sections and text.strip():
            sections.append(Section(
                title="",
                level=0,
                content=text.strip(),
                start_line=0,
                hierarchy_path=""
            ))
        
        logger.debug(f"Parsed {len(sections)} sections from markdown")
        return sections
    
    def _update_header_stack(
        self,
        stack: List[Tuple[int, str]],
        new_level: int,
        new_title: str
    ) -> List[Tuple[int, str]]:
        """
        Update header stack when encountering a new header.
        
        Args:
            stack: Current header stack
            new_level: Level of new header
            new_title: Title of new header
            
        Returns:
            Updated header stack
        """
        # Remove headers at same or lower level
        new_stack = [(level, title) for level, title in stack if level < new_level]
        new_stack.append((new_level, new_title))
        return new_stack
    
    def _build_hierarchy_path(
        self,
        stack: List[Tuple[int, str]],
        current_level: int,
        current_title: str
    ) -> str:
        """
        Build hierarchy path string from header stack.
        
        Args:
            stack: Current header stack
            current_level: Level of current section
            current_title: Title of current section
            
        Returns:
            Hierarchy path string (e.g., "Chapter 1 > Introduction > Overview")
        """
        if not stack and not current_title:
            return ""
        
        # Get path from stack (excluding current)
        path_parts = [title for level, title in stack if level < current_level]
        if current_title:
            path_parts.append(current_title)
        
        return " > ".join(path_parts) if path_parts else ""
    
    def count_headers(self, text: str) -> int:
        """
        Count number of markdown headers in text.
        
        Args:
            text: Markdown text
            
        Returns:
            Number of headers found
        """
        matches = self.HEADER_PATTERN.findall(text)
        return len(matches)
    
    def get_header_levels(self, text: str) -> List[int]:
        """
        Get list of header levels found in text.
        
        Args:
            text: Markdown text
            
        Returns:
            List of unique header levels (e.g., [1, 2, 3])
        """
        matches = self.HEADER_PATTERN.findall(text)
        levels = sorted(set(len(m[0]) for m in matches))
        return levels
    
    def extract_first_paragraph(
        self,
        text: str,
        max_chars: int = 300,
        skip_headers: bool = True
    ) -> str:
        """
        Extract first meaningful paragraph from text.
        
        Args:
            text: Source text
            max_chars: Maximum characters to return
            skip_headers: Whether to skip header lines
            
        Returns:
            First paragraph text (truncated if needed)
        """
        lines = text.split('\n')
        paragraph_lines: List[str] = []
        in_paragraph = False
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines at start
            if not line and not in_paragraph:
                continue
            
            # Skip headers if configured
            if skip_headers and self.HEADER_PATTERN.match(line):
                continue
            
            # Empty line ends paragraph
            if not line and in_paragraph:
                break
            
            # Add line to paragraph
            paragraph_lines.append(line)
            in_paragraph = True
        
        paragraph = ' '.join(paragraph_lines)
        
        # Truncate if needed
        if len(paragraph) > max_chars:
            paragraph = paragraph[:max_chars].rsplit(' ', 1)[0] + "..."
        
        return paragraph
    
    def split_by_paragraphs(self, text: str) -> List[str]:
        """
        Split text by double newlines (paragraphs).
        
        Args:
            text: Source text
            
        Returns:
            List of paragraph strings
        """
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
