"""Tests for the ErdosRenyiHandler graph generation pipeline.

Marker conventions
------------------
@pytest.mark.quick        — assumes data is already present in data/erdos_renyi/;
                            safe to run on every commit.
@pytest.mark.integration  — wipes data/erdos_renyi/ and regenerates everything
                            from scratch; excluded from the default test run.
"""

import pytest

from vcker.input_data.erdos_renyi import ErdosRenyiHandler

from .handler_test_base import BaseHandlerIntegrationTests, BaseHandlerTests


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_EXPECTED_CONFIGS = ErdosRenyiHandler.configs


# ---------------------------------------------------------------------------
# Quick tests — require data/erdos_renyi/*.clq to already exist
# ---------------------------------------------------------------------------


@pytest.mark.quick
class TestErdosRenyiHandlerQuick(BaseHandlerTests):
    """Fast smoke-tests against already-generated Erdös-Renyi data."""

    handler_class = ErdosRenyiHandler
    expected_count = len(_EXPECTED_CONFIGS)

    def test_graphs_have_correct_vertex_counts(self):
        """Each graph has exactly the number of vertices specified in its config (inferred from the file name)."""
        handler = ErdosRenyiHandler(force_redownload=False)
        handler.download_data()

        for name, graph in handler.get_named_graphs():
            parts = name.split(sep="_")
            n = int(parts[2])

            assert graph.n_vertices == n, (
                f"Expected {n} vertices, got {graph.n_vertices}"
            )


# ---------------------------------------------------------------------------
# Integration tests — regenerate from scratch
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestErdosRenyiHandlerIntegration(BaseHandlerIntegrationTests):
    """End-to-end tests that wipe and regenerate all Erdös-Renyi data."""

    handler_class = ErdosRenyiHandler
    expected_count = len(_EXPECTED_CONFIGS)
