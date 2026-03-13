"""SNAP (Stanford Network Analysis Project) Datasets - https://snap.stanford.edu/data/ . Real-world graph network dataset examples. Few massive hubs cover most edges, leaving vast, sparse peripheries rich in straight and flared crowns."""

import random
from pathlib import Path
from typing import override

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from .base import Handler
from .utils import download_url, unpack_txt_gz_file, url_filename


class SnapHandler(Handler):
    _url_list = [
        "https://snap.stanford.edu/data/ego-Facebook.html",
        "https://snap.stanford.edu/data/wiki-Vote.html",
        # "https://snap.stanford.edu/data/wiki-RfA.html",
        "https://snap.stanford.edu/data/cit-HepPh.html",
        "https://snap.stanford.edu/data/email-EuAll.html",
    ]

    def __init__(self, force_redownload: bool = False) -> None:
        super().__init__(
            folder_name="snap",
            class_name="SNAP",
            force_redownload=force_redownload,
        )

        self._full_urls: list[str] = []

        # Seed for reproducibility
        random.seed(2026)

    # --- Implementations

    @override
    def get_instances(self) -> tqdm:
        """Download the .txt.gz files from the stored URL mirrors."""
        if not self._full_urls:
            for url in self._url_list:
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                # Find .txt.gz file(s)
                filenames = [
                    str(a["href"])
                    for a in soup.find_all("a", href=True)
                    if str(a["href"]).endswith(".txt.gz")
                ]

                # Need just one
                first_filename = filenames[0]

                # Relative filenames (e.g. "facebook_combined.txt.gz") need the base
                # URL prepended so download_url can reach them.
                base_url = url.rsplit("/", 1)[0] + "/"
                self._full_urls.append(base_url + first_filename)

        return tqdm(self._full_urls, desc="Downloading files", unit="file")

    @override
    def instance_filename(self, instance: str) -> str:
        url = instance

        filename_gz = url_filename(url)

        return filename_gz[:-3]

    @override
    def download_instance(self, instance: str, filepath: Path) -> None:
        url = instance
        filepath_gz = Path(str(filepath) + ".gz")

        self.logger.info(f"  Downloading {filepath.stem}")

        # Downloading the .txt.gz file
        download_url(url, filepath_gz)

        # Unpack
        unpack_txt_gz_file(filepath_gz)
