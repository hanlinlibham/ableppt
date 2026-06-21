"""内容型布局 — 要点列表、章节分隔"""

from pptx.util import Inches
from pptx.enum.shapes import MSO_SHAPE
from ..helpers import (set_slide_bg, add_text, add_rect, add_rounded_rect,
                       add_rich_text, add_shape, add_page_header, setup_content_page)


def layout_bullet_points(slide, data, theme):
    """带图标/标记的要点列表 — 3~5 条要点，每条含标题+描述

    data keys:
        title (str): 页面标题
        subtitle (str, optional): 副标题
        items (list[dict]): 每项包含:
            icon (str): 图标文字（如 "01", 图标字符）
            label (str): 要点标题
            desc (str): 要点描述
            color (str, optional): 图标颜色 hex
        footnote (str, optional): 数据来源/脚注（auto-footer 渲染）
    """
    m, sw, content_y, content_w, footer_y = setup_content_page(slide, data, theme)

    items = data["items"]
    n = len(items)

    # 两列布局（>3 条时）或单列
    if n <= 3:
        _render_single_column(slide, items, theme, m, sw, content_y)
    else:
        _render_two_columns(slide, items, theme, m, sw, content_y)


def _render_single_column(slide, items, theme, m, sw, start_y):
    """单列布局"""
    item_h = 1.3
    footer_y = theme.get("footer_y", 7.10)
    # 自动调整间距
    n = len(items)
    avail = footer_y - start_y - 0.3
    gap = min(0.15, (avail - n * item_h) / max(n - 1, 1))

    for i, item in enumerate(items):
        y = start_y + i * (item_h + gap)
        icon_color = item.get("color", theme["primary"])

        # 图标圆圈
        add_shape(slide, MSO_SHAPE.OVAL,
                  m + 0.1, y + 0.1, 0.7, 0.7,
                  fill=icon_color)

        # 图标文字
        add_text(slide, item["icon"],
                 x=m + 0.1, y=y + 0.1, w=0.7, h=0.7,
                 font_size=14, color="FFFFFF", bold=True,
                 align="center", valign="middle",
                 font_name=theme["body_font"])

        # 标题
        add_text(slide, item["label"],
                 x=m + 1.1, y=y + 0.05, w=sw - 2 * m - 1.3, h=0.4,
                 font_size=theme["subtitle_size"] - 2, color=theme["text_dark"],
                 bold=True, font_name=theme["header_font"])

        # 描述
        add_text(slide, item["desc"],
                 x=m + 1.1, y=y + 0.5, w=sw - 2 * m - 1.3, h=0.75,
                 font_size=theme["body_size"], color=theme["text_muted"],
                 font_name=theme["body_font"])


def _render_two_columns(slide, items, theme, m, sw, start_y):
    """双列布局"""
    col_w = (sw - 2 * m - 0.5) / 2
    item_h = 1.2

    for i, item in enumerate(items):
        col = i % 2
        row = i // 2
        x_base = m + col * (col_w + 0.5)
        y = start_y + row * (item_h + 0.15)

        icon_color = item.get("color", theme["primary"])

        # 图标圆圈
        add_shape(slide, MSO_SHAPE.OVAL,
                  x_base + 0.1, y + 0.1, 0.6, 0.6,
                  fill=icon_color)

        add_text(slide, item["icon"],
                 x=x_base + 0.1, y=y + 0.1, w=0.6, h=0.6,
                 font_size=12, color="FFFFFF", bold=True,
                 align="center", valign="middle",
                 font_name=theme["body_font"])

        # 标题
        add_text(slide, item["label"],
                 x=x_base + 0.9, y=y + 0.0, w=col_w - 1.1, h=0.35,
                 font_size=theme["subtitle_size"] - 4, color=theme["text_dark"],
                 bold=True, font_name=theme["header_font"])

        # 描述
        add_text(slide, item["desc"],
                 x=x_base + 0.9, y=y + 0.4, w=col_w - 1.1, h=0.7,
                 font_size=theme["body_size"] - 1, color=theme["text_muted"],
                 font_name=theme["body_font"])


def layout_section_divider(slide, data, theme):
    """章节分隔页 — 大序号 + 章节标题

    data keys:
        number (str): 序号 (如 "01", "02")
        title (str): 章节标题
        subtitle (str, optional): 章节副标题
    """
    m = theme["margin"]
    sw = theme.get("slide_w", 13.333)
    sh = theme.get("slide_h", 7.5)

    set_slide_bg(slide, theme["bg_light"])

    # 左侧深色块（比例化）
    block_w = sw * 0.375
    add_rect(slide, 0, 0, block_w, sh, fill=theme["primary"])

    # 大序号
    add_text(slide, data["number"],
             x=0.5, y=1.5, w=block_w - 1.0, h=3.0,
             font_size=96, color=theme["accent"],
             bold=True, align="center", valign="middle",
             font_name=theme["header_font"])

    # 右侧标题
    right_x = block_w + 0.8
    right_w = sw - right_x - m
    cover_title_size = theme.get("cover_title_size", 36)
    add_text(slide, data["title"],
             x=right_x, y=2.5, w=right_w, h=1.5,
             font_size=cover_title_size - 4, color=theme["text_dark"],
             bold=True, font_name=theme["header_font"])

    if data.get("subtitle"):
        add_text(slide, data["subtitle"],
                 x=right_x, y=4.2, w=right_w, h=0.8,
                 font_size=theme["subtitle_size"], color=theme["text_muted"],
                 font_name=theme["body_font"])
