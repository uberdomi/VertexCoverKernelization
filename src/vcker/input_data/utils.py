from pathlib import Path


def get_project_root() -> Path:
    """Find the project root directory by locating pyproject.toml."""
    current_file = Path(__file__).resolve()
    for parent in current_file.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return current_file.parent.parent.parent.parent

def get_data_folder() -> Path:
    "Return the folder where the downloaded data should be located."
    root = get_project_root()
    data_folder = root / "data"
    
    if not data_folder.exists():
        data_folder.mkdir(parents=True, exist_ok=True)
    
    assert data_folder.exists()
    
    return data_folder