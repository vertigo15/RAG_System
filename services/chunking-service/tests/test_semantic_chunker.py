"""
Tests for SemanticChunker.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pipeline.strategies.semantic_chunker import SemanticChunker
from pipeline.models.config import ChunkingConfig


class TestSemanticChunker:
    """Tests for SemanticChunker."""
    
    def test_chunk_creates_chunks(self, default_config, sample_markdown):
        """Test that chunking creates chunks."""
        chunker = SemanticChunker(default_config)
        chunks = chunker.chunk(sample_markdown, chunk_size=500, chunk_overlap=50)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert "text" in chunk
            assert "chunk_index" in chunk
            assert "token_count" in chunk
    
    def test_chunk_has_hierarchy_path(self, default_config, sample_markdown):
        """Test that chunks have hierarchy_path field."""
        chunker = SemanticChunker(default_config)
        chunks = chunker.chunk(sample_markdown, chunk_size=500, chunk_overlap=50)
        
        # At least some chunks should have hierarchy_path
        paths = [c.get("hierarchy_path") for c in chunks if c.get("hierarchy_path")]
        assert len(paths) > 0
    
    def test_chunk_has_section_title(self, default_config, sample_markdown):
        """Test that chunks have section_title field."""
        chunker = SemanticChunker(default_config)
        chunks = chunker.chunk(sample_markdown, chunk_size=500, chunk_overlap=50)
        
        # At least some chunks should have section_title
        titles = [c.get("section_title") for c in chunks if c.get("section_title")]
        assert len(titles) > 0
    
    def test_overlap_enabled(self, default_config, sample_markdown):
        """Test that overlap is applied when enabled."""
        config = ChunkingConfig(
            chunk_size=200,
            chunk_overlap=20,
            semantic_overlap_enabled=True,
            semantic_overlap_tokens=30
        )
        chunker = SemanticChunker(config)
        chunks = chunker.chunk(sample_markdown, chunk_size=200, chunk_overlap=20)
        
        if len(chunks) > 1:
            # Check that later chunks have overlap marker
            overlap_count = sum(
                1 for c in chunks[1:] 
                if c.get("metadata", {}).get("has_overlap", False)
            )
            assert overlap_count > 0
    
    def test_overlap_disabled(self, sample_markdown):
        """Test that overlap is not applied when disabled."""
        config = ChunkingConfig(
            chunk_size=200,
            chunk_overlap=20,
            semantic_overlap_enabled=False,
            semantic_overlap_tokens=30
        )
        chunker = SemanticChunker(config)
        chunks = chunker.chunk(sample_markdown, chunk_size=200, chunk_overlap=20)
        
        # No chunks should have overlap when disabled
        for chunk in chunks:
            assert chunk.get("metadata", {}).get("has_overlap", False) == False
    
    def test_overlap_adds_text(self, default_config):
        """Test that overlap actually adds text from previous chunk."""
        config = ChunkingConfig(
            chunk_size=100,
            chunk_overlap=20,
            semantic_overlap_enabled=True,
            semantic_overlap_tokens=20
        )
        chunker = SemanticChunker(config)
        
        # Create text with clear sections
        text = """# Section 1

First section content. This is some text for testing overlap.

# Section 2

Second section content. This should have overlap from section 1.

# Section 3

Third section content. This should have overlap from section 2.
"""
        chunks = chunker.chunk(text, chunk_size=100, chunk_overlap=20)
        
        if len(chunks) > 1:
            # Chunks with overlap should start with "..."
            for chunk in chunks[1:]:
                if chunk.get("metadata", {}).get("has_overlap"):
                    assert chunk["text"].startswith("...")
    
    def test_chunk_includes_strategy(self, default_config, sample_markdown):
        """Test that chunks include strategy metadata."""
        chunker = SemanticChunker(default_config)
        chunks = chunker.chunk(sample_markdown, chunk_size=500, chunk_overlap=50)
        
        for chunk in chunks:
            assert chunk["metadata"]["chunking_strategy"] == "semantic"
    
    def test_chunk_indices_sequential(self, default_config, sample_markdown):
        """Test that chunk indices are sequential."""
        chunker = SemanticChunker(default_config)
        chunks = chunker.chunk(sample_markdown, chunk_size=200, chunk_overlap=20)
        
        for i, chunk in enumerate(chunks):
            assert chunk["chunk_index"] == i
    
    def test_strategy_name(self, default_config):
        """Test strategy name property."""
        chunker = SemanticChunker(default_config)
        assert chunker.strategy_name == "semantic"
    
    def test_hierarchy_path_contains_ancestors(self, structured_markdown):
        """Test that hierarchy path contains ancestor sections."""
        config = ChunkingConfig(min_chunk_size=5)
        chunker = SemanticChunker(config)
        # Use small chunk size to avoid merging nested sections
        chunks = chunker.chunk(structured_markdown, chunk_size=50, chunk_overlap=10)
        
        # Find chunks with nested hierarchy
        nested_paths = [
            c["hierarchy_path"] for c in chunks 
            if c.get("hierarchy_path") and " > " in c["hierarchy_path"]
        ]
        
        # Should have some nested hierarchy paths
        assert len(nested_paths) > 0
    
    def test_large_section_split(self, default_config):
        """Test that large sections are split into multiple chunks."""
        chunker = SemanticChunker(default_config)
        
        # Create a very large section
        large_content = "This is content. " * 500  # Very long content
        text = f"""# Large Section

{large_content}
"""
        chunks = chunker.chunk(text, chunk_size=100, chunk_overlap=20)
        
        # Should create multiple chunks from large section
        assert len(chunks) > 1
