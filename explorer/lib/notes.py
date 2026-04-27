"""Note loader for eBERlight Explorer.

Walks the note folders, parses optional YAML frontmatter, and returns
structured Note objects. Handles graceful degradation for notes without
frontmatter.

Ref: ADR-002 — Notes remain single source of truth.
Ref: ADR-003 — YAML frontmatter schema.
Ref: DC-001 (data_contracts.md) — Schema and controlled vocabularies.
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .ia import FOLDER_TO_CLUSTER

logger = logging.getLogger(__name__)

# Controlled vocabularies from DC-001
VALID_CLUSTERS = {"discover", "explore", "build"}
VALID_MODALITIES = {
    "tomography",
    "xrf_microscopy",
    "ptychography",
    "spectroscopy",
    "crystallography",
    "scattering",
    "cross_cutting",
}
VALID_BEAMLINES = {
    "2-BM",
    "2-ID-D",
    "2-ID-E",
    "3-ID",
    "5-BM",
    "7-BM",
    "9-BM",
    "9-ID",
    "11-BM",
    "11-ID-B",
    "11-ID-C",
    "12-ID",
    "17-BM",
    "20-BM",
    "20-ID",
    "26-ID",
    "32-ID",
    "34-ID",
}

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@dataclass
class Note:
    """Represents a single note file with parsed metadata."""

    path: Path
    folder: str
    title: str
    body: str
    cluster: str
    tags: list[str] = field(default_factory=list)
    modality: str | None = None
    beamline: list[str] = field(default_factory=list)
    related_publications: list[str] = field(default_factory=list)
    related_tools: list[str] = field(default_factory=list)
    description: str = ""
    category: str = ""
    has_frontmatter: bool = False


def _title_from_filename(filename: str) -> str:
    """Infer a human-readable title from a filename.

    Args:
        filename: The filename without extension (e.g., 'ai_ml_methods').

    Returns:
        Title-cased string with underscores replaced by spaces.
    """
    name = filename.replace("_", " ").replace("-", " ")
    return name.title()


def _validate_vocabulary(value: str, valid_set: set[str], field_name: str, path: Path) -> bool:
    """Check if a value is in the controlled vocabulary.

    Args:
        value: The value to validate.
        valid_set: Set of allowed values.
        field_name: Name of the field (for logging).
        path: Path to the note file (for logging).

    Returns:
        True if valid, False otherwise.
    """
    if value not in valid_set:
        logger.warning(
            "Invalid %s value '%s' in %s (allowed: %s)",
            field_name,
            value,
            path,
            ", ".join(sorted(valid_set)),
        )
        return False
    return True


def _parse_note(path: Path, folder: str) -> Note:
    """Parse a single note file, extracting frontmatter if present.

    Args:
        path: Path to the markdown file.
        folder: Name of the parent note folder.

    Returns:
        A Note object with parsed or inferred metadata.
    """
    content = path.read_text(encoding="utf-8")

    # Try to extract YAML frontmatter
    fm_match = _FRONTMATTER_RE.match(content)
    if fm_match:
        try:
            fm = yaml.safe_load(fm_match.group(1)) or {}
        except yaml.YAMLError:
            logger.warning("Invalid YAML frontmatter in %s", path)
            fm = {}
        body = content[fm_match.end():]
        has_frontmatter = bool(fm)
    else:
        fm = {}
        body = content
        has_frontmatter = False

    # Infer cluster from folder if not in frontmatter
    cluster = fm.get("cluster", FOLDER_TO_CLUSTER.get(folder, "explore"))
    if isinstance(cluster, str):
        _validate_vocabulary(cluster, VALID_CLUSTERS, "cluster", path)

    # Validate modality
    modality = fm.get("modality")
    if modality and isinstance(modality, str):
        _validate_vocabulary(modality, VALID_MODALITIES, "modality", path)

    # Validate beamlines
    beamline_raw = fm.get("beamline", [])
    beamlines = beamline_raw if isinstance(beamline_raw, list) else [beamline_raw]
    for bl in beamlines:
        if isinstance(bl, str):
            _validate_vocabulary(bl, VALID_BEAMLINES, "beamline", path)

    return Note(
        path=path,
        folder=folder,
        title=fm.get("title", _title_from_filename(path.stem)),
        body=body,
        cluster=cluster if isinstance(cluster, str) else "explore",
        tags=fm.get("tags", []) if isinstance(fm.get("tags"), list) else [],
        modality=modality if isinstance(modality, str) else None,
        beamline=[b for b in beamlines if isinstance(b, str)],
        related_publications=fm.get("related_publications", []) or [],
        related_tools=fm.get("related_tools", []) or [],
        description=fm.get("description", ""),
        category=fm.get("category", ""),
        has_frontmatter=has_frontmatter,
    )


def load_notes(root: Path) -> list[Note]:
    """Load all notes from the note folders.

    Walks each folder in FOLDER_TO_CLUSTER, finds all .md files, and
    parses them into Note objects. Notes without YAML frontmatter load
    with inferred metadata (title from filename, cluster from folder).

    Args:
        root: Path to the repository root.

    Returns:
        List of Note objects sorted by folder then filename.
    """
    notes: list[Note] = []

    for folder in sorted(FOLDER_TO_CLUSTER.keys()):
        folder_path = root / folder
        if not folder_path.is_dir():
            logger.warning("Note folder not found: %s", folder_path)
            continue

        for md_path in sorted(folder_path.rglob("*.md")):
            note = _parse_note(md_path, folder)
            notes.append(note)

    logger.info("Loaded %d notes from %d folders", len(notes), len(FOLDER_TO_CLUSTER))
    return notes
