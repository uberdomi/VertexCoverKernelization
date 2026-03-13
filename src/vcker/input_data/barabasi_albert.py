"""Barabási-Albert Model - heavy-tailed graph distribution using the preferential attachment mechanism with specific clustering coefficient and a small diameter - fitting observed evidence (e.g. WWW graphs). Vertices are organized around “clusters” of high degree vertices. Apart from the WWW, such models resemble graphs emerging by distinct applications such as collaboration networks (i.e. in biology, in science, or in film actors), word co-occurrences, or neural networks. https://en.wikipedia.org/wiki/Barab%C3%A1si%E2%80%93Albert_model"""

from pathlib import Path
from typing import ClassVar, override

import numpy as np
from tqdm import tqdm

from ..graphs import Graph
from .base import Handler


class BarabasiAlbertHandler(Handler):
    """Barabási-Albert Model - heavy-tailed graph distribution using the preferential attachment mechanism with specific clustering coefficient and a small diameter. https://en.wikipedia.org/wiki/Barab%C3%A1si%E2%80%93Albert_model"""

    # Adjust parameters
    configs: ClassVar[list[tuple[int, int]]] = [
        # n - m tuples
        (2000, 4),
        (2000, 8),
        (1000, 4),
        (1000, 8),
    ]

    def __init__(self, force_redownload: bool = False) -> None:
        super().__init__(
            folder_name="barabasi_albert",
            class_name="Barabási-Albert",
            force_redownload=force_redownload,
        )

        # Seed for reproducibility
        self._rng = np.random.default_rng(seed=2026)

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
        n, m = instance

        return f"ba_graph_{n}_{m}.clq"

    @override
    def download_instance(self, instance: tuple[int, int], filepath: Path) -> None:
        """Pseudo-code implementation:
        - Start of with a cycle of m vertices
        - for i = m + 1 to n:
            - add a new vertex to G
            - add m edges connecting it to the (already present) graph with probability ~ deg(v_i)^2 / Sum(deg(v_j)^2) (or not quadratic)
        - return G
        """
        n, m = instance

        assert m < n, f"The m parameter must be (a lot) smaller than n, got {m} vs {n}!"

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
