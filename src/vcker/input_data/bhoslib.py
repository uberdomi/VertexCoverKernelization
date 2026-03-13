"""Implementation of a handler class for the BHOSLIB - Benchmarks with Hidden Optimum Solutions - benchmark graph datasets."""

from pathlib import Path
from typing import override

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from .base import Handler


class BhoslibHandler(Handler):
    _input_link = "https://iridia.ulb.ac.be/~fmascia/maximum_clique/BHOSLIB-benchmark"

    def __init__(self, force_redownload: bool = False) -> None:
        super().__init__(
            folder_name="bhoslib",
            class_name="BHOSLIB",
            force_redownload=force_redownload,
        )

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

        return url.rsplit("/", 1)[-1]

    @override
    def download_instance(self, instance: str, filepath: Path) -> None:
        url = instance
        self.logger.info(f"  Downloading {filepath.stem}")

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
