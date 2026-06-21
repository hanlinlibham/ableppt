"""表格布局"""

from ..helpers import set_slide_bg, add_text, add_rect, add_table, add_page_header, setup_content_page


def layout_comparison_table(slide, data, theme):
    """对比表格页 — 标题 + 带高亮行的表格

    data keys:
        title (str): 页面标题
        subtitle (str, optional): 副标题
        headers (list[str]): 表头
        rows (list[list]): 数据行
        highlight_row (int, optional): 高亮行索引
        highlight_cols (list[int], optional): 高亮列索引列表
        footnote (str, optional): 数据来源/脚注（auto-footer 渲染）
    """
    # datasource 引用解析后 df 已注入，自动转换为 rows/headers
    if "df" in data and "rows" not in data:
        import pandas as pd
        df = data["df"]
        if isinstance(df, pd.DataFrame):
            data = dict(data)
            data["headers"] = data.get("headers") or list(df.columns)
            data["rows"] = df.values.tolist()

    m, sw, content_y, content_w, footer_y = setup_content_page(slide, data, theme)

    subtitle_h = 0
    if data.get("subtitle"):
        add_text(slide, data["subtitle"],
                 x=m, y=content_y, w=content_w, h=0.3,
                 font_size=theme["body_size"] - 1, color=theme["text_muted"],
                 font_name=theme["body_font"])
        subtitle_h = 0.4

    # 表格
    table_top = content_y + subtitle_h + 0.05
    n_rows = len(data["rows"])
    max_table_h = footer_y - table_top - 0.6
    table_h = min(n_rows * 0.5 + 0.5, max_table_h)

    add_table(
        slide,
        headers=data["headers"],
        rows=data["rows"],
        x=m, y=table_top, w=content_w, h=table_h,
        theme=theme,
        font_name=theme["body_font"],
        font_size=11,
        highlight_row=data.get("highlight_row"),
        highlight_cols=data.get("highlight_cols"),
        ib_style=True,
    )

    # footnote 统一由 PageComposer auto-footer 渲染，此处不再手动添加
