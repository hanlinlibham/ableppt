#!/usr/bin/env python3
"""给现有 PPT 添加占位符，生成模板

用法:
    python add_placeholders.py <input.pptx> <output.pptx> <map.json>

map.json 格式:
    {"原始文字": "{占位符名}", "2024年度": "{年度}", ...}

输出 (stdout):
    {"status": "ok", "output": "<path>", "replacements_made": N}
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ableppt.template.replacer import create_template_from_ppt


def main():
    parser = argparse.ArgumentParser(description="给现有 PPT 添加占位符")
    parser.add_argument("input", help="输入 .pptx 文件路径")
    parser.add_argument("output", help="输出模板 .pptx 文件路径")
    parser.add_argument("map_json", help="替换映射 .json 文件路径")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    map_path = Path(args.map_json)

    for label, p in [("输入文件", input_path), ("映射文件", map_path)]:
        if not p.exists():
            print(json.dumps({"status": "error",
                              "message": f"{label}不存在: {p}"}, ensure_ascii=False))
            sys.exit(1)

    with open(map_path, "r", encoding="utf-8") as f:
        placeholders = json.load(f)

    if not isinstance(placeholders, dict):
        print(json.dumps({"status": "error",
                          "message": "map.json 必须是 {原始文字: 占位符} 字典"}))
        sys.exit(1)

    # 将日志重定向到 stderr
    old_stdout = sys.stdout
    sys.stdout = sys.stderr

    output_path.parent.mkdir(parents=True, exist_ok=True)
    create_template_from_ppt(input_path, output_path, placeholders)

    sys.stdout = old_stdout
    print(json.dumps({
        "status": "ok",
        "output": str(output_path),
        "replacements_made": len(placeholders),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
