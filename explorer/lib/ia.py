"""Information architecture mapping for eBERlight Explorer.

Defines the single constant mapping 9 note folders to 3 task-oriented
clusters. This is the one place to change if the IA evolves.

Ref: IA-001 (information_architecture.md) — Folder-to-cluster mapping.
Ref: ADR-004 — 8 folders → 3 task clusters IA mapping.
"""

from typing import Final

# Folder-to-cluster mapping. Every note folder maps to exactly one cluster.
# The mapping is exhaustive (all folders assigned) and disjoint (no overlap).
FOLDER_TO_CLUSTER: Final[dict[str, str]] = {
    "01_program_overview": "discover",
    "02_xray_modalities": "explore",
    "03_ai_ml_methods": "explore",
    "04_publications": "explore",
    "05_tools_and_code": "build",
    "06_data_structures": "build",
    "07_data_pipeline": "build",
    "08_references": "discover",
    "09_noise_catalog": "explore",
}

# Human-readable cluster names and descriptions.
CLUSTER_META: Final[dict[str, dict[str, str]]] = {
    "discover": {
        "name": "Discover the Program",
        "description": (
            "BER mission, APS facility, 15 beamline profiles, "
            "partner facilities, research domains, glossary, and references."
        ),
        "color": "#0033A0",
    },
    "explore": {
        "name": "Explore the Science",
        "description": (
            "6 X-ray modalities, 14 AI/ML methods, 14 publication reviews, "
            "and 29+ noise/artifact types with troubleshooter."
        ),
        "color": "#00A3E0",
    },
    "build": {
        "name": "Build and Compute",
        "description": (
            "7 open-source tools with reverse engineering, HDF5 data schemas, "
            "EDA guides, and the end-to-end data pipeline architecture."
        ),
        "color": "#F47B20",
    },
}


def get_cluster_for_folder(folder_name: str) -> str | None:
    """Return the cluster ID for a given folder name.

    Args:
        folder_name: The folder name (e.g., '02_xray_modalities').

    Returns:
        Cluster ID ('discover', 'explore', or 'build'), or None if
        the folder is not in the mapping.
    """
    return FOLDER_TO_CLUSTER.get(folder_name)


def get_folders_for_cluster(cluster: str) -> list[str]:
    """Return all folder names belonging to a cluster.

    Args:
        cluster: Cluster ID ('discover', 'explore', or 'build').

    Returns:
        List of folder names in the cluster.
    """
    return [f for f, c in FOLDER_TO_CLUSTER.items() if c == cluster]
