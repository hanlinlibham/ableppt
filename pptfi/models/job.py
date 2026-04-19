"""
任务配置数据模型
"""

from typing import Dict, List, Any, Optional, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class DataSource(BaseModel):
    """数据源配置"""

    type: Literal["csv", "xlsx", "sql", "http", "tushare"]
    # CSV/Excel 配置
    path: Optional[str] = None
    encoding: Optional[str] = "utf-8"
    sheet_name: Optional[str] = None
    # SQL 配置
    conn: Optional[str] = None
    query: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    # HTTP 配置
    url: Optional[str] = None
    method: Optional[str] = "GET"
    headers: Optional[Dict[str, str]] = None
    # Tushare 配置
    api_name: Optional[str] = None  # pro_bar, index_daily, etc.
    ts_code: Optional[str] = None  # 股票/指数代码
    index_code: Optional[str] = None  # 指数代码
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    fields: Optional[List[str]] = None


class TransformOp(BaseModel):
    """数据转换操作"""

    type: Literal["groupby", "pivot", "merge", "compute", "filter", "sort", "rename"]
    # groupby 参数
    by: Optional[List[str]] = None
    agg: Optional[Dict[str, str]] = None
    # pivot 参数
    index: Optional[str] = None
    columns: Optional[str] = None
    values: Optional[str] = None
    # merge 参数
    on: Optional[str | List[str]] = None
    how: Optional[str] = "inner"
    # compute 参数
    expr: Optional[str] = None
    output_col: Optional[str] = None
    # filter 参数
    condition: Optional[str] = None
    # sort 参数
    sort_by: Optional[List[str]] = None
    ascending: Optional[bool] = True
    # rename 参数
    map: Optional[Dict[str, str]] = None


class Transform(BaseModel):
    """数据转换配置"""

    from_: str | List[str] = Field(..., alias="from")
    ops: List[TransformOp]


class ChartSeriesSpec(BaseModel):
    """图表系列配置"""

    key: str  # DataFrame 列名
    name: str  # 显示名称
    type: Optional[Literal["bar", "line", "area"]] = None  # 图表类型（composer 模式用）
    axis: Optional[Literal["primary", "secondary"]] = None
    slot: Optional[int] = None  # 对齐模板系列顺序


class ChartSpec(BaseModel):
    """图表配置"""

    mode: Literal["create", "update", "excel_embedded"] = "update"
    target: Optional[str] = None  # 模板中的图表名称（update 模式）
    target_placeholder: Optional[str] = None  # 占位符名称（create/excel_embedded 模式）
    chart_type: Optional[str] = None  # XL_CHART_TYPE（create 模式）或 Excel 图表类型
    source: str  # 数据源名称
    categories: str  # 分类列名
    series: List[ChartSeriesSpec]
    respect_template_types: bool = True
    series_order_strict: bool = True

    def has_secondary_axis(self) -> bool:
        """检查是否有次坐标轴系列"""
        return any(s.axis == "secondary" for s in self.series)


class TableSpec(BaseModel):
    """表格配置"""

    target: str  # 模板中的表格名称
    source: str  # 数据源名称
    columns: List[str]
    header: Optional[List[str]] = None
    number_format: Optional[Dict[str, str]] = None


class TextSpec(BaseModel):
    """文本配置"""

    target: str  # 模板中的文本框名称
    value: str  # 支持 Jinja2 模板语法


class SlideSpec(BaseModel):
    """幻灯片配置"""

    id: str
    layout: Optional[str] = None  # 版式名称
    texts: Optional[List[TextSpec]] = None
    tables: Optional[List[TableSpec]] = None
    charts: Optional[List[ChartSpec]] = None


class TemplateSpec(BaseModel):
    """模板配置"""

    path: str
    master: Optional[str] = None
    notes: Optional[str] = None


class OutputSpec(BaseModel):
    """输出配置"""

    path: str
    overwrite: bool = True
    add_metadata: bool = True  # 是否添加生成信息到元数据


class ComposerPageSpec(BaseModel):
    """Composer 模式的页面规格"""

    layout: str  # LAYOUT_REGISTRY 中的布局名称
    data: Dict[str, Any]  # 传给布局函数的 data dict


class Job(BaseModel):
    """完整的任务配置 — 支持 template 和 composer 两种模式"""

    model_config = ConfigDict(populate_by_name=True)

    mode: Literal["template", "composer"] = "template"
    # template 模式字段
    template: Optional[TemplateSpec] = None
    slides: Optional[List[SlideSpec]] = None
    # composer 模式字段
    theme: Optional[str] = None  # THEMES 中的名称
    aspect_ratio: Optional[str] = None  # "4:3" 或 "16:9"（默认 16:9）
    pages: Optional[List[ComposerPageSpec]] = None
    # 共用字段
    datasources: Dict[str, DataSource] = Field(default_factory=dict)
    transforms: Optional[Dict[str, Transform]] = None
    params: Optional[Dict[str, Any]] = None
    default_layout_config: Optional[Dict[str, Any]] = None  # 图表布局默认配置
    output: OutputSpec

    @model_validator(mode="after")
    def check_mode_fields(self):
        if self.mode == "template":
            if not self.template:
                raise ValueError("template 模式必须提供 template 字段")
            if not self.slides:
                raise ValueError("template 模式必须提供 slides 字段")
        elif self.mode == "composer":
            if not self.pages:
                raise ValueError("composer 模式必须提供 pages 字段")
        return self
