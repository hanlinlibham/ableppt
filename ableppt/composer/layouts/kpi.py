"""KPI 卡片布局 — 投行级克制风格"""

from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from ..helpers import set_slide_bg, add_text, add_rounded_rect, add_rect, add_page_header, setup_content_page


def layout_kpi_cards(slide, data, theme):
    """KPI 大数字卡片 — 3~6 个指标，分栏+极浅分割线

    data keys:
        title (str): 页面标题
        subtitle (str, optional): 副标题/说明
        cards (list[dict]): 每个 card 包含:
            label (str): 指标名
            value (str): 数值（已格式化）
            change (str, optional): 变化（如 "+5.9%"）
            note (str, optional): 脚注
        footnote (str, optional): 数据来源/脚注（auto-footer 渲染）
    """
    m, sw, content_y, content_w, footer_y = setup_content_page(slide, data, theme)

    if data.get("subtitle"):
        add_text(slide, data["subtitle"],
                 x=m, y=content_y, w=content_w, h=0.3,
                 font_size=theme["body_size"], color=theme["text_muted"],
                 font_name=theme["body_font"])

    cards = data["cards"]
    n = len(cards)

    # 自动 2x3 网格（6 卡时）或单行
    if n <= 4:
        _render_row(slide, cards, theme, m, sw, content_y + 0.5, footer_y)
    else:
        # 2x3 网格
        row1 = cards[:3]
        row2 = cards[3:]
        mid_y = content_y + 0.5
        row_h = (footer_y - mid_y - 0.3) / 2
        _render_row(slide, row1, theme, m, sw, mid_y, mid_y + row_h)
        _render_row(slide, row2, theme, m, sw, mid_y + row_h + 0.15, footer_y - 0.15)


def _render_row(slide, cards, theme, m, sw, start_y, end_y):
    """渲染一行 KPI 卡片 — 分栏+极浅分割线，无阴影/圆角"""
    n = len(cards)
    content_w = sw - 2 * m
    col_w = content_w / n
    card_h = end_y - start_y - 0.2

    # KPI 字号: 收敛到 28-32pt（原 44pt 太 SaaS 感）
    kpi_num_size = min(theme.get("kpi_size", 44), 32)
    change_size = min(theme["body_size"], 11)

    for i, card in enumerate(cards):
        cx = m + i * col_w

        # 分割线（第一栏不画左边线）
        if i > 0:
            add_rect(slide, cx, start_y + 0.2, 0.008, card_h - 0.4,
                     fill=theme["border"])

        # 指标名 — 小字、顶部
        add_text(slide, card["label"],
                 x=cx + 0.25, y=start_y + 0.15, w=col_w - 0.5, h=0.35,
                 font_size=theme["body_size"], color=theme["text_muted"],
                 align="left", font_name=theme["body_font"])

        # 大数字 — 28-32pt，克制
        add_text(slide, card["value"],
                 x=cx + 0.25, y=start_y + 0.55, w=col_w - 0.5, h=1.0,
                 font_size=kpi_num_size, color=theme["primary"],
                 bold=True, align="left", valign="middle",
                 font_name=theme["header_font"])

        # 变化值 — 10-12pt + 次要色
        if card.get("change"):
            change = card["change"]
            is_positive = change.startswith("+") or (not change.startswith("-") and "%" in change)
            color = theme["positive"] if is_positive else theme["negative"]
            add_text(slide, change,
                     x=cx + 0.25, y=start_y + 1.6, w=col_w - 0.5, h=0.3,
                     font_size=change_size, color=color,
                     font_name=theme["body_font"])

        # 脚注
        if card.get("note"):
            add_text(slide, card["note"],
                     x=cx + 0.25, y=start_y + 2.0, w=col_w - 0.5, h=0.5,
                     font_size=theme.get("footer_size", 8), color=theme["text_muted"],
                     font_name=theme["body_font"])
