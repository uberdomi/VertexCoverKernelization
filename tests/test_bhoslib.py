"""Tests for the BhoslibHandler data pipeline.

Marker conventions
------------------
@pytest.mark.quick        — assumes data is already present in data/bhoslib/;
                            safe to run on every commit.
@pytest.mark.integration  — wipes data/bhoslib/ and re-downloads everything
                            from scratch; run only when validating a fresh checkout.
                            Excluded from the default test run (see pyproject.toml).
"""

import pytest

from vcker.graphs import Graph
from vcker.input_data.bhoslib import BhoslibHandler

from .handler_test_base import BaseHandlerIntegrationTests, BaseHandlerTests


# ---------------------------------------------------------------------------
# Quick tests — require data/bhoslib/*.clq to already exist
# ---------------------------------------------------------------------------


@pytest.mark.quick
class TestBhoslibHandlerQuick(BaseHandlerTests):
    """Fast smoke-tests against already-downloaded BHOSLIB data."""

    handler_class = BhoslibHandler
    expected_count = None  # number of files depends on the remote page

    @pytest.mark.skip(
        reason="Reproducibility requires live network access; covered by integration tests."
    )
    def test_generation_is_reproducible(self):
        pass

    def test_graph_names_start_with_frb(self):
        """Graph names loaded from the BHOSLIB dataset start with 'frb'."""
        handler = BhoslibHandler(force_redownload=False)
        handler.download_data()

        _name, graph = next(handler.get_named_graphs())

        assert _name.startswith("frb")
        assert isinstance(graph, Graph)


# ---------------------------------------------------------------------------
# Integration tests — download from scratch
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestBhoslibHandlerIntegration(BaseHandlerIntegrationTests):
    """End-to-end tests that wipe and re-download all BHOSLIB data."""

    handler_class = BhoslibHandler
    expected_count = None  # number of files depends on the remote page
