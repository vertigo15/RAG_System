"""
Markdown formatting utilities.
"""

import re
from typing import List


def escape_markdown(text: str) -> str:
    """
    Escape special markdown characters in text that should be literal.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text
    """
    chars_to_escape = ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!', '|']
    escaped_text = text
    
    for char in chars_to_escape:
        escaped_text = escaped_text.replace(char, '\\' + char)
    
    return escaped_text


def escape_table_cell(cell: str) -> str:
    """
    Escape pipe characters in table cells.
    
    Args:
        cell: Table cell content
        
    Returns:
        Escaped cell content
    """
    return str(cell).replace('|', '\\|').replace('\n', ' ')


def create_markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    """
    Build a markdown table from data.
    
    Args:
        headers: List of header strings
        rows: List of row data (each row is a list of strings)
        
    Returns:
        Markdown table string
    """
    if not headers or not rows:
        return ""
    
    # Escape cells
    escaped_headers = [escape_table_cell(h) for h in headers]
    escaped_rows = [[escape_table_cell(cell) for cell in row] for row in rows]
    
    # Build table
    header_row = "| " + " | ".join(escaped_headers) + " |"
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"
    data_rows = [
        "| " + " | ".join(row) + " |"
        for row in escaped_rows
    ]
    
    return "\n".join([header_row, separator] + data_rows)


def sanitize_for_markdown(text: str) -> str:
    """
    Clean text for markdown inclusion.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Normalize whitespace (but preserve newlines)
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Replace multiple spaces with single space
        line = re.sub(r' +', ' ', line)
        # Strip leading/trailing whitespace
        line = line.strip()
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def format_header(text: str, level: int = 1) -> str:
    """
    Format text as a markdown header.
    
    Args:
        text: Header text
        level: Header level (1-6)
        
    Returns:
        Formatted header
    """
    level = max(1, min(6, level))  # Clamp between 1 and 6
    return f"{'#' * level} {text}"


def format_list_item(text: str, ordered: bool = False, level: int = 0) -> str:
    """
    Format text as a list item.
    
    Args:
        text: List item text
        ordered: Whether this is an ordered list
        level: Nesting level (0-based)
        
    Returns:
        Formatted list item
    """
    indent = "  " * level
    prefix = "1." if ordered else "-"
    return f"{indent}{prefix} {text}"


def format_bold(text: str) -> str:
    """Format text as bold."""
    return f"**{text}**"


def format_italic(text: str) -> str:
    """Format text as italic."""
    return f"*{text}*"


def format_bold_italic(text: str) -> str:
    """Format text as bold and italic."""
    return f"***{text}***"


def format_link(text: str, url: str) -> str:
    """Format text as a link."""
    return f"[{text}]({url})"


def format_image(alt_text: str, url: str = "", title: str = "") -> str:
    """
    Format an image reference.
    
    Args:
        alt_text: Alt text for the image
        url: Image URL (optional)
        title: Image title (optional)
        
    Returns:
        Formatted image reference
    """
    if title:
        return f"![{alt_text}]({url} \"{title}\")"
    elif url:
        return f"![{alt_text}]({url})"
    else:
        return f"![{alt_text}]"


def format_code_block(code: str, language: str = "") -> str:
    """
    Format code as a code block.
    
    Args:
        code: Code content
        language: Programming language for syntax highlighting
        
    Returns:
        Formatted code block
    """
    return f"```{language}\n{code}\n```"


def is_header_line(line: str) -> tuple[bool, int]:
    """
    Check if a line is a markdown header.
    
    Args:
        line: Line to check
        
    Returns:
        Tuple of (is_header, level)
    """
    match = re.match(r'^(#{1,6})\s+', line)
    if match:
        return True, len(match.group(1))
    return False, 0
