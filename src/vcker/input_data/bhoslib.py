"""Implementation of a handler class for the BHOSLIB - Benchmarks with Hidden Optimum Solutions - benchmark graph datasets."""

from pathlib import Path
from typing import override

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from .base import Handler
from .utils import url_filename, download_url


class BhoslibHandler(Handler):
    _input_link = "https://iridia.ulb.ac.be/~fmascia/maximum_clique/BHOSLIB-benchmark"

    def __init__(self, force_redownload: bool = False) -> None:
        super().__init__(
            folder_name="bhoslib",
            class_name="BHOSLIB",
            force_redownload=force_redownload,
        )

        self._url_list: list[str] = []

    # --- Implementations

    @override
    def get_instances(self) -> tqdm:
        """Parse the BHOSLIB benchmark page and store all .clq and .clq.b download URLs.

        No-op if URLs have already been fetched.
        """
        if not self._url_list:
            self.logger.info(f"Fetching file list from: {self._input_link}")
            response = requests.get(self._input_link, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            self._url_list = [
                str(a["href"])
                for a in soup.find_all("a", href=True)
                if "/BHOSLIB/" in str(a["href"]) and (str(a["href"]).endswith(".clq"))
            ]
            self.logger.info(f"Found {len(self._url_list)} file(s) on the page.")

        return tqdm(self._url_list, desc="Downloading files", unit="file")

    @override
    def instance_filename(self, instance: str) -> str:
        url = instance

        return url_filename(url)

    @override
    def download_instance(self, instance: str, filepath: Path) -> None:
        url = instance
        self.logger.info(f"  Downloading {filepath.stem}")

        download_url(url, filepath)
