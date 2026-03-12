"""Implementation of the Erdös-Renyi Random Graphs - https://en.wikipedia.org/wiki/Erd%C5%91s%E2%80%93R%C3%A9nyi_model"""

import logging
from collections.abc import Iterator
from typing import ClassVar
from pathlib import Path

import random
from tqdm import tqdm

from ..graphs import Graph
from .utils import get_data_folder

logger = logging.getLogger(__name__)


class ErdosRenyiHandler:
    # Adjust parameters
    configs: ClassVar[list[tuple[int, float]]] = [  # n - p
        (500, 0.6),
        (500, 0.7),
        (500, 0.8),
        (1000, 0.2),
        (1000, 0.3),
    ]

    def __init__(self, force_redownload: bool = False) -> None:
        self.force_redownload = force_redownload
        # Seed for reproducibility
        random.seed(2026)

        self._root_folder = get_data_folder() / "erdos_renyi"
        self._root_folder.mkdir(parents=True, exist_ok=True)

        self._downloaded_paths: list[Path] = []

    # --- Private functions

    def _download_instance(
        self,
        n: int,
        p: float,
    ) -> None:
        filepath = self._root_folder / f"er_graph_{n}_{p:.1f}.clq"

        if not self.force_redownload and filepath.exists():
            logger.info(f"  Skipping {filepath.stem!s:<30} (already exists)")
            self._downloaded_paths.append(filepath)
            return

        # Create a list of all possible (undirected) edges from a complete graph with 'n' nodes
        edge_list = [(src, dst) for dst in range(n) for src in range(dst)]

        # Pick each edge independently with probability 'p'
        edge_sub_list = [item for item in edge_list if random.random() < p]

        # Add the edges to the graph
        g = Graph(size=n)
        for src, dst in edge_sub_list:
            g.add_edge(src, dst)

        # Save the graph
        g.to_file(filepath)
        self._downloaded_paths.append(filepath)
        logger.info(f"  Saved to {filepath.stem}")

    # --- Main functionalities

    def download_data(self) -> None:
        self._downloaded_paths: list[Path] = []

        for n, p in tqdm(
            self.configs,
            desc="Creating Erdös-Renyi instances...",
            total=len(self.configs),
        ):
            self._download_instance(n, p)

        self._data_downloaded = True

    def get_named_graphs(self) -> Iterator[tuple[str, Graph]]:
        """Yield one Graph per downloaded .clq file, loading via the fast pandas path."""
        if not self._data_downloaded:
            logger.info("Erdös-Renyi data not downloaded yet, downloading now...")
            self.download_data()

        clq_paths = sorted(p for p in self._downloaded_paths if p.suffix == ".clq")
        for filepath in clq_paths:
            logger.info(f"Loading graph from {filepath.name}")
            g = Graph.from_file(filepath)
            yield filepath.stem, g
