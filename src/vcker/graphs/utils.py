from pathlib import Path


def get_graph_files(folder: Path) -> set[Path]:
    return set(folder.glob("*.clq"))
