"""Tests for the BarabasiAlbertHandler graph generation pipeline.

Marker conventions
------------------
@pytest.mark.quick        - assumes data is already present in data/barabasi_albert/;
                            safe to run on every commit.
@pytest.mark.integration  - wipes data/barabasi_albert/ and regenerates everything
                            from scratch; excluded from the default test run.
"""

import shutil

import pytest

from vcker.graphs import Graph
from vcker.input_data.barabasi_albert import BarabasiAlbertHandler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_EXPECTED_CONFIGS = BarabasiAlbertHandler.configs


# ---------------------------------------------------------------------------
# Quick tests - require data/BarabasiAlbert/*.clq to already exist
# ---------------------------------------------------------------------------


@pytest.mark.quick
class TestBarabasiAlbertHandlerQuick:
    """Fast smoke-tests against already-generated Barabási-Albert data."""

    def test_download_data_skips_existing(self):
        """download_data() completes without error and finds existing files."""
        handler = BarabasiAlbertHandler(force_redownload=False)
        handler.download_data()

        assert handler._data_downloaded
        assert len(handler._downloaded_paths) == len(_EXPECTED_CONFIGS)

    def test_get_named_graphs_yields_all_instances(self):
        """get_named_graphs() yields exactly one (name, Graph) pair per config."""
        handler = BarabasiAlbertHandler(force_redownload=False)
        handler.download_data()

        results = list(handler.get_named_graphs())

        assert len(results) == len(_EXPECTED_CONFIGS)
        for name, graph in results:
            assert isinstance(name, str) and name.startswith("ba_graph_")
            assert isinstance(graph, Graph)

    def test_graphs_have_correct_vertex_counts(self):
        """Each graph has exactly the number of vertices specified in its config."""
        handler = BarabasiAlbertHandler(force_redownload=False)
        handler.download_data()

        for name, graph in handler.get_named_graphs():
            parts = name.split(sep="_")
            n = int(parts[2])

            assert graph.n_vertices == n, (
                f"Expected {n} vertices, got {graph.n_vertices}"
            )

    def test_graphs_have_positive_edge_counts(self):
        """Each generated Barabási-Albert graph has at least one edge."""
        handler = BarabasiAlbertHandler(force_redownload=False)
        handler.download_data()

        for _name, graph in handler.get_named_graphs():
            assert graph.n_edges > 0

    def test_neighbors_are_subsets_of_nodes(self):
        """For the first graph: sampled neighbor sets stay within the node set."""
        handler = BarabasiAlbertHandler(force_redownload=False)
        handler.download_data()

        _name, graph = next(handler.get_named_graphs())

        for v in list(graph._nodes)[:20]:
            assert graph.neighbors(v).issubset(graph._nodes)

    def test_generation_is_reproducible(self):
        """Two handlers with the same seed produce identical edge counts."""
        h1 = BarabasiAlbertHandler(force_redownload=True)
        h1.download_data()

        h2 = BarabasiAlbertHandler(force_redownload=True)
        h2.download_data()

        for (_n1, g1), (_n2, g2) in zip(h1.get_named_graphs(), h2.get_named_graphs()):
            assert g1.n_edges == g2.n_edges


# ---------------------------------------------------------------------------
# Integration tests - regenerate from scratch
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestBarabasiAlbertHandlerIntegration:
    """End-to-end tests that wipe and regenerate all Barabási-Albert data."""

    @pytest.fixture(autouse=True)
    def clean_data_folder(self):
        """Remove the Barabási-Albert data folder before the test."""
        from vcker.input_data.utils import get_data_folder

        barabasi_albert_dir = get_data_folder() / "barabasi_albert"
        if barabasi_albert_dir.exists():
            shutil.rmtree(barabasi_albert_dir)

        yield

        # Leave the freshly-generated data in place for subsequent quick tests.

    def test_full_generation_from_scratch(self):
        """Force-generate all Barabási-Albert instances and confirm files exist on disk."""
        handler = BarabasiAlbertHandler(force_redownload=True)
        handler.download_data()

        assert handler._data_downloaded
        assert len(handler._downloaded_paths) == len(_EXPECTED_CONFIGS)
        for path in handler._downloaded_paths:
            assert path.exists(), f"Expected file not found: {path}"

    def test_full_pipeline_yields_graphs(self):
        """After fresh generation, get_named_graphs() yields valid Graph objects."""
        handler = BarabasiAlbertHandler(force_redownload=True)
        handler.download_data()

        count = 0
        for name, graph in handler.get_named_graphs():
            assert isinstance(name, str)
            assert graph.n_vertices > 0
            assert graph.n_edges > 0
            count += 1

        assert count == len(_EXPECTED_CONFIGS)
