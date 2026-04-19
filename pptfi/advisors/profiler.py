"""
DataFrame 列特征分析器

自动分析 DataFrame 中每列的数据特征，推荐图表类型、轴分配和数字格式。
针对中文金融/养老金领域的列名模式优化。
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional

import pandas as pd


@dataclass
class ColumnProfile:
    """单列的特征画像"""
    name: str
    dtype: str                          # "datetime" / "float" / "int" / "str"
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    is_percentage: bool = False         # 值域 in [-2, 2] 或列名含百分比关键词
    is_index: bool = False              # 列名含 指数/基准
    is_volume: bool = False             # 列名含 规模/市值/营收
    is_price: bool = False              # 列名含 价格/收盘价/净值
    is_date: bool = False               # datetime 类型或列名匹配日期模式
    suggested_chart_type: str = "line"
    suggested_axis: str = "primary"
    suggested_number_format: Optional[str] = None


# ============================================================================
# 列名匹配模式 — 从具体到通用排列
# ============================================================================

# 日期列检测
_DATE_PATTERNS = re.compile(
    r'日期|date|trade_date|交易日|报告期|年份|月份|季度|时间',
    re.IGNORECASE
)

# 百分比类列（折线 + 主轴 + 0%）
_PCT_PATTERNS = re.compile(
    r'累计收益率|年化收益率|滚动收益率|超额收益|'
    r'收益率|回报率|利率|'
    r'ROE|ROA|净利率|毛利率|利润率|'
    r'波动率|增长率|涨跌幅|换手率|'
    r'占比|比例|比率|百分比|pct',
    re.IGNORECASE
)

# 指数类列（柱状 + 次轴 + #,##0）
_INDEX_PATTERNS = re.compile(
    r'指数|基准|benchmark|index(?!_)',
    re.IGNORECASE
)

# 价格类列（柱状 + 次轴 + #,##0）
_PRICE_PATTERNS = re.compile(
    r'收盘价|开盘价|最高价|最低价|'
    r'价格|股价|净值|单位净值|NAV|close|price',
    re.IGNORECASE
)

# 规模类列（柱状 + 次轴 + #,##0）
_VOLUME_PATTERNS = re.compile(
    r'规模|市值|成交额|成交量|'
    r'营收|营业收入|利润|总资产|净资产|'
    r'volume|amount|market_cap|revenue',
    re.IGNORECASE
)


class DataFrameProfiler:
    """DataFrame 列特征分析器"""

    @classmethod
    def profile(cls, df: pd.DataFrame) -> List[ColumnProfile]:
        """
        分析 DataFrame 所有列的特征

        Args:
            df: 待分析的 DataFrame

        Returns:
            每列的特征画像列表
        """
        profiles = []
        for col in df.columns:
            profiles.append(cls._profile_column(df, col))
        return profiles

    @classmethod
    def _profile_column(cls, df: pd.DataFrame, col: str) -> ColumnProfile:
        """分析单列"""
        series = df[col]
        dtype = cls._detect_dtype(series, col)

        profile = ColumnProfile(name=col, dtype=dtype)

        # 日期列
        if dtype == "datetime" or _DATE_PATTERNS.search(col):
            profile.is_date = True
            profile.suggested_chart_type = "category"
            profile.suggested_axis = "category"
            profile.suggested_number_format = None
            return profile

        # 字符串列 — 不参与图表
        if dtype == "str":
            profile.suggested_chart_type = "category"
            profile.suggested_axis = "category"
            return profile

        # 数值列：计算值域
        numeric = pd.to_numeric(series, errors="coerce")
        profile.min_value = float(numeric.min()) if not numeric.isna().all() else None
        profile.max_value = float(numeric.max()) if not numeric.isna().all() else None

        # 按模式匹配优先级分类
        cls._classify_by_name(profile, col)

        # 如果名称未匹配到任何模式，用值域推断
        if not (profile.is_percentage or profile.is_index or
                profile.is_volume or profile.is_price):
            cls._classify_by_values(profile)

        return profile

    @classmethod
    def _detect_dtype(cls, series: pd.Series, col: str) -> str:
        """检测列的数据类型"""
        if pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        if pd.api.types.is_integer_dtype(series):
            return "int"
        if pd.api.types.is_float_dtype(series):
            return "float"
        # 尝试检测字符串格式的日期
        if series.dtype == object and _DATE_PATTERNS.search(col):
            try:
                pd.to_datetime(series.dropna().head(5))
                return "datetime"
            except (ValueError, TypeError):
                pass
        if series.dtype == object:
            return "str"
        return "float"

    @classmethod
    def _classify_by_name(cls, profile: ColumnProfile, col: str):
        """按列名模式分类（优先级：具体 > 通用）"""

        # 百分比类 → line + primary + 0%
        if _PCT_PATTERNS.search(col):
            profile.is_percentage = True
            profile.suggested_chart_type = "line"
            profile.suggested_axis = "primary"
            profile.suggested_number_format = "0%"
            return

        # 指数类 → bar + secondary + #,##0
        if _INDEX_PATTERNS.search(col):
            profile.is_index = True
            profile.suggested_chart_type = "bar"
            profile.suggested_axis = "secondary"
            profile.suggested_number_format = "#,##0"
            return

        # 价格类 → bar + secondary + #,##0
        if _PRICE_PATTERNS.search(col):
            profile.is_price = True
            profile.suggested_chart_type = "bar"
            profile.suggested_axis = "secondary"
            profile.suggested_number_format = "#,##0"
            return

        # 规模类 → bar + secondary + #,##0
        if _VOLUME_PATTERNS.search(col):
            profile.is_volume = True
            profile.suggested_chart_type = "bar"
            profile.suggested_axis = "secondary"
            profile.suggested_number_format = "#,##0"
            return

    @classmethod
    def _classify_by_values(cls, profile: ColumnProfile):
        """按值域推断类型"""
        if profile.min_value is not None and profile.max_value is not None:
            # 值域在 [-2, 2] → 可能是百分比
            if -2.0 <= profile.min_value and profile.max_value <= 2.0:
                profile.is_percentage = True
                profile.suggested_chart_type = "line"
                profile.suggested_axis = "primary"
                profile.suggested_number_format = "0%"
                return

        # 通用数值 → line + primary
        profile.suggested_chart_type = "line"
        profile.suggested_axis = "primary"
        profile.suggested_number_format = "General"
