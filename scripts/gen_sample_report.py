#!/usr/bin/env python3
"""样例公司年度分析报告生成器

独立示例脚本，演示如何使用 tushare + ableppt 生成完整投资分析报告。
新报告请优先使用 run_job.py + Job JSON 声明式编排。

使用 tushare 获取数据，生成包含复杂双轴图表的 PPT。
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tushare as ts
import pandas as pd
import numpy as np
from ableppt.config import settings

# ============================================================================
# 配置
# ============================================================================
STOCK_CODE = "600519.SH"
STOCK_NAME = "样例公司"
INDEX_CODE = "000300.SH"
INDEX_NAME = "沪深300"
YEAR = 2025
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "output" / "sample_report"
TEMPLATE_PATH = Path(__file__).resolve().parent.parent.parent / "aim" / "aim00.pptx"


def fetch_data():
    """从 tushare 获取所有需要的数据"""
    pro = ts.pro_api(settings.tushare_token)

    print("📊 获取样例公司日线数据...", file=sys.stderr)
    # 当年日线数据
    df_stock = ts.pro_bar(
        ts_code=STOCK_CODE,
        start_date=f"{YEAR}0101",
        end_date=f"{YEAR}1231",
        adj="qfq",
    )
    df_stock = df_stock.sort_values("trade_date").reset_index(drop=True)
    df_stock["trade_date"] = pd.to_datetime(df_stock["trade_date"], format="%Y%m%d")

    print("📊 获取沪深300指数数据...", file=sys.stderr)
    # 对应的沪深300指数（使用 pro_bar + asset='I' 替代 index_daily）
    df_index = ts.pro_bar(
        ts_code=INDEX_CODE,
        start_date=f"{YEAR}0101",
        end_date=f"{YEAR}1231",
        asset="I",
    )
    df_index = df_index.sort_values("trade_date").reset_index(drop=True)
    df_index["trade_date"] = pd.to_datetime(df_index["trade_date"], format="%Y%m%d")

    print("📊 获取近5年日线数据...", file=sys.stderr)
    # 近5年数据（成立以来走势）
    df_stock_5y = ts.pro_bar(
        ts_code=STOCK_CODE,
        start_date=f"{YEAR - 4}0101",
        end_date=f"{YEAR}1231",
        adj="qfq",
    )
    df_stock_5y = df_stock_5y.sort_values("trade_date").reset_index(drop=True)
    df_stock_5y["trade_date"] = pd.to_datetime(df_stock_5y["trade_date"], format="%Y%m%d")

    df_index_5y = ts.pro_bar(
        ts_code=INDEX_CODE,
        start_date=f"{YEAR - 4}0101",
        end_date=f"{YEAR}1231",
        asset="I",
    )
    df_index_5y = df_index_5y.sort_values("trade_date").reset_index(drop=True)
    df_index_5y["trade_date"] = pd.to_datetime(df_index_5y["trade_date"], format="%Y%m%d")

    return df_stock, df_index, df_stock_5y, df_index_5y


def compute_ytd_chart(df_stock, df_index):
    """计算当年收益率走势图数据：样例公司收益率 vs 沪深300收盘价"""

    # 合并数据
    df = pd.merge(
        df_stock[["trade_date", "close", "vol"]],
        df_index[["trade_date", "close"]],
        on="trade_date",
        how="inner",
        suffixes=("_stock", "_index"),
    )

    # 计算累计收益率
    base_stock = df["close_stock"].iloc[0]
    base_index = df["close_index"].iloc[0]
    df["样例公司累计收益率"] = (df["close_stock"] / base_stock - 1)
    df["沪深300指数"] = df["close_index"]

    # 日期列
    df = df.rename(columns={"trade_date": "日期"})

    return df[["日期", "沪深300指数", "样例公司累计收益率"]]


def compute_5y_chart(df_stock_5y, df_index_5y):
    """计算近5年走势数据：样例公司累计收益率 + 成交额"""

    stock = df_stock_5y[["trade_date", "close", "amount"]].copy()
    stock.columns = ["trade_date", "close_stock", "amount_stock"]
    index = df_index_5y[["trade_date", "close"]].copy()
    index.columns = ["trade_date", "close_index"]

    df = pd.merge(stock, index, on="trade_date", how="inner")

    # 累计收益率
    base_stock = df["close_stock"].iloc[0]
    df["样例公司累计收益率"] = (df["close_stock"] / base_stock - 1)
    # 成交额（万元）
    df["成交额(万元)"] = df["amount_stock"] / 10  # tushare amount 单位是千元

    df = df.rename(columns={"trade_date": "日期"})
    return df[["日期", "样例公司累计收益率", "成交额(万元)"]]


def compute_stats(df_stock, df_stock_5y):
    """计算关键统计指标"""
    # 当年收益率
    ytd_return = df_stock["close"].iloc[-1] / df_stock["close"].iloc[0] - 1

    # 5年累计收益率
    total_return = df_stock_5y["close"].iloc[-1] / df_stock_5y["close"].iloc[0] - 1

    # 年化收益率
    n_years = len(df_stock_5y) / 245  # 大约交易日数
    annualized = (1 + total_return) ** (1 / n_years) - 1 if n_years > 0 else 0

    # 最新价
    latest_price = df_stock["close"].iloc[-1]
    # 最新市值（假设总股本约12.56亿股）
    total_shares = 12.56  # 亿股
    market_cap = latest_price * total_shares  # 亿元

    return {
        "ytd_return": ytd_return,
        "total_return": total_return,
        "annualized": annualized,
        "latest_price": latest_price,
        "market_cap": market_cap,
        "report_date": df_stock["trade_date"].iloc[-1].strftime("%Y-%m-%d"),
        "start_date": df_stock_5y["trade_date"].iloc[0].strftime("%Y-%m-%d"),
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 获取数据
    df_stock, df_index, df_stock_5y, df_index_5y = fetch_data()

    print(f"✅ 获取到 {len(df_stock)} 条当年数据, {len(df_stock_5y)} 条5年数据", file=sys.stderr)

    # 计算图表数据
    ytd_df = compute_ytd_chart(df_stock, df_index)
    fivey_df = compute_5y_chart(df_stock_5y, df_index_5y)
    stats = compute_stats(df_stock, df_stock_5y)

    print(f"📈 当年收益率: {stats['ytd_return']:.2%}", file=sys.stderr)
    print(f"📈 5年累计收益率: {stats['total_return']:.2%}", file=sys.stderr)
    print(f"📈 年化收益率: {stats['annualized']:.2%}", file=sys.stderr)
    print(f"📈 最新价: {stats['latest_price']:.2f}", file=sys.stderr)

    # 保存 CSV
    ytd_csv = OUTPUT_DIR / "ytd_chart.csv"
    fivey_csv = OUTPUT_DIR / "fivey_chart.csv"
    ytd_df.to_csv(ytd_csv, index=False)
    fivey_df.to_csv(fivey_csv, index=False)

    print(f"💾 已保存 CSV: {ytd_csv}, {fivey_csv}", file=sys.stderr)

    # 构建 config.json
    config = {
        "text_data": {
            "标题": f"{STOCK_NAME}{YEAR}年度投资分析报告",
            "作者": "PPTFI 自动生成",
            "日期": stats["report_date"],
            "标题1": f"{STOCK_NAME}股价与估值分析",
            "标题2": f"{STOCK_NAME}财务与经营分析",
            "标题3": f"{STOCK_NAME}投资价值总结",
            "组合名称": f"{STOCK_NAME}（{STOCK_CODE}）",
            "报告日期": stats["report_date"],
            "成立日期": stats["start_date"],
            "资产规模": f"{stats['market_cap']:.0f}亿元",
            "本年收益": f"{stats['ytd_return']:.2%}",
            "本年收益金额": f"{stats['latest_price']:.2f}元/股",
            "累计收益率": f"{stats['total_return']:.2%}",
            "累计收益金额": f"近5年({YEAR-4}-{YEAR})",
            "平均年化": f"{stats['annualized']:.2%}",
        },
        "chart_configs": {
            "当年收益率走势图": {
                "csv_path": "ytd_chart.csv",
                "categories_col": "日期",
                "series_config": [
                    {
                        "key": "沪深300指数",
                        "name": f"{INDEX_NAME}指数(收盘价)",
                        "type": "bar",
                        "axis": "secondary",
                    },
                    {
                        "key": "样例公司累计收益率",
                        "name": f"{STOCK_NAME}累计收益率（左轴）",
                        "type": "line",
                        "axis": "primary",
                    },
                ],
                "style": {
                    "color_scheme": "aim00",
                    "line_width_pt": 2.0,
                    "marker_style": "none",
                },
                "layout": {
                    "title": f"{STOCK_NAME}{YEAR}年累计收益率走势图",
                    "legend": {
                        "position": "top",
                        "font_size_pt": 9,
                        "font_name": "黑体",
                    },
                    "value_axis": {
                        "number_format": "0%",
                        "font_size_pt": 9,
                        "font_name": "黑体",
                        "has_major_gridlines": False,
                    },
                    "secondary_value_axis": {
                        "number_format": "#,##0",
                        "font_size_pt": 9,
                        "font_name": "黑体",
                        "has_major_gridlines": False,
                    },
                    "date_axis": {
                        "base_unit": "days",
                        "number_format": "yyyy/mm",
                    },
                },
            },
            "组合成立以来收益率走势": {
                "csv_path": "fivey_chart.csv",
                "categories_col": "日期",
                "series_config": [
                    {
                        "key": "样例公司累计收益率",
                        "name": f"{STOCK_NAME}累计收益率",
                        "type": "line",
                        "axis": "primary",
                    },
                    {
                        "key": "成交额(万元)",
                        "name": "成交额(万元)",
                        "type": "area",
                        "axis": "secondary",
                    },
                ],
                "style": {
                    "color_scheme": "aim00",
                    "line_width_pt": 2.0,
                    "marker_style": "none",
                },
                "layout": {
                    "title": f"{STOCK_NAME}近5年走势（{YEAR-4}-{YEAR}）",
                    "legend": {
                        "position": "bottom",
                        "font_size_pt": 9,
                        "font_name": "黑体",
                    },
                    "value_axis": {
                        "number_format": "0%",
                        "font_size_pt": 9,
                        "font_name": "黑体",
                        "has_major_gridlines": False,
                    },
                    "secondary_value_axis": {
                        "number_format": "#,##0",
                        "font_size_pt": 9,
                        "font_name": "黑体",
                        "has_major_gridlines": False,
                    },
                    "date_axis": {
                        "base_unit": "days",
                        "number_format": "yyyy/mm",
                    },
                },
            },
        },
    }

    config_path = OUTPUT_DIR / "config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"💾 已保存配置: {config_path}", file=sys.stderr)

    # 调用 generate_ppt
    output_pptx = OUTPUT_DIR / f"sample_{YEAR}_report.pptx"

    print(f"\n🔧 生成 PPT...", file=sys.stderr)

    from ableppt.template.replacer import TemplateReplacer
    from ableppt.chart_builder.styles import StyleConfig
    from ableppt.chart_builder.layout import (
        ChartLayoutConfig,
        LegendConfig,
        ValueAxisConfig,
    )
    from ableppt.chart_builder.date_axis import DateAxisConfig
    from pptx.enum.chart import XL_LEGEND_POSITION

    # 导入 generate_ppt 的 build_chart_config
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from generate_ppt import build_chart_config

    chart_configs = {}
    for chart_name, chart_def in config["chart_configs"].items():
        print(f"  构建图表: {chart_name}", file=sys.stderr)
        chart_configs[chart_name] = build_chart_config(chart_name, chart_def, OUTPUT_DIR)

    replacer = TemplateReplacer(TEMPLATE_PATH)
    replacer.replace(data=config["text_data"], chart_configs=chart_configs)
    replacer.save(output_pptx)

    print(f"\n✅ 报告已生成: {output_pptx}", file=sys.stderr)
    print(json.dumps({"status": "ok", "output": str(output_pptx)}))


if __name__ == "__main__":
    main()
