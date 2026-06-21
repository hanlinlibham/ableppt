"""图表布局 — 基于 blocks 的可组合页面

提供两类布局:
1. 单 block 快捷布局 (layout_process_flow, layout_timeline, ...)
2. 自由组合布局 (layout_composite) — 在一页上放置多个 blocks
"""

from ..helpers import setup_content_page
from ..blocks import BLOCK_REGISTRY, render_block


# ── 通用: 单 block 页面渲染 ──────────────────────────────────────────

def _single_block_page(slide, data, theme, block_type):
    """通用模式: 页面框架 + 单个 block 填满内容区域"""
    m, sw, content_y, content_w, footer_y = setup_content_page(slide, data, theme)

    block_data = {k: v for k, v in data.items() if k not in ("title", "footnote")}

    fn = BLOCK_REGISTRY[block_type]
    fn(slide, block_data, theme,
       x=m, y=content_y, w=content_w, h=footer_y - content_y - 0.15)


# ── 快捷布局 ─────────────────────────────────────────────────────────

def layout_process_flow(slide, data, theme):
    """流程图页 — 步骤框 + 箭头连接

    data keys:
        title (str): 页面标题
        items (list): [{"label": str, "desc": str?, "icon": str?}]
        direction (str): "horizontal" | "vertical" (默认 horizontal)
        style (str): "box" | "chevron" (默认 box)
        footnote (str, optional): 脚注
    """
    _single_block_page(slide, data, theme, "process_flow")


def layout_timeline(slide, data, theme):
    """时间线页 — 水平轴 + 上下交替的里程碑

    data keys:
        title (str): 页面标题
        items (list): [{"date": str, "label": str, "desc": str?}]
        footnote (str, optional): 脚注
    """
    _single_block_page(slide, data, theme, "timeline")


def layout_pyramid(slide, data, theme):
    """金字塔页 — 从上到下逐层加宽

    data keys:
        title (str): 页面标题
        items (list): [{"label": str, "desc": str?}] (从塔尖到塔底)
        inverted (bool): True 则为漏斗（上宽下窄）
        footnote (str, optional): 脚注
    """
    _single_block_page(slide, data, theme, "pyramid")


def layout_comparison(slide, data, theme):
    """对比栏页 — 2~4 列并排对比

    data keys:
        title (str): 页面标题
        columns (list): [{"title": str, "items": [str], "highlight": bool?}]
        footnote (str, optional): 脚注
    """
    _single_block_page(slide, data, theme, "comparison")


def layout_icon_grid(slide, data, theme):
    """图标网格页 — 网格排列的图标+文字卡片

    data keys:
        title (str): 页面标题
        items (list): [{"icon": str, "label": str, "desc": str?}]
        cols (int, optional): 列数
        footnote (str, optional): 脚注
    """
    _single_block_page(slide, data, theme, "icon_grid")


def layout_matrix(slide, data, theme):
    """2x2 矩阵/象限页

    data keys:
        title (str): 页面标题
        quadrants (list): 4 项 [{"label": str, "desc": str?}]
        x_label (str, optional): X 轴标签
        y_label (str, optional): Y 轴标签
        footnote (str, optional): 脚注
    """
    _single_block_page(slide, data, theme, "matrix")


# ── 自由组合布局 ─────────────────────────────────────────────────────

def layout_composite(slide, data, theme):
    """自由组合页 — 在一页上放置多个 blocks

    data keys:
        title (str): 页面标题
        blocks (list): [
            {
                "type": str,            # BLOCK_REGISTRY 中的名称
                "area": [x, y, w, h],   # 渲染区域（英寸）
                ...                      # 其余字段透传给 block
            },
            ...
        ]
        footnote (str, optional): 脚注

    示例 — 上半部流程图 + 下半部左金字塔右对比:
        {
            "title": "投资分析框架",
            "blocks": [
                {
                    "type": "process_flow",
                    "area": [0.6, 1.0, 12.1, 2.2],
                    "items": [...]
                },
                {
                    "type": "pyramid",
                    "area": [0.6, 3.5, 5.5, 3.5],
                    "items": [...]
                },
                {
                    "type": "comparison",
                    "area": [6.5, 3.5, 6.2, 3.5],
                    "columns": [...]
                }
            ]
        }
    """
    from ..helpers import set_slide_bg, add_page_header
    m = theme["margin"]
    sw = theme.get("slide_w", 13.333)

    set_slide_bg(slide, theme["bg_light"])
    add_page_header(slide, data["title"], theme)

    for block_spec in data["blocks"]:
        render_block(slide, block_spec, theme)
