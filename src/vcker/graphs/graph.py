from typing import Optional, Set, Dict, List
import pandas as pd
from tqdm import tqdm
from pathlib import Path

class Graph:
    _nodes: Set[int]
    _edges: Dict[int, List[int]]
    _directed = False

    def __init__(self, size: Optional[int] = None) -> None:

        if size is not None:
            self._nodes = set(range(1, size + 1))
        
        self._edges = {}

    def add_edges(self, edge_df: pd.DataFrame) -> None:
        # 'edge_df' should have 'src' and 'dst' columns
        if set(edge_df.columns) != {"src", "dst"}:
            raise ValueError(
                f"Invalid column names: expected 'src' and 'dst', got {edge_df.columns}"
            )

        for _, row in tqdm(edge_df.iterrows(), desc=f"Adding {len(edge_df)} edges..."):
            self.add_edge(row["src"], row["dst"])
    
    def add_edge(self, src: int, dst: int) -> None:
        if src not in self._edges:
            self._nodes.add(src)
        
        if not self._edges.get(src):
            self._edges[src] = [dst]
        elif dst not in self._edges[src]:
            self._edges[src].append(dst)

        # Ensure the undirected graph stores both edges
        if not self._directed and src < dst:
            self.add_edge(dst, src)
    
    def print_info(self) -> None:
        n=  len(self._nodes)
        m_max = n * (n-1) // 2 if not self._directed else n * n
        m = 0
        for src, dst_list in self._edges.items():
            if not self._directed:
                for dst in dst_list:
                    if dst > src:
                        m += 1
            else:
                m += len(dst_list)
        
        print(f"The graph contains {n} nodes and {m} edges, covering {(100*m/m_max):.2f}% for an average vertex degree of {((2*m/n) if not self._directed else m/n):.2f}")
    
    def to_file(self, filename: Path) -> None:
        # TODO store in a convenient way
        pass
