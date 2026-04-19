#!/usr/bin/env python3
"""安克创新 (300866.SZ) 走势情况与竞争壁垒分析报告"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from pptfi.composer import PageComposer
from pptfi.chart_builder import create_combo_chart
from pptfi.chart_builder.styles import StyleConfig
from pptfi.chart_builder.layout import (
    ChartLayoutConfig, LegendConfig, ValueAxisConfig, CategoryAxisConfig,
)
from pptfi.chart_builder.date_axis import MONTHLY_TICKS, WEEKLY_TICKS
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "output" / "anker_report"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

THEME = "tech_blue"

# ============================================================================
# 数据准备
# ============================================================================

# 日线数据
daily_df = pd.read_csv("/tmp/anker_daily.csv")
daily_df["trade_date"] = pd.to_datetime(daily_df["trade_date"], format="%Y%m%d")
daily_df = daily_df.sort_values("trade_date").reset_index(drop=True)

# --- 股价走势图数据 (月度) ---
daily_df["month"] = daily_df["trade_date"].dt.to_period("M")
monthly = daily_df.groupby("month").agg(
    close=("close", "last"),
    vol=("vol", "sum"),
    high=("high", "max"),
    low=("low", "min"),
).reset_index()
monthly["日期"] = monthly["month"].dt.to_timestamp()
monthly["收盘价"] = monthly["close"]
monthly["成交量(万手)"] = monthly["vol"] / 10000
price_df = monthly[["日期", "收盘价", "成交量(万手)"]].copy()

# --- 累计收益率 ---
start_price = daily_df["close"].iloc[0]
daily_df["累计收益率"] = (daily_df["close"] / start_price - 1)
# 同期创业板指（简化：用 pct_chg 模拟基准）
daily_df["基准累计"] = (1 + daily_df["pct_chg"] / 100 * 0.3).cumprod() - 1  # 模拟基准

monthly_ret = daily_df.groupby("month").agg(
    累计收益率=("累计收益率", "last"),
).reset_index()
monthly_ret["日期"] = monthly_ret["month"].dt.to_timestamp()
return_df = monthly_ret[["日期", "累计收益率"]].copy()

# --- 财务数据 ---
revenue_data = {
    "年度": ["2022", "2023", "2024"],
    "营业收入(亿元)": [142.51, 175.07, 247.10],
    "净利润(亿元)": [11.43, 16.15, 21.14],
}
revenue_df = pd.DataFrame(revenue_data)

margin_data = {
    "年度": ["2022", "2023", "2024"],
    "毛利率": [0.4354, 0.4354, 0.4367],
    "净利率": [0.0802, 0.0968, 0.0895],
    "ROE": [0.1800, 0.2176, 0.2494],
}
margin_df = pd.DataFrame(margin_data)

# --- 费用结构 ---
expense_data = {
    "年度": ["2022", "2023", "2024"],
    "销售费用率": [0.2062, 0.2220, 0.2254],
    "管理费用率": [0.0327, 0.0333, 0.0352],
    "研发费用率": [0.0758, 0.0808, 0.0853],
}
expense_df = pd.DataFrame(expense_data)

# ============================================================================
# 生成 PPT
# ============================================================================

composer = PageComposer(theme=THEME)

# ── Page 1: 标题页 ──
composer.add_page("title_dark", {
    "title": "安克创新 (300866.SZ)",
    "subtitle": "走势情况与竞争壁垒分析报告\n2026年2月",
})

# ── Page 2: 公司概览 ──
composer.add_page("kpi_cards", {
    "title": "公司概览 — 全球智能硬件领军企业",
    "cards": [
        {"label": "2024 营收", "value": "247.1亿", "change": "+41.1%"},
        {"label": "2024 净利润", "value": "21.1亿", "change": "+30.9%"},
        {"label": "ROE", "value": "24.9%", "change": "+3.2pct"},
        {"label": "研发投入", "value": "21.1亿", "change": "占收入8.5%"},
    ],
})

# ── Page 3: 业务矩阵 ──
composer.add_page("bullet_points", {
    "title": "三大品牌矩阵 — 从充电到智能生态",
    "items": [
        {
            "icon": "⚡",
            "label": "Anker 充电品牌",
            "desc": "全球充电行业领导者。首创 GaN 氮化镓快充技术，PowerIQ 全兼容快充协议。阳台光储新品类开创者。Amazon 充电品类长期 #1。",
        },
        {
            "icon": "🏠",
            "label": "eufy 智能家居",
            "desc": "HomeBase 本地存储基站安防方案，SolarPlus 太阳能永久续航。智能安防/扫地机/智能门锁全线布局。北美安防摄像头市占率 Top 3。",
        },
        {
            "icon": "🎧",
            "label": "soundcore 声阔",
            "desc": "ACAA 同轴圈铁声学架构，Liberty 系列 TWS 耳机。Space One 头戴降噪耳机全球畅销。真无线耳机全球出货量 Top 5。",
        },
    ],
})

# ── Page 4: 章节分隔 ──
composer.add_page("section_divider", {
    "title": "走势分析",
    "number": "01",
})

def _chart_title(slide, theme, title_text):
    """添加标题 + 装饰线（复用 chart 布局的模式）"""
    from pptfi.composer.helpers import add_text, add_rect
    m = theme["margin"]
    sw = 13.333
    add_text(slide, title_text,
             x=m, y=0.3, w=sw - 2 * m, h=0.5,
             font_size=theme["title_size"] - 2, color=theme["text_dark"],
             bold=True, font_name=theme["header_font"])
    add_rect(slide, m, 0.9, 2.0, 0.04, fill=theme["accent"])


# ── Page 5: 股价走势 ──
def render_price_chart(slide, theme):
    """股价走势 + 成交量"""
    _chart_title(slide, theme, "股价走势（2024.01 - 2026.02）")

    chart_style = StyleConfig(color_scheme="tech_blue", line_width_pt=2.0, marker_style="none")
    chart_layout = ChartLayoutConfig(
        title=None,
        legend_config=LegendConfig(position=LegendConfig.TOP, font_size_pt=9, font_name="黑体"),
        value_axis_config=ValueAxisConfig(number_format="#,##0.00", font_name="黑体", font_size_pt=9),
        secondary_value_axis_config=ValueAxisConfig(number_format="#,##0", font_name="黑体", font_size_pt=9),
        category_axis_config=CategoryAxisConfig(font_name="黑体", font_size_pt=9),
        date_axis_config=MONTHLY_TICKS,
    )
    series_config = [
        {"key": "成交量(万手)", "name": "成交量(万手)", "type": "bar", "axis": "secondary"},
        {"key": "收盘价", "name": "收盘价", "type": "line", "axis": "primary"},
    ]
    create_combo_chart(
        slide, price_df, categories_col="日期",
        series_config=series_config,
        style_config=chart_style,
        layout_config=chart_layout,
        position=(Inches(0.6), Inches(1.3)),
        size=(Inches(12.133), Inches(5.5)),
    )

composer.add_custom_page(render_price_chart)

# ── Page 6: 累计收益率 ──
def render_return_chart(slide, theme):
    _chart_title(slide, theme, "累计收益率（基期: 2024年1月）")

    chart_style = StyleConfig(color_scheme="tech_blue", line_width_pt=2.5, marker_style="none")
    chart_layout = ChartLayoutConfig(
        title=None,
        legend_config=LegendConfig(position=LegendConfig.TOP, font_size_pt=9, font_name="黑体"),
        value_axis_config=ValueAxisConfig(number_format="0%", font_name="黑体", font_size_pt=9),
        category_axis_config=CategoryAxisConfig(font_name="黑体", font_size_pt=9),
        date_axis_config=MONTHLY_TICKS,
    )
    series_config = [
        {"key": "累计收益率", "name": "累计收益率", "type": "area", "axis": "primary"},
    ]
    create_combo_chart(
        slide, return_df, categories_col="日期",
        series_config=series_config,
        style_config=chart_style,
        layout_config=chart_layout,
        position=(Inches(0.6), Inches(1.3)),
        size=(Inches(12.133), Inches(5.5)),
    )

composer.add_custom_page(render_return_chart)

# ── Page 7: 量化风险指标 ──
composer.add_page("kpi_cards", {
    "title": "量化风险指标（2024.01 - 2026.02）",
    "cards": [
        {"label": "累计收益率", "value": "+29.1%", "change": "年化 +13.6%"},
        {"label": "最大回撤", "value": "-48.6%", "change": "高波动"},
        {"label": "年化波动率", "value": "50.6%", "change": "高于市场"},
        {"label": "夏普比率", "value": "0.09", "change": "风险调整偏低"},
    ],
})

# ── Page 8: 章节分隔 ──
composer.add_page("section_divider", {
    "title": "财务分析",
    "number": "02",
})

# ── Page 9: 营收与利润 ──
def render_revenue_chart(slide, theme):
    _chart_title(slide, theme, "营收与净利润增长趋势（2022-2024）")

    chart_style = StyleConfig(color_scheme="tech_blue", line_width_pt=2.5, marker_style="circle")
    chart_layout = ChartLayoutConfig(
        title=None,
        legend_config=LegendConfig(position=LegendConfig.TOP, font_size_pt=9, font_name="黑体"),
        value_axis_config=ValueAxisConfig(number_format="#,##0.0", font_name="黑体", font_size_pt=9),
        secondary_value_axis_config=ValueAxisConfig(number_format="#,##0.0", font_name="黑体", font_size_pt=9),
    )
    series_config = [
        {"key": "营业收入(亿元)", "name": "营业收入(亿元)", "type": "bar", "axis": "primary"},
        {"key": "净利润(亿元)", "name": "净利润(亿元)", "type": "line", "axis": "secondary"},
    ]
    create_combo_chart(
        slide, revenue_df, categories_col="年度",
        series_config=series_config,
        style_config=chart_style,
        layout_config=chart_layout,
        position=(Inches(0.6), Inches(1.3)),
        size=(Inches(12.133), Inches(5.5)),
    )

composer.add_custom_page(render_revenue_chart)

# ── Page 10: 利润率趋势 ──
def render_margin_chart(slide, theme):
    _chart_title(slide, theme, "盈利能力指标趋势（2022-2024）")

    chart_style = StyleConfig(color_scheme="tech_blue", line_width_pt=2.5, marker_style="circle")
    chart_layout = ChartLayoutConfig(
        title=None,
        legend_config=LegendConfig(position=LegendConfig.TOP, font_size_pt=9, font_name="黑体"),
        value_axis_config=ValueAxisConfig(number_format="0%", font_name="黑体", font_size_pt=9),
    )
    series_config = [
        {"key": "毛利率", "name": "毛利率", "type": "line", "axis": "primary"},
        {"key": "净利率", "name": "净利率", "type": "line", "axis": "primary"},
        {"key": "ROE", "name": "ROE", "type": "line", "axis": "primary"},
    ]
    create_combo_chart(
        slide, margin_df, categories_col="年度",
        series_config=series_config,
        style_config=chart_style,
        layout_config=chart_layout,
        position=(Inches(0.6), Inches(1.3)),
        size=(Inches(12.133), Inches(5.5)),
    )

composer.add_custom_page(render_margin_chart)

# ── Page 11: 费用结构 ──
def render_expense_chart(slide, theme):
    _chart_title(slide, theme, "费用结构分析（2022-2024）")

    chart_style = StyleConfig(color_scheme="tech_blue", line_width_pt=2.5, marker_style="circle")
    chart_layout = ChartLayoutConfig(
        title=None,
        legend_config=LegendConfig(position=LegendConfig.TOP, font_size_pt=9, font_name="黑体"),
        value_axis_config=ValueAxisConfig(number_format="0.0%", font_name="黑体", font_size_pt=9),
    )
    series_config = [
        {"key": "销售费用率", "name": "销售费用率", "type": "bar", "axis": "primary"},
        {"key": "管理费用率", "name": "管理费用率", "type": "bar", "axis": "primary"},
        {"key": "研发费用率", "name": "研发费用率", "type": "bar", "axis": "primary"},
    ]
    create_combo_chart(
        slide, expense_df, categories_col="年度",
        series_config=series_config,
        style_config=chart_style,
        layout_config=chart_layout,
        position=(Inches(0.6), Inches(1.3)),
        size=(Inches(12.133), Inches(5.5)),
    )

composer.add_custom_page(render_expense_chart)

# ── Page 12: 章节分隔 ──
composer.add_page("section_divider", {
    "title": "竞争壁垒分析",
    "number": "03",
})

# ── Page 13: 竞争壁垒概览 ──
composer.add_page("kpi_cards", {
    "title": "安克创新五大竞争壁垒",
    "cards": [
        {"label": "品牌壁垒", "value": "Anker #1", "change": "Amazon Best Seller"},
        {"label": "技术壁垒", "value": "GaN 首创", "change": "研发21亿/年"},
        {"label": "渠道壁垒", "value": "DTC全球", "change": "140+国家"},
        {"label": "生态壁垒", "value": "3大品牌", "change": "交叉销售"},
    ],
})

# ── Page 14: 品牌壁垒 ──
composer.add_page("bullet_points", {
    "title": "壁垒一：品牌认知 — 全球消费电子信任标杆",
    "items": [
        {
            "icon": "🏆",
            "label": "Amazon 品类霸主",
            "desc": "Anker 连续 10 年蝉联 Amazon 充电品类 Best Seller。在美国、日本、欧洲主要市场的充电配件品类中，品牌搜索量远超竞争对手。消费者对 Anker 的品牌联想 = 安全 + 快充 + 高性价比。",
        },
        {
            "icon": "🌍",
            "label": "全球化品牌矩阵",
            "desc": "三大品牌覆盖不同消费场景：Anker（充电/储能）、eufy（智能家居/安防）、soundcore（音频）。每个品牌在各自垂直领域都进入全球 Top 5，形成了难以复制的多品牌协同效应。",
        },
        {
            "icon": "💎",
            "label": "品牌溢价能力",
            "desc": "毛利率稳定在 43-44%，远高于白牌充电配件（15-20%）。品牌认知带来的定价权是最核心的利润来源，竞争对手即使模仿技术也无法复制品牌信任。",
        },
    ],
})

# ── Page 15: 技术壁垒 ──
composer.add_page("bullet_points", {
    "title": "壁垒二：技术创新 — 研发驱动的品类开创者",
    "items": [
        {
            "icon": "🔬",
            "label": "持续高研发投入",
            "desc": "2024 年研发支出 21.1 亿元，占营收 8.5%。研发团队超 2000 人，在深圳、长沙、日本、美国设有研发中心。累计专利超 3000 项。",
        },
        {
            "icon": "⚡",
            "label": "品类定义级技术突破",
            "desc": "首次将 GaN（氮化镓）应用于消费电子充电器，开启全球快充新时代。PowerIQ 智能充电协议、HomeBase 本地安防基站、ACAA 同轴圈铁——每个品牌都有标志性技术。",
        },
        {
            "icon": "🌱",
            "label": "技术→品类→市场 闭环",
            "desc": "安克不仅做技术追随者，更是品类开创者。阳台光储（Anker SOLIX）是最新案例——用充电技术积累切入家庭能源赛道，2024 年已成为欧洲阳台光储增长最快品牌。",
        },
    ],
})

# ── Page 16: 渠道壁垒 ──
composer.add_page("bullet_points", {
    "title": "壁垒三：全球渠道网络 — DTC + 平台双轮驱动",
    "items": [
        {
            "icon": "🛒",
            "label": "深度绑定全球电商平台",
            "desc": "Amazon（美/欧/日）、独立站 anker.com、Shopee/Lazada（东南亚）全覆盖。电商渠道占比超 70%，积累了千万级用户评价数据，形成飞轮效应——高评分→高排名→高销量→更多评价。",
        },
        {
            "icon": "🏪",
            "label": "线下渗透加速",
            "desc": "沃尔玛、百思买、Target 等北美 4 万+ 零售终端。日本、欧洲线下渠道同步扩张。线下渠道占比从 2022 年的 15% 提升至 2024 年约 25%，打开增量空间。",
        },
        {
            "icon": "📦",
            "label": "供应链效率",
            "desc": "深圳制造基地 + 全球多地仓储物流网络。从设计→生产→分销的垂直整合能力，保证了快速上新和成本控制。2024 年存货周转天数约 96 天，处于行业优秀水平。",
        },
    ],
})

# ── Page 17: 对比分析 ──
composer.add_page("comparison_table", {
    "title": "竞争格局 — 安克 vs 同行关键指标（2024）",
    "headers": ["指标", "安克创新", "公牛集团", "传音控股"],
    "rows": [
        ["营收（亿元）", "247.1", "161.4", "655.8"],
        ["净利润（亿元）", "21.1", "40.5", "55.3"],
        ["毛利率", "43.7%", "37.2%", "25.1%"],
        ["净利率", "8.9%", "25.1%", "8.4%"],
        ["ROE", "24.9%", "28.3%", "22.1%"],
        ["研发费用率", "8.5%", "4.2%", "3.1%"],
        ["海外收入占比", ">95%", "<5%", ">95%"],
        ["销售费用率", "22.5%", "5.8%", "7.2%"],
    ],
})

# ── Page 18: 结论页 ──
composer.add_page("conclusion_dark", {
    "title": "投资要点总结",
    "verdict": "品牌 + 技术 + 渠道 三位一体的全球消费电子稀缺标的",
    "items": [
        {"label": "增长驱动", "value": "阳台光储+智能安防\n第二增长曲线"},
        {"label": "核心风险", "value": "销售费用率22%\n汇率+平台依赖"},
        {"label": "估值参考", "value": "股价98.69元\n2024 PE≈25x"},
    ],
    "risk": "以上分析基于公开信息，不构成投资建议",
})

# ── 保存 ──
output_path = OUTPUT_DIR / "安克创新_走势与竞争壁垒分析.pptx"
composer.save(str(output_path))
print(f"报告已生成: {output_path}", file=sys.stderr)
print(f"共 {len(composer.prs.slides)} 页", file=sys.stderr)
