"""生成 GTM 风格演示数据集（data/gtm/*.csv）。

拟真宏观/市场序列，仅用于 job_gtm_demo.json 排版演示。
重新生成：python scripts/gen_gtm_demo_data.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "data" / "gtm"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(42)


def save(name: str, df: pd.DataFrame):
    df.to_csv(OUT / name, index=False)
    print(f"  {name}: {len(df)} rows")


# ── P1 经济增长 ──
q = pd.period_range("2021Q1", "2025Q2", freq="Q").astype(str)
n = len(q)
consume = rng.normal(2.2, 1.1, n)
invest = rng.normal(1.3, 0.9, n)
net_exp = rng.normal(0.3, 1.0, n)
inventory = rng.normal(0.0, 0.5, n)
gdp = pd.DataFrame({
    "季度": q,
    "最终消费": (consume / 100).round(4),
    "资本形成": (invest / 100).round(4),
    "净出口": (net_exp / 100).round(4),
    "库存变动": (inventory / 100).round(4),
})
gdp["GDP同比"] = gdp[["最终消费", "资本形成", "净出口", "库存变动"]].sum(axis=1).round(4)
save("gdp_contrib.csv", gdp)

ms = pd.date_range("2012-01-31", periods=160, freq="ME")
trend = 60 * np.exp(0.0024 * np.arange(160))
actual = trend * (1 + np.cumsum(rng.normal(0, 0.004, 160)))
actual[98:104] *= np.array([0.97, 0.93, 0.95, 0.97, 0.99, 1.0])  # 疫情缺口
save("gdp_trend.csv", pd.DataFrame({
    "月份": ms.strftime("%Y-%m-%d"),
    "实际GDP指数": actual.round(1),
    "趋势线": trend.round(1),
}))

# ── P2 通胀 ──
m2 = pd.date_range("2016-01-31", periods=114, freq="ME")
headline = np.clip(2.0 + np.cumsum(rng.normal(0, 0.18, 114)) * 0.55, -0.8, 6.0)
core = headline * 0.6 + 0.8 + rng.normal(0, 0.12, 114)
save("cpi.csv", pd.DataFrame({
    "月份": m2.strftime("%Y-%m-%d"),
    "CPI同比": (headline / 100).round(4),
    "核心CPI同比": (core / 100).round(4),
}))

q8 = pd.period_range("2023Q3", "2025Q2", freq="Q").astype(str)
food = rng.normal(0.8, 0.5, 8)
energy = rng.normal(0.2, 0.6, 8)
serv = rng.normal(0.9, 0.3, 8)
goods = rng.normal(0.3, 0.3, 8)
parts = pd.DataFrame({
    "季度": q8,
    "食品": (food / 100).round(4), "能源": (energy / 100).round(4),
    "服务": (serv / 100).round(4), "核心商品": (goods / 100).round(4),
})
parts["CPI同比"] = parts[["食品", "能源", "服务", "核心商品"]].sum(axis=1).round(4)
save("cpi_parts.csv", parts)

# ── P3 劳动力市场 ──
m3 = pd.date_range("2019-01-31", periods=78, freq="ME")
unemp = np.clip(5.1 + np.cumsum(rng.normal(0, 0.07, 78)), 3.6, 6.5)
wage = np.clip(3.0 + np.cumsum(rng.normal(0.005, 0.07, 78)), 1.2, 5.2)
save("labour.csv", pd.DataFrame({
    "月份": m3.strftime("%Y-%m-%d"),
    "调查失业率": (unemp / 100).round(4),
    "工资同比": (wage / 100).round(4),
}))

m4 = pd.date_range("2021-01-31", periods=54, freq="ME")
vac = np.clip(100 + np.cumsum(rng.normal(0.4, 4.0, 54)), 60, 160)
hire = vac * 0.7 + rng.normal(0, 6, 54) + 20
save("vacancy.csv", pd.DataFrame({
    "月份": m4.strftime("%Y-%m-%d"),
    "招聘需求指数": vac.round(1),
    "企业用工景气": hire.round(1),
}))

partic = np.clip(66.0 + np.cumsum(rng.normal(0.012, 0.10, 54)), 64.5, 68.5)
save("participation.csv", pd.DataFrame({
    "月份": m4.strftime("%Y-%m-%d"),
    "劳动参与率": (partic / 100).round(4),
}))

# ── P4 估值 ──
inds = ["白酒", "创新药", "半导体", "新能源", "银行", "家电", "软件", "有色", "券商", "煤炭"]
low = rng.uniform(6, 16, 10)
high = low + rng.uniform(16, 48, 10)
save("pe_range.csv", pd.DataFrame({
    "行业": inds,
    "十年最低": low.round(1), "十年最高": high.round(1),
    "十年均值": (low + (high - low) * rng.uniform(0.38, 0.55, 10)).round(1),
    "当前": (low + (high - low) * rng.uniform(0.08, 0.92, 10)).round(1),
}))

secs = ["能源", "原材料", "工业", "可选消费", "必需消费", "医疗", "金融", "信息技术", "全指"]
save("eps.csv", pd.DataFrame({
    "板块": secs,
    "2025E": (rng.uniform(-0.12, 0.22, 9)).round(3),
    "2026E": (rng.uniform(0.02, 0.30, 9)).round(3),
}))

# ── P5 贸易 ──
months5 = ["2025-02", "2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2025-08"]
statutory = np.array([5.1, 7.0, 19.0, 14.0, 14.9, 16.3, 19.2])
collected = np.array([3.0, 2.8, 6.4, 8.7, 10.8, 11.5, 11.6])
save("tariff.csv", pd.DataFrame({
    "月份": months5,
    "名义税率": (statutory / 100).round(4),
    "实际征收税率": (collected / 100).round(4),
}))

mkts = ["市场A", "市场B", "市场C", "市场D", "市场E", "市场F", "市场G", "市场H"]
pre = np.sort(rng.uniform(0.01, 0.11, 8))[::-1]
add = np.sort(rng.uniform(0.06, 0.34, 8))[::-1]
save("tariff_by_market.csv", pd.DataFrame({
    "市场": mkts[::-1],          # 横向条形图底部在前 → 倒序使最大值在顶
    "存量税率": pre[::-1].round(3),
    "新增税率": add[::-1].round(3),
}))

print("done ->", OUT)

# ── 资产收益 quilt 矩阵（追加） ──
assets = ["A股", "港股", "美股", "利率债", "信用债", "黄金", "商品", "现金"]
years = [str(y) for y in range(2019, 2026)]
rows = []
base = {"A股": 0.05, "港股": 0.02, "美股": 0.10, "利率债": 0.035,
        "信用债": 0.04, "黄金": 0.07, "商品": 0.03, "现金": 0.02}
for yy in years:
    for a in assets:
        rows.append({"年份": yy, "资产": a,
                     "收益率": round(base[a] + rng.normal(0, 0.12 if a in ("A股", "港股", "美股", "商品") else 0.03), 3)})
save("asset_returns.csv", pd.DataFrame(rows))
