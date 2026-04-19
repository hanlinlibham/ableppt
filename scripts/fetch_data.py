#!/usr/bin/env python3
"""原子工具：数据获取

从 datasources JSON 加载数据，可选执行 transforms，输出 CSV 文件。

用法:
    python fetch_data.py --config datasources.json --output data/
    python fetch_data.py --config datasources.json --output data/ --transforms transforms.json

输入:
    datasources.json — 与 Job.datasources 同结构的 JSON 文件
    transforms.json  — 与 Job.transforms 同结构的 JSON 文件（可选）

输出 (stdout):
    {"status": "ok", "datasets": {"name": {"path": "...", "rows": N, "columns": [...]}}}
    {"status": "error", "message": "..."}
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pptfi.models.job import DataSource, Transform
from pptfi.connectors import ConnectorFactory
from pptfi.transformers import DataFrameTransformer


def main():
    parser = argparse.ArgumentParser(description="数据获取工具")
    parser.add_argument("--config", required=True, help="datasources JSON 文件路径")
    parser.add_argument("--output", required=True, help="CSV 输出目录")
    parser.add_argument("--transforms", help="transforms JSON 文件路径（可选）")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(json.dumps({"status": "error", "message": f"配置文件不存在: {config_path}"},
                         ensure_ascii=False))
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 加载 datasources
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw_ds = json.load(f)

        datasources = {name: DataSource(**spec) for name, spec in raw_ds.items()}
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"datasources 解析失败: {e}"},
                         ensure_ascii=False))
        sys.exit(1)

    # 加载数据
    raw_dfs = {}
    for name, ds in datasources.items():
        try:
            print(f"正在加载: {name}", file=sys.stderr)
            raw_dfs[name] = ConnectorFactory.load_data(name, ds)
        except Exception as e:
            print(json.dumps({"status": "error", "message": f"加载 '{name}' 失败: {e}"},
                             ensure_ascii=False))
            sys.exit(1)

    # 可选：执行 transforms
    dfs = raw_dfs
    if args.transforms:
        transforms_path = Path(args.transforms)
        if not transforms_path.exists():
            print(json.dumps({"status": "error",
                              "message": f"transforms 文件不存在: {transforms_path}"},
                             ensure_ascii=False))
            sys.exit(1)

        try:
            with open(transforms_path, "r", encoding="utf-8") as f:
                raw_tf = json.load(f)
            transforms = {name: Transform(**spec) for name, spec in raw_tf.items()}
            dfs = DataFrameTransformer.apply_transforms(raw_dfs, transforms)
        except Exception as e:
            print(json.dumps({"status": "error", "message": f"transforms 执行失败: {e}"},
                             ensure_ascii=False))
            sys.exit(1)

    # 输出 CSV
    result = {}
    for name, df in dfs.items():
        csv_path = output_dir / f"{name}.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8")
        result[name] = {
            "path": str(csv_path),
            "rows": len(df),
            "columns": list(df.columns),
        }
        print(f"  已保存: {csv_path} ({len(df)} 行)", file=sys.stderr)

    print(json.dumps({"status": "ok", "datasets": result}, ensure_ascii=False))


if __name__ == "__main__":
    main()
