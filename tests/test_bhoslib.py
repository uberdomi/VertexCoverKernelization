"""Tests for the BhoslibHandler data pipeline.

Marker conventions
------------------
@pytest.mark.quick        — assumes data is already present in data/bhoslib/;
                            safe to run on every commit.
@pytest.mark.integration  — wipes data/bhoslib/ and re-downloads everything
                            from scratch; run only when validating a fresh checkout.
                            Excluded from the default test run (see pyproject.toml).
"""

import shutil

import pytest

from vcker.input_data.bhoslib import BhoslibHandler
from vcker.graphs import Graph


# ---------------------------------------------------------------------------
# Quick tests — require data/bhoslib/*.clq to already exist
# ---------------------------------------------------------------------------


@pytest.mark.quick
class TestBhoslibHandlerQuick:
    """Fast smoke-tests against already-downloaded data."""

    def test_download_data_skips_existing(self):
        """download_data() completes without error and finds existing files."""
        handler = BhoslibHandler(force_redownload=False)
        handler.download_data()

        assert handler._data_downloaded
        assert len(handler._downloaded_paths) > 0

    def test_get_named_graphs_yields_at_least_one(self):
        """get_named_graphs() yields at least one (name, Graph) pair."""
        handler = BhoslibHandler(force_redownload=False)
        handler.download_data()

        iterator = handler.get_named_graphs()
        name, graph = next(iterator)

        assert isinstance(name, str) and name.startswith("frb")
        assert isinstance(graph, Graph)

    def test_first_graph_has_correct_structure(self):
        """The first loaded graph has a positive vertex and edge count."""
        handler = BhoslibHandler(force_redownload=False)
        handler.download_data()

        _name, graph = next(handler.get_named_graphs())

        assert graph.n_vertices > 0
        assert graph.n_edges > 0

    def test_first_graph_neighbors_are_subsets_of_nodes(self):
        """Every neighbor of every node is itself a node in the graph."""
        handler = BhoslibHandler(force_redownload=False)
        handler.download_data()

        _name, graph = next(handler.get_named_graphs())

        for v in list(graph._nodes)[:20]:  # sample — not exhaustive
            assert graph.neighbors(v).issubset(graph._nodes)


# ---------------------------------------------------------------------------
# Integration tests — download from scratch
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestBhoslibHandlerIntegration:
    """End-to-end tests that wipe and re-download all data."""

    @pytest.fixture(autouse=True)
    def clean_data_folder(self):
        """Remove the bhoslib data folder before the test, restore nothing after."""
        from vcker.input_data.utils import get_data_folder

        bhoslib_dir = get_data_folder() / "bhoslib"
        if bhoslib_dir.exists():
            shutil.rmtree(bhoslib_dir)

        yield  # run the test

        # Leave the freshly-downloaded data in place for subsequent quick tests.

    def test_full_download_from_scratch(self):
        """Force-download all files and confirm paths exist on disk."""
        handler = BhoslibHandler(force_redownload=True)
        handler.download_data()

        assert handler._data_downloaded
        assert len(handler._downloaded_paths) > 0
        for path in handler._downloaded_paths:
            assert path.exists(), f"Expected file not found: {path}"

    def test_full_pipeline_yields_graphs(self):
        """After a fresh download, get_named_graphs() yields valid Graph objects."""
        handler = BhoslibHandler(force_redownload=True)
        handler.download_data()

        count = 0
        for name, graph in handler.get_named_graphs():
            assert isinstance(name, str)
            assert graph.n_vertices > 0
            assert graph.n_edges > 0
            count += 1

        assert count > 0, "No graphs were yielded after a fresh download."
