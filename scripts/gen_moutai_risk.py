#!/usr/bin/env python3
"""贵州茅台过去一年风险分析报告生成器

计算风险指标：年化波动率、最大回撤、Sharpe比率、Beta、VaR
图表1：茅台累计收益率 vs 沪深300（双轴：柱+线）
图表2：滚动波动率 vs 沪深300收盘价（双轴：面积+线）
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tushare as ts
import pandas as pd
from pptfi.config import settings

# ============================================================================
# 配置
# ============================================================================
STOCK_CODE = "600519.SH"
STOCK_NAME = "贵州茅台"
INDEX_CODE = "000300.SH"
INDEX_NAME = "沪深300"
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "output" / "moutai_risk"
TEMPLATE_PATH = Path(__file__).resolve().parent.parent.parent / "aim" / "aim03.pptx"

# 过去一年
END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=365)
START_STR = START_DATE.strftime("%Y%m%d")
END_STR = END_DATE.strftime("%Y%m%d")
YEAR = END_DATE.year


def fetch_data():
    """获取茅台和沪深300过去一年日线数据"""
    pro = ts.pro_api(settings.tushare_token)

    print("📊 获取贵州茅台日线数据...", file=sys.stderr)
    df_stock = ts.pro_bar(ts_code=STOCK_CODE, start_date=START_STR, end_date=END_STR, adj="qfq")
    df_stock = df_stock.sort_values("trade_date").reset_index(drop=True)
    df_stock["trade_date"] = pd.to_datetime(df_stock["trade_date"], format="%Y%m%d")

    print("📊 获取沪深300指数数据...", file=sys.stderr)
    df_index = ts.pro_bar(ts_code=INDEX_CODE, start_date=START_STR, end_date=END_STR, asset="I")
    df_index = df_index.sort_values("trade_date").reset_index(drop=True)
    df_index["trade_date"] = pd.to_datetime(df_index["trade_date"], format="%Y%m%d")

    return df_stock, df_index


def compute_risk_metrics(df_stock, df_index):
    """计算全部风险指标"""
    # 合并
    stock = df_stock[["trade_date", "close"]].copy()
    stock.columns = ["trade_date", "stock_close"]
    index = df_index[["trade_date", "close"]].copy()
    index.columns = ["trade_date", "index_close"]
    df = pd.merge(stock, index, on="trade_date", how="inner")

    # 日收益率
    df["stock_ret"] = df["stock_close"].pct_change()
    df["index_ret"] = df["index_close"].pct_change()
    df = df.dropna()

    # 年化波动率
    stock_vol = df["stock_ret"].std() * np.sqrt(245)
    index_vol = df["index_ret"].std() * np.sqrt(245)

    # 最大回撤
    cum_stock = (1 + df["stock_ret"]).cumprod()
    running_max = cum_stock.cummax()
    drawdown = (cum_stock - running_max) / running_max
    max_drawdown = drawdown.min()

    # Sharpe（假设无风险利率 2%）
    rf = 0.02
    annual_ret = (df["stock_close"].iloc[-1] / df["stock_close"].iloc[0]) - 1
    sharpe = (annual_ret - rf) / stock_vol if stock_vol > 0 else 0

    # Beta
    cov = np.cov(df["stock_ret"], df["index_ret"])
    beta = cov[0, 1] / cov[1, 1] if cov[1, 1] > 0 else 0

    # VaR (95%)
    var_95 = np.percentile(df["stock_ret"], 5)

    # 累计收益率
    total_return = df["stock_close"].iloc[-1] / df["stock_close"].iloc[0] - 1
    index_return = df["index_close"].iloc[-1] / df["index_close"].iloc[0] - 1

    return {
        "annual_vol": stock_vol,
        "index_vol": index_vol,
        "max_drawdown": max_drawdown,
        "sharpe": sharpe,
        "beta": beta,
        "var_95": var_95,
        "total_return": total_return,
        "index_return": index_return,
        "latest_price": df["stock_close"].iloc[-1],
        "report_date": df["trade_date"].iloc[-1].strftime("%Y-%m-%d"),
        "start_date": df["trade_date"].iloc[0].strftime("%Y-%m-%d"),
    }, df


def build_chart1_csv(df_stock, df_index):
    """图表1：茅台累计收益率 vs 沪深300收盘价"""
    stock = df_stock[["trade_date", "close"]].copy()
    stock.columns = ["trade_date", "close_stock"]
    index = df_index[["trade_date", "close"]].copy()
    index.columns = ["trade_date", "close_index"]
    df = pd.merge(stock, index, on="trade_date", how="inner")

    base = df["close_stock"].iloc[0]
    df["茅台累计收益率"] = df["close_stock"] / base - 1
    df["沪深300指数"] = df["close_index"]
    df = df.rename(columns={"trade_date": "日期"})
    return df[["日期", "沪深300指数", "茅台累计收益率"]]


def build_chart2_csv(df_stock, df_index):
    """图表2：20日滚动波动率（年化）vs 沪深300收盘价"""
    stock = df_stock[["trade_date", "close"]].copy()
    stock.columns = ["trade_date", "close_stock"]
    index = df_index[["trade_date", "close"]].copy()
    index.columns = ["trade_date", "close_index"]
    df = pd.merge(stock, index, on="trade_date", how="inner")

    df["daily_ret"] = df["close_stock"].pct_change()
    df["20日滚动波动率"] = df["daily_ret"].rolling(20).std() * np.sqrt(245)
    df["沪深300指数"] = df["close_index"]
    df = df.dropna()
    df = df.rename(columns={"trade_date": "日期"})
    return df[["日期", "沪深300指数", "20日滚动波动率"]]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 获取数据
    df_stock, df_index = fetch_data()
    print(f"✅ 获取到 {len(df_stock)} 条茅台数据, {len(df_index)} 条指数数据", file=sys.stderr)

    # 2. 计算风险指标
    metrics, _ = compute_risk_metrics(df_stock, df_index)
    print(f"📈 年化波动率: {metrics['annual_vol']:.2%}", file=sys.stderr)
    print(f"📉 最大回撤: {metrics['max_drawdown']:.2%}", file=sys.stderr)
    print(f"📊 Sharpe: {metrics['sharpe']:.2f}", file=sys.stderr)
    print(f"📊 Beta: {metrics['beta']:.2f}", file=sys.stderr)
    print(f"📊 VaR(95%): {metrics['var_95']:.2%}", file=sys.stderr)

    # 3. 生成图表 CSV
    chart1_df = build_chart1_csv(df_stock, df_index)
    chart2_df = build_chart2_csv(df_stock, df_index)

    chart1_csv = OUTPUT_DIR / "return_chart.csv"
    chart2_csv = OUTPUT_DIR / "volatility_chart.csv"
    chart1_df.to_csv(chart1_csv, index=False)
    chart2_df.to_csv(chart2_csv, index=False)
    print(f"💾 已保存 CSV: {chart1_csv}, {chart2_csv}", file=sys.stderr)

    # 4. 构建 config.json
    config = {
        "text_data": {
            "标题": f"{STOCK_NAME}过去一年风险分析报告",
            "作者": "PPTFI 自动生成",
            "日期": metrics["report_date"],
            "标题1": f"{STOCK_NAME}收益与风险概览",
            "标题2": f"{STOCK_NAME}波动率与回撤分析",
            "标题3": f"{STOCK_NAME}风险指标总结",
            "组合名称": f"{STOCK_NAME}（{STOCK_CODE}）",
            "报告日期": metrics["report_date"],
            "成立日期": metrics["start_date"],
            "资产规模": f"最新价 {metrics['latest_price']:.2f} 元",
            "本年收益": f"{metrics['total_return']:.2%}",
            "本年收益金额": f"沪深300: {metrics['index_return']:.2%}",
            "累计收益率": f"波动率 {metrics['annual_vol']:.2%}",
            "累计收益金额": f"最大回撤 {metrics['max_drawdown']:.2%}",
            "平均年化": f"Sharpe {metrics['sharpe']:.2f} | Beta {metrics['beta']:.2f} | VaR95 {metrics['var_95']:.2%}",
        },
        "chart_configs": {
            "当年收益率走势图": {
                "csv_path": "return_chart.csv",
                "categories_col": "日期",
                "series_config": [
                    {"key": "沪深300指数", "name": f"{INDEX_NAME}指数(收盘价)", "type": "bar", "axis": "secondary"},
                    {"key": "茅台累计收益率", "name": f"{STOCK_NAME}累计收益率（左轴）", "type": "line", "axis": "primary"},
                ],
                "style": {"color_scheme": "aim00", "line_width_pt": 2.0, "marker_style": "none"},
                "layout": {
                    "title": f"{STOCK_NAME}过去一年累计收益率 vs {INDEX_NAME}",
                    "legend": {"position": "top", "font_size_pt": 9, "font_name": "黑体"},
                    "value_axis": {"number_format": "0%", "font_size_pt": 9, "font_name": "黑体", "has_major_gridlines": False},
                    "secondary_value_axis": {"number_format": "#,##0", "font_size_pt": 9, "font_name": "黑体", "has_major_gridlines": False},
                    "date_axis": {"number_format": "yyyy/mm"},
                },
            },
            "组合成立以来收益率走势": {
                "csv_path": "volatility_chart.csv",
                "categories_col": "日期",
                "series_config": [
                    {"key": "沪深300指数", "name": f"{INDEX_NAME}指数(收盘价)", "type": "area", "axis": "secondary"},
                    {"key": "20日滚动波动率", "name": "20日滚动波动率（年化）", "type": "line", "axis": "primary"},
                ],
                "style": {"color_scheme": "aim00", "line_width_pt": 2.0, "marker_style": "none"},
                "layout": {
                    "title": f"{STOCK_NAME}20日滚动波动率（年化）",
                    "legend": {"position": "top", "font_size_pt": 9, "font_name": "黑体"},
                    "value_axis": {"number_format": "0%", "font_size_pt": 9, "font_name": "黑体", "has_major_gridlines": True},
                    "secondary_value_axis": {"number_format": "#,##0", "font_size_pt": 9, "font_name": "黑体", "has_major_gridlines": False},
                    "date_axis": {"number_format": "yyyy/mm"},
                },
            },
        },
    }

    config_path = OUTPUT_DIR / "config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    # 5. 生成 PPT
    print(f"\n🔧 生成 PPT...", file=sys.stderr)
    output_pptx = OUTPUT_DIR / f"moutai_risk_{YEAR}.pptx"

    from pptfi.template.replacer import TemplateReplacer
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from generate_ppt import build_chart_config

    chart_configs = {}
    for chart_name, chart_def in config["chart_configs"].items():
        print(f"  构建图表: {chart_name}", file=sys.stderr)
        chart_configs[chart_name] = build_chart_config(chart_name, chart_def, OUTPUT_DIR)

    replacer = TemplateReplacer(TEMPLATE_PATH)
    replacer.replace(data=config["text_data"], chart_configs=chart_configs)
    replacer.save(output_pptx)

    print(f"\n✅ 风险分析报告已生成: {output_pptx}", file=sys.stderr)
    print(json.dumps({"status": "ok", "output": str(output_pptx)}))


if __name__ == "__main__":
    main()
