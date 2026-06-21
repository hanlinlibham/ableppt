# 图表配置完整参考

## 兼容层说明

`pptfi.chart_builder` 现在是兼容入口，实际实现来自同工作区的 `ablechart`。因此这里的 chart config 仍然适用于 `pptfi`，但底层执行逻辑应按 `ablechart` 能力理解。

- 兼容状态可通过 `pptfi chart-engine-info` 查看
- Flow A / SDK 中出现的 `chart_builder` API，都是这层兼容 facade
- 瀑布图当前建议走单页 chart-engine spec 或 SDK `create_waterfall_chart`，不是 Job/composer 主路径

## config.json 完整格式

```json
{
  "text_data": {
    "标题": "2024年度投资报告",
    "日期": "2024-12-05",
    "组合名": "稳健增长组合"
  },
  "chart_configs": {
    "图表名": {
      "csv_path": "data.csv",
      "categories_col": "日期",
      "series_config": [...],
      "style": {...},
      "layout": {...}
    }
  }
}
```

## series_config 系列配置

每个系列是一个字典:

```json
[
  {"key": "沪深300指数", "name": "沪深300指数", "type": "bar", "axis": "secondary"},
  {"key": "组合收益率", "name": "组合收益率", "type": "line", "axis": "primary"}
]
```

| 字段 | 说明 | 可选值 |
|------|------|--------|
| `key` | CSV 中的列名 | 任意字符串 |
| `name` | 图例中的显示名 | 任意字符串 |
| `type` | 图表类型 | `bar`, `line`, `area` |
| `axis` | 绑定轴 | `primary`(左轴), `secondary`(右轴) |

## style 样式配置

```json
{
  "color_scheme": "aim00",
  "line_width_pt": 2.0,
  "marker_style": "none"
}
```

| 字段 | 说明 | 可选值 |
|------|------|--------|
| `color_scheme` | 颜色方案 | 见下方配色方案表 |
| `line_width_pt` | 折线宽度(pt) | `0.5`, `0.75`, `1.0`, `1.5`, `2.0`, `2.25`, `3.0` |
| `marker_style` | 标记点样式 | `none`, `circle`, `square`, `diamond`, `triangle` |
| `marker_size` | 标记点大小(pt) | 数字，默认 `5` |

### 配色方案完整表

| 名称 | 色值 (hex) | 说明 |
|------|-----------|------|
| `aim00` | `C0C0C0` `C00000` `305496` `808080` | 对比色：浅灰柱状图 + 深红折线 |
| `default` | `C00000` `0070C0` `ED7D31` `595959` `FF9999` `9DC3E6` `F4B183` `BFBFBF` | 深浅交替通用 |
| `dark_only` | `C00000` `0070C0` `ED7D31` `595959` | 深色系4色 |
| `light_only` | `FF9999` `9DC3E6` `F4B183` `BFBFBF` | 浅色系4色 |
| `red_series` | `C00000` `FF9999` | 深红+浅红 |
| `blue_series` | `0070C0` `9DC3E6` | 深蓝+浅蓝 |
| `orange_series` | `ED7D31` `F4B183` | 深橙+浅橙 |
| `gray_series` | `595959` `BFBFBF` | 深灰+浅灰 |

颜色按系列索引循环使用。

## layout 布局配置

```json
{
  "title": "组合2024年以来收益率走势图",
  "legend": {
    "position": "top",
    "font_size_pt": 9,
    "font_name": "黑体"
  },
  "value_axis": {
    "number_format": "0%",
    "font_size_pt": 9,
    "font_name": "黑体",
    "has_major_gridlines": false,
    "min_value": 0.0,
    "max_value": 1.0,
    "major_unit": 0.1
  },
  "secondary_value_axis": {
    "number_format": "#,##0",
    "font_size_pt": 9,
    "font_name": "黑体",
    "has_major_gridlines": false,
    "min_value": 2950,
    "max_value": 4450,
    "major_unit": 200
  },
  "date_axis": {
    "base_unit": "days",
    "major_unit": 30,
    "number_format": "yyyy/mm"
  }
}
```

### legend 图例

| 字段 | 说明 | 可选值 |
|------|------|--------|
| `position` | 位置 | `top`, `bottom`, `left`, `right`, `corner` |
| `font_size_pt` | 字体大小 | 数字 |
| `font_name` | 字体名 | `"黑体"`, `"宋体"` 等 |

### value_axis / secondary_value_axis 数值轴

| 字段 | 说明 | 示例 |
|------|------|------|
| `number_format` | 数字格式 | `"0%"`, `"#,##0"`, `"0.00"` |
| `font_size_pt` | 字体大小 | `9` |
| `font_name` | 字体名 | `"黑体"` |
| `has_major_gridlines` | 主网格线 | `true`/`false` |
| `min_value` | 轴最小值 | 数字（可选） |
| `max_value` | 轴最大值 | 数字（可选） |
| `major_unit` | 主刻度间隔 | 数字（可选） |

### date_axis 日期轴

| 字段 | 说明 | 示例 |
|------|------|------|
| `base_unit` | 基础单位 | `"days"`, `"months"`, `"years"` |
| `major_unit` | 主刻度间隔 | 数字（标签间隔数据点数）|
| `number_format` | 日期格式 | `"yyyy/mm"`, `"yyyy-mm-dd"`, `"mm-dd"` |

如果省略 `major_unit`，默认使用 `len(df) // 7`（约显示 7 个标签）。

### 日期轴预设

可在代码中直接使用预设，无需手动配置:

| 预设名 | 间隔 | 格式 | 适用数据量 |
|--------|------|------|-----------|
| `DAILY_TICKS` | 每天 | `mm-dd` | 1-30天 |
| `WEEKLY_TICKS` | 每周 | `yyyy-mm-dd` | 1-6个月 |
| `BIWEEKLY_TICKS` | 每两周 | `yyyy-mm-dd` | 季度 |
| `MONTHLY_TICKS` | 每月 | `yyyy-mm` | 年度 |
| `QUARTERLY_TICKS` | 每季度 | `yyyy-mm` | 多年 |
| `YEARLY_TICKS` | 每年 | `yyyy` | 长期 |

### 养老金图表预设

4 个内置预设函数，传入 DataFrame 即返回完整配置:

| 预设 | 函数 | 系列类型 | 所需 CSV 列 |
|------|------|----------|-------------|
| 当年收益率走势 | `get_chart1_config(df)` | bar(右)+line(左) | `分类`, `沪深300指数(收盘价)`, `组合收益率（左轴）` |
| 成立以来收益率 | `get_chart2_config(df)` | area(右)+line(左) | `分类`, `组合规模(万元)`, `累计收益率` |
| 权益仓位走势 | `get_chart3_config(df)` | area(右)+line(左) | `分类`, `沪深300指数(收盘价)`, `权益仓位（人社部口径）` |
| 久期走势 | `get_chart4_config(df)` | bar(右)+line(左) | `分类`, `中债新综合总财富指数(收盘价)`, `久期` |

使用 `scripts/list_presets.py --all` 可查询所有可用预设的完整信息。

## CSV 数据文件格式

第一列为分类列（通常是日期），后续列为数据系列:

```csv
日期,沪深300指数,组合收益率
2024-01-02,3500,0.001
2024-01-03,3520,0.005
...
```

## 瀑布图 Spec（Standalone CLI / SDK）

瀑布图当前不走这里的 `series_config` 结构，而是走一个更轻量的 chart-engine spec。仓库内置样例见：

- `waterfall_demo.json`
- `data/waterfall_attribution.csv`

最小格式：

```json
{
  "csv_path": "data/waterfall_attribution.csv",
  "categories_col": "阶段",
  "value_col": "贡献",
  "measure_col": "度量",
  "total_categories": ["期初收益", "期末收益"]
}
```

对应命令：

```bash
pptfi render-waterfall waterfall_demo.json output/waterfall-demo.pptx
```

可选字段：

| 字段 | 说明 |
|------|------|
| `title` | 幻灯片标题 |
| `subtitle` | 幻灯片副标题 |
| `position_inches` | 图表左上角坐标，`[x, y]` |
| `size_inches` | 图表尺寸，`[w, h]` |
| `positive_color` | 正贡献颜色 |
| `negative_color` | 负贡献颜色 |
| `total_color` | 总计柱颜色 |
| `show_legend` | 是否显示图例 |
