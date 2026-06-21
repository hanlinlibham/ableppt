"""结论页布局 — 投行级左右分栏"""

from pptx.util import Inches
from pptx.enum.shapes import MSO_SHAPE
from ..helpers import set_slide_bg, add_text, add_rect, add_rounded_rect


def layout_conclusion_dark(slide, data, theme):
    """深色结论页 — 左侧结论 + 右侧风险/指标卡片

    data keys:
        title (str, optional): 标题，默认 "结论"
        verdict (str): 核心结论
        score (str, optional): 评分（如 "7/10"）
        items (list[dict], optional): 摘要要点 [{label, value}]
        risk (str, optional): 风险提示
        footnote (str, optional): 脚注
    """
    m = theme["margin"]
    sw = theme.get("slide_w", 13.333)
    sh = theme.get("slide_h", 7.5)
    cover_title_size = theme.get("cover_title_size", 36)

    set_slide_bg(slide, theme["bg_dark"])

    # 顶部装饰线
    add_rect(slide, 0, 0, sw, 0.06, fill=theme["accent"])

    # 标题
    title = data.get("title", "结论")
    page_title_size = theme.get("page_title_size", 16)
    add_text(slide, title,
             x=m, y=0.3, w=sw - 2 * m, h=0.5,
             font_size=page_title_size, color=theme["text_light"],
             bold=True, font_name=theme["header_font"])

    # 分隔线
    add_rect(slide, m, 0.85, sw - 2 * m, theme.get("divider_h", 0.015),
             fill=theme["primary"])

    items = data.get("items", [])
    has_right = bool(items) or data.get("risk")

    if has_right:
        # 左右分栏模式
        left_w = (sw - 2 * m) * 0.55
        right_x = m + left_w + 0.4
        right_w = sw - right_x - m
    else:
        left_w = sw - 2 * m
        right_x = 0
        right_w = 0

    # ── 左侧: 核心结论 ──
    # 评分（如有）
    verdict_y = 1.2
    if data.get("score"):
        add_text(slide, data["score"],
                 x=m, y=verdict_y, w=left_w, h=0.8,
                 font_size=cover_title_size, color=theme["accent"],
                 bold=True, align="left",
                 font_name=theme["header_font"])
        verdict_y += 1.0

    # 核心结论
    add_text(slide, data["verdict"],
             x=m + 0.1, y=verdict_y, w=left_w - 0.2, h=1.8,
             font_size=theme["subtitle_size"] + 2, color=theme["text_light"],
             bold=True, align="left", valign="top",
             font_name=theme["header_font"])

    # 左侧下方: 3 条结论要点（如果 data 提供了 conclusions 列表）
    conclusions = data.get("conclusions", [])
    if conclusions:
        cy = verdict_y + 2.2
        for i, c in enumerate(conclusions[:3]):
            # 小色块标记
            add_rect(slide, m + 0.1, cy + 0.08, 0.25, 0.04, fill=theme["accent"])
            # 粗体标题
            c_title = c.get("title", c) if isinstance(c, dict) else str(c)
            add_text(slide, c_title,
                     x=m + 0.5, y=cy - 0.05, w=left_w - 0.7, h=0.35,
                     font_size=theme["body_size"], color=theme["text_light"],
                     bold=True, font_name=theme["header_font"])
            # 解释行
            c_desc = c.get("desc", "") if isinstance(c, dict) else ""
            if c_desc:
                add_text(slide, c_desc,
                         x=m + 0.5, y=cy + 0.3, w=left_w - 0.7, h=0.3,
                         font_size=theme["body_size"] - 1, color=theme["text_muted"],
                         font_name=theme["body_font"])
                cy += 0.8
            else:
                cy += 0.5

    # ── 右侧: 指标卡片 + 风险 ──
    if has_right:
        card_y = 1.2
        if items:
            for i, item in enumerate(items):
                # 极简卡片: 半透明背景
                add_rect(slide, right_x, card_y, right_w, 0.9,
                         fill=theme["primary"], line_color=theme["border"],
                         line_width=0.5)
                # 短横线装饰
                add_rect(slide, right_x + 0.15, card_y + 0.12, 0.2, 0.03,
                         fill=theme["accent"])
                add_text(slide, item["label"],
                         x=right_x + 0.15, y=card_y + 0.2, w=right_w - 0.3, h=0.25,
                         font_size=theme.get("footer_size", 8) + 1, color=theme["text_muted"],
                         font_name=theme["body_font"])
                add_text(slide, item["value"],
                         x=right_x + 0.15, y=card_y + 0.48, w=right_w - 0.3, h=0.35,
                         font_size=theme["body_size"] + 1, color=theme["text_light"],
                         bold=True, font_name=theme["header_font"])
                card_y += 1.05

        # 风险提示
        if data.get("risk"):
            risk_y = max(card_y + 0.2, 5.5)
            add_rect(slide, right_x, risk_y, right_w, 0.04, fill=theme["negative"])
            add_text(slide, f"Risk: {data['risk']}",
                     x=right_x, y=risk_y + 0.1, w=right_w, h=0.8,
                     font_size=theme.get("footer_size", 8) + 1, color=theme["text_muted"],
                     italic=True, font_name=theme["body_font"])

    # 脚注
    if data.get("footnote"):
        add_text(slide, data["footnote"],
                 x=m, y=6.9, w=sw - 2 * m, h=0.25,
                 font_size=theme.get("footer_size", 8), color=theme["text_muted"],
                 align="center", font_name=theme["body_font"])

    # 底部装饰线
    add_rect(slide, 0, sh - 0.06, sw, 0.06, fill=theme["accent"])
