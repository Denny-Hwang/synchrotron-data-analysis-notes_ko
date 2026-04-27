"""Footer component for eBERlight Explorer.

Renders the DOE acknowledgment block that must appear on every page.
Includes the funding statement, related links, and last-updated timestamp.

Ref: DS-001 (design_system.md) — Footer component spec.
Ref: FR-010 — DOE acknowledgment footer on every page.
Ref: NFR-001 — DOE Contract No. DE-AC02-06CH11357 requirement.
"""

import subprocess
from datetime import datetime

import streamlit as st


def _get_last_updated() -> str:
    """Get the last commit date from git, falling back to today's date.

    Returns:
        ISO date string (YYYY-MM-DD).
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ci"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()[:10]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return datetime.now().strftime("%Y-%m-%d")


def render_footer() -> None:
    """Render the DOE acknowledgment footer.

    Produces the footer with:
    - DOE funding statement with Contract No. DE-AC02-06CH11357
    - eBERlight program acknowledgment
    - Links to APS, eBERlight, and the source repository
    - Last-updated timestamp from git
    """
    last_updated = _get_last_updated()

    footer_html = f"""
    <div class="eberlight-footer">
        <p>
            This research used resources of the Advanced Photon Source,
            a U.S. Department of Energy (DOE) Office of Science user facility
            operated for the DOE Office of Science by Argonne National
            Laboratory under Contract No. DE-AC02-06CH11357.
        </p>
        <p>
            eBERlight is the integrated BER (Biological and Environmental Research)
            program at the Advanced Photon Source, combining multiple X-ray
            techniques for biological and environmental science.
        </p>
        <div class="eberlight-footer-links">
            <a href="https://www.aps.anl.gov/" target="_blank" rel="noopener">APS</a>
            <a href="https://eberlight.aps.anl.gov/" target="_blank" rel="noopener">eBERlight</a>
            <a href="https://github.com/Denny-Hwang/synchrotron-data-analysis-notes" target="_blank" rel="noopener">Repository</a>
        </div>
        <div class="eberlight-footer-updated">Last updated: {last_updated}</div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)
