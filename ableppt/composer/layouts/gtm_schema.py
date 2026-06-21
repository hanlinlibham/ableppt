"""GTM deck job 的 JSON Schema + 深度校验 — 结构化输出对齐的两半。

**schema 管语法**：``gtm_job_schema()`` 喂给模型的结构化输出接口（tool
input_schema / response_format），布局名、面板结构、deck 字段在解码层锁死。

**深度校验管语义**：``validate_gtm_job()`` 不渲染、不写文件，加载真实数据源后
对每个面板的 chart spec 跑 ablechart 的 validate_spec，把"列名拼错/类型
不符/文件缺失"这类 schema 管不到的错误一次性收集（带 did-you-mean 建议），
供模型自修正循环使用::

    report = validate_gtm_job("job.json")
    if not report["ok"]:
        ...  # 把 report["errors"] 喂回模型修正后重试
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Union

GTM_LAYOUTS = ("gtm_cover", "gtm_toc", "gtm_panels", "gtm_chart_text", "gtm_quilt")


def gtm_job_schema() -> Dict[str, Any]:
    """返回 GTM deck job 的 JSON Schema（draft-07 兼容）。

    面板内 chart 字段的完整 schema 见 ablechart.chart_spec_schema()；
    此处引用为宽松 object，两份 schema 可分层喂给模型（先页面后图表），
    也可由调用方将 chart_spec_schema 内联进 panel.chart。
    """
    try:
        from ablechart import chart_spec_schema
        chart_schema: Dict[str, Any] = chart_spec_schema()
        # 内联时去掉顶层 $schema/title，避免嵌套噪音
        chart_schema = {k: v for k, v in chart_schema.items() if not k.startswith("$") and k != "title"}
    except Exception:
        chart_schema = {"type": "object", "additionalProperties": True}

    panel = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "面板粗体小标题"},
            "subtitle": {"type": "string", "description": "灰色单位行"},
            "chart": chart_schema,
            "table": {
                "type": "object",
                "description": "面板内迷你数据表（GTM 的 Avg/最新 小表）",
                "properties": {
                    "columns": {"type": "array", "items": {"type": "string"}},
                    "rows": {"type": "array", "items": {"type": "array"}},
                    "row_colors": {"type": "array", "items": {"type": ["string", "null"]}},
                    "at": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
                    "width": {"type": "number"},
                },
                "required": ["columns", "rows"],
                "additionalProperties": True,
            },
        },
        "additionalProperties": True,
    }

    page_chrome = {
        "title": {"type": "string"},
        "section": {"type": "string", "description": "章节名（竖签）；缺省沿用上一页"},
        "source": {"type": "string", "description": "底部来源行"},
        "tag": {"type": "string"},
        "page_num": {"type": ["integer", "string"], "description": "省略时 deck 工作流自增"},
    }

    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "ableppt GTM deck job",
        "type": "object",
        "properties": {
            "mode": {"const": "composer"},
            "theme": {"type": "string", "default": "able_finance"},
            "deck": {
                "type": "object",
                "description": "deck 级默认值：自动注入每页 + 页码自增 + 目录生成",
                "properties": {
                    "brand": {"type": "string"},
                    "market": {"type": "string"},
                    "source": {"type": "string"},
                    "tag": {"type": "string"},
                    "start_page": {"type": "integer", "default": 1},
                },
                "additionalProperties": True,
            },
            "datasources": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "properties": {
                        "type": {"enum": ["csv", "excel", "tushare"]},
                        "path": {"type": "string"},
                    },
                    "required": ["type"],
                    "additionalProperties": True,
                },
            },
            "pages": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "properties": {
                        "layout": {"enum": list(GTM_LAYOUTS)},
                        "data": {
                            "type": "object",
                            "properties": {
                                **page_chrome,
                                # gtm_cover
                                "date": {"type": "string"},
                                # gtm_toc：items 省略时自动生成
                                "items": {"type": "array"},
                                # gtm_panels：1/2/1+2/2x2
                                "panels": {"type": "array", "items": panel, "maxItems": 4},
                                # gtm_chart_text
                                "panel": panel,
                                "bullets": {"type": "array", "items": {"type": "string"}},
                                "bullets_title": {"type": "string"},
                                # gtm_quilt
                                "datasource": {"type": "string"},
                                "year_col": {"type": "string"},
                                "asset_col": {"type": "string"},
                                "value_col": {"type": "string"},
                                "colors": {"type": "object"},
                            },
                            "additionalProperties": True,
                        },
                    },
                    "required": ["layout", "data"],
                    "additionalProperties": False,
                },
            },
            "output": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
                "additionalProperties": True,
            },
        },
        "required": ["mode", "pages", "output"],
        "additionalProperties": True,
    }


def validate_gtm_job(job: Union[str, Path, Dict]) -> Dict[str, Any]:
    """深度校验：加载数据源 + 逐面板跑 chart spec 语义校验，不渲染。

    Returns: {ok, errors, warnings, pages}
    错误信息带页面/面板定位前缀，可直接喂回模型自修正。
    """
    errors: list = []
    warnings: list = []

    if isinstance(job, (str, Path)):
        try:
            job = json.loads(Path(job).read_text(encoding="utf-8"))
        except Exception as exc:
            return {"ok": False, "errors": [f"job 文件解析失败: {exc}"], "warnings": [], "pages": 0}

    from ablechart import validate_spec

    # 数据源可达性
    dfs = {}
    for name, ds in (job.get("datasources") or {}).items():
        path = ds.get("path")
        if ds.get("type") == "csv" and path:
            try:
                import pandas as pd
                dfs[name] = pd.read_csv(path)
            except Exception as exc:
                errors.append(f"datasources.{name}: 读取失败 — {exc}")

    pages = job.get("pages") or []
    for i, page in enumerate(pages, 1):
        layout = page.get("layout", "")
        data = page.get("data") or {}
        where = f"pages[{i}]({layout})"

        if layout not in GTM_LAYOUTS:
            errors.append(f"{where}: 未知布局，允许: {', '.join(GTM_LAYOUTS)}")
            continue

        panels = list(data.get("panels") or [])
        if layout == "gtm_chart_text" and data.get("panel"):
            panels.append(data["panel"])
        if layout == "gtm_panels" and not panels:
            warnings.append(f"{where}: panels 为空")
        if layout == "gtm_panels" and len(panels) > 4:
            errors.append(f"{where}: 面板最多 4 个（2×2），当前 {len(panels)}")

        for j, panel in enumerate(panels, 1):
            spec = panel.get("chart")
            if not spec:
                warnings.append(f"{where}.panels[{j}]: 无 chart")
                continue
            spec = dict(spec)
            data_ref = spec.get("data")
            if isinstance(data_ref, str) and data_ref in dfs:
                spec["data"] = dfs[data_ref]  # 数据源名引用
            report = validate_spec(spec)
            prefix = f"{where}.panels[{j}]"
            errors.extend(f"{prefix}: {e}" for e in report["errors"])
            warnings.extend(f"{prefix}: {w}" for w in report["warnings"])

        if layout == "gtm_quilt":
            df = dfs.get(data.get("datasource"))
            if df is None and "df" not in data:
                errors.append(f"{where}: 需要 datasource（已注册的 csv）或 df")
            elif df is not None:
                for key, default in (("year_col", "年份"), ("asset_col", "资产"), ("value_col", "收益率")):
                    col = data.get(key, default)
                    if col not in df.columns:
                        errors.append(f"{where}: 找不到列 '{col}'，可用列: {', '.join(map(str, df.columns))}")

    return {"ok": not errors, "errors": errors, "warnings": warnings, "pages": len(pages)}
