#!/usr/bin/env python3
"""从 JSON 重建 PPT

用法: python rebuild_ppt.py <input.json> <output.pptx>
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pptfi.renderers.ppt_renderer import render_from_json_file


def main():
    parser = argparse.ArgumentParser(description="JSON → PPT 重建")
    parser.add_argument("input", help="输入 .json 文件路径")
    parser.add_argument("output", help="输出 .pptx 文件路径")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"错误: 文件不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 日志到 stderr
    old_stdout = sys.stdout
    sys.stdout = sys.stderr

    render_from_json_file(input_path, output_path)

    sys.stdout = old_stdout
    print(json.dumps({"status": "ok", "output": str(output_path)}))


if __name__ == "__main__":
    main()
