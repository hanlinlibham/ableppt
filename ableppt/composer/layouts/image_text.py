"""图片+文字布局 — 左右分栏，图片侧支持本地路径/URL/base64"""

from ..helpers import (set_slide_bg, add_text, add_rect, add_picture,
                       add_page_header)


def layout_image_text(slide, data, theme):
    """图片+文字（左右可切换）

    data keys:
        title (str): 页面标题
        image_side (str): "left" 或 "right"，默认 "left"
        image_path (str|None): 图片来源（本地路径/URL/base64），None 则用色块
        image_sizing (str): "cover"/"contain"/"stretch"，默认 "cover"
        image_fill_color (str): image_path=None 时色块颜色变量名，默认 "bg_dark"
        image_number (str|None): 大数字（如 "380亿"），可选
        image_number_label (str|None): 数字标签（如 "资产规模"），可选
        tag (str|None): 小标签文字（如 "团队介绍"），可选
        text_title (str): 副标题
        text_body (str): 正文段落
        bullets (list[str]|None): 要点列表，可选
        footnote (str|None): 底部小注，可选
        split_ratio (float): 图片区占内容宽比例，默认 0.50
    """
    m = theme["margin"]
    sw = theme.get("slide_w", 13.333)
    sh = theme.get("slide_h", 7.5)
    cw = sw - 2 * m

    # 背景 + 页面标题
    set_slide_bg(slide, theme["bg_light"])
    add_page_header(slide, data["title"], theme)

    # 装饰线
    add_rect(slide, m, 0.90, 2.0, 0.04, fill=theme["accent"])

    # 左右分栏计算
    ratio = data.get("split_ratio", 0.50)
    inner_gap = 0.40
    img_w = cw * ratio - inner_gap
    txt_w = cw * (1 - ratio) - inner_gap
    area_y = 1.10
    area_h = sh - area_y - 0.40

    img_side = data.get("image_side", "left")
    if img_side == "left":
        img_x = m
        txt_x = m + img_w + inner_gap * 2
    else:
        txt_x = m
        img_x = m + txt_w + inner_gap * 2

    # ── 图片区 ──
    if data.get("image_path"):
        sizing = data.get("image_sizing", "cover")
        add_picture(slide, data["image_path"],
                    img_x, area_y, img_w, area_h,
                    sizing=sizing)
    else:
        img_color = theme.get(
            data.get("image_fill_color", "bg_dark"), theme["bg_dark"])
        add_rect(slide, img_x, area_y, img_w, area_h, fill=img_color)

        if data.get("image_number"):
            add_text(slide, data["image_number"],
                     x=img_x, y=area_y + 1.50, w=img_w, h=1.50,
                     font_size=72, color=theme["accent"],
                     bold=True, align="center",
                     font_name=theme["header_font"])

        if data.get("image_number_label"):
            add_text(slide, data["image_number_label"],
                     x=img_x, y=area_y + 3.10, w=img_w, h=0.50,
                     font_size=theme["body_size"] + 2,
                     color=theme.get("text_light", "FFFFFF"),
                     align="center", font_name=theme["body_font"])

    # ── 文字区 ──
    ty = area_y

    if data.get("tag"):
        add_text(slide, data["tag"],
                 x=txt_x, y=ty, w=txt_w, h=0.35,
                 font_size=theme.get("caption_size", 10),
                 color=theme["accent"],
                 font_name=theme["body_font"])
        ty += 0.40

    if data.get("text_title"):
        add_text(slide, data["text_title"],
                 x=txt_x, y=ty, w=txt_w, h=0.65,
                 font_size=theme["subtitle_size"],
                 color=theme["text_dark"],
                 bold=True, font_name=theme["header_font"])
        ty += 0.70
        add_rect(slide, txt_x, ty, 1.50, 0.04, fill=theme["accent"])
        ty += 0.15

    if data.get("text_body"):
        add_text(slide, data["text_body"],
                 x=txt_x, y=ty, w=txt_w, h=2.20,
                 font_size=theme["body_size"],
                 color=theme["text_dark"],
                 font_name=theme["body_font"])
        ty += 2.30

    if data.get("bullets"):
        for bullet in data["bullets"]:
            add_rect(slide, txt_x, ty + 0.12, 0.08, 0.08,
                     fill=theme["accent"])
            add_text(slide, bullet,
                     x=txt_x + 0.20, y=ty, w=txt_w - 0.20, h=0.45,
                     font_size=theme["body_size"],
                     color=theme["text_dark"],
                     font_name=theme["body_font"])
            ty += 0.50

    if data.get("footnote"):
        add_text(slide, data["footnote"],
                 x=txt_x, y=area_y + area_h - 0.40, w=txt_w, h=0.40,
                 font_size=theme.get("caption_size", 10),
                 color=theme["text_muted"],
                 font_name=theme["body_font"])
