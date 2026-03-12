import logging
import re
import io
from pathlib import Path
import pandas as pd

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from typing import Iterator

from .utils import get_data_folder
from ..graphs import Graph, get_graph_files

INPUT_LINK = "https://iridia.ulb.ac.be/~fmascia/maximum_clique/BHOSLIB-benchmark"

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def get_bhoslib_folder() -> Path:
    """Return (and create) the folder where BHOSLIB data should be stored."""
    folder = get_data_folder() / "bhoslib"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


# ---------------------------------------------------------------------------
# Fetching archive URLs from the benchmark page
# ---------------------------------------------------------------------------


def fetch_file_urls() -> list[str]:
    """Parse the BHOSLIB benchmark page and return all .clq and .clq.b download URLs."""
    logger.info(f"Fetching file list from: {INPUT_LINK}")
    response = requests.get(INPUT_LINK, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    urls = [
        str(a["href"])
        for a in soup.find_all("a", href=True)
        if "/BHOSLIB/" in str(a["href"]) and (
            str(a["href"]).endswith(".clq") or str(a["href"]).endswith(".clq.b")
        )
    ]
    logger.info(f"Found {len(urls)} file(s) on the page.")
    return urls


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------


def download_bhoslib(
    dest_dir: Path | None = None,
    skip_existing: bool = True,
) -> list[Path]:
    """Download all BHOSLIB files to *dest_dir*.

    Parameters
    ----------
    dest_dir:
        Destination folder. Defaults to ``get_bhoslib_folder()``.
    skip_existing:
        When *True*, archives that already exist on disk are not re-downloaded.

    Returns
    -------
    List of paths to the downloaded (or pre-existing) archives.
    """
    if dest_dir is None:
        dest_dir = get_bhoslib_folder()
    dest_dir.mkdir(parents=True, exist_ok=True)

    urls = fetch_file_urls()
    downloaded: list[Path] = []

    for url in tqdm(urls, desc="Downloading files", unit="file"):
        filename = url.rsplit("/", 1)[-1]
        dest_path = dest_dir / filename

        if skip_existing and dest_path.exists():
            logger.info(f"  Skipping {filename!s:<30} (already exists)")
            downloaded.append(dest_path)
            continue

        logger.info(f"  Downloading {filename}")
        with requests.get(url, stream=True, timeout=120) as resp:
            resp.raise_for_status()
            total = int(resp.headers.get("content-length", 0))
            with (
                open(dest_path, "wb") as fout,
                tqdm(
                    total=total or None,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=f"  {filename}",
                    leave=False,
                ) as bar,
            ):
                for chunk in resp.iter_content(chunk_size=65536):
                    fout.write(chunk)
                    bar.update(len(chunk))

        downloaded.append(dest_path)
        logger.info(f"  Saved to {dest_path}")

    logger.info(f"Download complete — {len(downloaded)} file(s) ready.")
    return downloaded

# ---------------------------------------------------------------------------
# Class-based implementation
# ---------------------------------------------------------------------------

class BhoslibHandler:
    _input_link = "https://iridia.ulb.ac.be/~fmascia/maximum_clique/BHOSLIB-benchmark"
    
    def __init__(self, force_redownload = False) -> None:
        self.force_redownload = force_redownload
        self._data_downloaded = False
        self._graphs_processed = False
        
        self._root_folder = get_data_folder() / "bhoslib"
        self._root_folder.mkdir(parents=True, exist_ok=True)
    
    # --- Private functions
    
    def _fetch_file_urls(self) -> None:
        """Parse the BHOSLIB benchmark page and store all .clq and .clq.b download URLs."""
        logger.info(f"Fetching file list from: {INPUT_LINK}")
        response = requests.get(INPUT_LINK, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        urls = [
            str(a["href"])
            for a in soup.find_all("a", href=True)
            if "/BHOSLIB/" in str(a["href"]) and (
                str(a["href"]).endswith(".clq") or str(a["href"]).endswith(".clq.b")
            )
        ]
        logger.info(f"Found {len(urls)} file(s) on the page.")
        
        self._url_list = urls
    
    def _download_bhoslib(self) -> None:
        """Download all BHOSLIB files to target folder."""
        assert self._url_list is not None
        
        downloaded: list[Path] = []

        for url in tqdm(self._url_list, desc="Downloading files", unit="file"):
            filename = url.rsplit("/", 1)[-1]
            dest_path = self._root_folder / filename

            if not self.force_redownload and dest_path.exists():
                logger.info(f"  Skipping {filename!s:<30} (already exists)")
                downloaded.append(dest_path)
                continue

            logger.info(f"  Downloading {filename}")
            with requests.get(url, stream=True, timeout=120) as resp:
                resp.raise_for_status()
                total = int(resp.headers.get("content-length", 0))
                with (
                    open(dest_path, "wb") as fout,
                    tqdm(
                        total=total or None,
                        unit="B",
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=f"  {filename}",
                        leave=False,
                    ) as bar,
                ):
                    for chunk in resp.iter_content(chunk_size=65536):
                        fout.write(chunk)
                        bar.update(len(chunk))

            downloaded.append(dest_path)
            logger.info(f"  Saved to {dest_path}")

        logger.info(f"Download complete — {len(downloaded)} file(s) ready.")
        self._downloaded_paths = downloaded
    
    def _load_dimacs_ascii(self, path: Path) -> tuple[int, int, pd.DataFrame]:
        """Load a DIMACS ascii .clq file into a DataFrame of edges.

        Returns (n_vertices, n_edges, df) where df has columns ['src', 'dst'].
        Vertices are converted to 0-indexed integers.
        """
        with open(path) as f:
            content = f.read()

        # Extract the p-line
        m = re.search(r"^p edge (\d+) (\d+)", content, re.MULTILINE)
        assert m is not None, "No Regex match!"
        n_vertices, n_edges = int(m.group(1)), int(m.group(2))

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

        return n_vertices, n_edges, df

    def _input_clq_files(self) -> set[Path]:
        return set(self._root_folder.glob("*.clq"))
    
    # --- Main functionalities
    
    def download_data(self) -> None:
        self._fetch_file_urls()
        self._download_bhoslib()
        
        self._data_downloaded = True
    
    def get_graphs(self) -> Iterator[Graph]:
        # Check saved graphs
        if not self._data_downloaded:
            logger.info("BHOSLIB data not downloaded yet, downloading now...")
            self.download_data()
        
        grap_files = get_graph_files(self._root_folder)
        for filepath in grap_files:
            yield Graph.from_file(filepath)

# ---------------------------------------------------------------------------
# Entry point for quick testing
# ---------------------------------------------------------------------------


def bhoslib_test_run():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logger.info("=== BHOSLIB Data Pipeline ===")

    downloaded = download_bhoslib()

    logger.info(f"Pipeline complete — {len(downloaded)} file(s) downloaded.")


def main():
    bhoslib_test_run()


if __name__ == "__main__":
    main()
