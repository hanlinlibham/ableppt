# API Contracts — 函数签名与数据接口

> 本文档是 pptfi 所有公开 API 的精确合约。编码前必读。

---

## 1. create_combo_chart()

```python
from pptfi.chart_builder.api import create_combo_chart

create_combo_chart(
    slide,                          # pptx Slide 对象
    df,                             # pandas DataFrame
    categories_col,                 # str — X轴列名
    series_config,                  # List[Dict] — 见下方格式
    position=(Inches(1), Inches(2)),  # (left, top) 元组
    size=(Inches(8), Inches(4.5)),    # (width, height) 元组
    style_config=None,              # StyleConfig 实例
    layout_config=None,             # ChartLayoutConfig 实例
)
```

### series_config 格式（4个字段全部必需）

```python
series_config = [
    {"key": "营收(亿)", "name": "营收(亿)", "type": "bar", "axis": "primary"},
    {"key": "增长率",   "name": "增长率",   "type": "line", "axis": "secondary"},
]
```

| 字段 | 说明 | 可选值 |
|------|------|--------|
| `key` | DataFrame 列名 | 必须与 df 列名完全一致 |
| `name` | 图表图例显示名 | 任意字符串 |
| `type` | 图表类型 | `"bar"`, `"line"`, `"area"` |
| `axis` | 轴分配 | `"primary"` (左轴), `"secondary"` (右轴) |

**常见错误**：用 `column` 代替 `key`、用 `chart_type` 代替 `type`、缺少 `name` 字段。

---

## 2. StyleConfig

```python
from pptfi.chart_builder.styles import StyleConfig

StyleConfig(
    color_scheme="tech_blue",   # 配色方案名（见 COLOR_SCHEMES）
    line_width_pt=2.0,          # 线宽 pt: 0.5/0.75/1.0/1.5/2.0/2.25/3.0
    marker_style="none",        # "none"/"circle"/"square"/"diamond"/"triangle"
    marker_size=5,              # 标记点大小 pt
)
```

---

## 3. ChartLayoutConfig

```python
from pptfi.chart_builder.layout import (
    ChartLayoutConfig, LegendConfig, ValueAxisConfig, CategoryAxisConfig,
)
from pptfi.chart_builder.date_axis import MONTHLY_TICKS  # DateAxisConfig 预设

ChartLayoutConfig(
    title=None,                         # str — 图表内标题（通常 None，标题放页面上）
    legend_config=LegendConfig(...),    # 图例
    category_axis_config=CategoryAxisConfig(...),  # 横轴
    value_axis_config=ValueAxisConfig(...),        # 主值轴（左）
    secondary_value_axis_config=ValueAxisConfig(...),  # 次值轴（右）
    date_axis_config=MONTHLY_TICKS,     # DateAxisConfig 日期轴（优先于 category_axis_config）
)
```

**关键：`date_axis_config` 在 ChartLayoutConfig 上，不在 CategoryAxisConfig 上。**

### LegendConfig

```python
LegendConfig(
    position=LegendConfig.TOP,   # TOP/BOTTOM/LEFT/RIGHT/CORNER
    font_size_pt=9,
    font_name="黑体",
)
```

### CategoryAxisConfig

```python
CategoryAxisConfig(
    is_date_axis=False,          # 是否日期轴
    major_unit_days=None,        # 主刻度天数
    font_name="黑体",
    font_size_pt=10,
    number_format=None,          # 如 "yyyy-mm-dd"
)
```

**没有 `date_axis` 参数。** 日期轴预设传入 `ChartLayoutConfig(date_axis_config=...)`。

### ValueAxisConfig

```python
ValueAxisConfig(
    number_format="#,##0",       # 数字格式
    font_name="黑体",
    font_size_pt=9,
)
```

### 日期轴预设

| 预设 | 间隔 | 适用 |
|------|------|------|
| `DAILY_TICKS` | 1天 | 1-30天 |
| `WEEKLY_TICKS` | 7天 | 1-6月 |
| `BIWEEKLY_TICKS` | 14天 | 季度 |
| `MONTHLY_TICKS` | 1月 | 年度 |
| `QUARTERLY_TICKS` | 3月 | 多年 |
| `YEARLY_TICKS` | 1年 | 长期 |

---

## 4. PageComposer

```python
from pptfi.composer import PageComposer

composer = PageComposer(theme="jp_finance")  # 主题名（从 theme 自动读取 slide_w/slide_h）

# 方式一：注册布局
composer.add_page("layout_name", data_dict)
# 自动注入页眉（add_page_header）和页脚（add_page_footer）
# 封面/结论/分隔页除外（title_dark, title_light, conclusion_dark, section_divider）
# 页脚来源从 data["footnote"] 获取（兼容回退 data["source"]），页码自动计算

# 方式二：自定义渲染（无 data）
composer.add_custom_page(render_fn)
# render_fn 签名: def render_fn(slide, theme) → None   ← 只有 2 个参数

# 方式三：自定义渲染（带 data）
composer.add_custom_page(render_fn, data=my_dict)
# render_fn 签名: def render_fn(slide, data, theme) → None  ← 3 个参数

composer.save("output.pptx")          # 自动运行 DeckLinter
composer.save("output.pptx", lint=False)  # 跳过审计
```

**常见错误**：`render_fn(slide, prs, theme)` — 没有 `prs` 参数。

---

## 4.1 ChartJunkCleaner（自动，无需手动调用）

`ChartBuilder.build()` 完成后自动执行清洗：
- 移除图表外边框、plotArea 边框
- Y 轴网格线 → 极浅灰色虚线 (`#E8E8E8`, 0.5pt, dot)
- 坐标轴刻度线 → none
- 图例框边框/填充 → 移除

手动使用：
```python
from pptfi.chart_builder.cleaner import clean_chart, ChartJunkCleaner
clean_chart(chart)  # 便捷函数
# 或
ChartJunkCleaner(chart).clean()  # 完整控制
```

---

## 4.2 DeckLinter（保存时自动运行）

```python
from pptfi.qa.deck_linter import DeckLinter

linter = DeckLinter("output.pptx")
report = linter.run()
linter.print_summary(report)        # 终端摘要
linter.to_json(report)              # JSON 字符串
linter.write_to_notes(report)       # 写入 PPT slide notes
```

检查规则：`header_missing`, `footer_missing`, `bounds_overflow`（动态阈值，适配 4:3/16:9）, `title_size_overflow`, `chart_misaligned`, `insight_missing`（图表页无结论先行文本）

---

## 4.3 页眉/页脚 Helpers

```python
from pptfi.composer.helpers import add_page_header, add_page_footer

add_page_header(slide, "页面标题", theme)
# 输出: 16pt 标题 + 全宽 primary 色分隔线 (使用 theme tokens: page_title_size, header_y, divider_y)

add_page_footer(slide, theme, source="Wind, 公司年报", page_num=3, brand="PPT Station")
# 输出: 左侧来源 + 右侧页码/品牌 (使用 theme tokens: footer_size, footer_y)
```

**注意**：注册布局自动调用，custom_page 不自动调用（需手动使用）。

---

## 4.4 PptEngine — Job JSON 渲染

### source / datasource / footnote 语义

| 字段 | 位置 | 语义 |
|------|------|------|
| `datasource` | 顶层或 left/right/top/bottom 嵌套 | **新 canonical key**，始终视为 datasource 引用 |
| `source` | 顶层或 left/right/top/bottom 嵌套 | 值匹配已知 datasource 时解析为 DataFrame 并 pop；不匹配时保留为脚注文本（兼容回退） |
| `footnote` | 顶层 | 页脚来源文本，auto-footer 优先读取 |

**推荐**：顶层脚注用 `footnote`，嵌套 datasource 引用用 `source` 或 `datasource`。

### default_layout_config（Job 级）

```json
{
  "default_layout_config": {
    "legend_config": {"font_size_pt": 8, "font_name": "黑体"},
    "value_axis_config": {"font_size_pt": 8, "font_name": "黑体"},
    "secondary_value_axis_config": {"font_size_pt": 8}
  }
}
```

- **作用**：所有含 `df` 的图表页（包括 left/right 嵌套）自动继承此配置
- **合并策略**：浅合并，per-page `layout_config` 的 key 覆盖默认 key（整个子对象替换，非字段级合并）
- **无 `df` 的页面**（kpi_cards, bullet_points 等）不注入
- **Optional**：不提供时不注入，完全兼容旧 JSON

---

## 5. 布局数据接口

### title_dark / title_light

```python
{"title": "标题", "subtitle": "副标题"}  # subtitle 可选
```

### kpi_cards

```python
{
    "title": "页面标题",
    "footnote": "来源: Wind, 公司年报",  # 可选，auto-footer 渲染
    "cards": [
        {"label": "指标名", "value": "数值", "change": "+5.9%"},  # change/note 可选
    ]
}
```

**常见错误**：用 `title` 代替 `label`，用 `unit` 作为单独字段（应把单位写进 `value`）。

### bullet_points

```python
{
    "title": "页面标题",
    "footnote": "来源: 行业报告",  # 可选，auto-footer 渲染
    "items": [
        {"icon": "01", "label": "要点标题", "desc": "要点描述"},
    ]
}
```

**常见错误**：用 `title` 代替 `label`，用 `body` 代替 `desc`。

### chart_full / chart_text

```python
{
    "title": "页面标题",
    "df": df,                    # pandas DataFrame（引擎从 source/datasource 解析）
    "categories_col": "日期",    # X轴列名
    "series_config": [...],      # 同 create_combo_chart 的 series_config
    "insight": "结论先行文本...",  # 可选，2-3行结论摘要（header 和图表之间）
    "footnote": "来源: Wind",    # 可选，auto-footer 渲染
    "style_config": StyleConfig(...),      # 可选
    "layout_config": ChartLayoutConfig(...), # 可选（可由 default_layout_config 继承）
}
```

**Job JSON 中**：`df` 由 `source`/`datasource` 字段解析，不直接传 DataFrame。

### two_charts（50/50 双图）

```python
{
    "title": "页面标题",
    "left_title": "左图标题",    # 可选
    "right_title": "右图标题",   # 可选
    "insight": "结论先行文本...", # 可选，header 和图表之间
    "footnote": "来源: Wind",    # 可选，auto-footer 渲染
    "left": {
        "df": df1, "categories_col": "日期", "series_config": [...],
        "style_config": ..., "layout_config": ...,
    },
    "right": {
        "df": df2, "categories_col": "日期", "series_config": [...],
        "style_config": ..., "layout_config": ...,
    },
}
```

**Job JSON 中**：left/right 内用 `source`/`datasource` 指向数据源，`footnote` 放顶层。

### two_charts_vertical（上下双图）

```python
{
    "title": "页面标题",
    "top_title": "上图标题",     # 可选
    "bottom_title": "下图标题",  # 可选
    "insight": "结论先行文本...", # 可选，header 和上图之间
    "footnote": "来源: Wind",    # 可选，auto-footer 渲染
    "top": {
        "df": df1, "categories_col": "日期", "series_config": [...],
        "style_config": ..., "layout_config": ...,
    },
    "bottom": {
        "df": df2, "categories_col": "日期", "series_config": [...],
        "style_config": ..., "layout_config": ...,
    },
}
```

**设计特点**：两个图表均使用全宽（最大化时间轴跨度），上下等高，中间 0.15" 间隔。适合共享日期轴的趋势对比。

**Job JSON 中**：top/bottom 内用 `source`/`datasource` 指向数据源。

### chart_table（左图右表）

```python
{
    "title": "页面标题",
    "df": df,                    # 图表数据
    "categories_col": "日期",
    "series_config": [...],
    "headers": ["指标", "值"],   # 表格表头（可省略，从 table_df/df 自动提取）
    "rows": [["A", "1"], ...],   # 表格数据行（可省略，从 table_df/df 自动转换）
    "table_df": table_df,        # 可选，表格数据 DataFrame（自动转为 headers/rows）
    "insight": "结论先行文本...", # 可选
    "chart_ratio": 0.62,         # 可选，图表宽度占比（默认 0.62）
    "footnote": "来源: Wind",    # 可选
}
```

**设计特点**：左图表 (62%) + 右表格 (38%)，表格使用投行级样式（ib_style）。适合趋势可视化 + 截面数据快照组合。

**Job JSON 中**：图表数据用 `source`/`datasource`，表格数据用 `table_df` 对应的 datasource 或直接传 `headers`/`rows`。

### comparison_table

```python
{
    "title": "标题",
    "headers": ["指标", "公司A", "公司B"],
    "rows": [["营收", "100亿", "80亿"], ...],
    "highlight_row": 0,       # 可选，高亮行索引
    "highlight_cols": [1, 2], # 可选，高亮列索引列表
    "footnote": "来源: Wind, 公司年报",  # 可选，auto-footer 渲染
}
```

表格默认启用投行级样式（`ib_style=True`）：无垂直边框、数值列自动右对齐、斑马纹。
**注意**：footnote 统一由 auto-footer 渲染（不再在表格下方手动添加）。

### section_divider

```python
{"title": "章节名", "number": "01"}
```

### conclusion_dark（左右分栏布局）

```python
{
    "verdict": "核心结论（必填）",
    "title": "结论",                          # 可选，默认"结论"
    "score": "8/10",                          # 可选，左侧顶部大字
    "conclusions": [                          # 可选，左侧要点列表（最多3条）
        {"title": "高壁垒", "desc": "品牌+渠道双重优势"},
        {"title": "稳增长", "desc": "营收年化增速 20%+"},
    ],
    "items": [{"label": "评分", "value": "8/10"}],  # 可选，右侧指标卡片
    "risk": "风险提示文字",                     # 可选，右侧底部
    "footnote": "脚注",                        # 可选
}
```

布局结构：左侧 55%（score + verdict + conclusions）| 右侧 45%（items 卡片 + risk）

**常见错误**：用 `summary` 代替 `verdict`，用 `cards` 代替 `items`。`conclusions`（左侧要点）和 `items`（右侧指标）是不同字段。

---

## 6. 完整示例：双轴组合图（自定义页面）

```python
from pptx.util import Inches
from pptfi.composer import PageComposer
from pptfi.chart_builder.api import create_combo_chart
from pptfi.chart_builder.styles import StyleConfig
from pptfi.chart_builder.layout import (
    ChartLayoutConfig, LegendConfig, ValueAxisConfig, CategoryAxisConfig,
)
from pptfi.chart_builder.date_axis import MONTHLY_TICKS

def render_my_chart(slide, theme):
    # 页眉（自动: 16pt 标题 + 全宽分隔线）
    from pptfi.composer.helpers import add_page_header, add_page_footer
    add_page_header(slide, "股价走势（2024-2026）", theme)

    # 图表 — style_config 可省略，自动使用主题配色
    m = theme["margin"]
    content_y = theme.get("content_y", 1.00)
    footer_y = theme.get("footer_y", 7.10)
    create_combo_chart(
        slide, price_df, categories_col="日期",
        series_config=[
            {"key": "成交量", "name": "成交量", "type": "bar", "axis": "secondary"},
            {"key": "收盘价", "name": "收盘价", "type": "line", "axis": "primary"},
        ],
        position=(Inches(m), Inches(content_y)),
        size=(Inches(12.133), Inches(footer_y - content_y - 0.3)),
        # style_config 省略 — 自动使用 jp_finance 配色
        layout_config=ChartLayoutConfig(
            legend_config=LegendConfig(position=LegendConfig.TOP, font_size_pt=9, font_name="黑体"),
            value_axis_config=ValueAxisConfig(number_format="#,##0.00", font_name="黑体", font_size_pt=9),
            secondary_value_axis_config=ValueAxisConfig(number_format="#,##0", font_name="黑体", font_size_pt=9),
            date_axis_config=MONTHLY_TICKS,
        ),
    )
    # 页脚（来源 + 页码）
    add_page_footer(slide, theme, source="Tushare, Wind")

composer = PageComposer(theme="jp_finance")
composer.add_custom_page(render_my_chart)
composer.save("output.pptx")  # 自动运行 DeckLinter
```
