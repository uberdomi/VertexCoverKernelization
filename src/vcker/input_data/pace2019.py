"""PACE 2019 - Parameterized Algorithms and Computational Experiments Challenge. Many real-world graphs tutored for the VC problem, used for benchmarking various state-of-the-art solvers during the challenge."""

import random
import zipfile
from pathlib import Path
from typing import override

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from .base import Handler
from .utils import download_url, url_filename


class Pace2019Handler(Handler):
    _input_link = "https://zenodo.org/records/3368306"
    # Adjust
    _n_instances = 5

    def __init__(self, force_redownload: bool = False) -> None:
        super().__init__(
            folder_name="pace2019",
            class_name="PACE2019",
            force_redownload=force_redownload,
        )

        self._zip_path: Path | None = None

        # Seed for reproducibility
        random.seed(2026)

    # --- Implementations

    @override
    def get_instances(self) -> tqdm:
        """Parse the BHOSLIB benchmark page and store all .clq and .clq.b download URLs.

        No-op if URLs have already been fetched.
        """
        if not self._zip_path:
            self.logger.info(f"Fetching zip file list from: {self._input_link}")

            # Get URL
            response = requests.get(self._input_link, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Find all <link> tags where type is 'application/zip'
            # The [attr="value"] syntax is standard CSS
            links = soup.select('link[type="application/zip"]')

            zip_urls: list[str] = [  # type: ignore
                link.get("href") for link in links
            ]

            for url in zip_urls:
                filepath = self.get_root() / url_filename(url=url)
                if not self.force_redownload and filepath.exists():
                    self.logger.info(
                        f"  Skipping {filepath.stem!s:<30} (already exists)"
                    )
                    continue

                download_url(url, filepath)
                # zip_path pointing to the last extracted .zip file
                self._zip_path = filepath

        assert self._zip_path is not None

        # Return the .zip contents to be extracted
        with zipfile.ZipFile(self._zip_path, "r") as zip_ref:
            zip_files = [member for member in zip_ref.infolist() if not member.is_dir()]
            subset = random.sample(zip_files, self._n_instances)

            return tqdm(subset, desc="Extracting")

    @override
    def instance_filename(self, instance: zipfile.ZipInfo) -> str:
        filename = Path(instance.filename)

        new_path = Path(*filename.parts[1:])

        return str(new_path)

    @override
    def download_instance(self, instance: str, filepath: Path) -> None:
        assert self._zip_path is not None

        # Return the .zip contents to be extracted
        with (
            zipfile.ZipFile(self._zip_path, "r") as zip_ref,
            zip_ref.open(instance) as source,
            open(filepath, "wb") as target,
        ):
            target.write(source.read())
