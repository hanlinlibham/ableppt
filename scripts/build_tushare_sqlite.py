#!/usr/bin/env python3
"""Fetch market data from Tushare and persist it into a local sqlite DB."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import tushare as ts

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pptfi.config import settings


INDEXES = {
    "000300.SH": "沪深300",
    "000905.SH": "中证500",
    "000852.SH": "中证1000",
    "000016.SH": "上证50",
    "399006.SZ": "创业板指",
    "000688.SH": "科创50",
}

STOCKS = {
    "600519.SH": "贵州茅台",
    "300750.SZ": "宁德时代",
    "000333.SZ": "美的集团",
    "601318.SH": "中国平安",
    "601899.SH": "紫金矿业",
}


def fetch_index_bars(pro, start_date: str, end_date: str) -> pd.DataFrame:
    frames = []
    for ts_code, name in INDEXES.items():
        df = pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        if df is None or df.empty:
            continue
        df["name"] = name
        frames.append(df)
    result = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if not result.empty:
        result["trade_date"] = pd.to_datetime(result["trade_date"], format="%Y%m%d")
        result = result.sort_values(["ts_code", "trade_date"]).reset_index(drop=True)
    return result


def fetch_stock_bars(start_date: str, end_date: str) -> pd.DataFrame:
    frames = []
    for ts_code, name in STOCKS.items():
        df = ts.pro_bar(ts_code=ts_code, start_date=start_date, end_date=end_date, adj="qfq")
        if df is None or df.empty:
            continue
        df["name"] = name
        frames.append(df)
    result = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if not result.empty:
        result["trade_date"] = pd.to_datetime(result["trade_date"], format="%Y%m%d")
        result = result.sort_values(["ts_code", "trade_date"]).reset_index(drop=True)
    return result


def fetch_stock_daily_basic(pro, start_date: str, end_date: str) -> pd.DataFrame:
    frames = []
    for ts_code, name in STOCKS.items():
        df = pro.daily_basic(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date,
            fields="ts_code,trade_date,close,turnover_rate,turnover_rate_f,volume_ratio,pe,pb,ps_ttm,dv_ratio,total_mv,circ_mv",
        )
        if df is None or df.empty:
            continue
        df["name"] = name
        frames.append(df)
    result = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if not result.empty:
        result["trade_date"] = pd.to_datetime(result["trade_date"], format="%Y%m%d")
        result = result.sort_values(["ts_code", "trade_date"]).reset_index(drop=True)
    return result


def build_views(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP VIEW IF EXISTS v_latest_stock_valuation;
        CREATE VIEW v_latest_stock_valuation AS
        WITH latest AS (
          SELECT ts_code, MAX(trade_date) AS trade_date
          FROM stock_daily_basic
          GROUP BY ts_code
        )
        SELECT b.*
        FROM stock_daily_basic b
        JOIN latest l
          ON b.ts_code = l.ts_code
         AND b.trade_date = l.trade_date;

        DROP VIEW IF EXISTS v_index_latest_return;
        CREATE VIEW v_index_latest_return AS
        WITH ordered AS (
          SELECT
            ts_code,
            name,
            trade_date,
            close,
            LAG(close) OVER (PARTITION BY ts_code ORDER BY trade_date) AS prev_close
          FROM index_bars
        ),
        latest AS (
          SELECT ts_code, MAX(trade_date) AS trade_date
          FROM ordered
          GROUP BY ts_code
        )
        SELECT
          o.ts_code,
          o.name,
          o.trade_date,
          o.close,
          CASE
            WHEN o.prev_close IS NULL OR o.prev_close = 0 THEN NULL
            ELSE o.close / o.prev_close - 1
          END AS daily_return
        FROM ordered o
        JOIN latest l
          ON o.ts_code = l.ts_code
         AND o.trade_date = l.trade_date;
        """
    )


def persist_tables(db_path: Path, index_bars: pd.DataFrame, stock_bars: pd.DataFrame, stock_daily_basic: pd.DataFrame) -> dict:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(db_path)) as conn:
        if not index_bars.empty:
            index_bars.to_sql("index_bars", conn, if_exists="replace", index=False)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_index_bars_code_date ON index_bars(ts_code, trade_date)")
        if not stock_bars.empty:
            stock_bars.to_sql("stock_bars", conn, if_exists="replace", index=False)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_stock_bars_code_date ON stock_bars(ts_code, trade_date)")
        if not stock_daily_basic.empty:
            stock_daily_basic.to_sql("stock_daily_basic", conn, if_exists="replace", index=False)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_stock_basic_code_date ON stock_daily_basic(ts_code, trade_date)")

        meta = pd.DataFrame(
            [
                {"key": "built_at", "value": datetime.now().isoformat(timespec="seconds")},
                {"key": "index_count", "value": str(len(INDEXES))},
                {"key": "stock_count", "value": str(len(STOCKS))},
            ]
        )
        meta.to_sql("metadata", conn, if_exists="replace", index=False)
        build_views(conn)

    return {
        "db_path": str(db_path),
        "tables": {
            "index_bars": len(index_bars),
            "stock_bars": len(stock_bars),
            "stock_daily_basic": len(stock_daily_basic),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a sqlite market cache from Tushare")
    parser.add_argument("--output", default="pptfi/data/tushare_market.sqlite", help="sqlite output path")
    parser.add_argument("--start-date", default="20210101")
    parser.add_argument("--end-date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    token = settings.tushare_token
    if not token:
        print(json.dumps({"status": "error", "message": "Tushare token not configured"}, ensure_ascii=False))
        return 1

    pro = ts.pro_api(token)

    index_bars = fetch_index_bars(pro, args.start_date, args.end_date)
    stock_bars = fetch_stock_bars(args.start_date, args.end_date)
    stock_daily_basic = fetch_stock_daily_basic(pro, args.start_date, args.end_date)

    payload = persist_tables(Path(args.output), index_bars, stock_bars, stock_daily_basic)
    payload["status"] = "ok"
    payload["date_range"] = {"start": args.start_date, "end": args.end_date}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
