"""
Tests for chunking utility modules.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pipeline.utils.tokenizer import Tokenizer
from pipeline.utils.markdown_parser import MarkdownParser, Section
from pipeline.utils.hierarchy_builder import HierarchyBuilder


class TestTokenizer:
    """Tests for Tokenizer utility."""
    
    def test_encode_decode_roundtrip(self, tokenizer):
        """Test that encode/decode produces original text."""
        text = "Hello, world! This is a test."
        tokens = tokenizer.encode(text)
        decoded = tokenizer.decode(tokens)
        assert decoded == text
    
    def test_count_tokens(self, tokenizer):
        """Test token counting."""
        text = "Hello world"
        count = tokenizer.count_tokens(text)
        assert count > 0
        assert count == len(tokenizer.encode(text))
    
    def test_truncate_to_tokens(self, tokenizer):
        """Test truncation to max tokens."""
        text = "This is a longer text that should be truncated to a smaller size."
        truncated = tokenizer.truncate_to_tokens(text, max_tokens=5)
        assert tokenizer.count_tokens(truncated) <= 5
    
    def test_truncate_short_text(self, tokenizer):
        """Test truncation of text shorter than limit."""
        text = "Short"
        truncated = tokenizer.truncate_to_tokens(text, max_tokens=100)
        assert truncated == text
    
    def test_get_last_n_tokens(self, tokenizer):
        """Test getting last N tokens."""
        text = "First part. Second part. Third part."
        last_tokens = tokenizer.get_last_n_tokens(text, n=3)
        assert tokenizer.count_tokens(last_tokens) == 3
    
    def test_split_by_tokens(self, tokenizer):
        """Test splitting text by token count."""
        text = "Word " * 100  # Create text with many words
        chunks = tokenizer.split_by_tokens(text, chunk_size=20, chunk_overlap=5)
        assert len(chunks) > 1
        # Each chunk should be approximately 20 tokens
        for chunk in chunks[:-1]:  # Excluding last which may be smaller
            assert tokenizer.count_tokens(chunk) <= 20


class TestMarkdownParser:
    """Tests for MarkdownParser utility."""
    
    def test_parse_simple_headers(self, markdown_parser):
        """Test parsing document with simple headers."""
        text = """# Header 1

Content for section 1.

## Header 2

Content for section 2.
"""
        sections = markdown_parser.parse(text)
        assert len(sections) == 2
        assert sections[0].title == "Header 1"
        assert sections[0].level == 1
        assert sections[1].title == "Header 2"
        assert sections[1].level == 2
    
    def test_parse_nested_headers(self, markdown_parser, structured_markdown):
        """Test parsing document with nested hierarchy."""
        sections = markdown_parser.parse(structured_markdown)
        assert len(sections) > 0
        
        # Check hierarchy paths
        for section in sections:
            if section.level > 1:
                assert " > " in section.hierarchy_path or section.title in section.hierarchy_path
    
    def test_count_headers(self, markdown_parser, sample_markdown):
        """Test header counting."""
        count = markdown_parser.count_headers(sample_markdown)
        assert count >= 8  # Sample has multiple headers
    
    def test_get_header_levels(self, markdown_parser, sample_markdown):
        """Test getting unique header levels."""
        levels = markdown_parser.get_header_levels(sample_markdown)
        assert 1 in levels
        assert 2 in levels
    
    def test_extract_first_paragraph(self, markdown_parser):
        """Test extracting first paragraph."""
        text = """# Title

This is the first paragraph with important content.

This is the second paragraph.
"""
        para = markdown_parser.extract_first_paragraph(text, max_chars=100)
        assert "first paragraph" in para
        assert "second paragraph" not in para
    
    def test_extract_first_paragraph_truncation(self, markdown_parser):
        """Test first paragraph truncation."""
        text = "This is a very long paragraph " * 20
        para = markdown_parser.extract_first_paragraph(text, max_chars=50)
        assert len(para) <= 53  # 50 + "..."
        assert para.endswith("...")
    
    def test_parse_no_headers(self, markdown_parser, simple_text):
        """Test parsing text without headers."""
        sections = markdown_parser.parse(simple_text)
        assert len(sections) == 1
        assert sections[0].title == ""
        assert sections[0].level == 0


class TestHierarchyBuilder:
    """Tests for HierarchyBuilder utility."""
    
    def test_update_builds_path(self, hierarchy_builder):
        """Test that update builds correct path."""
        path1 = hierarchy_builder.update(1, "Chapter 1")
        assert path1 == "Chapter 1"
        
        path2 = hierarchy_builder.update(2, "Section 1.1")
        assert path2 == "Chapter 1 > Section 1.1"
        
        path3 = hierarchy_builder.update(3, "Subsection 1.1.1")
        assert path3 == "Chapter 1 > Section 1.1 > Subsection 1.1.1"
    
    def test_update_resets_at_same_level(self, hierarchy_builder):
        """Test that same level header resets stack."""
        hierarchy_builder.update(1, "Chapter 1")
        hierarchy_builder.update(2, "Section 1.1")
        
        # New section at same level should reset
        path = hierarchy_builder.update(2, "Section 1.2")
        assert path == "Chapter 1 > Section 1.2"
        assert "Section 1.1" not in path
    
    def test_update_resets_at_higher_level(self, hierarchy_builder):
        """Test that higher level header resets entire stack."""
        hierarchy_builder.update(1, "Chapter 1")
        hierarchy_builder.update(2, "Section 1.1")
        hierarchy_builder.update(3, "Subsection")
        
        # New chapter should reset everything
        path = hierarchy_builder.update(1, "Chapter 2")
        assert path == "Chapter 2"
        assert "Chapter 1" not in path
    
    def test_get_current_path(self, hierarchy_builder):
        """Test getting current path."""
        hierarchy_builder.update(1, "A")
        hierarchy_builder.update(2, "B")
        
        assert hierarchy_builder.get_current_path() == "A > B"
    
    def test_get_depth(self, hierarchy_builder):
        """Test getting hierarchy depth."""
        assert hierarchy_builder.get_depth() == 0
        
        hierarchy_builder.update(1, "A")
        assert hierarchy_builder.get_depth() == 1
        
        hierarchy_builder.update(2, "B")
        assert hierarchy_builder.get_depth() == 2
    
    def test_reset(self, hierarchy_builder):
        """Test reset clears state."""
        hierarchy_builder.update(1, "A")
        hierarchy_builder.update(2, "B")
        
        hierarchy_builder.reset()
        
        assert hierarchy_builder.get_depth() == 0
        assert hierarchy_builder.get_current_path() == ""
    
    def test_extract_section_title(self):
        """Test extracting section title from path."""
        path = "Chapter 1 > Section 1.1 > Overview"
        title = HierarchyBuilder.extract_section_title(path)
        assert title == "Overview"
    
    def test_extract_section_title_single(self):
        """Test extracting title from single-level path."""
        path = "Introduction"
        title = HierarchyBuilder.extract_section_title(path)
        assert title == "Introduction"
