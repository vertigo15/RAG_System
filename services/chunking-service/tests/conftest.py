"""
Pytest fixtures for chunking service tests.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pipeline.models.config import ChunkingConfig
from pipeline.utils.tokenizer import Tokenizer
from pipeline.utils.markdown_parser import MarkdownParser
from pipeline.utils.hierarchy_builder import HierarchyBuilder


@pytest.fixture
def default_config():
    """Default chunking configuration."""
    return ChunkingConfig()


@pytest.fixture
def small_config():
    """Config with smaller chunk sizes for testing."""
    return ChunkingConfig(
        chunk_size=100,
        chunk_overlap=20,
        min_chunk_size=20,
        max_chunk_size=200,
        semantic_overlap_tokens=20
    )


@pytest.fixture
def tokenizer():
    """Tokenizer instance."""
    return Tokenizer()


@pytest.fixture
def markdown_parser():
    """Markdown parser instance."""
    return MarkdownParser()


@pytest.fixture
def hierarchy_builder():
    """Hierarchy builder instance."""
    return HierarchyBuilder()


@pytest.fixture
def sample_markdown():
    """Sample markdown document for testing."""
    return """# Introduction

This is the introduction section. It provides an overview of the document
and sets the context for what follows.

## Background

The background section explains the history and motivation behind this work.
We have been working on this for several years.

## Objectives

Our main objectives are:
- Improve chunking quality
- Add overlap between sections
- Track document hierarchy

# Methods

This section describes the methods used in our research.

## Data Collection

We collected data from multiple sources including databases and APIs.
The data was then processed and cleaned.

## Analysis

The analysis was performed using statistical methods.
We used regression analysis and clustering.

# Results

The results show significant improvements.

## Performance Metrics

- Accuracy: 95%
- Precision: 92%
- Recall: 88%

## Discussion

These results indicate that our approach is effective.
Further research is needed to validate these findings.

# Conclusion

In conclusion, we have demonstrated the effectiveness of our approach.
Future work will focus on scaling and optimization.
"""


@pytest.fixture
def simple_text():
    """Simple text without markdown structure."""
    return """This is a simple document without any headers or structure.
It contains multiple sentences that form a single paragraph.
The text continues with more information about various topics.
We include enough content here to test basic chunking functionality.
The chunker should be able to split this into multiple pieces.
Each piece should have some overlap with the adjacent chunks.
This helps maintain context across chunk boundaries.
The final chunk may be smaller than the target size."""


@pytest.fixture
def structured_markdown():
    """Well-structured markdown with clear hierarchy."""
    return """# Chapter 1: Getting Started

Welcome to the getting started guide.

## 1.1 Installation

To install, run the following command:
```
pip install package
```

## 1.2 Configuration

Configure the settings in config.yaml file.

# Chapter 2: Usage

This chapter covers basic usage.

## 2.1 Basic Commands

Here are the basic commands you need to know.

### 2.1.1 Command One

The first command does X.

### 2.1.2 Command Two

The second command does Y.

## 2.2 Advanced Usage

For advanced users, additional options are available.

# Chapter 3: Troubleshooting

Common issues and solutions.
"""
