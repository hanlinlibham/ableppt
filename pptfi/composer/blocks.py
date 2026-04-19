"""可组合图表构件 — 每个 block 渲染到指定 (x, y, w, h) 区域

设计原则:
- 所有 block 函数签名: (slide, data, theme, x, y, w, h, **kwargs)
- 不涉及页面级元素（标题/页眉/页脚），只负责区域内渲染
- 可被 layout_diagram / layout_composite 组合到一页
- 也可被其他布局函数直接调用
"""

import math
from pptx.util import Inches, Pt, Emu
from pptx.enum.shapes import MSO_SHAPE
from .helpers import (add_text, add_rect, add_rounded_rect, add_shape,
                      _rgb, add_line)


# ── Block Registry ─────────────────────────────────────────────────────

BLOCK_REGISTRY = {}


def _register(name):
    def decorator(fn):
        BLOCK_REGISTRY[name] = fn
        return fn
    return decorator


def render_block(slide, block_spec, theme):
    """根据 block_spec 分派渲染

    block_spec: {
        "type": str,               # BLOCK_REGISTRY 中的名称
        "area": [x, y, w, h],      # 渲染区域（英寸）
        ...                         # 其余字段透传给 block 函数
    }
    """
    block_type = block_spec["type"]
    if block_type not in BLOCK_REGISTRY:
        raise ValueError(f"未知 block 类型: {block_type}。可用: {list(BLOCK_REGISTRY.keys())}")

    area = block_spec.get("area")
    if not area or len(area) != 4:
        raise ValueError(f"block 需要 area=[x, y, w, h]，收到: {area}")

    fn = BLOCK_REGISTRY[block_type]
    x, y, w, h = area
    # 透传除 type/area 外的所有字段
    data = {k: v for k, v in block_spec.items() if k not in ("type", "area")}
    fn(slide, data, theme, x, y, w, h)


# ══════════════════════════════════════════════════════════════════════
# Block 1: 流程图 (Process Flow)
# ══════════════════════════════════════════════════════════════════════

@_register("process_flow")
def block_process_flow(slide, data, theme, x, y, w, h, **kwargs):
    """流程图 — 步骤框 + 箭头连接

    data:
        items: [{"label": str, "desc": str?, "icon": str?}]
        direction: "horizontal" | "vertical" (默认 horizontal)
        style: "box" | "chevron" (默认 box)
    """
    items = data["items"]
    n = len(items)
    if n == 0:
        return

    direction = data.get("direction", "horizontal")

    if direction == "horizontal":
        _flow_horizontal(slide, items, theme, x, y, w, h, data.get("style", "box"))
    else:
        _flow_vertical(slide, items, theme, x, y, w, h, data.get("style", "box"))


def _flow_horizontal(slide, items, theme, x, y, w, h, style):
    n = len(items)
    arrow_w = 0.35
    total_arrows = arrow_w * (n - 1)
    box_w = (w - total_arrows) / n
    box_h = h

    for i, item in enumerate(items):
        bx = x + i * (box_w + arrow_w)
        color = item.get("color", theme["primary"])

        if style == "chevron":
            shape = add_shape(slide, MSO_SHAPE.CHEVRON,
                              bx, y, box_w, box_h, fill=color)
        else:
            add_rounded_rect(slide, bx, y, box_w, box_h, fill=color)

        # 图标/序号
        icon = item.get("icon", str(i + 1))
        add_text(slide, icon,
                 x=bx, y=y + 0.15, w=box_w, h=0.45,
                 font_size=20, color="FFFFFF",
                 bold=True, align="center",
                 font_name=theme["header_font"])

        # 标签
        add_text(slide, item["label"],
                 x=bx + 0.15, y=y + 0.65, w=box_w - 0.3, h=0.45,
                 font_size=theme["body_size"] + 1, color="FFFFFF",
                 bold=True, align="center",
                 font_name=theme["header_font"])

        # 描述
        if item.get("desc"):
            add_text(slide, item["desc"],
                     x=bx + 0.15, y=y + 1.10, w=box_w - 0.3, h=box_h - 1.25,
                     font_size=theme["body_size"] - 1, color="FFFFFF",
                     align="center",
                     font_name=theme["body_font"])

        # 箭头
        if i < n - 1:
            ax = bx + box_w + 0.02
            ay = y + box_h / 2 - 0.20
            add_shape(slide, MSO_SHAPE.CHEVRON,
                      ax, ay, arrow_w - 0.04, 0.40,
                      fill=theme.get("text_muted", "9E9E9E"))


def _flow_vertical(slide, items, theme, x, y, w, h, style):
    n = len(items)
    arrow_h = 0.30
    total_arrows = arrow_h * (n - 1)
    box_h = (h - total_arrows) / n
    box_w = w

    for i, item in enumerate(items):
        by = y + i * (box_h + arrow_h)
        color = item.get("color", theme["primary"])

        add_rounded_rect(slide, x, by, box_w, box_h, fill=color)

        icon = item.get("icon", str(i + 1))
        # 左侧序号圆
        add_shape(slide, MSO_SHAPE.OVAL,
                  x + 0.20, by + (box_h - 0.50) / 2, 0.50, 0.50,
                  fill=theme["accent"])
        add_text(slide, icon,
                 x=x + 0.20, y=by + (box_h - 0.50) / 2, w=0.50, h=0.50,
                 font_size=14, color="FFFFFF",
                 bold=True, align="center", valign="middle",
                 font_name=theme["header_font"])

        # 标签 + 描述
        tx = x + 0.90
        tw = box_w - 1.10
        add_text(slide, item["label"],
                 x=tx, y=by + 0.10, w=tw, h=0.35,
                 font_size=theme["body_size"] + 1, color="FFFFFF",
                 bold=True, font_name=theme["header_font"])
        if item.get("desc"):
            add_text(slide, item["desc"],
                     x=tx, y=by + 0.45, w=tw, h=box_h - 0.55,
                     font_size=theme["body_size"] - 1, color="FFFFFF",
                     font_name=theme["body_font"])

        # 向下箭头
        if i < n - 1:
            ax = x + box_w / 2 - 0.15
            ay = by + box_h + 0.02
            add_shape(slide, MSO_SHAPE.DOWN_ARROW,
                      ax, ay, 0.30, arrow_h - 0.04,
                      fill=theme.get("text_muted", "9E9E9E"))


# ══════════════════════════════════════════════════════════════════════
# Block 2: 时间线 (Timeline)
# ══════════════════════════════════════════════════════════════════════

@_register("timeline")
def block_timeline(slide, data, theme, x, y, w, h, **kwargs):
    """时间线 — 水平轴 + 上下交替的里程碑

    data:
        items: [{"date": str, "label": str, "desc": str?}]
    """
    items = data["items"]
    n = len(items)
    if n == 0:
        return

    # 时间轴位于区域垂直中央
    axis_y = y + h * 0.45
    axis_thickness = 0.03

    # 主轴线
    add_rect(slide, x, axis_y, w, axis_thickness, fill=theme["primary"])

    # 节点间距
    margin = 0.4  # 左右留白
    span = w - 2 * margin
    gap = span / max(n - 1, 1)

    for i, item in enumerate(items):
        cx = x + margin + i * gap  # 节点圆心 x
        is_above = (i % 2 == 0)  # 上下交替

        # 节点圆
        dot_r = 0.15
        add_shape(slide, MSO_SHAPE.OVAL,
                  cx - dot_r, axis_y - dot_r + axis_thickness / 2,
                  dot_r * 2, dot_r * 2,
                  fill=theme["accent"])

        # 竖线
        line_h = h * 0.22
        if is_above:
            line_top = axis_y - line_h - dot_r
            add_rect(slide, cx - 0.008, line_top, 0.016, line_h,
                     fill=theme["border"])
        else:
            line_top = axis_y + axis_thickness + dot_r
            add_rect(slide, cx - 0.008, line_top, 0.016, line_h,
                     fill=theme["border"])

        # 文字
        text_w = gap * 0.9 if gap > 0.5 else 1.5
        text_x = cx - text_w / 2

        if is_above:
            # 日期在最上面
            add_text(slide, item["date"],
                     x=text_x, y=y, w=text_w, h=0.35,
                     font_size=theme["body_size"] - 1, color=theme["accent"],
                     bold=True, align="center",
                     font_name=theme["header_font"])
            # 标签
            label_y = y + 0.30
            add_text(slide, item["label"],
                     x=text_x, y=label_y, w=text_w, h=0.35,
                     font_size=theme["body_size"], color=theme["text_dark"],
                     bold=True, align="center",
                     font_name=theme["header_font"])
            if item.get("desc"):
                add_text(slide, item["desc"],
                         x=text_x, y=label_y + 0.32, w=text_w, h=0.50,
                         font_size=theme["body_size"] - 2,
                         color=theme["text_muted"],
                         align="center",
                         font_name=theme["body_font"])
        else:
            # 标签在轴下方
            label_y = line_top + line_h + 0.05
            add_text(slide, item["date"],
                     x=text_x, y=label_y, w=text_w, h=0.35,
                     font_size=theme["body_size"] - 1, color=theme["accent"],
                     bold=True, align="center",
                     font_name=theme["header_font"])
            add_text(slide, item["label"],
                     x=text_x, y=label_y + 0.30, w=text_w, h=0.35,
                     font_size=theme["body_size"], color=theme["text_dark"],
                     bold=True, align="center",
                     font_name=theme["header_font"])
            if item.get("desc"):
                add_text(slide, item["desc"],
                         x=text_x, y=label_y + 0.62, w=text_w, h=0.50,
                         font_size=theme["body_size"] - 2,
                         color=theme["text_muted"],
                         align="center",
                         font_name=theme["body_font"])


# ══════════════════════════════════════════════════════════════════════
# Block 3: 金字塔 (Pyramid)
# ══════════════════════════════════════════════════════════════════════

@_register("pyramid")
def block_pyramid(slide, data, theme, x, y, w, h, **kwargs):
    """金字塔 — 从上到下逐层加宽的层叠结构

    data:
        items: [{"label": str, "desc": str?, "color": str?}]
              (从塔尖到塔底排列)
        inverted: bool (默认 False; True 则为漏斗，上宽下窄)
    """
    items = data["items"]
    n = len(items)
    if n == 0:
        return

    inverted = data.get("inverted", False)
    gap = 0.06  # 层间间隙
    layer_h = (h - gap * (n - 1)) / n
    min_w = w * 0.25  # 最窄层宽度

    for i, item in enumerate(items):
        # 宽度从窄到宽（金字塔）或从宽到窄（漏斗）
        if inverted:
            ratio = 1 - (i / max(n - 1, 1)) * (1 - min_w / w)
        else:
            ratio = min_w / w + (i / max(n - 1, 1)) * (1 - min_w / w)

        lw = w * ratio
        lx = x + (w - lw) / 2
        ly = y + i * (layer_h + gap)

        # 颜色: 用户自定义 > 自动渐变
        if item.get("color"):
            color = item["color"]
        else:
            # 从 primary 到 accent 的渐变效果：奇偶交替
            color = theme["primary"] if i % 2 == 0 else theme.get("secondary", theme["accent"])

        add_rounded_rect(slide, lx, ly, lw, layer_h, fill=color)

        # 标签
        add_text(slide, item["label"],
                 x=lx + 0.15, y=ly + 0.05, w=lw - 0.3, h=layer_h * 0.5,
                 font_size=theme["body_size"] + 1, color="FFFFFF",
                 bold=True, align="center", valign="middle",
                 font_name=theme["header_font"])

        # 描述
        if item.get("desc"):
            add_text(slide, item["desc"],
                     x=lx + 0.15, y=ly + layer_h * 0.45, w=lw - 0.3,
                     h=layer_h * 0.50,
                     font_size=theme["body_size"] - 1, color="FFFFFF",
                     align="center", valign="top",
                     font_name=theme["body_font"])


# ══════════════════════════════════════════════════════════════════════
# Block 4: 对比栏 (Comparison)
# ══════════════════════════════════════════════════════════════════════

@_register("comparison")
def block_comparison(slide, data, theme, x, y, w, h, **kwargs):
    """对比栏 — 2~4 列并排对比

    data:
        columns: [{
            "title": str,
            "items": [str],
            "color": str?,       # 标题栏颜色
            "highlight": bool?   # 高亮列（推荐方案）
        }]
    """
    columns = data["columns"]
    n = len(columns)
    if n == 0:
        return

    col_gap = 0.20
    col_w = (w - col_gap * (n - 1)) / n
    header_h = 0.65

    default_colors = [theme["primary"], theme.get("secondary", theme["accent"]),
                      theme["accent"], theme.get("text_muted", "9E9E9E")]

    for i, col in enumerate(columns):
        cx = x + i * (col_w + col_gap)
        is_highlight = col.get("highlight", False)
        col_color = col.get("color", default_colors[i % len(default_colors)])

        # 标题栏
        add_rounded_rect(slide, cx, y, col_w, header_h, fill=col_color)
        add_text(slide, col["title"],
                 x=cx, y=y, w=col_w, h=header_h,
                 font_size=theme["body_size"] + 2, color="FFFFFF",
                 bold=True, align="center", valign="middle",
                 font_name=theme["header_font"])

        # 内容区背景
        content_y = y + header_h + 0.05
        content_h = h - header_h - 0.05
        bg = "F0F4F8" if is_highlight else theme.get("table_zebra_even", "F8FAFC")
        add_rect(slide, cx, content_y, col_w, content_h, fill=bg)

        # 高亮边框
        if is_highlight:
            border_w = 0.03
            add_rect(slide, cx, content_y, border_w, content_h, fill=col_color)
            add_rect(slide, cx + col_w - border_w, content_y, border_w, content_h,
                     fill=col_color)

        # 列表项
        items = col.get("items", [])
        item_y = content_y + 0.15
        for text in items:
            # bullet 小方块
            add_rect(slide, cx + 0.20, item_y + 0.12, 0.07, 0.07,
                     fill=col_color)
            add_text(slide, text,
                     x=cx + 0.38, y=item_y, w=col_w - 0.55, h=0.35,
                     font_size=theme["body_size"], color=theme["text_dark"],
                     font_name=theme["body_font"])
            item_y += 0.40


# ══════════════════════════════════════════════════════════════════════
# Block 5: 图标网格 (Icon Grid)
# ══════════════════════════════════════════════════════════════════════

@_register("icon_grid")
def block_icon_grid(slide, data, theme, x, y, w, h, **kwargs):
    """图标网格 — 网格排列的图标+文字卡片

    data:
        items: [{"icon": str, "label": str, "desc": str?, "color": str?}]
        cols: int (默认自动: <=4 用 2 列, <=6 用 3 列, >6 用 4 列)
    """
    items = data["items"]
    n = len(items)
    if n == 0:
        return

    # 自动列数
    cols = data.get("cols")
    if cols is None:
        if n <= 4:
            cols = 2
        elif n <= 6:
            cols = 3
        else:
            cols = 4

    rows = math.ceil(n / cols)
    gap_x = 0.20
    gap_y = 0.15
    card_w = (w - gap_x * (cols - 1)) / cols
    card_h = (h - gap_y * (rows - 1)) / rows

    icon_size = 0.55

    for i, item in enumerate(items):
        col = i % cols
        row = i // cols
        cx = x + col * (card_w + gap_x)
        cy = y + row * (card_h + gap_y)

        icon_color = item.get("color", theme["primary"])

        # 卡片背景（极浅）
        add_rect(slide, cx, cy, card_w, card_h,
                 fill=theme.get("table_zebra_even", "F8FAFC"))

        # 左侧色条
        add_rect(slide, cx, cy, 0.04, card_h, fill=icon_color)

        # 图标圆
        add_shape(slide, MSO_SHAPE.OVAL,
                  cx + 0.20, cy + 0.20, icon_size, icon_size,
                  fill=icon_color)
        add_text(slide, item["icon"],
                 x=cx + 0.20, y=cy + 0.20, w=icon_size, h=icon_size,
                 font_size=14, color="FFFFFF",
                 bold=True, align="center", valign="middle",
                 font_name=theme["header_font"])

        # 标签
        tx = cx + 0.20 + icon_size + 0.15
        tw = card_w - icon_size - 0.55
        add_text(slide, item["label"],
                 x=tx, y=cy + 0.15, w=tw, h=0.35,
                 font_size=theme["body_size"] + 1, color=theme["text_dark"],
                 bold=True, font_name=theme["header_font"])

        # 描述
        if item.get("desc"):
            add_text(slide, item["desc"],
                     x=tx, y=cy + 0.50, w=tw, h=card_h - 0.65,
                     font_size=theme["body_size"] - 1,
                     color=theme["text_muted"],
                     font_name=theme["body_font"])


# ══════════════════════════════════════════════════════════════════════
# Block 6: 矩阵/象限 (Matrix / Quadrant)
# ══════════════════════════════════════════════════════════════════════

@_register("matrix")
def block_matrix(slide, data, theme, x, y, w, h, **kwargs):
    """2x2 矩阵/象限图

    data:
        quadrants: [
            {"label": str, "desc": str?, "color": str?},  # 左上
            {"label": str, "desc": str?, "color": str?},  # 右上
            {"label": str, "desc": str?, "color": str?},  # 左下
            {"label": str, "desc": str?, "color": str?},  # 右下
        ]
        x_label: str?  # X 轴标签
        y_label: str?  # Y 轴标签
    """
    quads = data["quadrants"]
    if len(quads) < 4:
        quads = quads + [{"label": ""}] * (4 - len(quads))

    gap = 0.08
    qw = (w - gap) / 2
    qh = (h - gap) / 2

    default_colors = [
        theme["primary"],
        theme.get("secondary", theme["accent"]),
        theme["accent"],
        theme.get("text_muted", "9E9E9E"),
    ]

    positions = [
        (x, y),              # 左上
        (x + qw + gap, y),   # 右上
        (x, y + qh + gap),   # 左下
        (x + qw + gap, y + qh + gap),  # 右下
    ]

    for i, (qx, qy) in enumerate(positions):
        q = quads[i]
        color = q.get("color", default_colors[i])
        add_rounded_rect(slide, qx, qy, qw, qh, fill=color)

        add_text(slide, q["label"],
                 x=qx + 0.15, y=qy + 0.15, w=qw - 0.3, h=0.45,
                 font_size=theme["body_size"] + 2, color="FFFFFF",
                 bold=True, align="center",
                 font_name=theme["header_font"])

        if q.get("desc"):
            add_text(slide, q["desc"],
                     x=qx + 0.15, y=qy + 0.60, w=qw - 0.3, h=qh - 0.80,
                     font_size=theme["body_size"] - 1, color="FFFFFF",
                     align="center",
                     font_name=theme["body_font"])

    # 轴标签
    if data.get("x_label"):
        add_text(slide, data["x_label"],
                 x=x, y=y + h + 0.02, w=w, h=0.30,
                 font_size=theme["body_size"] - 1, color=theme["text_muted"],
                 align="center", font_name=theme["body_font"])
    if data.get("y_label"):
        # Y 轴标签放在左侧
        add_text(slide, data["y_label"],
                 x=x - 0.50, y=y + h * 0.35, w=0.45, h=0.40,
                 font_size=theme["body_size"] - 1, color=theme["text_muted"],
                 align="center", font_name=theme["body_font"])


