"""GTM 页面布局族 — 提炼自 J.P. Morgan《Guide to the Markets》的页面骨架。

页面构成（对应 GTM 原版）：
- 左上角蓝色箭头 + 页标题（20pt 左对齐）+ 全宽细分隔线
- 右上角页签：[GTM | 市场 | 页码] 三格框
- 左侧竖向章节签（按章节配色，白字竖排）
- 1 / 2 / 1+2 三种面板编排；面板 = 粗体小标题 + 灰色单位行 + pptchartengine 图表
- 面板内可叠加迷你数据表（GTM 的 Avg/2Q25 小表，行文字可按系列着色）
- 底部来源行（7.5pt 灰）+ 右下品牌字 + 左下页码

面板里的 ``chart`` 字段就是 pptchartengine 的声明式 spec（data 支持内联
dict / CSV 路径 / DataFrame），模型只需产出一个 job JSON 即可编排整页。
"""

from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

from ..helpers import add_line, add_text

# GTM 页面几何（16:9，13.333 × 7.5 英寸）
_MARGIN_L = 0.85
_MARGIN_R = 0.45
_TITLE_Y = 0.38
_RULE_Y = 0.96
_CONTENT_TOP = 1.18
_CONTENT_BOTTOM = 6.82
_FOOTER_Y = 6.98
_GAP = 0.42          # 双栏面板间距
_DIVIDER_X_FRACTION = 0.495

# 章节签配色（GTM：每章一色）
SECTION_COLORS = {
    "宏观": "00A0DF", "经济": "00A0DF", "local": "00A0DF",
    "全球": "0072CE", "global": "0072CE",
    "权益": "7F9C3D", "equities": "7F9C3D",
    "固收": "C9A84C", "fixed income": "C9A84C",
    "另类": "7B5EA7", "alternatives": "7B5EA7",
    "资产配置": "1F3864", "principles": "1F3864",
}

ACCENT = "00A0DF"
TITLE_COLOR = "1A1A1A"
PANEL_TITLE_COLOR = "1A1A1A"
PANEL_SUB_COLOR = "595959"
SOURCE_COLOR = "7F7F7F"
FONT = "微软雅黑"


def layout_gtm_panels(slide, data, theme):
    """GTM 面板页。

    data keys:
        title (str): 页标题
        section (str, optional): 章节名（决定左侧竖签文字与颜色）
        section_color (str, optional): 覆盖章节色
        tag (str, optional): 角标市场代码，默认 "GTM"
        page_num (int/str, optional): 角标页码
        panels (list[dict]): 1~3 个面板
            {title, subtitle, chart: <pptchartengine spec>, table: {...}}
            3 个面板时第 1 个占左半全高，2/3 在右侧上下排
        source (str, optional): 底部来源行
        brand (str, optional): 右下品牌字
    """
    _draw_chrome(slide, data, theme)

    panels = data.get("panels") or []
    rects = _panel_rects(len(panels))
    if len(panels) >= 2:
        _draw_divider(slide)

    for panel, rect in zip(panels, rects):
        _render_panel(slide, panel, rect, theme)


# ============================================================================
# 页面骨架
# ============================================================================

def _draw_chrome(slide, data, theme):
    sw = 13.333

    # 蓝色箭头标
    chevron = slide.shapes.add_shape(
        MSO_SHAPE.CHEVRON, Inches(0.22), Inches(_TITLE_Y + 0.07), Inches(0.42), Inches(0.30))
    chevron.fill.solid()
    chevron.fill.fore_color.rgb = RGBColor.from_string(ACCENT)
    chevron.line.fill.background()
    chevron.shadow.inherit = False

    # 页标题
    add_text(slide, str(data.get("title", "")),
             x=_MARGIN_L, y=_TITLE_Y, w=sw - 4.0, h=0.5,
             font_size=20, font_name=FONT, color=TITLE_COLOR, bold=True)

    # 全宽细分隔线
    add_line(slide, _MARGIN_L, _RULE_Y, sw - _MARGIN_L - _MARGIN_R, color="404040", width=1)

    # 右上角页签 [GTM | 市场 | 页码]
    cells = [str(data.get("tag", "GTM"))]
    if data.get("market"):
        cells.append(str(data["market"]))
    if data.get("page_num") is not None:
        cells.append(str(data["page_num"]))
    _draw_tag_boxes(slide, cells, right=sw - _MARGIN_R, y=_TITLE_Y + 0.06)

    # 左侧竖向章节签
    section = data.get("section")
    if section:
        color = (data.get("section_color")
                 or SECTION_COLORS.get(str(section).lower())
                 or SECTION_COLORS.get(str(section))
                 or ACCENT)
        _draw_section_tab(slide, str(section), color)

    # 底部来源行 + 品牌 + 页码
    if data.get("source"):
        add_text(slide, str(data["source"]),
                 x=_MARGIN_L, y=_FOOTER_Y, w=8.6, h=0.42,
                 font_size=7.5, font_name=FONT, color=SOURCE_COLOR)
    if data.get("brand"):
        add_text(slide, str(data["brand"]),
                 x=sw - 3.6, y=_FOOTER_Y, w=3.1, h=0.34,
                 font_size=13, font_name=FONT, color="1A1A1A", bold=True, align="right")
    if data.get("page_num") is not None:
        add_text(slide, str(data["page_num"]),
                 x=0.22, y=7.08, w=0.5, h=0.3,
                 font_size=10, font_name=FONT, color="595959")


def _draw_tag_boxes(slide, cells, *, right, y):
    box_h = 0.30
    widths = [max(0.52, 0.16 + 0.105 * len(c)) for c in cells]
    x = right - sum(widths)
    for text, w in zip(cells, widths):
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE if text == cells[0] else MSO_SHAPE.RECTANGLE,
            Inches(x), Inches(y), Inches(w), Inches(box_h))
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor.from_string("FFFFFF")
        shape.line.color.rgb = RGBColor.from_string("404040")
        shape.line.width = Pt(0.75)
        shape.shadow.inherit = False
        tf = shape.text_frame
        tf.text = text
        tf.word_wrap = False
        para = tf.paragraphs[0]
        para.alignment = PP_ALIGN.CENTER
        run = para.runs[0]
        run.font.size = Pt(10)
        run.font.name = FONT
        run.font.bold = True
        run.font.color.rgb = RGBColor.from_string("1A1A1A")
        x += w


def _draw_section_tab(slide, text, color):
    w, h = 0.34, max(1.1, 0.32 + 0.21 * len(text))
    tab = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.18), Inches(_CONTENT_TOP + 0.25), Inches(w), Inches(h))
    tab.fill.solid()
    tab.fill.fore_color.rgb = RGBColor.from_string(color)
    tab.line.fill.background()
    tab.shadow.inherit = False
    tab.rotation = 0
    tf = tab.text_frame
    tf.word_wrap = False
    tf.text = "\n".join(text)  # 中文逐字竖排
    for para in tf.paragraphs:
        para.alignment = PP_ALIGN.CENTER
        for run in para.runs:
            run.font.size = Pt(10)
            run.font.name = FONT
            run.font.bold = True
            run.font.color.rgb = RGBColor.from_string("FFFFFF")


def _draw_divider(slide):
    x = _MARGIN_L + (13.333 - _MARGIN_L - _MARGIN_R) * _DIVIDER_X_FRACTION
    line = slide.shapes.add_connector(1, Inches(x), Inches(_CONTENT_TOP),
                                      Inches(x), Inches(_CONTENT_BOTTOM))
    line.line.color.rgb = RGBColor.from_string("BFBFBF")
    line.line.width = Pt(0.75)
    line.shadow.inherit = False


# ============================================================================
# 面板
# ============================================================================

def _panel_rects(n):
    """返回 n 个面板的 (x, y, w, h)。"""
    full_w = 13.333 - _MARGIN_L - _MARGIN_R
    full_h = _CONTENT_BOTTOM - _CONTENT_TOP
    half_w = full_w * _DIVIDER_X_FRACTION - _GAP / 2
    right_x = _MARGIN_L + full_w * _DIVIDER_X_FRACTION + _GAP / 2
    right_w = full_w - full_w * _DIVIDER_X_FRACTION - _GAP / 2

    if n <= 1:
        return [(_MARGIN_L, _CONTENT_TOP, full_w, full_h)]
    if n == 2:
        return [
            (_MARGIN_L, _CONTENT_TOP, half_w, full_h),
            (right_x, _CONTENT_TOP, right_w, full_h),
        ]
    half_h = (full_h - 0.30) / 2
    return [
        (_MARGIN_L, _CONTENT_TOP, half_w, full_h),
        (right_x, _CONTENT_TOP, right_w, half_h),
        (right_x, _CONTENT_TOP + half_h + 0.30, right_w, half_h),
    ]


def _render_panel(slide, panel, rect, theme):
    from pptchartengine import render_chart

    x, y, w, h = rect
    cursor = y

    if panel.get("title"):
        add_text(slide, str(panel["title"]), x=x, y=cursor, w=w, h=0.28,
                 font_size=12, font_name=FONT, color=PANEL_TITLE_COLOR, bold=True)
        cursor += 0.28
    if panel.get("subtitle"):
        add_text(slide, str(panel["subtitle"]), x=x, y=cursor, w=w, h=0.22,
                 font_size=9.5, font_name=FONT, color=PANEL_SUB_COLOR)
        cursor += 0.24

    chart_spec = panel.get("chart")
    if chart_spec:
        spec = dict(chart_spec)
        # 面板标题由页面层渲染，图表内不再重复
        spec.pop("title", None)
        spec.pop("subtitle", None)
        spec["position"] = [x, cursor]
        spec["chart_size"] = [w, y + h - cursor]
        render_chart(slide, spec)

    table = panel.get("table")
    if table:
        _render_mini_table(slide, table, rect=(x, cursor, w, y + h - cursor))


def _render_mini_table(slide, table, *, rect):
    """面板内迷你数据表（GTM 的 Avg / 2Q25 小表）。

    table keys:
        columns (list[str]): 表头（第一格通常留空）
        rows (list[list]): 数据行，首列为行标签
        row_colors (list[str], optional): 各行标签颜色（与系列色呼应）
        at (list[float], optional): 表左上角在面板图区内的比例坐标，默认 [0.35, 0.02]
        width (float, optional): 表宽（英寸），默认按列数估算
    """
    px, py, pw, ph = rect
    columns = table.get("columns") or []
    rows = table.get("rows") or []
    if not rows or not columns:
        return
    row_colors = table.get("row_colors") or []
    fx, fy = table.get("at", [0.35, 0.02])
    n_cols = len(columns)
    n_rows = len(rows) + 1
    width = float(table.get("width", min(pw * 0.62, 0.85 + 0.75 * (n_cols - 1))))
    height = 0.21 * n_rows

    gfx = slide.shapes.add_table(
        n_rows, n_cols,
        Inches(px + pw * fx), Inches(py + ph * fy),
        Inches(width), Inches(height))
    tbl = gfx.table
    tbl.first_row = False
    tbl.horz_banding = False
    # 首列放行标签，列宽加权
    tbl.columns[0].width = Inches(width * 0.40)
    for c in range(1, n_cols):
        tbl.columns[c].width = Inches(width * 0.60 / (n_cols - 1))

    def style(cell, text, *, bold, color, align):
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor.from_string("FFFFFF")
        cell.margin_left = Pt(3)
        cell.margin_right = Pt(3)
        cell.margin_top = Pt(1)
        cell.margin_bottom = Pt(1)
        tf = cell.text_frame
        tf.text = str(text)
        para = tf.paragraphs[0]
        para.alignment = align
        run = para.runs[0] if para.runs else para.add_run()
        run.font.size = Pt(8.5)
        run.font.name = FONT
        run.font.bold = bold
        run.font.color.rgb = RGBColor.from_string(color)

    for c, header in enumerate(columns):
        style(tbl.cell(0, c), header, bold=True, color="1A1A1A",
              align=PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER)
    for r, row in enumerate(rows, start=1):
        label_color = (row_colors[r - 1] if r - 1 < len(row_colors) and row_colors[r - 1]
                       else "1A1A1A").lstrip("#").upper()
        for c, value in enumerate(row):
            style(tbl.cell(r, c), value,
                  bold=(c == 0), color=label_color if c == 0 else "404040",
                  align=PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER)
