"""Tests for the Pace2019Handler data pipeline.

Marker conventions
------------------
@pytest.mark.quick        — assumes data is already present in data/pace2019/;
                            safe to run on every commit.
@pytest.mark.integration  — wipes data/pace2019/ and re-downloads everything
                            from scratch; run only when validating a fresh checkout.
                            Excluded from the default test run (see pyproject.toml).
"""

import pytest

from vcker.graphs import Graph
from vcker.input_data import get_handler
from vcker.input_data.pace2019 import Pace2019Handler

from .handler_test_base import BaseHandlerIntegrationTests, BaseHandlerTests


# ---------------------------------------------------------------------------
# Quick tests — require data/pace2019/*.gr to already exist
# ---------------------------------------------------------------------------


@pytest.mark.quick
class TestPace2019HandlerQuick(BaseHandlerTests):
    """Fast smoke-tests against already-downloaded PACE 2019 data."""

    handler_class = "Pace2019Handler"
    expected_count = Pace2019Handler._n_instances

    @pytest.mark.skip(
        reason="Reproducibility requires live network access; covered by integration tests."
    )
    def test_generation_is_reproducible(self):
        pass

    def test_graph_names_start_with_vc_exact(self):
        """Graph names from the PACE 2019 dataset start with 'vc-exact'."""
        handler = get_handler("Pace2019Handler", False)
        handler.download_data()

        for name, graph in handler.get_named_graphs():
            assert name.startswith("vc-exact"), (
                f"Expected name to start with 'vc-exact', got '{name}'"
            )
            assert isinstance(graph, Graph)


# ---------------------------------------------------------------------------
# Integration tests — download from scratch
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestPace2019HandlerIntegration(BaseHandlerIntegrationTests):
    """End-to-end tests that wipe and re-download all PACE 2019 data."""

    handler_class = "Pace2019Handler"
    expected_count = Pace2019Handler._n_instances
