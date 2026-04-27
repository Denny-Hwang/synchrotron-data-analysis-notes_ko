"""Tests for the note loader.

Tests frontmatter parsing, graceful degradation for notes without
frontmatter, and controlled vocabulary validation.

Ref: TST-001 (test_plan.md) — Unit tests for note parser.
Ref: DC-001 (data_contracts.md) — Schema and vocabularies.
"""

import textwrap
from pathlib import Path

import pytest

import sys

_EXPLORER_DIR = Path(__file__).resolve().parent.parent
if str(_EXPLORER_DIR) not in sys.path:
    sys.path.insert(0, str(_EXPLORER_DIR))

from lib.notes import Note, _parse_note, _title_from_filename, load_notes


def test_title_from_filename() -> None:
    """Underscores and hyphens become spaces, result is title-cased."""
    assert _title_from_filename("ai_ml_methods") == "Ai Ml Methods"
    assert _title_from_filename("tomography") == "Tomography"
    assert _title_from_filename("xrf-microscopy") == "Xrf Microscopy"


def test_parse_note_with_frontmatter(tmp_path: Path) -> None:
    """Notes with valid YAML frontmatter are parsed correctly."""
    note_file = tmp_path / "test_note.md"
    note_file.write_text(textwrap.dedent("""\
        ---
        title: "TomoGAN Denoising"
        cluster: explore
        tags: [denoising, GAN, tomography]
        modality: tomography
        beamline: [2-BM, 32-ID]
        related_publications: [review_tomogan_2020.md]
        ---
        # TomoGAN

        Body content here.
    """))

    note = _parse_note(note_file, "03_ai_ml_methods")

    assert note.title == "TomoGAN Denoising"
    assert note.cluster == "explore"
    assert note.tags == ["denoising", "GAN", "tomography"]
    assert note.modality == "tomography"
    assert note.beamline == ["2-BM", "32-ID"]
    assert note.related_publications == ["review_tomogan_2020.md"]
    assert note.has_frontmatter is True
    assert "Body content here." in note.body


def test_parse_note_without_frontmatter(tmp_path: Path) -> None:
    """Notes without frontmatter get inferred title and cluster."""
    note_file = tmp_path / "xrf_microscopy.md"
    note_file.write_text("# XRF Microscopy\n\nContent about XRF.")

    note = _parse_note(note_file, "02_xray_modalities")

    assert note.title == "Xrf Microscopy"  # inferred from filename
    assert note.cluster == "explore"  # inferred from folder mapping
    assert note.tags == []
    assert note.modality is None
    assert note.beamline == []
    assert note.has_frontmatter is False


def test_parse_note_partial_frontmatter(tmp_path: Path) -> None:
    """Notes with only some frontmatter fields use defaults for the rest."""
    note_file = tmp_path / "partial.md"
    note_file.write_text(textwrap.dedent("""\
        ---
        title: "Partial Note"
        tags: [test]
        ---
        Body.
    """))

    note = _parse_note(note_file, "01_program_overview")

    assert note.title == "Partial Note"
    assert note.tags == ["test"]
    assert note.cluster == "discover"  # inferred from folder
    assert note.modality is None
    assert note.has_frontmatter is True


def test_invalid_vocabulary_warns(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Invalid controlled vocabulary values produce warnings."""
    note_file = tmp_path / "bad.md"
    note_file.write_text(textwrap.dedent("""\
        ---
        title: "Bad Values"
        cluster: invalid_cluster
        modality: invalid_modality
        beamline: [99-ZZ]
        tags: []
        ---
        Body.
    """))

    import logging
    with caplog.at_level(logging.WARNING):
        note = _parse_note(note_file, "01_program_overview")

    assert "Invalid cluster value" in caplog.text
    assert "Invalid modality value" in caplog.text
    assert "Invalid beamline value" in caplog.text
    # Note still loads despite warnings
    assert note.title == "Bad Values"


def test_load_notes_from_real_repo() -> None:
    """load_notes loads notes from the actual repo."""
    repo_root = _EXPLORER_DIR.parent
    notes = load_notes(repo_root)

    # Should find notes in at least some folders
    assert len(notes) > 0

    # All notes should have a non-empty title
    for note in notes:
        assert note.title, f"Note at {note.path} has empty title"

    # All notes should have a valid cluster
    valid_clusters = {"discover", "explore", "build"}
    for note in notes:
        assert note.cluster in valid_clusters, f"Note {note.path} has invalid cluster: {note.cluster}"
