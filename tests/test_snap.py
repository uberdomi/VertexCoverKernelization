"""Tests for the SnapHandler data pipeline.

Marker conventions
------------------
@pytest.mark.quick        — assumes data is already present in data/snap/;
                            safe to run on every commit.
@pytest.mark.integration  — wipes data/snap/ and re-downloads everything
                            from scratch; run only when validating a fresh checkout.
                            Excluded from the default test run (see pyproject.toml).
"""

import pytest

from vcker.input_data import get_handler
from vcker.input_data.snap import SnapHandler

from .handler_test_base import BaseHandlerIntegrationTests, BaseHandlerTests


# ---------------------------------------------------------------------------
# Quick tests — require data/snap/*.txt to already exist
# ---------------------------------------------------------------------------


@pytest.mark.quick
class TestSnapHandlerQuick(BaseHandlerTests):
    """Fast smoke-tests against already-downloaded SNAP data."""

    handler_class = "SnapHandler"
    expected_count = len(SnapHandler._url_list)  # one graph per source URL

    @pytest.mark.skip(
        reason="Reproducibility requires live network access; covered by integration tests."
    )
    def test_generation_is_reproducible(self):
        pass

    def test_snap_graphs_are_non_trivial(self):
        """Every SNAP real-world network has at least 1 000 vertices."""
        handler = get_handler("SnapHandler", False)
        handler.download_data()

        for name, graph in handler.get_named_graphs():
            assert graph.n_vertices >= 1000, (
                f"Expected at least 1 000 vertices in SNAP graph '{name}', "
                f"got {graph.n_vertices}"
            )


# ---------------------------------------------------------------------------
# Integration tests — download from scratch
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestSnapHandlerIntegration(BaseHandlerIntegrationTests):
    """End-to-end tests that wipe and re-download all SNAP data."""

    handler_class = "SnapHandler"
    expected_count = len(SnapHandler._url_list)
