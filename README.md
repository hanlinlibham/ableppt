# pptfi

金融类 PPT 整体解决方案。支持从结构化数据生成、编排、解析、重建、审计可编辑 `pptx`，适合投研、资管、养老金、财务分析等场景。

## CLI Quickstart

安装为可执行 CLI：

```bash
pip install -e .
```

安装后可直接使用：

```bash
pptfi --help
pptfi chart-engine-info
pptfi parse-template aim/aim03.pptx
pptfi generate aim/aim03.pptx config.json output.pptx
pptfi validate-job job_hikvision.json
pptfi render job_hikvision.json
pptfi render-waterfall waterfall_demo.json output/waterfall-demo.pptx
pptfi parse-waterfall output/waterfall-demo.pptx
pptfi render-scatter scatter_demo.json output/scatter-demo.pptx
pptfi parse-scatter output/scatter-demo.pptx
pptfi render-bubble bubble_demo.json output/bubble-demo.pptx
pptfi parse-bubble output/bubble-demo.pptx
pptfi describe-chart output/海康威视竞争壁垒分析.pptx --slide 3
pptfi validate-ppt output/海康威视竞争壁垒分析.pptx --json
pptfi demo-waterfall output/waterfall-demo.pptx
```

也支持模块方式：

```bash
python -m pptfi --help
```

## SDK Quickstart

```python
from pptfi import (
    chart_engine_info,
    parse_template,
    generate_ppt,
    render_job,
    render_waterfall,
    render_scatter,
    render_bubble,
)

placeholders = parse_template("aim/aim03.pptx")
result = render_job("job_hikvision.json")
compat = chart_engine_info()
waterfall = render_waterfall("waterfall_demo.json", "output/waterfall-demo.pptx")
scatter = render_scatter("scatter_demo.json", "output/scatter-demo.pptx")
bubble = render_bubble("bubble_demo.json", "output/bubble-demo.pptx")
print(result["output"])
```

## Chart Engine Compatibility

`pptfi.chart_builder` 现在是兼容层，不再是独立维护的一套图表实现。运行时会把导入转发到同工作区里的 `pptchartengine`。

- 旧导入路径继续兼容：`from pptfi.chart_builder import create_combo_chart`
- 顶层 SDK 继续导出：`create_combo_chart`、`create_waterfall_chart`、`create_scatter_chart`、`create_bubble_chart`、`prepare_waterfall_dataframe`
- `pptfi chart-engine-info` 会显示当前兼容层实际映射到的模块和文件

当前建议：

- Flow A / Flow B 内提到的 `chart_builder`，都应理解为对 `pptchartengine` 的兼容入口
- 写文档、样例、测试时，不要再把 `pptfi.chart_builder` 描述成“另一套底层引擎”
- 瀑布图当前既支持 chart-engine 单页输出，也支持 composer `waterfall` 布局

## Waterfall Quickstart

仓库内置了一个最小可运行样例：

- 规格文件：`waterfall_demo.json`
- composer job：`job_waterfall_demo.json`
- 规格文件：`scatter_demo.json` / `bubble_demo.json`
- composer job：`job_scatter_demo.json` / `job_bubble_demo.json`
- 数据文件：`data/waterfall_attribution.csv`
- 包 CLI：`pptfi render-waterfall waterfall_demo.json output/waterfall-demo.pptx`
- 兼容脚本：`python scripts/render_waterfall.py waterfall_demo.json output/waterfall-demo.pptx`

这份 JSON 是轻量 chart-engine spec，不是 `PptEngine` Job Schema。最小字段如下：

```json
{
  "csv_path": "data/waterfall_attribution.csv",
  "categories_col": "阶段",
  "value_col": "贡献",
  "measure_col": "度量",
  "total_categories": ["期初收益", "期末收益"]
}
```

## 目录结构

```
pptfi/
├── README.md                   # 本文件
├── waterfall_demo.json         # 单页瀑布图样例规格
├── scripts/                    # CLI 工具（全部 stdout=JSON, stderr=日志）
│   ├── generate_ppt.py         # Flow A: 模板替换生成
│   ├── run_job.py              # Flow B: Job JSON 声明式编排
│   ├── render_waterfall.py     # 单页瀑布图样例包装
│   ├── parse_ppt.py            # Flow C-1: PPT → JSON
│   ├── rebuild_ppt.py          # Flow C-2: JSON → PPT
│   ├── parse_template.py       # 工具: 解析模板占位符
│   ├── describe_chart.py       # 工具: 描述已有图表结构
│   ├── list_presets.py         # 工具: 查询配色/日期轴/图表预设
│   ├── add_placeholders.py     # 工具: 给现有 PPT 注入占位符
│   ├── gen_moutai_report.py    # 示例: 茅台年度分析报告
│   └── gen_moutai_risk.py      # 示例: 茅台风险分析报告
├── data/
│   └── waterfall_attribution.csv
├── reference/                  # 详细参考文档
│   ├── chart-config.md         # 图表配置完整字段
│   ├── job-schema.md           # Job JSON Schema
│   ├── placeholder-syntax.md   # 占位符语法
│   ├── connectors-transforms.md# 数据连接器 + 变换操作
│   ├── workflow-template.md    # Flow A 详解
│   ├── workflow-engine.md      # Flow B 详解
│   ├── workflow-parse-rebuild.md# Flow C 详解
│   └── workflow-tushare.md     # Flow D 详解
└── tests/                      # CLI / SDK / shell 合同测试
    ├── test_cli_sdk_contract.py
    ├── test_system_contract.py
    ├── test_parse_template.sh
    ├── test_generate_ppt.sh
    ├── test_run_job.sh
    ├── test_parse_rebuild.sh
    └── test_describe_chart.sh
```

## 四条工作流

### Flow A — 模板替换

最常用。模板 PPT 中放好 `{变量名}` 和 `{@图:图表名}` 占位符，配合 config.json + CSV 数据生成最终 PPT。图表样式最丰富（双轴、8 种配色、日期轴预设）。

```bash
# 1. 查看模板有哪些占位符
python scripts/parse_template.py aim/aim03.pptx

# 2. 准备 config.json + CSV，然后生成
python scripts/generate_ppt.py aim/aim03.pptx config.json output.pptx

# 3. 验证生成的图表
python scripts/describe_chart.py output.pptx
```

### Flow B — Job JSON 声明式编排

适合多数据源编排。一个 job.json 声明数据源（CSV/Excel/Tushare）、变换管道、幻灯片配置，一键生成。

```bash
# 验证 schema
pptfi validate-job job.json --dry-run

# 正式生成
pptfi render job.json
```

> 兼容说明：
> - `scripts/run_job.py` / `scripts/render_ppt.py` 仍然可用，但推荐主入口切到 `pptfi validate-job` / `pptfi render`
> - Job 引擎的图表渲染分支对复杂双轴图和瀑布图仍然不是当前主路径
> - 复杂双轴图优先用 Flow A；瀑布图优先用 `render-waterfall` 或 SDK `create_waterfall_chart`

### Flow C — 解析→编辑→重建

对已有 PPT 做微调（批量文本替换、结构检查）。不适合改图表数据。

```bash
python scripts/parse_ppt.py input.pptx parsed.json   # PPT → JSON
# 编辑 parsed.json ...
python scripts/rebuild_ppt.py parsed.json output.pptx  # JSON → PPT
```

### Flow D — Tushare 实时数据

在 Flow A 或 B 中接入 Tushare 实时 A 股数据。需要 `TUSHARE_TOKEN` 环境变量或 `.env` 文件。

```bash
# 完整示例：茅台年度报告（自动拉数据+生成图表+输出 PPT）
python scripts/gen_moutai_report.py

# 风险分析报告
python scripts/gen_moutai_risk.py
```

## 工具脚本速查

| 脚本 | 用途 | 用法 |
|------|------|------|
| `parse_template.py` | 解析模板占位符清单 | `<template.pptx> [--flat]` |
| `describe_chart.py` | 描述已有图表结构 | `<input.pptx> [--slide N]` |
| `render_waterfall.py` | 从 chart-engine spec 生成单页瀑布图 PPT | `<config.json> <output.pptx>` |
| `list_presets.py` | 查询所有可用预设 | `[--color-schemes\|--date-axis\|--chart-presets\|--all]` |
| `add_placeholders.py` | 给已有 PPT 注入占位符 | `<in.pptx> <out.pptx> <map.json>` |

所有脚本遵循统一约定：**JSON 输出到 stdout，日志输出到 stderr**。

## 内置预设

### 配色方案（8 种）

| 名称 | 色值 | 场景 |
|------|------|------|
| `aim00` | `C0C0C0` `C00000` `305496` `808080` | 养老金报告：浅灰柱+深红线 |
| `default` | 深红/深蓝/深橙/深灰 + 浅色 | 通用 |
| `dark_only` | `C00000` `0070C0` `ED7D31` `595959` | 深色系 |
| `light_only` | `FF9999` `9DC3E6` `F4B183` `BFBFBF` | 浅色系 |
| `red/blue/orange/gray_series` | 各两色渐变 | 单系列强调 |

### 日期轴预设（6 种）

| 预设 | 间隔 | 格式 | 数据量 |
|------|------|------|--------|
| `DAILY_TICKS` | 1 天 | `mm-dd` | 1-30 天 |
| `WEEKLY_TICKS` | 7 天 | `yyyy-mm-dd` | 1-6 个月 |
| `BIWEEKLY_TICKS` | 14 天 | `yyyy-mm-dd` | 季度 |
| `MONTHLY_TICKS` | 1 月 | `yyyy-mm` | 年度 |
| `QUARTERLY_TICKS` | 3 月 | `yyyy-mm` | 多年 |
| `YEARLY_TICKS` | 1 年 | `yyyy` | 长期 |

### 养老金图表预设（4 种）

| 预设 | 系列 | 所需列 |
|------|------|--------|
| 当年收益率走势 | bar(右)+line(左) | `分类`, `沪深300指数(收盘价)`, `组合收益率（左轴）` |
| 成立以来收益率 | area(右)+line(左) | `分类`, `组合规模(万元)`, `累计收益率` |
| 权益仓位走势 | area(右)+line(左) | `分类`, `沪深300指数(收盘价)`, `权益仓位（人社部口径）` |
| 久期走势 | bar(右)+line(左) | `分类`, `中债新综合总财富指数(收盘价)`, `久期` |

## 智能配置（新增）

skill 底层的 `pptfi` 新增了两个模块，可大幅减少手工配置：

### StyleExtractor — 从参考 PPT 提取风格

```python
from pptfi.extractors import StyleExtractor
profile = StyleExtractor("reference.pptx").extract()
style_config = profile.to_style_config()      # → StyleConfig
layout_config = profile.to_chart_layout_config()  # → ChartLayoutConfig
```

### ChartAdvisor — DataFrame 自动推荐图表配置

```python
from pptfi.advisors import ChartAdvisor
rec = ChartAdvisor.suggest(df, title="三一重工 vs 沪深300")
# rec.to_kwargs() → {"categories_col", "series_config", "layout_config", "style_config"}
```

自动识别中文金融列名（收益率→line/primary/0%，指数→bar/secondary/#,##0 等），3 行代替 30+ 行手工配置。

## 测试

```bash
cd pptfi

# 系统合同测试
python -m pytest tests/test_system_contract.py

# CLI / SDK 合同测试
python -m pytest tests/test_cli_sdk_contract.py
```

## 关键约束

1. **路径**：脚本内部用 `Path(__file__).resolve()` 定位项目根，不要用绝对路径。CSV 路径相对于 config.json 所在目录。
2. **merge 变换未实现**：Job JSON 中不要用 `merge`，用 `from: [src1, src2]` concat 替代。
3. **占位符匹配**：`{@图:ChartName}` 与 config.json 中的 key 必须完全一致（区分大小写）。
4. **Tushare 索引数据**：用 `pro_bar(asset="I")` 而非 `index_daily`（后者可能失败）。

## 参考文档

| 文档 | 内容 |
|------|------|
| [chart-config.md](reference/chart-config.md) | 图表系列、样式、布局、日期轴完整字段 |
| [layout-waterfall.md](reference/layout-waterfall.md) | 瀑布图设计稿与当前接入状态 |
| [job-schema.md](reference/job-schema.md) | Job JSON 声明式配置完整结构 |
| [placeholder-syntax.md](reference/placeholder-syntax.md) | 文本/图表/表格占位符格式 |
| [connectors-transforms.md](reference/connectors-transforms.md) | 3 种数据源 + 7 种变换操作 |
| [workflow-template.md](reference/workflow-template.md) | Flow A 模板替换详解 |
| [workflow-engine.md](reference/workflow-engine.md) | Flow B Job 引擎详解 |
| [workflow-parse-rebuild.md](reference/workflow-parse-rebuild.md) | Flow C 解析重建详解 |
| [workflow-tushare.md](reference/workflow-tushare.md) | Flow D Tushare 集成详解 |
