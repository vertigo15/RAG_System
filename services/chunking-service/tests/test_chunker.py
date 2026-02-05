"""
Tests for Chunker orchestrator.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pipeline.chunker import Chunker
from pipeline.models.config import ChunkingConfig


class TestChunker:
    """Tests for Chunker orchestrator."""
    
    def test_chunk_with_simple_strategy(self, default_config, simple_text):
        """Test chunking with explicit simple strategy."""
        chunker = Chunker(default_config)
        chunks = chunker.chunk(simple_text, strategy="simple", chunk_size=100, chunk_overlap=20)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk["metadata"]["chunking_strategy"] == "simple"
    
    def test_chunk_with_semantic_strategy(self, default_config, sample_markdown):
        """Test chunking with explicit semantic strategy."""
        chunker = Chunker(default_config)
        chunks = chunker.chunk(sample_markdown, strategy="semantic", chunk_size=200, chunk_overlap=20)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk["metadata"]["chunking_strategy"] == "semantic"
    
    def test_chunk_with_hierarchical_strategy(self, sample_markdown):
        """Test chunking with explicit hierarchical strategy."""
        config = ChunkingConfig(min_chunk_size=10)
        chunker = Chunker(config)
        chunks = chunker.chunk(sample_markdown, strategy="hierarchical", chunk_size=200, chunk_overlap=20)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk["metadata"]["chunking_strategy"] == "hierarchical"
    
    def test_auto_select_simple_for_small_text(self, default_config):
        """Test auto-selection chooses simple for small documents."""
        config = ChunkingConfig(
            semantic_threshold_chars=5000,
            hierarchical_threshold_chars=60000,
            min_headers_for_semantic=3
        )
        chunker = Chunker(config)
        
        # Small text without headers
        small_text = "This is a short document. " * 10
        
        # Use auto strategy
        chunks = chunker.chunk(small_text, strategy="auto", chunk_size=100, chunk_overlap=20)
        
        # Should use simple strategy
        assert all(c["metadata"]["chunking_strategy"] == "simple" for c in chunks)
    
    def test_auto_select_semantic_for_medium_structured(self, default_config, sample_markdown):
        """Test auto-selection chooses semantic for medium structured documents."""
        config = ChunkingConfig(
            semantic_threshold_chars=1000,  # Lower threshold
            hierarchical_threshold_chars=100000,  # Higher threshold
            min_headers_for_semantic=2
        )
        chunker = Chunker(config)
        
        chunks = chunker.chunk(sample_markdown, strategy="auto", chunk_size=200, chunk_overlap=20)
        
        # Should use semantic strategy for medium structured document
        assert all(c["metadata"]["chunking_strategy"] == "semantic" for c in chunks)
    
    def test_auto_select_hierarchical_for_large(self, default_config):
        """Test auto-selection chooses hierarchical for large documents."""
        config = ChunkingConfig(
            semantic_threshold_chars=1000,
            hierarchical_threshold_chars=5000,  # Low threshold for testing
            min_headers_for_semantic=2
        )
        chunker = Chunker(config)
        
        # Large document with structure
        large_text = """# Section 1

""" + "Content. " * 500 + """

# Section 2

""" + "More content. " * 500
        
        chunks = chunker.chunk(large_text, strategy="auto", chunk_size=200, chunk_overlap=20)
        
        # Should use hierarchical strategy for large document
        assert all(c["metadata"]["chunking_strategy"] == "hierarchical" for c in chunks)
    
    def test_auto_select_considers_header_count(self, default_config):
        """Test auto-selection considers minimum header count."""
        config = ChunkingConfig(
            semantic_threshold_chars=100,
            hierarchical_threshold_chars=100000,
            min_headers_for_semantic=5  # Require 5 headers
        )
        chunker = Chunker(config)
        
        # Document with only 2 headers (less than min)
        text = """# Header 1

Content for section 1. This is some text.

## Header 2

Content for section 2. This is more text.
"""
        
        chunks = chunker.chunk(text, strategy="auto", chunk_size=100, chunk_overlap=20)
        
        # Should use simple because not enough headers
        assert all(c["metadata"]["chunking_strategy"] == "simple" for c in chunks)
    
    def test_unknown_strategy_falls_back_to_simple(self, default_config, simple_text):
        """Test that unknown strategy falls back to simple."""
        chunker = Chunker(default_config)
        chunks = chunker.chunk(simple_text, strategy="unknown_strategy", chunk_size=100, chunk_overlap=20)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk["metadata"]["chunking_strategy"] == "simple"
    
    def test_update_config(self, default_config, simple_text):
        """Test updating configuration."""
        chunker = Chunker(default_config)
        
        # Update config
        new_config = ChunkingConfig(
            chunk_size=50,
            chunk_overlap=10
        )
        chunker.update_config(new_config)
        
        assert chunker.config.chunk_size == 50
        assert chunker.config.chunk_overlap == 10
    
    def test_config_passed_to_strategies(self, sample_markdown):
        """Test that config is passed to strategy chunkers."""
        config = ChunkingConfig(
            semantic_overlap_enabled=True,
            semantic_overlap_tokens=25
        )
        chunker = Chunker(config)
        
        # The semantic chunker should use the config
        assert chunker.semantic_chunker.config.semantic_overlap_tokens == 25
    
    def test_empty_text(self, default_config):
        """Test chunking empty text."""
        chunker = Chunker(default_config)
        chunks = chunker.chunk("", strategy="simple", chunk_size=100, chunk_overlap=20)
        
        assert len(chunks) == 0


class TestAutoSelectionLogic:
    """Detailed tests for auto-selection logic."""
    
    def test_threshold_boundary_hierarchical(self):
        """Test hierarchical threshold boundary."""
        config = ChunkingConfig(
            hierarchical_threshold_chars=1000,
            semantic_threshold_chars=500,
            min_headers_for_semantic=1
        )
        chunker = Chunker(config)
        
        # Just over hierarchical threshold
        text = "# Header\n" + "x" * 1001
        strategy = chunker._auto_select_strategy(text)
        assert strategy == "hierarchical"
    
    def test_threshold_boundary_semantic(self):
        """Test semantic threshold boundary."""
        config = ChunkingConfig(
            hierarchical_threshold_chars=10000,
            semantic_threshold_chars=500,
            min_headers_for_semantic=1
        )
        chunker = Chunker(config)
        
        # Over semantic threshold, under hierarchical, with headers
        text = "# Header\n" + "x" * 600
        strategy = chunker._auto_select_strategy(text)
        assert strategy == "semantic"
    
    def test_no_headers_uses_simple(self):
        """Test that text without headers uses simple."""
        config = ChunkingConfig(
            hierarchical_threshold_chars=10000,
            semantic_threshold_chars=100,
            min_headers_for_semantic=1
        )
        chunker = Chunker(config)
        
        # Over semantic threshold but no headers
        text = "x" * 500
        strategy = chunker._auto_select_strategy(text)
        assert strategy == "simple"
    
    def test_medium_text_with_good_structure(self):
        """Test medium text with good structure uses semantic."""
        config = ChunkingConfig(
            hierarchical_threshold_chars=100000,
            semantic_threshold_chars=100,
            min_headers_for_semantic=3
        )
        chunker = Chunker(config)
        
        # Medium text with 4 headers
        text = """# H1
content
## H2
content
## H3
content
## H4
content
""" + "x" * 4000
        
        strategy = chunker._auto_select_strategy(text)
        assert strategy == "semantic"
