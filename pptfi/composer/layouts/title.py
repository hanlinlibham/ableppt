"""标题页布局"""

from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from ..helpers import set_slide_bg, add_text, add_line, add_rect


def layout_title_dark(slide, data, theme):
    """深色标题页 — 大标题 + 副标题 + 日期 + 底部装饰线

    data keys:
        title (str): 主标题
        subtitle (str, optional): 副标题
        date (str, optional): 日期
        author (str, optional): 作者
    """
    m = theme["margin"]
    sw = theme.get("slide_w", 13.333)
    sh = theme.get("slide_h", 7.5)
    cover_title_size = theme.get("cover_title_size", 36)

    # 深色背景
    set_slide_bg(slide, theme["bg_dark"])

    # 顶部装饰线
    add_rect(slide, 0, 0, sw, 0.06, fill=theme["accent"])

    # 主标题
    add_text(slide, data["title"],
             x=m, y=2.2, w=sw - 2 * m, h=1.8,
             font_size=cover_title_size, color=theme["text_light"],
             bold=True, align="center", valign="middle",
             font_name=theme["header_font"])

    # 副标题
    if data.get("subtitle"):
        add_text(slide, data["subtitle"],
                 x=m, y=4.2, w=sw - 2 * m, h=0.8,
                 font_size=theme["subtitle_size"], color=theme["secondary"],
                 align="center", font_name=theme["body_font"])

    # 底部信息栏
    bottom_parts = []
    if data.get("author"):
        bottom_parts.append(data["author"])
    if data.get("date"):
        bottom_parts.append(data["date"])
    if bottom_parts:
        footer_size = theme.get("footer_size", 8)
        add_text(slide, "  |  ".join(bottom_parts),
                 x=m, y=sh - 1.2, w=sw - 2 * m, h=0.5,
                 font_size=footer_size + 2, color=theme["text_muted"],
                 align="center", font_name=theme["body_font"])

    # 底部装饰线
    add_rect(slide, 0, sh - 0.06, sw, 0.06, fill=theme["accent"])


def layout_title_light(slide, data, theme):
    """浅色标题页 — 左侧色块 + 右侧标题

    data keys:
        title (str): 主标题
        subtitle (str, optional): 副标题
        date (str, optional): 日期
    """
    m = theme["margin"]
    sw = theme.get("slide_w", 13.333)
    sh = theme.get("slide_h", 7.5)
    cover_title_size = theme.get("cover_title_size", 36)

    set_slide_bg(slide, theme["bg_light"])

    # 左侧色块（比例化）
    block_w = sw * 0.34
    add_rect(slide, 0, 0, block_w, sh, fill=theme["primary"])

    # 左侧标题（白色）
    add_text(slide, data["title"],
             x=0.5, y=2.5, w=block_w - 1.0, h=2.5,
             font_size=cover_title_size - 8, color=theme["text_light"],
             bold=True, align="left", font_name=theme["header_font"])

    # 右侧副标题
    right_x = block_w + 1.0
    right_w = sw - right_x - m
    if data.get("subtitle"):
        add_text(slide, data["subtitle"],
                 x=right_x, y=2.8, w=right_w, h=1.5,
                 font_size=theme["subtitle_size"], color=theme["text_dark"],
                 align="left", font_name=theme["body_font"])

    # 日期
    if data.get("date"):
        footer_size = theme.get("footer_size", 8)
        add_text(slide, data["date"],
                 x=right_x, y=4.5, w=right_w, h=0.5,
                 font_size=footer_size + 2, color=theme["text_muted"],
                 align="left", font_name=theme["body_font"])
