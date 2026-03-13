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
        dtype="int64",
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
        dtype="int64",
    )
    df -= 1  # convert to 0-indexed

    return n_vertices, df


def preprocess_txt_file(filepath: Path) -> str:
    cleaned_data = []

    # regex for one or more horizontal whitespace characters (space or tab)
    # [ \t]+ targets specifically horizontal space
    whitespace_pattern = re.compile(r"[ \t]+")

    with open(filepath, "r") as f:
        for line in f:
            # 1. Skip comments
            if line.startswith("#"):
                continue

            # 2. Strip trailing/leading newline/whitespace
            line = line.strip()
            if not line:
                continue

            # 3. Squeeze multiple spaces/tabs into a single ' '
            normalized_line = whitespace_pattern.sub(" ", line)
            cleaned_data.append(normalized_line)

    # Convert the list of strings into a single string for pandas
    edge_lines = "\n".join(cleaned_data)

    return edge_lines


def load_txt(filepath: Path) -> tuple[int, pd.DataFrame]:
    assert str(filepath).endswith(".txt"), "Invalid file name (expected .txt format)!"

    # File cleanup
    edge_lines = preprocess_txt_file(filepath)

    df = pd.read_csv(
        io.StringIO(edge_lines),
        sep=" ",
        names=["src", "dst"],
        dtype="int64",
    )
    # df -= 1  # Don't convert to 0-indexed - already starting at 0

    n_vertices = len(set(df["src"].to_list()) | set(df["dst"].to_list()))

    return n_vertices, df
