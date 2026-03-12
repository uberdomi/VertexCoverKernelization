"""Preferential Attachment Model (PAM) - heavy-tailed graph distribution with specific clustering coefficient and a small diameter - fitting observed evidence (e.g. WWW graphs). Vertices are organized around “clusters” of high degree vertices. Apart from the WWW, such models resemble graphs emerging by distinct applications such as collaboration networks (i.e. in biology, in science, or in film actors), word co-occurrences, or neural networks"""

import logging
from collections.abc import Iterator
from typing import ClassVar
from pathlib import Path
import numpy as np

from tqdm import tqdm

from ..graphs import Graph
from .utils import get_data_folder

logger = logging.getLogger(__name__)


class PamHandler:
    """Preferential Attachment Model (PAM) - heavy-tailed graph distribution with specific clustering coefficient and a small diameter"""

    # Adjust parameters
    configs: ClassVar[list[tuple[int, int]]] = [  # n - m
        (2000, 4),
        (2000, 8),
        (1000, 4),
        (1000, 8),
    ]

    def __init__(self, force_redownload: bool = False) -> None:
        self.force_redownload = force_redownload
        # Seed for reproducibility
        self._rng = np.random.default_rng(seed=2026)

        self._root_folder = get_data_folder() / "pam"
        self._root_folder.mkdir(parents=True, exist_ok=True)

        self._downloaded_paths: list[Path] = []
        self._data_downloaded = False

    # --- Private functions

    def _download_instance(
        self,
        n: int,
        m: int,
    ) -> None:
        """Pseudo-code implementation:
        - Start of with a cycle of m vertices
        - for i = m + 1 to n:
            - add a new vertex to G
            - add m edges connecting it to the (already present) graph with probability ~ deg(v_i)^2 / Sum(deg(v_j)^2) (or not quadratic)
        - return G

        Args:
            n (int): Number of nodes
            m (int): Number of new neighbors of the newly added vertices. The total number of edges is m(n - m + 1) = O(n) for m << n

        """
        assert m < n, f"The m parameter must be (a lot) smaller than n, got {m} vs {n}!"
        filepath = self._root_folder / f"pam_graph_{n}_{m}.clq"

        if not self.force_redownload and filepath.exists():
            logger.info(f"  Skipping {filepath.stem!s:<30} (already exists)")
            self._downloaded_paths.append(filepath)
            return

        # Initialize the cycle
        g = Graph(size=n)

        g.add_edge(0, m)
        for i in range(m):
            g.add_edge(i, i + 1)

        # Iterate adding new nodes
        vertex_degrees = [m for _ in range(m)]

        def get_p_dist() -> list[float]:
            weights = [i for i in vertex_degrees]  # i**2
            denominator = sum(weights)
            return [w / denominator for w in weights]

        for i in range(m, n):
            new_neighbors = self._rng.choice(
                np.arange(i), size=m, replace=False, p=get_p_dist()
            )

            vertex_degrees.append(m)

            for neighbor_idx in new_neighbors:
                vertex_degrees[neighbor_idx] += 1
                g.add_edge(neighbor_idx, i)

        # Save the graph
        g.to_file(filepath)
        self._downloaded_paths.append(filepath)
        logger.info(f"  Saved to {filepath.stem}")

    # --- Main functionalities

    def download_data(self) -> None:
        self._downloaded_paths: list[Path] = []

        for n, m in tqdm(
            self.configs,
            desc="Creating PAM instances...",
            total=len(self.configs),
        ):
            self._download_instance(n, m)

        self._data_downloaded = True

    def get_named_graphs(self) -> Iterator[tuple[str, Graph]]:
        """Yield one Graph per downloaded .clq file, loading via the fast pandas path."""
        if not self._data_downloaded:
            logger.info(
                "Preferential Attachment Model data not downloaded yet, downloading now..."
            )
            self.download_data()

        clq_paths = sorted(p for p in self._downloaded_paths if p.suffix == ".clq")
        for filepath in clq_paths:
            logger.info(f"Loading graph from {filepath.name}")
            g = Graph.from_file(filepath)
            yield filepath.stem, g
