#!/usr/bin/env python3
"""查询 ableppt 包中所有可用预设

用法:
    python list_presets.py [--color-schemes | --date-axis | --chart-presets | --all]

输出 (stdout): JSON
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def get_color_schemes():
    from ableppt.chart_builder.styles import COLOR_SCHEMES
    return {name: colors for name, colors in COLOR_SCHEMES.items()}


def get_date_axis_presets():
    from ableppt.chart_builder.date_axis import (
        DAILY_TICKS, WEEKLY_TICKS, BIWEEKLY_TICKS,
        MONTHLY_TICKS, QUARTERLY_TICKS, YEARLY_TICKS,
    )
    presets = {
        "DAILY_TICKS": DAILY_TICKS,
        "WEEKLY_TICKS": WEEKLY_TICKS,
        "BIWEEKLY_TICKS": BIWEEKLY_TICKS,
        "MONTHLY_TICKS": MONTHLY_TICKS,
        "QUARTERLY_TICKS": QUARTERLY_TICKS,
        "YEARLY_TICKS": YEARLY_TICKS,
    }
    result = {}
    for name, cfg in presets.items():
        result[name] = {
            "base_unit": cfg.base_unit,
            "major_unit": cfg.major_unit,
            "major_unit_scale": cfg.major_unit_scale,
            "number_format": cfg.number_format,
        }
    return result


def get_chart_presets():
    from ableppt.template.chart_presets import CHART_PRESET_FUNCTIONS
    return list(CHART_PRESET_FUNCTIONS.keys())


def main():
    parser = argparse.ArgumentParser(description="查询所有可用预设")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--color-schemes", action="store_true", help="仅显示配色方案")
    group.add_argument("--date-axis", action="store_true", help="仅显示日期轴预设")
    group.add_argument("--chart-presets", action="store_true", help="仅显示图表预设")
    group.add_argument("--all", action="store_true", default=True, help="显示全部（默认）")
    args = parser.parse_args()

    result = {}

    if args.color_schemes:
        result["color_schemes"] = get_color_schemes()
    elif args.date_axis:
        result["date_axis_presets"] = get_date_axis_presets()
    elif args.chart_presets:
        result["chart_presets"] = get_chart_presets()
    else:
        result["color_schemes"] = get_color_schemes()
        result["date_axis_presets"] = get_date_axis_presets()
        result["chart_presets"] = get_chart_presets()

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
