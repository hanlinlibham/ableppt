"""Scatter / bubble chart layouts."""

from pptx.util import Inches

from ..helpers import add_text, setup_content_page, require_columns


def _render_xy_family(slide, data, theme, *, family: str):
    from ableppt.chart_builder import create_bubble_chart, create_scatter_chart

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
    _needed = [data["x_col"], data["y_col"]]
    if family != "scatter":
        _needed.append(data.get("size_col"))
    require_columns(data["df"], _needed, where=f"{family} 图表")
    common_kwargs = {
        "slide": slide,
        "df": data["df"],
        "x_col": data["x_col"],
        "y_col": data["y_col"],
        "series_name": data.get("series_name"),
        "position": (Inches(m), Inches(chart_top)),
        "size": (Inches(content_w), Inches(chart_h)),
        "color": data.get("color", theme.get("primary", "1E2761")),
        "marker_size": data.get("marker_size", 9),
    }

    if family == "scatter":
        create_scatter_chart(**common_kwargs)
    else:
        create_bubble_chart(
            **common_kwargs,
            size_col=data["size_col"],
        )


def layout_scatter(slide, data, theme):
    """Standalone scatter page inside composer."""

    _render_xy_family(slide, data, theme, family="scatter")


def layout_bubble(slide, data, theme):
    """Standalone bubble page inside composer."""

    _render_xy_family(slide, data, theme, family="bubble")
