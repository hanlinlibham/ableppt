"""GTM 页面 spec 示例库 — 给 LLM 的 few-shot 弹药（与 pptchartengine
的 chart_spec_examples 同思路：按场景检索最小可用 JSON）。

用法::

    from pptfi.composer.layouts.gtm_examples import gtm_page_examples
    prompt += gtm_page_examples()          # 全部
    prompt += gtm_page_examples("quilt")   # 单场景
"""

from __future__ import annotations

import json
from typing import Optional

GTM_PAGE_EXAMPLES = [
    ("deck|工作流|整本", "deck 级编排：品牌/市场默认值继承 + 页码自增 + 目录自动生成", {
        "mode": "composer",
        "deck": {"brand": "XX资产研究", "market": "CN", "start_page": 1},
        "pages": [
            {"layout": "gtm_cover", "data": {"title": "市场洞察", "date": "2026年6月"}},
            {"layout": "gtm_toc", "data": {}},
            {"layout": "gtm_panels", "data": {"title": "…", "section": "宏观", "panels": ["…"]}}
        ],
        "output": {"path": "deck.pptx"}
    }),
    ("cover|封面", "GTM 封面：箭头组 + 大标题 + 日期", {
        "layout": "gtm_cover",
        "data": {"title": "市场洞察", "subtitle": "2026年中期展望", "date": "2026年6月11日"}
    }),
    ("toc|目录", "目录：items 缺省时按后续页面 section/title 自动生成", {
        "layout": "gtm_toc", "data": {}
    }),
    ("panels|双栏|面板页", "标准 GTM 双栏面板页；chart 即 pptchartengine spec", {
        "layout": "gtm_panels",
        "data": {
            "title": "通货膨胀", "section": "宏观", "source": "来源：…",
            "panels": [
                {"title": "CPI与核心CPI", "subtitle": "同比",
                 "chart": {"chart": "line", "data": "data/cpi.csv",
                           "layout": {"y_axis": {"format": "0%"}}},
                 "table": {"columns": ["", "均值", "最新"],
                           "rows": [["CPI同比", "2.1%", "2.4%"]],
                           "row_colors": ["#29ABE2"]}},
                {"title": "通胀分项贡献", "subtitle": "百分点",
                 "chart": {"chart": "contribution", "data": "data/cpi_parts.csv",
                           "total": "CPI同比"}}
            ]
        }
    }),
    ("1+2|三面板", "左一右二：第 1 个面板占左半全高，2/3 右侧上下排（panels 给 3 个即可）", {
        "layout": "gtm_panels",
        "data": {"title": "劳动力市场", "section": "宏观",
                 "panels": [{"title": "左大图", "chart": "…"},
                            {"title": "右上", "chart": "…"},
                            {"title": "右下", "chart": "…"}]}
    }),
    ("2x2|四面板|仪表盘", "2×2 网格：panels 给 4 个即可", {
        "layout": "gtm_panels",
        "data": {"title": "宏观全景", "section": "宏观",
                 "panels": ["…", "…", "…", "…"]}
    }),
    ("quilt|收益矩阵|资产排序", "资产收益排序矩阵（GTM 标志页）：长表 年份/资产/收益率", {
        "layout": "gtm_quilt",
        "data": {"title": "大类资产年度收益排序", "section": "资产配置",
                 "datasource": "asset_returns",
                 "year_col": "年份", "asset_col": "资产", "value_col": "收益率"}
    }),
    ("chart_text|图文|点评", "左图右点评：panel 同面板页，bullets 为观点列表", {
        "layout": "gtm_chart_text",
        "data": {"title": "权益市场观点", "section": "权益",
                 "panel": {"title": "行业估值区间",
                           "chart": {"chart": "range", "data": "data/pe.csv",
                                     "low": "低", "high": "高"}},
                 "bullets": ["观点一……", "观点二……"]}
    }),
]


def gtm_page_examples(scenario: Optional[str] = None) -> str:
    """返回 GTM 页面 spec 示例（markdown），scenario 关键词模糊匹配。"""
    rows = GTM_PAGE_EXAMPLES
    if scenario:
        token = str(scenario).strip().lower()
        matched = [r for r in rows if token in r[0].lower() or token in r[1].lower()]
        rows = matched or rows
    parts = ["# GTM 页面 spec 场景示例\n"]
    for keywords, note, spec in rows:
        parts.append(f"## {keywords.split('|')[0]}（{note}）")
        parts.append("```json")
        parts.append(json.dumps(spec, ensure_ascii=False, indent=2))
        parts.append("```\n")
    return "\n".join(parts)
