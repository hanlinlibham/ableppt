# Job JSON 完整 Schema

Job JSON 是 PptEngine 的声明式配置格式，支持两种模式：
- **template 模式**（默认）：基于 PPT 模板 + slides 配置进行占位符替换
- **composer 模式**（推荐）：基于 PageComposer + pages 配置从零构建 PPT

## 顶层字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `mode` | 否 | `"template"` (默认) 或 `"composer"` |
| `template` | 条件 | template 模式必填 |
| `slides` | 条件 | template 模式必填 |
| `theme` | 条件 | composer 模式用，默认 `"jp_finance"` |
| `pages` | 条件 | composer 模式必填 |
| `datasources` | 否 | 数据源配置（两种模式共用）|
| `transforms` | 否 | 数据转换配置（两种模式共用）|
| `params` | 否 | 自定义参数 |
| `output` | 是 | 输出配置 |

## Composer 模式 annotated skeleton

```json
{
  "mode": "composer",
  "theme": "jp_finance",               // THEMES 中的名称
  "datasources": {
    "数据源名称": {
      "type": "csv",                    // "csv" | "xlsx" | "tushare"
      // ... 类型相关字段见下方
    }
  },
  "transforms": {                       // 可选
    "转换后名称": {
      "from": "数据源名称",
      "ops": [{"type": "sort", "sort_by": ["trade_date"]}]
    }
  },
  "pages": [                            // 页面列表（按顺序生成）
    {
      "layout": "title_dark",           // LAYOUT_REGISTRY 中的布局名称
      "data": {                         // 传给布局函数的 data dict
        "title": "报告标题",
        "date": "2026-02"
      }
    },
    {
      "layout": "chart_full",
      "data": {
        "title": "营收与利润",
        "source": "revenue_df",         // ← 引用 datasources/transforms 中的名称
        "categories_col": "年度",
        "series_config": [
          {"key": "营收", "name": "营收(亿元)", "type": "bar", "axis": "primary"},
          {"key": "利润", "name": "利润(亿元)", "type": "line", "axis": "secondary"}
        ],
        "style_config": {"color_scheme": "jp_finance"},
        "layout_config": {
          "legend_config": {"font_size_pt": 9},
          "value_axis_config": {"number_format": "#,##0"}
        }
      }
    }
  ],
  "output": {
    "path": "output/report.pptx",
    "overwrite": true,
    "add_metadata": true
  }
}
```

### source 引用解析规则

引擎在渲染时自动将 `source` 引用解析为实际 DataFrame：

1. **顶层 source**：`data.source` → `data.df`（替换为 DataFrame）
2. **嵌套 source**（`two_charts`）：`data.left.source` / `data.right.source` → 各自的 `df`
3. 引用范围：可引用 `datasources` 或 `transforms` 中的任意 key

### style_config / layout_config 的 JSON 表达

- `style_config`：直接传 `StyleConfig` 构造参数的 dict，如 `{"color_scheme": "jp_finance", "line_width_pt": 2.0}`
- `layout_config`：支持嵌套子对象：
  - `legend_config` → `LegendConfig` 参数
  - `value_axis_config` / `secondary_value_axis_config` → `ValueAxisConfig` 参数
  - `category_axis_config` → `CategoryAxisConfig` 参数
  - `date_axis_config` → 预设名字符串：`"daily"`, `"weekly"`, `"biweekly"`, `"monthly"`, `"quarterly"`, `"yearly"`

## Template 模式 annotated skeleton

```json
{
  "template": {
    "path": "aim/aim03.pptx",       // 模板路径（相对于 ppt-st 项目根，或绝对路径）
    "master": null,                   // 母版名称（可选）
    "notes": null                     // 备注（可选）
  },
  "datasources": {
    "数据源名称": {                   // 自定义名称，后续 source 字段引用
      "type": "csv",                  // "csv" | "xlsx" | "tushare"
      // ... 类型相关字段见下方
    }
  },
  "transforms": {                     // 可选：数据转换
    "转换后名称": {
      "from": "数据源名称",          // 字符串或数组（多源 concat）
      "ops": [                        // 有序操作列表
        {"type": "sort", "sort_by": ["trade_date"]}
      ]
    }
  },
  "slides": [                         // 幻灯片列表（按顺序对应模板页）
    {
      "id": "slide_1",               // 唯一标识
      "layout": null,                 // 版式名（null 使用模板现有页）
      "texts": [                      // 文本替换
        {"target": "文本框名", "value": "替换值（支持 Jinja2）"}
      ],
      "tables": [                     // 表格渲染
        {"target": "表格名", "source": "数据源名", "columns": ["col1"], "header": ["列1"]}
      ],
      "charts": [                     // 图表渲染
        {
          "mode": "update",           // "create" | "update" | "excel_embedded"
          "target": "图表名",         // update 模式下模板中的图表名称
          "source": "数据源名",
          "categories": "日期列名",
          "series": [
            {"key": "列名", "name": "显示名", "axis": "primary"}
          ]
        }
      ]
    }
  ],
  "params": {},                       // 自定义参数（传入渲染上下文）
  "output": {
    "path": "output/report.pptx",    // 输出路径
    "overwrite": true,
    "add_metadata": true              // 是否添加生成信息到 PPT 元数据
  }
}
```

## DataSource 字段表

### type: "csv"

| 字段 | 必填 | 说明 |
|------|------|------|
| `path` | 是 | CSV 文件路径（相对于 data_dir 或绝对路径）|
| `encoding` | 否 | 编码，默认 `utf-8` |

### type: "xlsx"

| 字段 | 必填 | 说明 |
|------|------|------|
| `path` | 是 | Excel 文件路径 |
| `sheet_name` | 否 | 工作表名，默认第一个 |
| `encoding` | 否 | 编码，默认 `utf-8` |

### type: "tushare"

| 字段 | 必填 | 说明 |
|------|------|------|
| `api_name` | 否 | API 接口名，默认 `index_daily`。支持 `index_daily`, `pro_bar` |
| `ts_code` | 是 | 股票/指数代码，如 `600519.SH`, `000300.SH` |
| `start_date` | 否 | 起始日期 `YYYYMMDD`，默认一年前 |
| `end_date` | 否 | 结束日期 `YYYYMMDD`，默认今天 |
| `fields` | 否 | 返回字段列表 |

前置条件: 环境变量 `TUSHARE_TOKEN` 或 `.env` 文件中配置。

## TransformOp 字段表

每个 op 是 `transforms[name].ops[]` 数组中的一项。

### type: "groupby"

| 字段 | 必填 | 说明 |
|------|------|------|
| `by` | 是 | 分组列名列表 |
| `agg` | 是 | 聚合方式 `{"列名": "sum/mean/count/..."}` |

### type: "pivot"

| 字段 | 必填 | 说明 |
|------|------|------|
| `index` | 是 | 行索引列名 |
| `columns` | 是 | 列索引列名 |
| `values` | 是 | 值列名 |

### type: "merge"

**未实现** — 会抛 `NotImplementedError`。用 `from: [src1, src2]` 做 concat 替代。

### type: "compute"

| 字段 | 必填 | 说明 |
|------|------|------|
| `expr` | 是 | pandas eval 表达式，如 `"close / close.iloc[0] - 1"` |
| `output_col` | 是 | 输出列名 |

### type: "filter"

| 字段 | 必填 | 说明 |
|------|------|------|
| `condition` | 是 | pandas query 表达式，如 `"close > 100"` |

### type: "sort"

| 字段 | 必填 | 说明 |
|------|------|------|
| `sort_by` | 是 | 排序列名列表 |
| `ascending` | 否 | 是否升序，默认 `true` |

### type: "rename"

| 字段 | 必填 | 说明 |
|------|------|------|
| `map` | 是 | 列名映射 `{"旧名": "新名"}` |

## SlideSpec

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | 是 | 唯一标识 |
| `layout` | 否 | 版式名称（null 使用模板现有页面）|
| `texts` | 否 | 文本替换列表 `[{target, value}]` |
| `tables` | 否 | 表格渲染列表 `[{target, source, columns, header?, number_format?}]` |
| `charts` | 否 | 图表渲染列表（见 ChartSpec）|

## ChartSpec

| 字段 | 必填 | 说明 |
|------|------|------|
| `mode` | 否 | `"create"` / `"update"` / `"excel_embedded"`，默认 `"update"` |
| `target` | 条件 | update 模式下的模板图表名称 |
| `target_placeholder` | 条件 | create/excel_embedded 模式下的占位符名 |
| `source` | 是 | 数据源名称（引用 datasources 或 transforms 的键）|
| `categories` | 是 | 分类列名 |
| `series` | 是 | 系列配置 `[{key, name, axis?}]` |

## ComposerPageSpec（composer 模式）

| 字段 | 必填 | 说明 |
|------|------|------|
| `layout` | 是 | LAYOUT_REGISTRY 中的布局名称 |
| `data` | 是 | 传给布局函数的 data dict（各布局字段见下表）|

### 各布局的 data 字段

| 布局 | 必填字段 | 可选字段 |
|------|---------|---------|
| `title_dark` | `title` | `subtitle`, `date` |
| `title_light` | `title` | `subtitle`, `date` |
| `kpi_cards` | `title`, `cards: [{label, value}]` | `cards[].change`, `cards[].color` |
| `chart_full` | `title`, `source`, `categories_col`, `series_config` | `subtitle`, `style_config`, `layout_config` |
| `chart_text` | `title`, `source`, `categories_col`, `series_config`, `text_body` | `text_title`, `text_bullets`, `style_config`, `layout_config` |
| `two_charts` | `title`, `left: {source, categories_col, series_config}`, `right: {...}` | `left_title`, `right_title` |
| `comparison_table` | `title`, `headers`, `rows` | |
| `bullet_points` | `title`, `items: [{icon, label, desc}]` | |
| `section_divider` | `title`, `number` | |
| `conclusion_dark` | `verdict` | `items` |

### series_config 字段（composer 模式）

| 字段 | 必填 | 说明 |
|------|------|------|
| `key` | 是 | DataFrame 列名 |
| `name` | 是 | 图表中显示的系列名称 |
| `type` | 否 | `"bar"`, `"line"`, `"area"`（默认按引擎决定）|
| `axis` | 否 | `"primary"` (左轴) 或 `"secondary"` (右轴) |

## 示例: Composer 模式完整版

```json
{
  "mode": "composer",
  "theme": "jp_finance",
  "datasources": {
    "revenue": {"type": "csv", "path": "data/revenue.csv"},
    "stock": {
      "type": "tushare",
      "api_name": "pro_bar",
      "ts_code": "600519.SH",
      "start_date": "20240101",
      "end_date": "20241231"
    }
  },
  "transforms": {
    "stock_sorted": {
      "from": "stock",
      "ops": [{"type": "sort", "sort_by": ["trade_date"]}]
    }
  },
  "pages": [
    {
      "layout": "title_dark",
      "data": {"title": "贵州茅台2024年度分析", "date": "2024-12"}
    },
    {
      "layout": "kpi_cards",
      "data": {
        "title": "核心指标",
        "cards": [
          {"label": "营收", "value": "1,505亿", "change": "+17.2%"},
          {"label": "净利润", "value": "747亿", "change": "+19.1%"},
          {"label": "毛利率", "value": "91.5%", "change": "+0.3pp"}
        ]
      }
    },
    {
      "layout": "chart_full",
      "data": {
        "title": "营收与利润趋势",
        "source": "revenue",
        "categories_col": "年度",
        "series_config": [
          {"key": "营收", "name": "营收(亿元)", "type": "bar", "axis": "primary"},
          {"key": "净利润", "name": "净利润(亿元)", "type": "line", "axis": "secondary"}
        ],
        "style_config": {"color_scheme": "jp_finance"},
        "layout_config": {
          "legend_config": {"font_size_pt": 9, "font_name": "黑体"},
          "value_axis_config": {"number_format": "#,##0"},
          "secondary_value_axis_config": {"number_format": "#,##0"}
        }
      }
    },
    {
      "layout": "two_charts",
      "data": {
        "title": "股价与成交量",
        "left_title": "日收盘价",
        "right_title": "日成交量",
        "left": {
          "source": "stock_sorted",
          "categories_col": "trade_date",
          "series_config": [{"key": "close", "name": "收盘价", "type": "line", "axis": "primary"}],
          "layout_config": {"date_axis_config": "monthly"}
        },
        "right": {
          "source": "stock_sorted",
          "categories_col": "trade_date",
          "series_config": [{"key": "vol", "name": "成交量(手)", "type": "bar", "axis": "primary"}],
          "layout_config": {"date_axis_config": "monthly"}
        }
      }
    },
    {
      "layout": "conclusion_dark",
      "data": {"verdict": "茅台护城河坚固，品牌溢价持续"}
    }
  ],
  "output": {"path": "output/moutai_2024.pptx"}
}
```

## 示例: Template 模式最小版

```json
{
  "template": {"path": "aim/aim03.pptx"},
  "datasources": {},
  "slides": [
    {
      "id": "cover",
      "texts": [
        {"target": "标题", "value": "2024年度报告"}
      ]
    }
  ],
  "output": {"path": "/tmp/minimal.pptx"}
}
```

## 示例: Template 模式完整版（含 Tushare + 变换 + 图表）

```json
{
  "template": {"path": "aim/aim03.pptx"},
  "datasources": {
    "stock": {
      "type": "tushare",
      "api_name": "pro_bar",
      "ts_code": "600519.SH",
      "start_date": "20240101",
      "end_date": "20241231"
    },
    "index": {
      "type": "tushare",
      "api_name": "pro_bar",
      "ts_code": "000300.SH",
      "start_date": "20240101",
      "end_date": "20241231"
    }
  },
  "transforms": {
    "merged": {
      "from": ["stock", "index"],
      "ops": [
        {"type": "sort", "sort_by": ["trade_date"]},
        {"type": "rename", "map": {"close": "收盘价"}}
      ]
    }
  },
  "slides": [
    {
      "id": "cover",
      "texts": [
        {"target": "标题", "value": "贵州茅台2024年度分析"},
        {"target": "日期", "value": "2024-12-31"}
      ]
    },
    {
      "id": "chart_page",
      "charts": [
        {
          "mode": "update",
          "target": "当年收益率走势图",
          "source": "merged",
          "categories": "trade_date",
          "series": [
            {"key": "收盘价", "name": "茅台收盘价", "axis": "primary"}
          ]
        }
      ]
    }
  ],
  "params": {"year": 2024},
  "output": {
    "path": "output/moutai_2024.pptx",
    "overwrite": true,
    "add_metadata": true
  }
}
```
