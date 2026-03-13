from .bhoslib import BhoslibHandler
from .erdos_renyi import ErdosRenyiHandler
from .barabasi_albert import BarabasiAlbertHandler
from .base import Handler

from typing import Literal

supported_handlers = Literal["BHOSLIB", "ErdosRenyi", "BarabasiAlbert"]


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
        case _:
            raise ValueError(f"Invalid class provided: {cls}")


__all__ = [
    "supported_handlers",
    "get_handler",
    "Handler",
    "BhoslibHandler",
    "ErdosRenyiHandler",
    "BarabasiAlbertHandler",
]
