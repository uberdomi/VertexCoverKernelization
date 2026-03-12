import logging
from collections.abc import Iterator
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from ..graphs import Graph
from .utils import get_data_folder

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Class-based implementation
# ---------------------------------------------------------------------------


class BhoslibHandler:
    _input_link = "https://iridia.ulb.ac.be/~fmascia/maximum_clique/BHOSLIB-benchmark"

    def __init__(self, force_redownload: bool = False) -> None:
        self.force_redownload = force_redownload
        self._data_downloaded = False

        self._root_folder = get_data_folder() / "bhoslib"
        self._root_folder.mkdir(parents=True, exist_ok=True)

        self._url_list: list[str] = []
        self._downloaded_paths: list[Path] = []

    # --- Private functions

    def _fetch_file_urls(self) -> None:
        """Parse the BHOSLIB benchmark page and store all .clq and .clq.b download URLs.

        No-op if URLs have already been fetched.
        """
        if self._url_list:
            return

        logger.info(f"Fetching file list from: {self._input_link}")
        response = requests.get(self._input_link, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        self._url_list = [
            str(a["href"])
            for a in soup.find_all("a", href=True)
            if "/BHOSLIB/" in str(a["href"])
            and (str(a["href"]).endswith(".clq") or str(a["href"]).endswith(".clq.b"))
        ]
        logger.info(f"Found {len(self._url_list)} file(s) on the page.")

    def _download_bhoslib(self) -> None:
        """Download all BHOSLIB files to target folder."""
        assert self._url_list, "URL list is empty — call _fetch_file_urls() first."

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

        self._downloaded_paths = downloaded
        logger.info(f"Download complete — {len(self._downloaded_paths)} file(s) ready.")

    # --- Main functionalities

    def download_data(self) -> None:
        self._fetch_file_urls()
        self._download_bhoslib()

        self._data_downloaded = True

    def get_graphs(self) -> Iterator[Graph]:
        """Yield one Graph per downloaded .clq file, loading via the fast pandas path."""
        if not self._data_downloaded:
            logger.info("BHOSLIB data not downloaded yet, downloading now...")
            self.download_data()

        clq_paths = sorted(p for p in self._downloaded_paths if p.suffix == ".clq")
        for filepath in clq_paths:
            logger.info(f"Loading graph from {filepath.name}")
            g = Graph.from_file(filepath)
            yield g


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

    handler = BhoslibHandler()
    handler.download_data()

    for graph in handler.get_graphs():
        graph.print_info()


def main():
    bhoslib_test_run()


if __name__ == "__main__":
    main()
