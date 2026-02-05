"""
Hierarchy Builder Utility
Builds and manages document hierarchy paths from markdown structure.
"""

import logging
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class HierarchyNode:
    """Represents a node in the document hierarchy."""
    title: str
    level: int
    path: str
    parent_path: Optional[str] = None
    children: List[str] = field(default_factory=list)


class HierarchyBuilder:
    """
    Builds and tracks document hierarchy from markdown headers.
    
    Maintains a stack of headers to construct paths like:
    "Financial Report > Q3 Results > Revenue Analysis"
    """
    
    def __init__(self, separator: str = " > "):
        """
        Initialize hierarchy builder.
        
        Args:
            separator: String to use between path components
        """
        self.separator = separator
        self._stack: List[Tuple[int, str]] = []  # (level, title)
        self._nodes: Dict[str, HierarchyNode] = {}
        logger.debug(f"HierarchyBuilder initialized with separator: '{separator}'")
    
    def reset(self):
        """Reset the hierarchy state."""
        self._stack = []
        self._nodes = {}
    
    def update(self, level: int, title: str) -> str:
        """
        Update hierarchy with a new header and return the path.
        
        Args:
            level: Header level (1 for #, 2 for ##, etc.)
            title: Header title
            
        Returns:
            Full hierarchy path for this header
        """
        # Remove headers at same or higher level (lower number = higher in hierarchy)
        while self._stack and self._stack[-1][0] >= level:
            self._stack.pop()
        
        # Add new header to stack
        self._stack.append((level, title))
        
        # Build path
        path = self.get_current_path()
        
        # Store node
        parent_path = self._get_parent_path()
        self._nodes[path] = HierarchyNode(
            title=title,
            level=level,
            path=path,
            parent_path=parent_path
        )
        
        # Update parent's children
        if parent_path and parent_path in self._nodes:
            self._nodes[parent_path].children.append(path)
        
        logger.debug(f"Hierarchy updated: level={level}, title='{title}', path='{path}'")
        return path
    
    def get_current_path(self) -> str:
        """
        Get current hierarchy path.
        
        Returns:
            Current path string (e.g., "Chapter 1 > Section 1.1 > Overview")
        """
        if not self._stack:
            return ""
        return self.separator.join(title for _, title in self._stack)
    
    def _get_parent_path(self) -> Optional[str]:
        """Get parent path (excluding current level)."""
        if len(self._stack) <= 1:
            return None
        return self.separator.join(title for _, title in self._stack[:-1])
    
    def get_path_at_level(self, max_level: int) -> str:
        """
        Get hierarchy path up to specified level.
        
        Args:
            max_level: Maximum level to include
            
        Returns:
            Path string up to max_level
        """
        filtered = [(l, t) for l, t in self._stack if l <= max_level]
        return self.separator.join(t for _, t in filtered)
    
    def get_depth(self) -> int:
        """
        Get current hierarchy depth.
        
        Returns:
            Number of levels in current stack
        """
        return len(self._stack)
    
    def get_parent_title(self) -> Optional[str]:
        """
        Get parent section title.
        
        Returns:
            Parent title or None if at root
        """
        if len(self._stack) < 2:
            return None
        return self._stack[-2][1]
    
    def get_ancestors(self) -> List[str]:
        """
        Get list of ancestor titles (excluding current).
        
        Returns:
            List of ancestor titles from root to parent
        """
        if len(self._stack) <= 1:
            return []
        return [title for _, title in self._stack[:-1]]
    
    def build_path_from_titles(self, titles: List[str]) -> str:
        """
        Build a path string from list of titles.
        
        Args:
            titles: List of section titles
            
        Returns:
            Formatted path string
        """
        return self.separator.join(titles) if titles else ""
    
    def get_all_nodes(self) -> Dict[str, HierarchyNode]:
        """
        Get all tracked hierarchy nodes.
        
        Returns:
            Dictionary of path -> HierarchyNode
        """
        return self._nodes.copy()
    
    def get_node(self, path: str) -> Optional[HierarchyNode]:
        """
        Get a specific hierarchy node by path.
        
        Args:
            path: Full hierarchy path
            
        Returns:
            HierarchyNode or None if not found
        """
        return self._nodes.get(path)
    
    @staticmethod
    def extract_section_title(path: str, separator: str = " > ") -> str:
        """
        Extract the last section title from a path.
        
        Args:
            path: Full hierarchy path
            separator: Path separator
            
        Returns:
            Last section title
        """
        if not path:
            return ""
        parts = path.split(separator)
        return parts[-1].strip() if parts else ""
