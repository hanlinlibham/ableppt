#!/usr/bin/env python3
"""解析 .pptx 模板，输出占位符清单（JSON）

用法: python parse_template.py <template.pptx>
输出: JSON 到 stdout，日志到 stderr
"""

import sys
import json
import argparse
from pathlib import Path

# 确保 ableppt 可导入
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ableppt.template.replacer import TemplateReplacer


def main():
    parser = argparse.ArgumentParser(description="解析 PPT 模板占位符")
    parser.add_argument("template", help="模板 .pptx 文件路径")
    parser.add_argument("--flat", action="store_true", help="不按页面分组，输出扁平列表")
    args = parser.parse_args()

    template_path = Path(args.template)
    if not template_path.exists():
        print(f"错误: 文件不存在: {template_path}", file=sys.stderr)
        sys.exit(1)

    # 重定向 print 到 stderr，保持 stdout 纯净
    import io
    old_stdout = sys.stdout
    sys.stdout = sys.stderr

    replacer = TemplateReplacer(template_path)
    result = replacer.extract_placeholders(by_page=not args.flat)

    # 恢复 stdout 并输出 JSON
    sys.stdout = old_stdout
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()  # trailing newline


if __name__ == "__main__":
    main()
