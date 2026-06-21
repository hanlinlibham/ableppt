"""GTM 提示词工具包 — 把模型产出 job JSON 所需的一切打包成一份提示词。

解决链路里最后一个"模型必须抄对"的信息：**数据列名**。
``datasource_manifest()`` 把每个数据源的 列名/类型/样例值/范围 生成清单注入
提示词，模型照抄即可；``gtm_prompt_kit()`` 进一步把 页面示例 + 图表示例 +
数据清单 + 产出规则 组装成完整的 system prompt 物料::

    from ableppt.composer.layouts.gtm_prompt import gtm_prompt_kit
    system_prompt = gtm_prompt_kit(data_dir="data/gtm")
    # → 配合 gtm_job_schema() 做约束解码，模型一次产出可渲染的 job
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd


def _profile_df(df: pd.DataFrame, *, max_cols: int = 20) -> List[str]:
    """单个 DataFrame 的列清单（markdown 行）。"""
    lines = ["| 列名 | 类型 | 样例 | 范围 |", "|------|------|------|------|"]
    for col in list(df.columns)[:max_cols]:
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            kind = "数值"
            sample = f"{series.iloc[0]:g}"
            rng = f"{series.min():g} ~ {series.max():g}"
        elif pd.api.types.is_datetime64_any_dtype(series):
            kind = "日期"
            sample = str(series.iloc[0])[:10]
            rng = f"{str(series.min())[:10]} ~ {str(series.max())[:10]}"
        else:
            kind = "文本"
            uniques = series.astype(str).unique()
            sample = "、".join(uniques[:3]) + ("…" if len(uniques) > 3 else "")
            rng = f"{len(uniques)} 个取值"
        lines.append(f"| {col} | {kind} | {sample} | {rng} |")
    return lines


def datasource_manifest(
    sources: Union[str, Path, Dict[str, Any], List[Union[str, Path]]],
    *,
    base_dir: Union[str, Path, None] = None,
) -> str:
    """生成数据源清单（markdown），供注入模型提示词。

    sources 支持：
    - job JSON 路径（读取其 datasources，并扫描 pages 里 chart.data 的 CSV 引用）
    - 目录路径（扫描其中全部 CSV）
    - CSV 路径列表
    - job 的 datasources dict（{name: {type, path}}）
    """
    base = Path(base_dir) if base_dir else Path(".")
    entries: List[tuple] = []  # (display_name, path)

    if isinstance(sources, dict):
        for name, ds in sources.items():
            if ds.get("path"):
                entries.append((name, base / ds["path"]))
    elif isinstance(sources, (list, tuple)):
        entries = [(Path(p).stem, base / p) for p in sources]
    else:
        path = Path(sources)
        if path.suffix.lower() == ".json":
            job = json.loads(path.read_text(encoding="utf-8"))
            job_base = Path(base_dir) if base_dir else path.parent
            for name, ds in (job.get("datasources") or {}).items():
                if ds.get("path"):
                    entries.append((name, job_base / ds["path"]))
            # pages 里直接引用的 CSV
            seen = {str(p) for _, p in entries}
            for page in job.get("pages") or []:
                panels = list((page.get("data") or {}).get("panels") or [])
                if (page.get("data") or {}).get("panel"):
                    panels.append(page["data"]["panel"])
                for panel in panels:
                    ref = (panel.get("chart") or {}).get("data")
                    if isinstance(ref, str) and ref.lower().endswith(".csv"):
                        full = job_base / ref
                        if str(full) not in seen:
                            seen.add(str(full))
                            entries.append((ref, full))
        elif path.is_dir():
            entries = [(p.name, p) for p in sorted(path.glob("*.csv"))]
        else:
            entries = [(path.name, path)]

    parts = ["# 可用数据源清单\n",
             "图表 spec 中的列名必须与下表完全一致（含全角字符）。\n"]
    for name, p in entries:
        try:
            df = pd.read_csv(p)
        except Exception as exc:
            parts.append(f"## {name}\n读取失败：{exc}\n")
            continue
        parts.append(f"## {name}")
        parts.append(f"路径 `{p}`，{len(df)} 行 × {len(df.columns)} 列\n")
        parts.extend(_profile_df(df))
        parts.append("")
    return "\n".join(parts)


_RULES = """\
# GTM 报告 job 产出规则

1. 产出一个 job JSON：mode="composer"，deck 给品牌/市场默认值，pages 为页面数组
2. 第 1 页 gtm_cover、第 2 页 gtm_toc（data 留空 {} 即可，目录自动生成）
3. 内容页 gtm_panels：1 图整页 / 2 图双栏 / 3 图左一右二 / 4 图 2×2；
   每个面板 = title（粗体小标题）+ subtitle（单位行）+ chart（图表 spec）
4. 观点页用 gtm_chart_text（左图右 bullets）；资产收益矩阵用 gtm_quilt
5. 图表 spec 里的列名照抄数据清单；不确定的字段宁可省略——引擎会推断并在
   warnings 里说明
6. 页码、章节竖签、目录、品牌字都不用管，deck 工作流自动处理
7. 产出后调用 `ableppt validate-job <job> --deep` 自检；按返回的 errors
   （含"是否想用 xxx"建议）修正后再渲染
"""


def gtm_prompt_kit(
    *,
    data_dir: Union[str, Path, None] = None,
    job: Union[str, Path, None] = None,
    datasources: Optional[Dict[str, Any]] = None,
    include_chart_examples: bool = True,
) -> str:
    """组装完整提示词物料：规则 + 页面示例 + 图表示例 + 数据清单。

    与 ``gtm_job_schema()``（约束解码用）配合使用：schema 管语法，
    本工具包给模型"写什么"的弹药。
    """
    from .gtm_examples import gtm_page_examples

    parts = [_RULES, gtm_page_examples()]
    if include_chart_examples:
        try:
            from ablechart import chart_spec_examples
            parts.append(chart_spec_examples())
        except Exception:
            pass

    source: Any = None
    if datasources:
        source = datasources
    elif job:
        source = job
    elif data_dir:
        source = data_dir
    if source is not None:
        parts.append(datasource_manifest(source))

    return "\n\n".join(parts)
