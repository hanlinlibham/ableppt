"""
图表推荐引擎

基于 DataFrame 列特征分析，自动推荐图表类型/轴分配/数轴格式，
产出可直接传入 create_combo_chart() 的完整配置。

纯规则引擎，确定性输出，可通过 overrides 覆盖任何推荐。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import pandas as pd

from ..chart_builder.styles import StyleConfig, DEFAULT_STYLE_CONFIG
from ..chart_builder.layout import (
    ChartLayoutConfig, LegendConfig, ValueAxisConfig,
)
from .profiler import DataFrameProfiler, ColumnProfile


@dataclass
class ChartRecommendation:
    """图表推荐结果 — 可直接消费的完整配置"""

    categories_col: str
    series_config: List[Dict]
    layout_config: ChartLayoutConfig
    style_config: StyleConfig

    def to_kwargs(self) -> Dict:
        """解包为 composer.add_page / create_combo_chart 可消费的参数字典"""
        return {
            "categories_col": self.categories_col,
            "series_config": self.series_config,
            "layout_config": self.layout_config,
            "style_config": self.style_config,
        }


class ChartAdvisor:
    """图表推荐引擎 — 分析 DataFrame 并产出完整图表配置"""

    @classmethod
    def suggest(
        cls,
        df: pd.DataFrame,
        purpose: Optional[str] = None,
        style_profile=None,
        title: Optional[str] = None,
        overrides: Optional[Dict] = None,
    ) -> ChartRecommendation:
        """
        分析 DataFrame 并推荐图表配置

        Args:
            df: 待绘图的 DataFrame
            purpose: 图表用途描述（预留，当前未使用）
            style_profile: StyleProfile 实例（来自 StyleExtractor）。
                          如提供，用其样式替代默认样式。
            title: 图表标题
            overrides: 覆盖字典，可覆盖推荐的任何字段。支持的 key:
                - "categories_col": str
                - "series_config": List[Dict] (完全替换)
                - "series_overrides": Dict[str, Dict] (按列名覆盖单个系列)
                - "layout_config": ChartLayoutConfig (完全替换)
                - "style_config": StyleConfig (完全替换)

        Returns:
            ChartRecommendation 实例
        """
        overrides = overrides or {}

        # 1. 分析列特征
        profiles = DataFrameProfiler.profile(df)

        # 2. 确定分类列
        categories_col = overrides.get(
            "categories_col",
            cls._pick_categories_col(profiles, df)
        )

        # 3. 构建系列配置
        if "series_config" in overrides:
            series_config = overrides["series_config"]
        else:
            series_config = cls._build_series_config(
                profiles, categories_col, overrides.get("series_overrides")
            )

        # 4. 构建布局配置
        if "layout_config" in overrides:
            layout_config = overrides["layout_config"]
        else:
            layout_config = cls._build_layout_config(
                profiles, series_config, title
            )

        # 5. 样式配置
        if "style_config" in overrides:
            style_config = overrides["style_config"]
        elif style_profile is not None:
            style_config = style_profile.to_style_config()
        else:
            style_config = DEFAULT_STYLE_CONFIG

        return ChartRecommendation(
            categories_col=categories_col,
            series_config=series_config,
            layout_config=layout_config,
            style_config=style_config,
        )

    @classmethod
    def _pick_categories_col(cls, profiles: List[ColumnProfile],
                              df: pd.DataFrame) -> str:
        """选择分类列（datetime 优先，其次是字符串列，最后是第一列）"""
        # 优先：datetime 列
        for p in profiles:
            if p.is_date:
                return p.name

        # 其次：字符串列
        for p in profiles:
            if p.dtype == "str":
                return p.name

        # 最后：第一列
        return df.columns[0]

    @classmethod
    def _build_series_config(
        cls,
        profiles: List[ColumnProfile],
        categories_col: str,
        series_overrides: Optional[Dict[str, Dict]] = None,
    ) -> List[Dict]:
        """根据列特征构建 series_config"""
        series_overrides = series_overrides or {}
        config = []

        for p in profiles:
            # 跳过分类列
            if p.name == categories_col:
                continue
            # 跳过非图表列
            if p.suggested_axis == "category":
                continue

            entry = {
                "key": p.name,
                "name": p.name,
                "type": p.suggested_chart_type,
                "axis": p.suggested_axis,
            }

            # 应用列级覆盖
            if p.name in series_overrides:
                entry.update(series_overrides[p.name])

            config.append(entry)

        return config

    @classmethod
    def _build_layout_config(
        cls,
        profiles: List[ColumnProfile],
        series_config: List[Dict],
        title: Optional[str],
    ) -> ChartLayoutConfig:
        """根据系列配置自动推导布局"""

        # 从 profiles 建立 name → profile 映射
        profile_map = {p.name: p for p in profiles}

        # 主轴格式：取第一个 primary 系列的推荐格式
        primary_format = None
        for sc in series_config:
            if sc.get("axis") == "primary":
                p = profile_map.get(sc["key"])
                if p and p.suggested_number_format:
                    primary_format = p.suggested_number_format
                    break

        # 次轴格式：取第一个 secondary 系列的推荐格式
        secondary_format = None
        for sc in series_config:
            if sc.get("axis") == "secondary":
                p = profile_map.get(sc["key"])
                if p and p.suggested_number_format:
                    secondary_format = p.suggested_number_format
                    break

        # 构建 legend
        legend_cfg = LegendConfig(
            position=LegendConfig.TOP,
            font_size_pt=9,
            font_name="黑体",
        )

        # 构建主轴
        value_axis_cfg = ValueAxisConfig(
            number_format=primary_format,
            font_size_pt=9,
            font_name="黑体",
            has_major_gridlines=False,
        )

        # 构建次轴（仅当有 secondary 系列时）
        secondary_cfg = None
        has_secondary = any(sc.get("axis") == "secondary" for sc in series_config)
        if has_secondary:
            secondary_cfg = ValueAxisConfig(
                number_format=secondary_format,
                font_size_pt=9,
                font_name="黑体",
                has_major_gridlines=False,
            )

        return ChartLayoutConfig(
            title=title,
            legend_config=legend_cfg,
            value_axis_config=value_axis_cfg,
            secondary_value_axis_config=secondary_cfg,
        )
