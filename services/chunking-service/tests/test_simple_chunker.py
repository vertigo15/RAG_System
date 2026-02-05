"""
Tests for SimpleChunker.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pipeline.strategies.simple_chunker import SimpleChunker
from pipeline.models.config import ChunkingConfig


class TestSimpleChunker:
    """Tests for SimpleChunker."""
    
    def test_chunk_creates_chunks(self, small_config, simple_text):
        """Test that chunking creates multiple chunks."""
        chunker = SimpleChunker(small_config)
        chunks = chunker.chunk(simple_text, chunk_size=100, chunk_overlap=20)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert "text" in chunk
            assert "chunk_index" in chunk
            assert "token_count" in chunk
    
    def test_chunk_respects_size(self, default_config, simple_text):
        """Test that chunks respect size limit."""
        chunker = SimpleChunker(default_config)
        chunk_size = 50
        chunks = chunker.chunk(simple_text, chunk_size=chunk_size, chunk_overlap=10)
        
        # Most chunks should be close to target size
        for chunk in chunks[:-1]:  # Excluding last
            assert chunk["token_count"] <= chunk_size + 5  # Small tolerance
    
    def test_chunk_has_overlap(self, small_config):
        """Test that chunks have overlap metadata."""
        chunker = SimpleChunker(small_config)
        text = "word " * 200  # Long enough for multiple chunks
        chunks = chunker.chunk(text, chunk_size=50, chunk_overlap=10)
        
        # First chunk should not have overlap
        assert chunks[0]["metadata"]["has_overlap"] == False
        
        # Subsequent chunks should have overlap
        for chunk in chunks[1:]:
            assert chunk["metadata"]["has_overlap"] == True
            assert chunk["metadata"]["overlap_tokens"] == 10
    
    def test_chunk_includes_strategy(self, default_config, simple_text):
        """Test that chunks include strategy metadata."""
        chunker = SimpleChunker(default_config)
        chunks = chunker.chunk(simple_text, chunk_size=100, chunk_overlap=20)
        
        for chunk in chunks:
            assert chunk["metadata"]["chunking_strategy"] == "simple"
    
    def test_chunk_hierarchy_path_is_none(self, default_config, simple_text):
        """Test that simple chunker sets hierarchy_path to None."""
        chunker = SimpleChunker(default_config)
        chunks = chunker.chunk(simple_text, chunk_size=100, chunk_overlap=20)
        
        for chunk in chunks:
            assert chunk["hierarchy_path"] is None
    
    def test_chunk_indices_sequential(self, default_config, simple_text):
        """Test that chunk indices are sequential."""
        chunker = SimpleChunker(default_config)
        chunks = chunker.chunk(simple_text, chunk_size=50, chunk_overlap=10)
        
        for i, chunk in enumerate(chunks):
            assert chunk["chunk_index"] == i
    
    def test_empty_text(self, default_config):
        """Test chunking empty text."""
        chunker = SimpleChunker(default_config)
        chunks = chunker.chunk("", chunk_size=100, chunk_overlap=20)
        
        assert len(chunks) == 0
    
    def test_very_short_text(self, default_config):
        """Test chunking text shorter than chunk size."""
        chunker = SimpleChunker(default_config)
        text = "Short text."
        chunks = chunker.chunk(text, chunk_size=100, chunk_overlap=20)
        
        assert len(chunks) == 1
        assert chunks[0]["text"] == text
    
    def test_strategy_name(self, default_config):
        """Test strategy name property."""
        chunker = SimpleChunker(default_config)
        assert chunker.strategy_name == "simple"
