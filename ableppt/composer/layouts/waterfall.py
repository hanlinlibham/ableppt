"""Waterfall layout — standalone bridge / attribution page."""

from pptx.util import Inches

from ..helpers import add_text, setup_content_page


def layout_waterfall(slide, data, theme):
    """Waterfall chart page.

    data keys:
        title (str): 页面标题
        df (DataFrame): 原始语义 waterfall 数据
        categories_col (str): 类别列名
        value_col (str): 数值列名
        measure_col (str, optional): measure 列名
        total_categories (list[str], optional): 额外 total 类别
        subtitle (str, optional): 页面副标题
        insight (str, optional): 结论先行文本
        positive_color / negative_color / total_color (str, optional)
        show_connectors / show_value_labels / show_legend (bool, optional)
        footnote (str, optional): 来源，footer 自动处理
    """

    from ableppt.chart_builder import create_waterfall_chart

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
    from ..helpers import require_columns
    require_columns(
        data["df"],
        [data["categories_col"], data["value_col"], data.get("measure_col")],
        where="waterfall 图表",
    )
    create_waterfall_chart(
        slide=slide,
        df=data["df"],
        categories_col=data["categories_col"],
        value_col=data["value_col"],
        measure_col=data.get("measure_col"),
        total_categories=data.get("total_categories"),
        position=(Inches(m), Inches(chart_top)),
        size=(Inches(content_w), Inches(chart_h)),
        layout_config=data.get("layout_config"),
        positive_color=data.get("positive_color", theme.get("positive", "10B981")),
        negative_color=data.get("negative_color", theme.get("negative", "EF4444")),
        total_color=data.get("total_color", theme.get("primary", "1E2761")),
        show_legend=data.get("show_legend", False),
        show_connectors=data.get("show_connectors", True),
        show_value_labels=data.get("show_value_labels", True),
        label_font_name=theme.get("body_font", "微软雅黑"),
    )
