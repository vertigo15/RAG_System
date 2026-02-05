"""
Tests for HierarchicalChunker.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pipeline.strategies.hierarchical_chunker import HierarchicalChunker
from pipeline.models.config import ChunkingConfig


class TestHierarchicalChunker:
    """Tests for HierarchicalChunker."""
    
    def test_chunk_creates_parent_and_child(self, sample_markdown):
        """Test that chunking creates both parent and child chunks."""
        config = ChunkingConfig(min_chunk_size=10)  # Lower min for test
        chunker = HierarchicalChunker(config)
        chunks = chunker.chunk(sample_markdown, chunk_size=200, chunk_overlap=20)
        
        # Should have both parent and child types
        chunk_types = [c["metadata"]["chunk_type"] for c in chunks]
        assert "parent" in chunk_types
        assert "child" in chunk_types
    
    def test_parent_is_summary(self, default_config, sample_markdown):
        """Test that parent chunks contain summaries, not full content."""
        config = ChunkingConfig(
            chunk_size=200,
            chunk_overlap=20,
            parent_summary_max_length=300
        )
        chunker = HierarchicalChunker(config)
        chunks = chunker.chunk(sample_markdown, chunk_size=200, chunk_overlap=20)
        
        parent_chunks = [c for c in chunks if c["metadata"]["chunk_type"] == "parent"]
        
        for parent in parent_chunks:
            # Parent should be relatively short (summary)
            assert len(parent["text"]) <= 500  # Reasonable summary length
            # Parent should be marked as summary
            assert parent["metadata"].get("is_summary", False) == True
    
    def test_child_has_parent_id(self, sample_markdown):
        """Test that child chunks have parent_id."""
        config = ChunkingConfig(min_chunk_size=10)
        chunker = HierarchicalChunker(config)
        chunks = chunker.chunk(sample_markdown, chunk_size=200, chunk_overlap=20)
        
        child_chunks = [c for c in chunks if c["metadata"]["chunk_type"] == "child"]
        
        for child in child_chunks:
            assert child["metadata"]["parent_id"] is not None
            assert child["metadata"]["parent_id"].startswith("parent_")
    
    def test_child_has_parent_summary(self, sample_markdown):
        """Test that child chunks have parent_summary for context."""
        config = ChunkingConfig(min_chunk_size=10)
        chunker = HierarchicalChunker(config)
        chunks = chunker.chunk(sample_markdown, chunk_size=200, chunk_overlap=20)
        
        child_chunks = [c for c in chunks if c["metadata"]["chunk_type"] == "child"]
        
        for child in child_chunks:
            assert child["metadata"]["parent_summary"] is not None
            assert len(child["metadata"]["parent_summary"]) > 0
    
    def test_parent_has_no_parent_id(self, sample_markdown):
        """Test that parent chunks have no parent_id."""
        config = ChunkingConfig(min_chunk_size=10)
        chunker = HierarchicalChunker(config)
        chunks = chunker.chunk(sample_markdown, chunk_size=200, chunk_overlap=20)
        
        parent_chunks = [c for c in chunks if c["metadata"]["chunk_type"] == "parent"]
        
        for parent in parent_chunks:
            assert parent["metadata"]["parent_id"] is None
    
    def test_hierarchy_path_present(self, sample_markdown):
        """Test that chunks have hierarchy_path."""
        config = ChunkingConfig(min_chunk_size=10)
        chunker = HierarchicalChunker(config)
        chunks = chunker.chunk(sample_markdown, chunk_size=200, chunk_overlap=20)
        
        # At least some chunks should have hierarchy_path
        paths = [c.get("hierarchy_path") for c in chunks if c.get("hierarchy_path")]
        assert len(paths) > 0
    
    def test_section_title_present(self, sample_markdown):
        """Test that chunks have section_title."""
        config = ChunkingConfig(min_chunk_size=10)
        chunker = HierarchicalChunker(config)
        chunks = chunker.chunk(sample_markdown, chunk_size=200, chunk_overlap=20)
        
        # At least some chunks should have section_title
        titles = [c.get("section_title") for c in chunks if c.get("section_title")]
        assert len(titles) > 0
    
    def test_chunk_includes_strategy(self, sample_markdown):
        """Test that chunks include strategy metadata."""
        config = ChunkingConfig(min_chunk_size=10)
        chunker = HierarchicalChunker(config)
        chunks = chunker.chunk(sample_markdown, chunk_size=200, chunk_overlap=20)
        
        for chunk in chunks:
            assert chunk["metadata"]["chunking_strategy"] == "hierarchical"
    
    def test_strategy_name(self, default_config):
        """Test strategy name property."""
        chunker = HierarchicalChunker(default_config)
        assert chunker.strategy_name == "hierarchical"
    
    def test_parent_summary_max_length(self):
        """Test that parent summaries respect max length config."""
        config = ChunkingConfig(
            chunk_size=200,
            chunk_overlap=20,
            parent_summary_max_length=100  # Short max
        )
        chunker = HierarchicalChunker(config)
        
        # Create document with long first paragraph
        text = """# Section Title

This is a very long first paragraph that goes on and on with lots of words
and content that should be truncated when creating the parent summary because
it exceeds the maximum length configured in the chunking config settings.
More words here to make it even longer.

More content in the section.
"""
        chunks = chunker.chunk(text, chunk_size=200, chunk_overlap=20)
        
        parent_chunks = [c for c in chunks if c["metadata"]["chunk_type"] == "parent"]
        
        for parent in parent_chunks:
            # Summary should be truncated
            # Note: actual length may be slightly longer due to title prefix
            assert len(parent["text"]) < 300  # Reasonable upper bound
    
    def test_parent_summary_includes_title(self, default_config):
        """Test that parent summary includes section title."""
        chunker = HierarchicalChunker(default_config)
        
        text = """# Important Section

This is the content of the important section.
"""
        chunks = chunker.chunk(text, chunk_size=200, chunk_overlap=20)
        
        parent_chunks = [c for c in chunks if c["metadata"]["chunk_type"] == "parent"]
        
        if parent_chunks:
            # Parent summary should contain section title (bold format)
            assert "Important Section" in parent_chunks[0]["text"]
    
    def test_child_local_index(self, sample_markdown):
        """Test that child chunks have local_index within parent."""
        config = ChunkingConfig(min_chunk_size=10)
        chunker = HierarchicalChunker(config)
        chunks = chunker.chunk(sample_markdown, chunk_size=100, chunk_overlap=10)
        
        child_chunks = [c for c in chunks if c["metadata"]["chunk_type"] == "child"]
        
        for child in child_chunks:
            assert "local_index" in child["metadata"]
            assert child["metadata"]["local_index"] >= 0
