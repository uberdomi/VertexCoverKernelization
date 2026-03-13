"""Base Handler class implementation"""

import logging
import shutil
from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from tqdm import tqdm

from ..graphs import Graph
from .utils import get_data_folder


class Handler(ABC):
    def __init__(
        self, folder_name: str, class_name: str, force_redownload: bool = False
    ) -> None:
        self.logger = logging.getLogger(__name__)

        self._root_folder = get_data_folder() / folder_name
        self._root_folder.mkdir(parents=True, exist_ok=True)

        self.class_name = class_name
        self.force_redownload = force_redownload

        self._downloaded_paths: list[Path] = []
        self._data_downloaded = False

        self.logger.info(
            f"{self.class_name} initialized with root folder {folder_name}"
        )

    # --- Abstract functions

    @abstractmethod
    def get_instances(self) -> tqdm:
        """Get all the available instances this class supports

        Returns:
            tqdm: Iterator over the instances to be downloaded/generated.
        """
        pass

    @abstractmethod
    def instance_filename(self, instance: Any) -> str:
        """Generate a valid file name out of the instance to be downloaded/generated.

        Args:
            instance (Any): One instance to be downloaded/generated

        Returns:
            str: Corresponding instance file name
        """

    @abstractmethod
    def download_instance(self, instance: Any, filepath: Path) -> None:
        """The download/generation logic for one instance from the class list.

        Args:
            instance (Any): One instance to be downloaded/generated
            filepath (Path): Path under which the instance should be saved
        """
        pass

    # --- Helper functionalities

    def get_root(self) -> Path:
        """Root data folder associated with the handler class."""
        return self._root_folder

    def delete_data(self) -> None:
        """Delete all data from the root data folder."""
        root = self.get_root()

        if root.exists():
            shutil.rmtree(root)
            self.logger.info(f"{root} data removed successfully!")

    def get_downloaded_paths(self) -> list[Path]:
        if not self._data_downloaded:
            self.logger.warning(f"{self.class_name} not yet downloaded!")
            return []

        return sorted(p for p in self._downloaded_paths if p.suffix in {".clq", ".gr"})

    # --- Main functionalities

    def download_data(self) -> None:
        self._downloaded_paths: list[Path] = []
        root = self.get_root()

        for instance in self.get_instances():
            filepath = root / self.instance_filename(instance)

            if not self.force_redownload and filepath.exists():
                self.logger.info(f"  Skipping {filepath.stem!s:<30} (already exists)")
                self._downloaded_paths.append(filepath)
                continue

            self.download_instance(instance=instance, filepath=filepath)
            if not filepath.exists():
                self.logger.warning(f"{filepath.stem} could not be saved!")
            else:
                self._downloaded_paths.append(filepath)
                self.logger.info(f"  Saved to {filepath.stem}")

        self._data_downloaded = True

    def get_named_graphs(self) -> Iterator[tuple[str, Graph]]:
        """Yield one Graph per downloaded .clq/.gr file, loading via the fast pandas path."""
        if not self._data_downloaded:
            self.logger.info(
                f"{self.class_name} data not downloaded yet, downloading now..."
            )
            self.download_data()

        for filepath in self.get_downloaded_paths():
            self.logger.info(f"Loading graph from {filepath.name}")
            g = Graph.from_file(filepath)
            yield filepath.stem, g
