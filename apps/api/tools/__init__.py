"""Pluggable tool packages — auto-discovered via manifest.json + plugin export."""

from __future__ import annotations

import importlib.abc
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

_TOOLS_ROOT = Path(__file__).resolve().parent


class _HyphenatedToolFinder(importlib.abc.MetaPathFinder):
    """Enable ``importlib.import_module("tools.json-formatter")`` for hyphenated dirs."""

    def find_spec(self, fullname: str, path=None, target=None):  # noqa: ANN001, ARG002
        if not fullname.startswith("tools.") or fullname == "tools.base":
            return None
        parts = fullname.split(".")
        if len(parts) < 2 or "-" not in parts[1]:
            return None

        tool_dir = _TOOLS_ROOT / parts[1]
        if not tool_dir.is_dir():
            return None

        if len(parts) == 2:
            init_file = tool_dir / "__init__.py"
            if not init_file.is_file():
                return None
            return importlib.util.spec_from_file_location(
                fullname,
                init_file,
                submodule_search_locations=[str(tool_dir)],
            )

        # tools.<id>.views → tools/<id>/views.py
        *rest, leaf = parts[2:]
        module_dir = tool_dir.joinpath(*rest) if rest else tool_dir
        py_file = module_dir / f"{leaf}.py"
        pkg_init = module_dir / leaf / "__init__.py"

        if py_file.is_file():
            return importlib.util.spec_from_file_location(fullname, py_file)
        if pkg_init.is_file():
            return importlib.util.spec_from_file_location(
                fullname,
                pkg_init,
                submodule_search_locations=[str(module_dir / leaf)],
            )
        return None


def _ensure_hyphen_importer() -> None:
    if any(isinstance(f, _HyphenatedToolFinder) for f in sys.meta_path):
        return
    sys.meta_path.insert(0, _HyphenatedToolFinder())


_ensure_hyphen_importer()
