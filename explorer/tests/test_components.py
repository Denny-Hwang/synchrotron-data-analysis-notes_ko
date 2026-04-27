"""Smoke tests for eBERlight Explorer UI components.

Each render function is tested to ensure it runs without error and
produces non-empty output via st.markdown.

Ref: TST-001 (test_plan.md) — Component smoke tests.
"""

from unittest.mock import MagicMock, patch


@patch("streamlit.markdown")
def test_render_header(mock_markdown: MagicMock) -> None:
    """render_header() calls st.markdown with non-empty HTML."""
    from components.header import render_header

    render_header()

    mock_markdown.assert_called_once()
    html_output = mock_markdown.call_args[0][0]
    assert len(html_output.strip()) > 0
    assert "eBERlight Explorer" in html_output
    assert "eberlight-header" in html_output


@patch("streamlit.markdown")
def test_render_breadcrumb_with_items(mock_markdown: MagicMock) -> None:
    """render_breadcrumb() renders linked and current items."""
    from components.breadcrumb import render_breadcrumb

    render_breadcrumb([("Home", "/"), ("Explore", "/explore"), ("TomoGAN", None)])

    mock_markdown.assert_called_once()
    html_output = mock_markdown.call_args[0][0]
    assert "Home" in html_output
    assert "Explore" in html_output
    assert "TomoGAN" in html_output
    assert 'class="current"' in html_output
    assert "eberlight-breadcrumb" in html_output


@patch("streamlit.markdown")
def test_render_breadcrumb_empty(mock_markdown: MagicMock) -> None:
    """render_breadcrumb() with empty list produces no output."""
    from components.breadcrumb import render_breadcrumb

    render_breadcrumb([])

    mock_markdown.assert_not_called()


@patch("streamlit.markdown")
def test_render_footer(mock_markdown: MagicMock) -> None:
    """render_footer() includes DOE acknowledgment and contract number."""
    from components.footer import render_footer

    render_footer()

    mock_markdown.assert_called_once()
    html_output = mock_markdown.call_args[0][0]
    assert len(html_output.strip()) > 0
    assert "DE-AC02-06CH11357" in html_output
    assert "eberlight-footer" in html_output
    assert "Advanced Photon Source" in html_output
    assert "eBERlight" in html_output
