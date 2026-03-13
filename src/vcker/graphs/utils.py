from pathlib import Path
import pandas as pd
import io
import re


def get_graph_files(folder: Path) -> set[Path]:
    return set(folder.glob("*.clq")).union(set(folder.glob("*.gr")))


def load_clq(filepath: Path) -> tuple[int, pd.DataFrame]:
    assert str(filepath).endswith(".clq"), "Invalid file name (expected .clq format)!"

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

    return n_vertices, df


def load_gr(filepath: Path) -> tuple[int, pd.DataFrame]:
    assert str(filepath).endswith(".gr"), "Invalid file name (expected .gr format)!"

    with open(filepath) as f:
        content = f.read()

    # Extract the p-line
    m = re.search(r"^p td (\d+) (\d+)", content, re.MULTILINE)
    assert m is not None, "No Regex match!"
    n_vertices = int(m.group(1))

    # Feed only edge lines to pandas
    edge_lines = "\n".join(
        line
        for line in content.splitlines()
        if not (line.startswith("p ") or line.startswith("c "))
    )
    df = pd.read_csv(
        io.StringIO(edge_lines),
        sep=" ",
        names=["src", "dst"],
        dtype="int32",
    )
    df -= 1  # convert to 0-indexed

    return n_vertices, df
