"""
底层 XML 解析：从图表元素提取系列颜色、线宽、标记点样式

与 chart_builder/styles.py 中 _apply_line_style() 互为镜像：
- _apply_line_style: 写入 XML
- 本模块: 从 XML 读取
"""

from typing import List, Optional

from pptfi.chart_builder.oxml_ns import NAMESPACES

# EMU → pt 转换因子
_EMU_PER_PT = 12700

# 标准线宽（pt），用于 snap
_STANDARD_LINE_WIDTHS = [0.5, 0.75, 1.0, 1.5, 2.0, 2.25, 3.0]


def _snap_to_nearest(value: float, targets: List[float]) -> float:
    """将值吸附到最近的标准值"""
    return min(targets, key=lambda t: abs(t - value))


def extract_series_colors(chart_element) -> List[str]:
    """
    从图表元素提取所有系列的颜色。

    遍历所有 <c:ser>，按图表类型提取颜色：
    - Bar/Area: <c:spPr><a:solidFill><a:srgbClr val="..."/>
    - Line/Scatter: <c:spPr><a:ln><a:solidFill><a:srgbClr val="..."/>

    Args:
        chart_element: 图表的 lxml 根元素 (chart._element)

    Returns:
        颜色列表（6位十六进制 RGB），按系列顺序排列
    """
    colors = []
    plot_area = chart_element.find('.//c:plotArea', namespaces=NAMESPACES)
    if plot_area is None:
        return colors

    bar_area_tags = {'barChart', 'areaChart'}

    for plot_tag in ['barChart', 'lineChart', 'areaChart', 'scatterChart']:
        for plot_elem in plot_area.findall(f'.//c:{plot_tag}', namespaces=NAMESPACES):
            tag_local = plot_tag
            is_bar_area = tag_local in bar_area_tags

            for ser in plot_elem.findall('c:ser', namespaces=NAMESPACES):
                color = _extract_color_from_ser(ser, is_bar_area)
                colors.append(color if color else "000000")

    return colors


def _extract_color_from_ser(ser, is_bar_area: bool) -> Optional[str]:
    """从单个系列元素提取颜色"""
    spPr = ser.find('c:spPr', namespaces=NAMESPACES)
    if spPr is None:
        return None

    if is_bar_area:
        # Bar/Area: solidFill 直接在 spPr 下
        srgb = spPr.find('a:solidFill/a:srgbClr', namespaces=NAMESPACES)
        if srgb is not None:
            return srgb.get('val')
    else:
        # Line/Scatter: solidFill 在 ln 下
        srgb = spPr.find('a:ln/a:solidFill/a:srgbClr', namespaces=NAMESPACES)
        if srgb is not None:
            return srgb.get('val')

    # 通用回退：任何位置的 srgbClr
    srgb = spPr.find('.//a:srgbClr', namespaces=NAMESPACES)
    if srgb is not None:
        return srgb.get('val')

    return None


def extract_series_line_widths(chart_element) -> List[Optional[float]]:
    """
    从图表元素提取所有系列的线宽（pt）。

    提取 <a:ln w="..."/>，EMU / 12700 → pt，snap 到标准值。

    Args:
        chart_element: 图表的 lxml 根元素

    Returns:
        线宽列表（pt），None 表示未设置或非线型图表
    """
    widths = []
    plot_area = chart_element.find('.//c:plotArea', namespaces=NAMESPACES)
    if plot_area is None:
        return widths

    for plot_tag in ['barChart', 'lineChart', 'areaChart', 'scatterChart']:
        for plot_elem in plot_area.findall(f'.//c:{plot_tag}', namespaces=NAMESPACES):
            for ser in plot_elem.findall('c:ser', namespaces=NAMESPACES):
                spPr = ser.find('c:spPr', namespaces=NAMESPACES)
                if spPr is None:
                    widths.append(None)
                    continue

                ln = spPr.find('a:ln', namespaces=NAMESPACES)
                if ln is None:
                    widths.append(None)
                    continue

                w_attr = ln.get('w')
                if w_attr is not None:
                    pt_value = int(w_attr) / _EMU_PER_PT
                    widths.append(_snap_to_nearest(pt_value, _STANDARD_LINE_WIDTHS))
                else:
                    widths.append(None)

    return widths


def extract_series_marker_styles(chart_element) -> List[Optional[str]]:
    """
    从图表元素提取所有系列的标记点样式。

    提取 <c:marker><c:symbol val="..."/>

    Args:
        chart_element: 图表的 lxml 根元素

    Returns:
        标记点样式列表（"none", "circle", "square" 等），None 表示未设置
    """
    markers = []
    plot_area = chart_element.find('.//c:plotArea', namespaces=NAMESPACES)
    if plot_area is None:
        return markers

    for plot_tag in ['barChart', 'lineChart', 'areaChart', 'scatterChart']:
        for plot_elem in plot_area.findall(f'.//c:{plot_tag}', namespaces=NAMESPACES):
            for ser in plot_elem.findall('c:ser', namespaces=NAMESPACES):
                marker = ser.find('c:marker', namespaces=NAMESPACES)
                if marker is None:
                    markers.append(None)
                    continue

                symbol = marker.find('c:symbol', namespaces=NAMESPACES)
                if symbol is not None:
                    markers.append(symbol.get('val'))
                else:
                    markers.append(None)

    return markers
