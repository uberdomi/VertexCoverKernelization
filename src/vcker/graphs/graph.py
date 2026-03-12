import pandas as pd
from tqdm import tqdm
from pathlib import Path


class Graph:
    _nodes: set[int]
    _edges: dict[int, set[int]]

    def __init__(self, size: int | None = None) -> None:
        self._directed = False

        if size is not None:
            self._nodes = set(range(1, size + 1))
        else:
            self._nodes = set()

        self._edges = {}
        self._n_edges = 0

    def add_edges(self, edge_df: pd.DataFrame) -> None:
        # 'edge_df' should have 'src' and 'dst' columns
        if set(edge_df.columns) != {"src", "dst"}:
            raise ValueError(
                f"Invalid column names: expected 'src' and 'dst', got {edge_df.columns}"
            )

        for row in tqdm(
            edge_df.itertuples(index=False), desc=f"Adding {len(edge_df)} edges..."
        ):
            self.add_edge(row.src, row.dst) # type: ignore

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

    def print_info(self) -> None:
        n = len(self._nodes)
        m_max = n * (n - 1) if not self._directed else n * n
        m = self._n_edges

        print(
            f"The graph contains {n} nodes and {m} (directed) edges, covering {(100 * m / m_max):.2f}% for an average vertex degree of {(m/n):.2f}"
        )

    # --- File I/O
    # Using the DIMACS ASCII format (.clq files)

    @classmethod
    def from_file(cls, filepath: Path) -> "Graph":
        assert str(filepath).endswith(".clq"), "Invalid file name (expected .clq format)!"
        
        n_vertices = 0
        edges = []
        with open(filepath) as f:
            for line in f:
                if line.startswith("p "):
                    n_vertices = int(line.split()[2])
                elif line.startswith("e "):
                    parts = line.split()
                    edges.append((int(parts[1]) - 1, int(parts[2]) - 1))
        g = cls(size=n_vertices)
        for src, dst in edges:
            g.add_edge(src, dst)
        return g

    def to_file(self, filepath: Path) -> None:
        with open(filepath, "w") as f:
            f.write("c Saved by vcker\n")
            f.write(f"p edge {len(self._nodes)} {self._n_edges}\n")
            for src, dsts in self._edges.items():
                for dst in dsts:
                    if self._directed or src < dst:
                        f.write(f"e {src + 1} {dst + 1}\n")
