"""Tests for the BarabasiAlbertHandler graph generation pipeline.

Marker conventions
------------------
@pytest.mark.quick        - assumes data is already present in data/barabasi_albert/;
                            safe to run on every commit.
@pytest.mark.integration  - wipes data/barabasi_albert/ and regenerates everything
                            from scratch; excluded from the default test run.
"""

import pytest

from vcker.input_data.barabasi_albert import BarabasiAlbertHandler

from .handler_test_base import BaseHandlerIntegrationTests, BaseHandlerTests


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_EXPECTED_CONFIGS = BarabasiAlbertHandler.configs


# ---------------------------------------------------------------------------
# Quick tests — require data/barabasi_albert/*.clq to already exist
# ---------------------------------------------------------------------------


@pytest.mark.quick
class TestBarabasiAlbertHandlerQuick(BaseHandlerTests):
    """Fast smoke-tests against already-generated Barabási-Albert data."""

    handler_class = BarabasiAlbertHandler
    expected_count = len(_EXPECTED_CONFIGS)

    def test_graphs_have_correct_vertex_counts(self):
        """Each graph has exactly the number of vertices specified in its config (inferred from the file name)."""
        handler = BarabasiAlbertHandler(force_redownload=False)
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
class TestBarabasiAlbertHandlerIntegration(BaseHandlerIntegrationTests):
    """End-to-end tests that wipe and regenerate all Barabási-Albert data."""

    handler_class = BarabasiAlbertHandler
    expected_count = len(_EXPECTED_CONFIGS)
