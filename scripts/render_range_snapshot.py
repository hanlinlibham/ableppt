#!/usr/bin/env python3
"""渲染 standalone range snapshot chart.

用法: python scripts/render_range_snapshot.py <config.json> <output.pptx>
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pptfi.operations import render_range_snapshot


def main():
    if len(sys.argv) != 3:
        print(
            json.dumps(
                {"status": "error", "message": "用法: render_range_snapshot.py <config.json> <output.pptx>"},
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    result = render_range_snapshot(sys.argv[1], sys.argv[2])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
