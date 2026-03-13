"""Shared test framework for any Handler implementation.

Provides two base classes:

    BaseHandlerTests
        Five shared quick-test cases that assume data has already been
        generated/downloaded to disk.  Concrete subclasses must set:

            handler_class : type[Handler]
                The Handler subclass under test.
            expected_count : int | None
                Exact number of graphs expected from get_named_graphs(), or
                None to assert "at least one".

    BaseHandlerIntegrationTests
        Two integration-level cases that wipe the handler's data folder before
        each test and regenerate everything from scratch.  Same class attributes
        required as above.

Usage (quick)::

    @pytest.mark.quick
    class TestMyHandlerQuick(BaseHandlerTests):
        handler_class = MyHandler
        expected_count = len(MyHandler.configs)

Usage (integration)::

    @pytest.mark.integration
    class TestMyHandlerIntegration(BaseHandlerIntegrationTests):
        handler_class = MyHandler
        expected_count = len(MyHandler.configs)
"""

import pytest

from vcker.input_data import Handler, get_handler, supported_handlers


class BaseHandlerTests:
    """Shared quick-test cases for any Handler subclass.

    Assumes data is already present on disk (generated or downloaded by a
    prior run).  Safe to run on every commit when data is cached.
    """

    handler_class: supported_handlers
    expected_count: int | None = None

    def make_handler(self, force_redownload: bool = False) -> Handler:
        return get_handler(self.handler_class, force_redownload)

    def test_skip_existing_files(self):
        """download_data() with force_redownload=False skips already-present files."""
        handler = self.make_handler(force_redownload=False)
        handler.download_data()

        assert handler._data_downloaded
        assert len(handler._downloaded_paths) > 0

    def test_get_named_graphs_count(self):
        """get_named_graphs() returns the expected number of (name, Graph) pairs."""
        handler = self.make_handler()
        handler.download_data()

        results = list(handler.get_named_graphs())

        if self.expected_count is not None:
            assert len(results) == self.expected_count
        else:
            assert len(results) > 0

    def test_graphs_have_positive_edge_count(self):
        """Every loaded graph has at least one edge."""
        handler = self.make_handler()
        handler.download_data()

        for _name, graph in handler.get_named_graphs():
            assert graph.n_edges > 0

    def test_neighbors_are_subsets_of_vertices(self):
        """For a sample of vertices in the first graph, all neighbors lie within the vertex set."""
        handler = self.make_handler()
        handler.download_data()

        _name, graph = next(handler.get_named_graphs())

        for v in list(graph._nodes)[:20]:
            assert graph.neighbors(v).issubset(graph._nodes)

    def test_generation_is_reproducible(self):
        """Two independently-initialized handlers produce graphs with identical edge counts."""
        h1 = self.make_handler(force_redownload=True)
        h1.download_data()

        h2 = self.make_handler(force_redownload=True)
        h2.download_data()

        for (_, g1), (_, g2) in zip(h1.get_named_graphs(), h2.get_named_graphs()):
            assert g1.n_edges == g2.n_edges


class BaseHandlerIntegrationTests:
    """Shared integration-test cases for any Handler subclass.

    Wipes the handler's data folder before each test and regenerates (or
    re-downloads) everything from scratch.
    """

    handler_class: supported_handlers
    expected_count: int | None = None

    def make_handler(self, force_redownload: bool = True) -> Handler:
        return get_handler(self.handler_class, force_redownload)

    @pytest.fixture(autouse=True)
    def clean_data_folder(self):
        """Wipe the handler's data folder before each integration test."""
        self.make_handler().delete_data()
        yield

    def test_files_exist_after_download(self):
        """After a fresh download/generation, all expected files exist on disk."""
        handler = self.make_handler(force_redownload=True)
        handler.download_data()

        assert handler._data_downloaded
        assert len(handler._downloaded_paths) > 0
        for path in handler._downloaded_paths:
            assert path.exists(), f"Expected file not found: {path}"

    def test_full_pipeline_yields_valid_graphs(self):
        """After a fresh download/generation, get_named_graphs() yields valid Graph objects."""
        handler = self.make_handler(force_redownload=True)
        handler.download_data()

        count = 0
        for name, graph in handler.get_named_graphs():
            assert isinstance(name, str)
            assert graph.n_vertices > 0
            assert graph.n_edges > 0
            count += 1

        if self.expected_count is not None:
            assert count == self.expected_count
        else:
            assert count > 0
