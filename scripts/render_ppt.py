#!/usr/bin/env python3
"""原子工具：渲染 PPT

从 Job JSON 渲染 PPT 文件。支持 template 和 composer 两种模式。

用法:
    python render_ppt.py job.json
    python render_ppt.py job.json --data-dir data/   # 覆盖 CSV 路径前缀

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

from ableppt.models.job import Job


def main():
    parser = argparse.ArgumentParser(description="PPT 渲染工具")
    parser.add_argument("job_json", help="Job JSON 配置文件路径")
    parser.add_argument("--data-dir", help="覆盖 CSV datasource 的路径前缀")
    args = parser.parse_args()

    job_path = Path(args.job_json)
    if not job_path.exists():
        print(json.dumps({"status": "error", "message": f"文件不存在: {job_path}"},
                         ensure_ascii=False))
        sys.exit(1)

    # 加载并验证 Job JSON
    try:
        with open(job_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        # 可选：覆盖 CSV 路径前缀
        if args.data_dir:
            data_dir = Path(args.data_dir)
            for ds in raw.get("datasources", {}).values():
                if ds.get("type") == "csv" and ds.get("path"):
                    original = Path(ds["path"])
                    if not original.is_absolute():
                        ds["path"] = str(data_dir / original.name)

        job = Job(**raw)
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Job JSON 加载失败: {e}"},
                         ensure_ascii=False))
        sys.exit(1)

    # 渲染
    try:
        from ableppt.engine import PptEngine

        with contextlib.redirect_stdout(sys.stderr):
            engine = PptEngine()
            output_path = engine.render(job)

        print(json.dumps({"status": "ok", "output": str(output_path)},
                         ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"渲染失败: {e}"},
                         ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
