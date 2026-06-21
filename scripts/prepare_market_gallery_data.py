#!/usr/bin/env python3
"""Prepare market comparison datasets from the local sqlite cache."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

import pandas as pd


SERIES_MAP = {
    "000300.SH": "沪深300",
    "000905.SH": "中证500",
    "000852.SH": "中证1000",
    "399006.SZ": "创业板指",
}


def load_index_prices(db_path: Path, start_date: str) -> pd.DataFrame:
    codes = "', '".join(SERIES_MAP.keys())
    query = f"""
    SELECT ts_code, trade_date, close, amount
    FROM index_bars
    WHERE ts_code IN ('{codes}')
      AND trade_date >= '{start_date}'
    ORDER BY trade_date, ts_code
    """
    with sqlite3.connect(str(db_path)) as conn:
        df = pd.read_sql_query(query, conn)
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    df["name"] = df["ts_code"].map(SERIES_MAP)
    return df


def build_return_trend(df: pd.DataFrame) -> pd.DataFrame:
    pivot = df.pivot(index="trade_date", columns="name", values="close").sort_index().ffill()
    normalized = pivot / pivot.iloc[0] - 1
    normalized = normalized.reset_index().rename(columns={"trade_date": "日期"})
    return normalized


def build_rolling_vol(df: pd.DataFrame, window: int = 21) -> pd.DataFrame:
    pivot = df.pivot(index="trade_date", columns="name", values="close").sort_index().ffill()
    returns = pivot.pct_change().fillna(0)
    vol = returns.rolling(window).std() * (252 ** 0.5)
    vol = vol.dropna().reset_index().rename(columns={"trade_date": "日期"})
    return vol


def build_index_close_vol(df: pd.DataFrame, ts_code: str = "000300.SH", window: int = 21) -> pd.DataFrame:
    subset = df[df["ts_code"] == ts_code].copy().sort_values("trade_date")
    subset["trade_date"] = pd.to_datetime(subset["trade_date"])
    subset["daily_return"] = subset["close"].pct_change()
    subset["波动率"] = subset["daily_return"].rolling(window).std() * (252 ** 0.5)
    subset = subset.dropna().rename(columns={"trade_date": "日期", "close": "指数点位"})
    return subset[["日期", "指数点位", "波动率"]]


def build_drawdown(df: pd.DataFrame) -> pd.DataFrame:
    pivot = df.pivot(index="trade_date", columns="name", values="close").sort_index().ffill()
    rolling_max = pivot.cummax()
    drawdown = pivot / rolling_max - 1
    drawdown = drawdown.reset_index().rename(columns={"trade_date": "日期"})
    return drawdown


def build_monthly_returns(df: pd.DataFrame) -> pd.DataFrame:
    pivot = df.pivot(index="trade_date", columns="name", values="close").sort_index().ffill()
    monthly = pivot.resample("M").last().pct_change().dropna()
    monthly.index = monthly.index.strftime("%Y-%m")
    monthly = monthly.reset_index().rename(columns={"trade_date": "月份"})
    if "index" in monthly.columns:
        monthly = monthly.rename(columns={"index": "月份"})
    return monthly


def build_monthly_return_signal(df: pd.DataFrame, ts_code: str = "000300.SH") -> pd.DataFrame:
    subset = df[df["ts_code"] == ts_code].copy().sort_values("trade_date")
    pivot = subset.set_index("trade_date")[["close"]].rename(columns={"close": "收盘价"})
    monthly = pivot.resample("M").last().pct_change().dropna()
    monthly["3月均值"] = monthly["收盘价"].rolling(3).mean()
    monthly["3月均值"] = monthly["3月均值"].fillna(monthly["收盘价"])
    monthly.index = monthly.index.strftime("%Y-%m")
    monthly = monthly.reset_index().rename(columns={"trade_date": "月份", "index": "月份", "收盘价": "月度收益"})
    return monthly


def build_index_close_cumret(df: pd.DataFrame, ts_code: str = "000300.SH") -> pd.DataFrame:
    subset = df[df["ts_code"] == ts_code].copy().sort_values("trade_date")
    subset["trade_date"] = pd.to_datetime(subset["trade_date"])
    subset["累计收益率"] = subset["close"] / subset["close"].iloc[0] - 1
    subset = subset.rename(columns={"trade_date": "日期", "close": "指数点位"})
    return subset[["日期", "指数点位", "累计收益率"]]


def build_index_summary(df: pd.DataFrame) -> pd.DataFrame:
    pivot = df.pivot(index="trade_date", columns="name", values="close").sort_index().ffill()
    trailing = pivot.tail(252) if len(pivot) >= 252 else pivot
    returns = trailing.iloc[-1] / trailing.iloc[0] - 1
    vol = trailing.pct_change().dropna().std() * (252 ** 0.5)
    summary = pd.DataFrame({"指数": returns.index, "年化收益率": returns.values, "年化波动率": vol.reindex(returns.index).values})
    return summary


def load_latest_stock_valuation(db_path: Path) -> pd.DataFrame:
    query = """
    SELECT ts_code, name, trade_date, close, pe, pb, total_mv
    FROM v_latest_stock_valuation
    ORDER BY total_mv DESC
    """
    with sqlite3.connect(str(db_path)) as conn:
        df = pd.read_sql_query(query, conn)
    return df.rename(
        columns={
            "ts_code": "股票代码",
            "name": "股票名称",
            "trade_date": "日期",
            "close": "收盘价",
            "pe": "PE",
            "pb": "PB",
            "total_mv": "总市值"
        }
    )


def build_index_close_amount(df: pd.DataFrame, ts_code: str = "000300.SH") -> pd.DataFrame:
    subset = df[df["ts_code"] == ts_code].copy()
    subset = subset.sort_values("trade_date")
    subset["trade_date"] = pd.to_datetime(subset["trade_date"])
    # index_daily amount is in thousand RMB; convert to trillion RMB for a readable secondary axis.
    subset["amount_trillion"] = subset["amount"] / 1_000_000_000
    subset = subset.rename(columns={"trade_date": "日期", "close": "指数点位", "amount_trillion": "成交额(万亿元)"})
    return subset[["日期", "指数点位", "成交额(万亿元)"]]


def build_valuation_dual_table(db_path: Path) -> pd.DataFrame:
    query = """
    SELECT name, pe, pb, total_mv
    FROM v_latest_stock_valuation
    ORDER BY total_mv DESC
    """
    with sqlite3.connect(str(db_path)) as conn:
        df = pd.read_sql_query(query, conn)
    # tushare total_mv is in 10k RMB; convert to trillion RMB for a readable secondary axis
    df["total_mv_trillion"] = df["total_mv"] / 100_000_000
    return df.rename(columns={"name": "股票", "pe": "PE", "pb": "PB", "total_mv_trillion": "总市值(万亿元)"})[
        ["股票", "PE", "PB", "总市值(万亿元)"]
    ]


def build_stock_price_turnover(db_path: Path, ts_code: str = "600519.SH") -> pd.DataFrame:
    query = f"""
    SELECT b.trade_date, b.close, d.turnover_rate
    FROM stock_bars b
    JOIN stock_daily_basic d
      ON b.ts_code = d.ts_code
     AND b.trade_date = d.trade_date
    WHERE b.ts_code = '{ts_code}'
    ORDER BY b.trade_date
    """
    with sqlite3.connect(str(db_path)) as conn:
        df = pd.read_sql_query(query, conn)
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df.rename(columns={"trade_date": "日期", "close": "收盘价", "turnover_rate": "换手率"})[
        ["日期", "收盘价", "换手率"]
    ]


def build_stock_price_pe(db_path: Path, ts_code: str = "600519.SH") -> pd.DataFrame:
    query = f"""
    SELECT b.trade_date, b.close, d.pe
    FROM stock_bars b
    JOIN stock_daily_basic d
      ON b.ts_code = d.ts_code
     AND b.trade_date = d.trade_date
    WHERE b.ts_code = '{ts_code}'
    ORDER BY b.trade_date
    """
    with sqlite3.connect(str(db_path)) as conn:
        df = pd.read_sql_query(query, conn)
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df.rename(columns={"trade_date": "日期", "close": "收盘价", "pe": "PE"})[
        ["日期", "收盘价", "PE"]
    ]


def write_csvs(output_dir: Path, start_date: str, db_path: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw = load_index_prices(db_path, start_date)

    datasets = {
        "returns_trend": build_return_trend(raw),
        "rolling_vol": build_rolling_vol(raw),
        "drawdown": build_drawdown(raw),
        "monthly_returns": build_monthly_returns(raw),
        "hs300_close_vol": build_index_close_vol(raw),
        "hs300_monthly_signal": build_monthly_return_signal(raw),
        "hs300_close_cumret": build_index_close_cumret(raw),
        "index_summary": build_index_summary(raw),
        "latest_stock_valuation": load_latest_stock_valuation(db_path),
        "hs300_close_amount": build_index_close_amount(raw),
        "valuation_dual": build_valuation_dual_table(db_path),
        "moutai_price_turnover": build_stock_price_turnover(db_path),
        "moutai_price_pe": build_stock_price_pe(db_path),
    }

    result = {}
    for name, df in datasets.items():
        path = output_dir / f"{name}.csv"
        df.to_csv(path, index=False, encoding="utf-8")
        result[name] = {"path": str(path), "rows": len(df), "columns": list(df.columns)}
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare market gallery datasets from sqlite")
    parser.add_argument("--db", default="ableppt/data/tushare_market.sqlite")
    parser.add_argument("--output", default="ableppt/data/market_gallery")
    parser.add_argument("--start-date", default="20240101")
    args = parser.parse_args()

    payload = write_csvs(Path(args.output), args.start_date, Path(args.db))
    print(json.dumps({"status": "ok", "datasets": payload}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
