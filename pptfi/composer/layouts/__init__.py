"""布局函数注册表"""

from .title import layout_title_dark, layout_title_light
from .kpi import layout_kpi_cards
from .chart import (layout_chart_full, layout_chart_text, layout_two_charts,
                    layout_two_charts_vertical, layout_chart_table)
from .table import layout_comparison_table
from .content import layout_bullet_points, layout_section_divider
from .conclusion import layout_conclusion_dark
from .image_text import layout_image_text
from .waterfall import layout_waterfall
from .xy import layout_bubble, layout_scatter
from .gtm import (layout_gtm_panels, layout_gtm_cover, layout_gtm_toc,
                  layout_gtm_quilt, layout_gtm_chart_text)
from .diagram import (layout_process_flow, layout_timeline, layout_pyramid,
                      layout_comparison, layout_icon_grid, layout_matrix,
                      layout_composite)

LAYOUT_REGISTRY = {
    "title_dark": layout_title_dark,
    "title_light": layout_title_light,
    "kpi_cards": layout_kpi_cards,
    "chart_full": layout_chart_full,
    "chart_text": layout_chart_text,
    "two_charts": layout_two_charts,
    "two_charts_vertical": layout_two_charts_vertical,
    "chart_table": layout_chart_table,
    "comparison_table": layout_comparison_table,
    "bullet_points": layout_bullet_points,
    "section_divider": layout_section_divider,
    "conclusion_dark": layout_conclusion_dark,
    "image_text": layout_image_text,
    "waterfall": layout_waterfall,
    "gtm_panels": layout_gtm_panels,
    "gtm_cover": layout_gtm_cover,
    "gtm_toc": layout_gtm_toc,
    "gtm_quilt": layout_gtm_quilt,
    "gtm_chart_text": layout_gtm_chart_text,
    "scatter": layout_scatter,
    "bubble": layout_bubble,
    # Diagram 布局 (基于 blocks 可组合)
    "process_flow": layout_process_flow,
    "timeline": layout_timeline,
    "pyramid": layout_pyramid,
    "comparison": layout_comparison,
    "icon_grid": layout_icon_grid,
    "matrix": layout_matrix,
    "composite": layout_composite,
}
