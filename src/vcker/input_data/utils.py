import zipfile
from pathlib import Path

import requests
from tqdm import tqdm

# --- File I/O


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


# --- Url Utils


def url_filename(url: str) -> str:
    return url.rsplit("/", 1)[-1]


def download_url(url: str, filepath: Path):
    with requests.get(url, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        with (
            open(filepath, "wb") as fout,
            tqdm(
                total=total or None,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=f"  {filepath.stem}",
                leave=False,
            ) as bar,
        ):
            for chunk in resp.iter_content(chunk_size=65536):
                fout.write(chunk)
                bar.update(len(chunk))


# --- Zip utils


def unzip_to_folder(zip_path: Path, target_dir):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for member in tqdm(zip_ref.infolist(), desc="Extracting"):
            filename = Path(member.filename)

            if member.is_dir():
                continue

            # Strip the first directory: 'archive/file.txt' -> 'file.txt'
            # We take all parts of the path EXCEPT the first one
            new_path = Path(*filename.parts[1:])

            # Define the final destination
            final_path = target_dir / new_path
            final_path.parent.mkdir(parents=True, exist_ok=True)

            with zip_ref.open(member) as source, open(final_path, "wb") as target:
                target.write(source.read())

    print(f"Extracted to: {target_dir}")
