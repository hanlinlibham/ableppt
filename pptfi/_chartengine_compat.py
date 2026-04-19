from __future__ import annotations

import sys
from pathlib import Path


def ensure_chartengine_on_path() -> None:
    """Allow `pptfi` to reuse the sibling `pptchartengine` package in this repo.

    This keeps `pptfi.chart_builder.*` import-compatible while routing the actual
    implementation to `pptchartengine`.
    """

    try:
        import pptchartengine  # noqa: F401
        return
    except ModuleNotFoundError:
        pass

    root = Path(__file__).resolve().parents[2] / "pptchartengine" / "src"
    if root.exists():
        root_str = str(root)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)
