"""Implementation of the Erdös-Renyi Random Graphs - https://en.wikipedia.org/wiki/Erd%C5%91s%E2%80%93R%C3%A9nyi_model"""

import random
from pathlib import Path
from typing import ClassVar, override

from tqdm import tqdm

from ..graphs import Graph
from .base import Handler


class ErdosRenyiHandler(Handler):
    """Erdös-Renyi Random Graphs - https://en.wikipedia.org/wiki/Erd%C5%91s%E2%80%93R%C3%A9nyi_model"""

    # Adjust parameters
    configs: ClassVar[list[tuple[int, float]]] = [
        # n - p tuples
        (500, 0.6),
        (500, 0.7),
        (500, 0.8),
        (1000, 0.2),
        (1000, 0.3),
    ]

    def __init__(self, force_redownload: bool = False) -> None:
        super().__init__(
            folder_name="erdos_renyi",
            class_name="Erdös-Renyi",
            force_redownload=force_redownload,
        )

        # Seed for reproducibility
        random.seed(2026)

    # --- Implementations

    @override
    def get_instances(self) -> tqdm:
        return tqdm(
            self.configs,
            desc=f"Creating {self.class_name} instances...",
            total=len(self.configs),
        )

    @override
    def instance_filename(self, instance: tuple[int, float]) -> str:
        n, p = instance

        return f"er_graph_{n}_{p:.1f}.clq"

    @override
    def download_instance(self, instance: tuple[int, float], filepath: Path) -> None:
        n, p = instance

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
