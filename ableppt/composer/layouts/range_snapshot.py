"""Range snapshot layout — standalone valuation/range page."""

from pptx.util import Inches

from ..helpers import add_text, setup_content_page


def layout_range_snapshot(slide, data, theme):
    """Range snapshot chart page.

    data keys:
        title (str): 页面标题
        df (DataFrame): 原始语义 range snapshot 数据
        categories_col (str): 类别列名
        min_col / max_col / average_col / current_col (str): 语义列名
        subtitle (str, optional): 页面副标题
        insight (str, optional): 结论先行文本
        range_color / average_color / current_color (str, optional)
        number_format (str, optional)
        show_average_ticks / show_current_markers / show_current_labels (bool, optional)
        footnote (str, optional): 来源，footer 自动处理
    """

    from ableppt.chart_builder import create_range_snapshot_chart

    m, sw, content_y, content_w, footer_y = setup_content_page(slide, data, theme)

    subtitle_h = 0.0
    if data.get("subtitle"):
        add_text(
            slide,
            data["subtitle"],
            x=m,
            y=content_y - 0.05,
            w=content_w,
            h=0.3,
            font_size=theme.get("chart_subtitle_size", 11),
            color=theme["text_muted"],
            font_name=theme["body_font"],
        )
        subtitle_h = 0.35

    insight_h = 0.0
    if data.get("insight"):
        add_text(
            slide,
            data["insight"],
            x=m,
            y=content_y + subtitle_h,
            w=content_w,
            h=0.5,
            font_size=theme.get("body_size", 12),
            color=theme["text_muted"],
            font_name=theme["body_font"],
        )
        insight_h = 0.55

    chart_top = content_y + subtitle_h + insight_h + 0.05
    chart_h = footer_y - chart_top - 0.25
    create_range_snapshot_chart(
        slide=slide,
        df=data["df"],
        categories_col=data["categories_col"],
        min_col=data["min_col"],
        max_col=data["max_col"],
        average_col=data["average_col"],
        current_col=data["current_col"],
        orientation=data.get("orientation", "vertical"),
        position=(Inches(m), Inches(chart_top)),
        size=(Inches(content_w), Inches(chart_h)),
        layout_config=data.get("layout_config"),
        range_color=data.get("range_color", theme.get("text_muted", "5F6772")),
        average_color=data.get("average_color", theme.get("accent", theme.get("positive", "87A330"))),
        current_color=data.get("current_color", theme.get("primary", "1E88E5")),
        number_format=data.get("number_format", "0.0x"),
        show_average_ticks=data.get("show_average_ticks", True),
        show_current_markers=data.get("show_current_markers", True),
        show_current_labels=data.get("show_current_labels", True),
        label_font_name=theme.get("body_font", "微软雅黑"),
        axis_break=data.get("axis_break"),
    )
