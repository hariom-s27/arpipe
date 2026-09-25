"""R1: the reconstructed package must import every discoverable module."""

import importlib
import pkgutil

import arpipe


def test_every_arpipe_module_imports() -> None:
    for module in pkgutil.walk_packages(arpipe.__path__, prefix="arpipe."):
        importlib.import_module(module.name)
