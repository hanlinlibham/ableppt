# Flow A — 模板替换生成 PPT

最常用的工作流：解析模板中的占位符，准备数据，用 `generate_ppt.py` 渲染。

## 端到端流程

### Step 1: 解析模板占位符

```bash
python scripts/parse_template.py aim/aim00.pptx
```

输出示例:
```json
{
  "pages": [
    {"page_number": 1, "text_placeholders": ["标题", "日期"], "chart_placeholders": ["当年收益率走势图"]},
    {"page_number": 2, "text_placeholders": ["组合名称"], "chart_placeholders": []}
  ],
  "all_text": ["标题", "日期", "组合名称"],
  "all_chart": ["当年收益率走势图"]
}
```

### Step 2: 准备 CSV 数据

为每个图表准备 CSV 文件。第一列为分类列（通常是日期），后续列对应系列的 `key`。

```csv
日期,沪深300指数,组合收益率
2024-01-02,3500,0.001
2024-01-03,3520,0.005
```

### Step 3: 编写 config.json

```json
{
  "text_data": {
    "标题": "2024年度投资报告",
    "日期": "2024-12-31",
    "组合名称": "稳健增长组合"
  },
  "chart_configs": {
    "当年收益率走势图": {
      "csv_path": "ytd_chart.csv",
      "categories_col": "日期",
      "series_config": [
        {"key": "沪深300指数", "name": "沪深300指数(收盘价)", "type": "bar", "axis": "secondary"},
        {"key": "组合收益率", "name": "组合收益率（左轴）", "type": "line", "axis": "primary"}
      ],
      "style": {
        "color_scheme": "aim00",
        "line_width_pt": 2.0,
        "marker_style": "none"
      },
      "layout": {
        "title": "组合2024年以来收益率走势图",
        "legend": {"position": "top", "font_size_pt": 9, "font_name": "黑体"},
        "value_axis": {"number_format": "0%", "font_size_pt": 9, "has_major_gridlines": false},
        "secondary_value_axis": {"number_format": "#,##0", "font_size_pt": 9},
        "date_axis": {"number_format": "yyyy/mm"}
      }
    }
  }
}
```

关键规则:
- `csv_path` 相对于 config.json 所在目录
- `chart_configs` 的键名必须与模板中 `{@图:xxx}` 的 `xxx` 完全一致
- `series_config` 的 `key` 必须与 CSV 列名完全一致

### Step 4: 生成 PPT

```bash
python scripts/generate_ppt.py aim/aim00.pptx config.json /tmp/output.pptx
```

stdout 输出: `{"status": "ok", "output": "/tmp/output.pptx"}`

### Step 5: 验证

用 `describe_chart.py` 检查生成的图表:

```bash
python scripts/describe_chart.py /tmp/output.pptx
```

## Flow A vs Flow B 选择

| 场景 | 推荐 |
|------|------|
| 模板已有占位符，需替换文本+图表 | Flow A |
| 需要从多个数据源声明式编排 | Flow B |
| 需要 Tushare 实时数据 | Flow B 或 Flow D |
| 快速原型、简单报告 | Flow A |

## 故障排查

| 症状 | 原因 | 解决 |
|------|------|------|
| 占位符未替换 | 名称不匹配（区分大小写）| 先用 `parse_template.py` 确认 |
| 图表未生成 | `chart_configs` 键名与占位符不匹配 | 检查 `{@图:xxx}` 中的 `xxx` |
| CSV 加载失败 | `csv_path` 路径错误 | 路径相对于 config.json 目录 |
| 图表无数据 | `key` 与 CSV 列名不匹配 | 检查 CSV 表头 |
| 日期轴标签太密 | 未设置 `date_axis.major_unit` | 添加 `"major_unit": N` 或省略（自动 len/7）|
