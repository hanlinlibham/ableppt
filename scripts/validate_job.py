#!/usr/bin/env python3
"""原子工具：Job JSON Schema 校验

校验 Job JSON 文件的合法性，composer 模式额外校验布局名称和 source 引用。

用法:
    python validate_job.py job.json
    python validate_job.py job.json --dry-run   # 校验 + 尝试连接数据源

输出 (stdout):
    {"status": "ok", "mode": "...", "summary": {...}}
    {"status": "error", "errors": [...]}

退出码: 0=通过, 1=失败
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pptfi.models.job import Job


def main():
    parser = argparse.ArgumentParser(description="Job JSON 校验工具")
    parser.add_argument("job_json", help="Job JSON 文件路径")
    parser.add_argument("--dry-run", action="store_true",
                        help="额外尝试连接数据源（不渲染）")
    args = parser.parse_args()

    job_path = Path(args.job_json)
    if not job_path.exists():
        print(json.dumps({"status": "error", "errors": [f"文件不存在: {job_path}"]},
                         ensure_ascii=False))
        sys.exit(1)

    # 1. 基础 Schema 校验
    errors = []
    try:
        with open(job_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        job = Job(**raw)
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "errors": [f"JSON 语法错误: {e}"]},
                         ensure_ascii=False))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "errors": [f"Schema 校验失败: {e}"]},
                         ensure_ascii=False))
        sys.exit(1)

    # 2. Composer 模式额外校验
    if job.mode == "composer":
        from pptfi.composer.layouts import LAYOUT_REGISTRY

        all_sources = set(job.datasources.keys())
        if job.transforms:
            all_sources.update(job.transforms.keys())

        for i, page in enumerate(job.pages):
            # 校验布局名称
            if page.layout not in LAYOUT_REGISTRY:
                available = ", ".join(LAYOUT_REGISTRY.keys())
                errors.append(f"pages[{i}]: 未知布局 '{page.layout}'。可用: {available}")

            # 校验 datasource/source 引用
            if "datasource" in page.data:
                if page.data["datasource"] not in all_sources:
                    errors.append(
                        f"pages[{i}]: datasource '{page.data['datasource']}' "
                        f"不存在于 datasources/transforms 中"
                    )
            # source 值不在已知数据源中 → 视为脚注文本，不报错

            # 校验嵌套 datasource/source 引用 (two_charts)
            for key in ("left", "right"):
                if key in page.data and isinstance(page.data[key], dict):
                    sub = page.data[key]
                    ds_ref = sub.get("datasource") or sub.get("source")
                    if ds_ref and ds_ref not in all_sources:
                        errors.append(
                            f"pages[{i}].data.{key}: datasource/source '{ds_ref}' "
                            f"不存在于 datasources/transforms 中"
                        )

    if errors:
        print(json.dumps({"status": "error", "errors": errors}, ensure_ascii=False))
        sys.exit(1)

    # 3. 构造摘要
    summary = {"mode": job.mode, "datasources": list(job.datasources.keys())}
    if job.mode == "template":
        summary["slides"] = len(job.slides)
        summary["template"] = job.template.path
    elif job.mode == "composer":
        summary["pages"] = len(job.pages)
        summary["theme"] = job.theme or "able_finance"
        summary["layouts"] = [p.layout for p in job.pages]

    if job.transforms:
        summary["transforms"] = list(job.transforms.keys())

    # 4. 可选 dry-run：尝试连接数据源
    if args.dry_run and job.datasources:
        from pptfi.connectors import ConnectorFactory

        ds_status = {}
        for name, ds in job.datasources.items():
            try:
                print(f"尝试连接: {name}", file=sys.stderr)
                df = ConnectorFactory.load_data(name, ds)
                ds_status[name] = {"ok": True, "rows": len(df), "columns": list(df.columns)}
            except Exception as e:
                ds_status[name] = {"ok": False, "error": str(e)}
        summary["datasource_check"] = ds_status

    print(json.dumps({"status": "ok", "summary": summary}, ensure_ascii=False))


if __name__ == "__main__":
    main()
