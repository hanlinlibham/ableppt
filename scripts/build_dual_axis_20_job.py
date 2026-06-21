#!/usr/bin/env python3
"""Generate a 20-page dual-axis gallery job JSON from the local sqlite cache."""

from __future__ import annotations

import json
from pathlib import Path


OUTPUT_JOB = Path(__file__).resolve().parent.parent / "job_dual_axis_20_gallery.json"
DB_PATH = "pptfi/data/tushare_market.sqlite"

INDEXES = [
    ("000300.SH", "沪深300"),
    ("000905.SH", "中证500"),
    ("000852.SH", "中证1000"),
    ("000016.SH", "上证50"),
    ("399006.SZ", "创业板指"),
    ("000688.SH", "科创50"),
]

STOCKS = [
    ("600519.SH", "贵州茅台"),
    ("300750.SZ", "宁德时代"),
    ("000333.SZ", "美的集团"),
    ("601318.SH", "中国平安"),
]


def index_amount_datasource(ts_code: str, name: str) -> tuple[str, dict]:
    key = f"idx_amount_{ts_code.replace('.', '_')}"
    query = f"""
    SELECT
      trade_date AS 日期,
      close AS 指数点位,
      amount / 1000000000.0 AS 成交额万亿元
    FROM index_bars
    WHERE ts_code = '{ts_code}'
    ORDER BY trade_date
    """
    return key, {"type": "sql", "conn": DB_PATH, "query": " ".join(query.split())}


def index_cumret_datasource(ts_code: str, name: str) -> tuple[str, dict]:
    key = f"idx_cumret_{ts_code.replace('.', '_')}"
    query = f"""
    SELECT
      trade_date AS 日期,
      close AS 指数点位,
      close / FIRST_VALUE(close) OVER (ORDER BY trade_date) - 1.0 AS 累计收益率
    FROM index_bars
    WHERE ts_code = '{ts_code}'
    ORDER BY trade_date
    """
    return key, {"type": "sql", "conn": DB_PATH, "query": " ".join(query.split())}


def stock_turnover_datasource(ts_code: str, name: str) -> tuple[str, dict]:
    key = f"stk_turnover_{ts_code.replace('.', '_')}"
    query = f"""
    SELECT
      b.trade_date AS 日期,
      b.close AS 收盘价,
      d.turnover_rate AS 换手率
    FROM stock_bars b
    JOIN stock_daily_basic d
      ON b.ts_code = d.ts_code
     AND b.trade_date = d.trade_date
    WHERE b.ts_code = '{ts_code}'
    ORDER BY b.trade_date
    """
    return key, {"type": "sql", "conn": DB_PATH, "query": " ".join(query.split())}


def stock_pe_datasource(ts_code: str, name: str) -> tuple[str, dict]:
    key = f"stk_pe_{ts_code.replace('.', '_')}"
    query = f"""
    SELECT
      b.trade_date AS 日期,
      b.close AS 收盘价,
      d.pe AS PE
    FROM stock_bars b
    JOIN stock_daily_basic d
      ON b.ts_code = d.ts_code
     AND b.trade_date = d.trade_date
    WHERE b.ts_code = '{ts_code}'
    ORDER BY b.trade_date
    """
    return key, {"type": "sql", "conn": DB_PATH, "query": " ".join(query.split())}


def chart_page(title: str, insight: str, source_key: str, primary_key: str, secondary_key: str, *,
               primary_name: str, secondary_name: str, page_label: str,
               primary_number_format: str, secondary_number_format: str,
               date_axis: str = "monthly") -> dict:
    return {
        "layout": "chart_full",
        "data": {
            "title": title,
            "insight": insight,
            "source": source_key,
            "categories_col": "日期",
            "series_config": [
                {"key": secondary_key, "name": secondary_name, "type": "bar", "axis": "secondary"},
                {"key": primary_key, "name": primary_name, "type": "line", "axis": "primary"}
            ],
            "style_config": {"color_scheme": "jp_finance", "line_width_pt": 1.5, "marker_style": "none"},
            "layout_config": {
                "value_axis_config": {"number_format": primary_number_format, "font_name": "黑体", "font_size_pt": 9},
                "secondary_value_axis_config": {"number_format": secondary_number_format, "font_name": "黑体", "font_size_pt": 8},
                "date_axis_config": date_axis
            },
            "footnote": f"Source: sqlite cache | Dual Axis Gallery {page_label}"
        }
    }


def main() -> int:
    datasources: dict[str, dict] = {}
    pages: list[dict] = []
    page_no = 1

    # 6 pages: index level + amount
    for ts_code, name in INDEXES:
        key, ds = index_amount_datasource(ts_code, name)
        datasources[key] = ds
        pages.append(
            chart_page(
                title=f"{name}点位与成交额",
                insight="line + bar 双轴，用于比较指数水平和交易热度。",
                source_key=key,
                primary_key="指数点位",
                secondary_key="成交额万亿元",
                primary_name="指数点位(左轴)",
                secondary_name="成交额(右轴, 万亿元)",
                page_label=f"{page_no:02d}",
                primary_number_format="#,##0",
                secondary_number_format="0.0",
            )
        )
        page_no += 1

    # 6 pages: index level + cumulative return
    for ts_code, name in INDEXES:
        key, ds = index_cumret_datasource(ts_code, name)
        datasources[key] = ds
        pages.append(
            chart_page(
                title=f"{name}点位与累计收益率",
                insight="line + line 双轴，用于比较价格水平和累计收益变化。",
                source_key=key,
                primary_key="指数点位",
                secondary_key="累计收益率",
                primary_name="指数点位(左轴)",
                secondary_name="累计收益率(右轴)",
                page_label=f"{page_no:02d}",
                primary_number_format="#,##0",
                secondary_number_format="0.0%",
            )
        )
        page_no += 1

    # 4 pages: stock price + turnover
    for ts_code, name in STOCKS:
        key, ds = stock_turnover_datasource(ts_code, name)
        datasources[key] = ds
        pages.append(
            chart_page(
                title=f"{name}收盘价与换手率",
                insight="个股 time-series 双轴，用于比较价格和交易活跃度。",
                source_key=key,
                primary_key="收盘价",
                secondary_key="换手率",
                primary_name="收盘价(左轴)",
                secondary_name="换手率(右轴)",
                page_label=f"{page_no:02d}",
                primary_number_format="#,##0.0",
                secondary_number_format="0.0",
            )
        )
        page_no += 1

    # 4 pages: stock price + PE
    for ts_code, name in STOCKS:
        key, ds = stock_pe_datasource(ts_code, name)
        datasources[key] = ds
        pages.append(
            chart_page(
                title=f"{name}收盘价与PE",
                insight="个股双折线双轴，用于看价格与估值的同步和背离。",
                source_key=key,
                primary_key="收盘价",
                secondary_key="PE",
                primary_name="收盘价(左轴)",
                secondary_name="PE(右轴)",
                page_label=f"{page_no:02d}",
                primary_number_format="#,##0.0",
                secondary_number_format="0.0",
            )
        )
        page_no += 1

    payload = {
        "mode": "composer",
        "theme": "dashboard_shell_16_9",
        "aspect_ratio": "16:9",
        "datasources": datasources,
        "pages": pages,
        "output": {"path": "dual_axis_20_gallery.pptx"},
    }
    OUTPUT_JOB.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "ok", "job": str(OUTPUT_JOB), "page_count": len(pages)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
