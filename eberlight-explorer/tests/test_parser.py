"""콘텐츠 파서 유틸리티 테스트."""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.content_parser import (
    load_yaml,
    extract_title,
    extract_metadata_table,
    extract_section,
    extract_tldr,
)


def test_load_yaml():
    data = load_yaml("content_index.yaml")
    assert "sections" in data
    assert len(data["sections"]) > 0


def test_load_modalities():
    data = load_yaml("modality_metadata.yaml")
    assert "modalities" in data
    assert len(data["modalities"]) == 6


def test_load_methods():
    data = load_yaml("method_taxonomy.yaml")
    assert "categories" in data
    assert len(data["categories"]) == 5


def test_load_publications():
    data = load_yaml("publication_catalog.yaml")
    assert "publications" in data
    assert len(data["publications"]) > 0


def test_load_tools():
    data = load_yaml("tool_catalog.yaml")
    assert "tools" in data
    assert len(data["tools"]) > 0


def test_extract_title():
    md = "# My Title\n\nSome content here."
    assert extract_title(md) == "My Title"


def test_extract_title_no_title():
    md = "Some content without a heading."
    assert extract_title(md) == "Untitled"


def test_extract_section():
    md = "## Background\n\nSome bg.\n\n## Method\n\nSome method.\n\n## Results\n\nResults here."
    result = extract_section(md, "Method")
    assert "Some method." in result
    assert "Results here" not in result


def test_extract_section_not_found():
    md = "## Background\n\nSome bg."
    result = extract_section(md, "NonExistent")
    assert result is None


def test_extract_tldr():
    md = "## TL;DR\n\nThis is the summary.\n\n## Background\n\nMore stuff."
    result = extract_tldr(md)
    assert "This is the summary." in result


def test_extract_metadata_table():
    md = """## Metadata

| Field | Value |
|-------|-------|
| **Title** | My Paper |
| **Year** | 2023 |
| **Authors** | Smith, J. |

## Content
"""
    meta = extract_metadata_table(md)
    assert meta["Title"] == "My Paper"
    assert meta["Year"] == "2023"
