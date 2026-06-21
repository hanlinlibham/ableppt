#!/usr/bin/env python3
"""Standalone waterfall CLI wrapper.

用法:
    python render_waterfall.py waterfall_demo.json output.pptx

输出 (stdout):
    {"status": "ok", "output": "<path>", "summary": {...}}
    {"status": "error", "message": "..."}
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ableppt.operations import render_waterfall


def main():
    parser = argparse.ArgumentParser(description="渲染单页瀑布图 PPT")
    parser.add_argument("config", help="瀑布图 JSON 规范文件")
    parser.add_argument("output", help="输出 PPTX 路径")
    args = parser.parse_args()

    try:
        result = render_waterfall(args.config, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
