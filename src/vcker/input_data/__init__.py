from .bhoslib import BhoslibHandler
from .erdos_renyi import ErdosRenyiHandler
from .barabasi_albert import BarabasiAlbertHandler
from .pace2019 import Pace2019Handler
from .snap import SnapHandler
from .base import Handler

from typing import Literal

supported_handlers = Literal[
    "BHOSLIB", "ErdosRenyi", "BarabasiAlbert", "Pace2019Handler", "SnapHandler"
]


def get_handler(
    cls: supported_handlers,
    force_download: bool = False,
) -> Handler:
    match cls:
        case "BHOSLIB":
            return BhoslibHandler(force_download)
        case "ErdosRenyi":
            return ErdosRenyiHandler(force_download)
        case "BarabasiAlbert":
            return BarabasiAlbertHandler(force_download)
        case "Pace2019Handler":
            return Pace2019Handler(force_download)
        case "SnapHandler":
            return SnapHandler(force_download)
        case _:
            raise ValueError(f"Invalid class provided: {cls}")


__all__ = [
    "supported_handlers",
    "get_handler",
    "Handler",
    "BhoslibHandler",
    "ErdosRenyiHandler",
    "BarabasiAlbertHandler",
    "Pace2019Handler",
    "SnapHandler",
]
