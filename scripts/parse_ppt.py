#!/usr/bin/env python3
"""将 PPT 解析为 JSON 中间格式

用法: python parse_ppt.py <input.pptx> [output.json]
如果不指定 output.json，则输出到 stdout
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ableppt.parsers.ppt_parser import PPTParser


def main():
    parser = argparse.ArgumentParser(description="PPT → JSON 解析")
    parser.add_argument("input", help="输入 .pptx 文件路径")
    parser.add_argument("output", nargs="?", help="输出 .json 文件路径（可选，默认输出到 stdout）")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误: 文件不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    # 重定向 print 到 stderr
    old_stdout = sys.stdout
    sys.stdout = sys.stderr

    ppt_parser = PPTParser(input_path)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        ppt_parser.save_to_json(output_path)
        sys.stdout = old_stdout
        print(json.dumps({"status": "ok", "output": str(output_path)}))
    else:
        result = ppt_parser.parse()
        sys.stdout = old_stdout
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        print()


if __name__ == "__main__":
    main()
