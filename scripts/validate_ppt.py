#!/usr/bin/env python3
"""validate_ppt.py — CLI 入口: 对生成的 PPT 执行 DeckLinter 检查

用法:
    python scripts/validate_ppt.py output/report.pptx
    python scripts/validate_ppt.py output/report.pptx --json
    python scripts/validate_ppt.py output/report.pptx --write-notes
"""

import sys
import argparse
from pathlib import Path

# 确保 ableppt 可以被导入
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ableppt.qa.deck_linter import DeckLinter


def main():
    parser = argparse.ArgumentParser(description="PPT quality lint (institutional standard)")
    parser.add_argument("pptx", help="Path to .pptx file")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--write-notes", action="store_true",
                        help="Write lint results into PPT slide notes")
    args = parser.parse_args()

    path = Path(args.pptx)
    if not path.exists():
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)

    linter = DeckLinter(str(path))
    report = linter.run()

    if args.json:
        print(linter.to_json(report))
    else:
        linter.print_summary(report, file=sys.stdout)

    if args.write_notes:
        linter.write_to_notes(report)
        print(f"Lint results written to slide notes in {path}")

    # Exit code: 1 if errors, 0 otherwise
    sys.exit(1 if report["summary"]["errors"] > 0 else 0)


if __name__ == "__main__":
    main()
