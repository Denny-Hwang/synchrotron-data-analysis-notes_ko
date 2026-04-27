"""Tests for the IA mapping.

Verifies that the folder-to-cluster mapping is exhaustive and disjoint.

Ref: TST-001 (test_plan.md) — IA mapping tests.
Ref: IA-001 (information_architecture.md).
Ref: ADR-004 — 8 folders → 3 task clusters IA mapping.
"""

import sys
from pathlib import Path

_EXPLORER_DIR = Path(__file__).resolve().parent.parent
if str(_EXPLORER_DIR) not in sys.path:
    sys.path.insert(0, str(_EXPLORER_DIR))

from lib.ia import (
    CLUSTER_META,
    FOLDER_TO_CLUSTER,
    get_cluster_for_folder,
    get_folders_for_cluster,
)


def test_all_note_folders_mapped() -> None:
    """Every expected note folder is present in the mapping."""
    expected = {
        "01_program_overview",
        "02_xray_modalities",
        "03_ai_ml_methods",
        "04_publications",
        "05_tools_and_code",
        "06_data_structures",
        "07_data_pipeline",
        "08_references",
        "09_noise_catalog",
    }
    assert set(FOLDER_TO_CLUSTER.keys()) == expected


def test_mapping_is_exhaustive() -> None:
    """Every folder maps to a known cluster."""
    valid_clusters = {"discover", "explore", "build"}
    for folder, cluster in FOLDER_TO_CLUSTER.items():
        assert cluster in valid_clusters, f"{folder} maps to unknown cluster '{cluster}'"


def test_mapping_is_disjoint() -> None:
    """Each folder maps to exactly one cluster (no duplicates in values)."""
    # This is automatically true since it's a dict, but let's verify
    # by checking the reverse: each cluster's folders are unique across clusters
    all_folders: list[str] = []
    for cluster in ["discover", "explore", "build"]:
        folders = get_folders_for_cluster(cluster)
        all_folders.extend(folders)

    assert len(all_folders) == len(set(all_folders)), "Some folders appear in multiple clusters"
    assert len(all_folders) == len(FOLDER_TO_CLUSTER), "Not all folders covered by clusters"


def test_cluster_meta_complete() -> None:
    """CLUSTER_META has entries for all clusters."""
    for cluster_id in {"discover", "explore", "build"}:
        assert cluster_id in CLUSTER_META
        meta = CLUSTER_META[cluster_id]
        assert "name" in meta
        assert "description" in meta
        assert "color" in meta


def test_get_cluster_for_folder() -> None:
    """get_cluster_for_folder returns correct cluster or None."""
    assert get_cluster_for_folder("01_program_overview") == "discover"
    assert get_cluster_for_folder("03_ai_ml_methods") == "explore"
    assert get_cluster_for_folder("07_data_pipeline") == "build"
    assert get_cluster_for_folder("nonexistent") is None


def test_get_folders_for_cluster() -> None:
    """get_folders_for_cluster returns correct folder lists."""
    discover = get_folders_for_cluster("discover")
    assert "01_program_overview" in discover
    assert "08_references" in discover

    build = get_folders_for_cluster("build")
    assert "05_tools_and_code" in build
    assert "06_data_structures" in build
    assert "07_data_pipeline" in build
