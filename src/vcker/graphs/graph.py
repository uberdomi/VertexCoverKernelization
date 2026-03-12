import io
import re
from pathlib import Path

import pandas as pd
from tqdm import tqdm


class Graph:
    _nodes: set[int]
    _edges: dict[int, set[int]]

    def __init__(self, size: int | None = None) -> None:
        self._directed = False

        if size is not None:
            self._nodes = set(range(size))
        else:
            self._nodes = set()

        self._edges = {}
        self._n_edges = 0

    # --- Graph creation

    def add_edges(self, edge_df: pd.DataFrame) -> None:
        # 'edge_df' should have 'src' and 'dst' columns
        if set(edge_df.columns) != {"src", "dst"}:
            raise ValueError(
                f"Invalid column names: expected 'src' and 'dst', got {edge_df.columns}"
            )

        for row in tqdm(
            edge_df.itertuples(index=False),
            total=len(edge_df),
            desc=f"Adding {len(edge_df)} edges...",
        ):
            self.add_edge(row.src, row.dst)  # type: ignore

    def add_edge(self, src: int, dst: int) -> None:
        if src not in self._edges:
            self._nodes.add(src)

        if dst not in self._edges:
            self._nodes.add(dst)

        if not self._edges.get(src):
            self._edges[src] = {dst}
            self._n_edges += 1
        elif dst not in self._edges[src]:
            self._edges[src].add(dst)
            self._n_edges += 1

        # Ensure the undirected graph stores both edges
        if not self._directed and src < dst:
            self.add_edge(dst, src)

    # --- Graph information

    @property
    def n_vertices(self) -> int:
        return len(self._nodes)

    @property
    def n_edges(self) -> int:
        return self._n_edges if self._directed else self._n_edges // 2

    def neighbors(self, v: int) -> set[int]:
        return self._edges.get(v, set())

    def degree(self, v: int) -> int:
        return len(self._edges.get(v, set()))

    def print_info(self) -> None:
        n = self.n_vertices
        m_max = n * (n - 1) // 2 if not self._directed else n * n
        m = self.n_edges

        print(
            f"The graph contains {n} nodes and {m} (directed) edges, covering {(100 * m / m_max):.2f}% for an average vertex degree of {(m / n):.2f}"
        )

    # --- File I/O
    # Using the DIMACS ASCII format (.clq files)

    @classmethod
    def from_file(cls, filepath: Path) -> "Graph":
        assert str(filepath).endswith(".clq"), (
            "Invalid file name (expected .clq format)!"
        )

        with open(filepath) as f:
            content = f.read()

        # Extract the p-line
        m = re.search(r"^p edge (\d+) (\d+)", content, re.MULTILINE)
        assert m is not None, "No Regex match!"
        n_vertices = int(m.group(1))

        # Feed only edge lines to pandas
        edge_lines = "\n".join(
            line[2:] for line in content.splitlines() if line.startswith("e ")
        )
        df = pd.read_csv(
            io.StringIO(edge_lines),
            sep=" ",
            names=["src", "dst"],
            dtype="int32",
        )
        df -= 1  # convert to 0-indexed

        g = cls(size=n_vertices)
        g.add_edges(edge_df=df)

        return g

    def to_file(self, filepath: Path) -> None:
        with open(filepath, "w") as f:
            f.write("c Saved by vcker\n")
            f.write(f"p edge {self.n_vertices} {self.n_edges}\n")
            for src, dsts in self._edges.items():
                for dst in dsts:
                    if self._directed or src < dst:
                        f.write(f"e {src + 1} {dst + 1}\n")
