#!/usr/bin/env python3
"""PptEngine CLI — 通过 Job JSON 声明式编排生成 PPT

用法:
    python run_job.py <job.json> [--dry-run]

    --dry-run  仅验证 Job JSON schema，不执行渲染

输出 (stdout):
    {"status": "ok", "output": "<path>"}
    {"status": "error", "message": "..."}
"""

import sys
import json
import argparse
import contextlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pptfi.models.job import Job


def main():
    parser = argparse.ArgumentParser(description="PptEngine CLI: Job JSON → PPT")
    parser.add_argument("job_json", help="Job JSON 配置文件路径")
    parser.add_argument("--dry-run", action="store_true",
                        help="仅验证 Job JSON schema，不渲染")
    args = parser.parse_args()

    job_path = Path(args.job_json)
    if not job_path.exists():
        print(json.dumps({"status": "error", "message": f"文件不存在: {job_path}"}))
        sys.exit(1)

    # 加载并验证 Job JSON
    try:
        with open(job_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        job = Job(**raw)
    except Exception as e:
        print(json.dumps({"status": "error",
                          "message": f"Job JSON 验证失败: {e}"}, ensure_ascii=False))
        sys.exit(1)

    if args.dry_run:
        summary = {"status": "ok", "message": "schema 验证通过",
                   "mode": job.mode,
                   "datasources": list(job.datasources.keys())}
        if job.mode == "template":
            summary["slides"] = len(job.slides)
        elif job.mode == "composer":
            summary["pages"] = len(job.pages)
            summary["theme"] = job.theme or "able_finance"
        print(json.dumps(summary, ensure_ascii=False))
        return

    # 渲染
    try:
        from pptfi.engine import PptEngine

        # 将引擎日志重定向到 stderr
        with contextlib.redirect_stdout(sys.stderr):
            engine = PptEngine()
            output_path = engine.render(job)

        print(json.dumps({"status": "ok", "output": str(output_path)},
                         ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"status": "error",
                          "message": f"渲染失败: {e}"}, ensure_ascii=False),
              file=sys.stdout)
        sys.exit(1)


if __name__ == "__main__":
    main()
