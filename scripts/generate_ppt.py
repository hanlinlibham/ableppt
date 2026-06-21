#!/usr/bin/env python3
"""根据模板 + 数据 JSON 配置文件 → 生成 PPT

用法: python generate_ppt.py <template.pptx> <config.json> <output.pptx>

config.json 格式:
{
  "text_data": { "标题": "xxx", "日期": "2024-12-05" },
  "chart_configs": {
    "图表名": {
      "csv_path": "data.csv",
      "categories_col": "日期",
      "series_config": [
        {"key": "列名", "name": "显示名", "type": "bar", "axis": "primary"},
        {"key": "列名2", "name": "显示名2", "type": "line", "axis": "secondary"}
      ],
      "style": {
        "color_scheme": "aim00",
        "line_width_pt": 2.0,
        "marker_style": "none"
      },
      "layout": {
        "title": "图表标题",
        "legend": {"position": "top", "font_size_pt": 9, "font_name": "黑体"},
        "value_axis": {"number_format": "0%", "font_size_pt": 9},
        "secondary_value_axis": {"number_format": "#,##0", "font_size_pt": 9},
        "date_axis": {"number_format": "yyyy/mm", "base_unit": "days"}
      }
    }
  }
}
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from pptx.enum.chart import XL_LEGEND_POSITION

from ableppt.template.replacer import TemplateReplacer
from ableppt.chart_builder.styles import StyleConfig
from ableppt.chart_builder.layout import ChartLayoutConfig, LegendConfig, ValueAxisConfig
from ableppt.chart_builder.date_axis import DateAxisConfig


LEGEND_POSITION_MAP = {
    "top": XL_LEGEND_POSITION.TOP,
    "bottom": XL_LEGEND_POSITION.BOTTOM,
    "left": XL_LEGEND_POSITION.LEFT,
    "right": XL_LEGEND_POSITION.RIGHT,
    "corner": XL_LEGEND_POSITION.CORNER,
}


def build_chart_config(chart_name: str, chart_def: dict, config_dir: Path) -> dict:
    """从 JSON 配置构建图表配置字典（供 TemplateReplacer 使用）"""

    # 加载 CSV 数据
    csv_path = config_dir / chart_def["csv_path"]
    if not csv_path.exists():
        print(f"  错误: CSV 文件不存在: {csv_path}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(str(csv_path))

    # 转换日期列
    categories_col = chart_def["categories_col"]
    if categories_col in df.columns:
        try:
            df[categories_col] = pd.to_datetime(df[categories_col])
        except Exception:
            pass  # 非日期列保持原样

    series_config = chart_def["series_config"]

    # 构建样式配置
    style_def = chart_def.get("style", {})
    style_config = StyleConfig(
        color_scheme=style_def.get("color_scheme", "aim00"),
        line_width_pt=style_def.get("line_width_pt", 2.0),
        marker_style=style_def.get("marker_style", "none"),
    )

    # 构建布局配置
    layout_def = chart_def.get("layout", {})

    legend_def = layout_def.get("legend", {})
    legend_pos = LEGEND_POSITION_MAP.get(legend_def.get("position", "top"), XL_LEGEND_POSITION.TOP)
    legend_config = LegendConfig(
        position=legend_pos,
        font_size_pt=legend_def.get("font_size_pt", 9),
        font_name=legend_def.get("font_name", "黑体"),
    )

    va_def = layout_def.get("value_axis", {})
    value_axis_config = ValueAxisConfig(
        number_format=va_def.get("number_format", "0%"),
        font_size_pt=va_def.get("font_size_pt", 9),
        font_name=va_def.get("font_name", "黑体"),
        has_major_gridlines=va_def.get("has_major_gridlines", False),
    )

    sva_def = layout_def.get("secondary_value_axis", {})
    secondary_value_axis_config = ValueAxisConfig(
        number_format=sva_def.get("number_format", "#,##0"),
        font_size_pt=sva_def.get("font_size_pt", 9),
        font_name=sva_def.get("font_name", "黑体"),
        has_major_gridlines=sva_def.get("has_major_gridlines", False),
    )

    layout_config = ChartLayoutConfig(
        title=layout_def.get("title", ""),
        legend_config=legend_config,
        value_axis_config=value_axis_config,
        secondary_value_axis_config=secondary_value_axis_config,
    )

    # 日期轴配置
    da_def = layout_def.get("date_axis", {})
    if da_def:
        label_interval = da_def.get("major_unit", len(df) // 7)
        date_axis_config = DateAxisConfig(
            base_unit=da_def.get("base_unit", "days"),
            major_unit=label_interval,
            number_format=da_def.get("number_format", "yyyy/mm"),
        )
        layout_config.date_axis_config = date_axis_config

    return {
        "df": df,
        "categories_col": categories_col,
        "series_config": series_config,
        "style_config": style_config,
        "layout_config": layout_config,
    }


def main():
    parser = argparse.ArgumentParser(description="模板替换生成 PPT")
    parser.add_argument("template", help="模板 .pptx 文件路径")
    parser.add_argument("config", help="配置 .json 文件路径")
    parser.add_argument("output", help="输出 .pptx 文件路径")
    args = parser.parse_args()

    template_path = Path(args.template)
    config_path = Path(args.config)
    output_path = Path(args.output)

    if not template_path.exists():
        print(f"错误: 模板文件不存在: {template_path}", file=sys.stderr)
        sys.exit(1)
    if not config_path.exists():
        print(f"错误: 配置文件不存在: {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    config_dir = config_path.parent

    # 重定向 print 到 stderr
    old_stdout = sys.stdout
    sys.stdout = sys.stderr

    # 构建图表配置
    chart_configs = {}
    for chart_name, chart_def in config.get("chart_configs", {}).items():
        print(f"构建图表配置: {chart_name}")
        chart_configs[chart_name] = build_chart_config(chart_name, chart_def, config_dir)

    # 执行替换
    text_data = config.get("text_data", {})
    replacer = TemplateReplacer(template_path)
    replacer.replace(data=text_data, chart_configs=chart_configs)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    replacer.save(output_path)

    sys.stdout = old_stdout
    print(json.dumps({"status": "ok", "output": str(output_path)}))


if __name__ == "__main__":
    main()
