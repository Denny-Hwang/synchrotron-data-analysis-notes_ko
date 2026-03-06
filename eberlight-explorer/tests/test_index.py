"""인덱스 검증 테스트."""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.build_index import validate_file_references, count_repo_files


def test_validate_file_references():
    errors = validate_file_references()
    # Print errors for debugging
    for e in errors:
        print(e)
    assert len(errors) == 0, f"Found {len(errors)} missing file references"


def test_count_repo_files():
    counts = count_repo_files()
    assert counts["md"] > 50, f"Expected 50+ md files, got {counts['md']}"
