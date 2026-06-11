# pptfi

`pptfi` 是一套面向金融场景的 **PowerPoint 自动化解决方案**。它负责把：

- 结构化数据
- 模板与布局
- 图表引擎
- 报告编排
- 解析 / 重建
- QA 审计

组合成一条可执行的工作流，最终输出 **原生可编辑 `.pptx`**。

底层图表能力由独立仓库 `pptchartengine` 提供；本仓库负责系统层能力和对外工作流。

## 你可以拿它做什么

- 用模板 + 数据快速生成金融汇报
- 用 Job JSON 声明式地生成整套报告
- 解析已有 PPT，做结构化编辑，再重建
- 生成 standalone 图表页：
  - waterfall
  - scatter
  - bubble
- 用 DeckLinter 审计输出结果

典型场景：

- 投研报告
- 资管 / 养老金月报
- 风险收益分析
- 财务桥图 / 收益归因
- 多页董事会 / 投委会材料

## 安装

```bash
pip install -e .
```

安装后会暴露 CLI：

```bash
pptfi --help
```

也支持模块方式：

```bash
python -m pptfi --help
```

## CLI Quickstart

### 系统入口

```bash
pptfi chart-engine-info
pptfi validate-job job_hikvision.json
pptfi render job_hikvision.json
pptfi validate-ppt output/海康威视竞争壁垒分析.pptx --json
```

### 模板工作流

```bash
pptfi parse-template aim/aim03.pptx
pptfi generate aim/aim03.pptx config.json output/demo.pptx
```

### Standalone 图表家族

```bash
pptfi render-waterfall waterfall_demo.json output/waterfall-demo.pptx
pptfi parse-waterfall output/waterfall-demo.pptx

pptfi render-scatter scatter_demo.json output/scatter-demo.pptx
pptfi parse-scatter output/scatter-demo.pptx

pptfi render-bubble bubble_demo.json output/bubble-demo.pptx
pptfi parse-bubble output/bubble-demo.pptx
```

### Composer 页面示例

```bash
pptfi render job_waterfall_demo.json
pptfi render job_scatter_demo.json
pptfi render job_bubble_demo.json
```

## SDK Quickstart

```python
from pptfi import (
    render_job,
    render_waterfall,
    render_scatter,
    render_bubble,
)

render_job("job_hikvision.json")
render_waterfall("waterfall_demo.json", "output/waterfall-demo.pptx")
render_scatter("scatter_demo.json", "output/scatter-demo.pptx")
render_bubble("bubble_demo.json", "output/bubble-demo.pptx")
```

## 系统边界

### 这个仓库负责

- CLI / SDK
- connectors / transforms
- engine / composer / layouts
- template replacement
- parser / renderer
- QA / DeckLinter
- sample jobs / demo specs / docs

### 这个仓库不负责

- 独立维护底层 chart engine 实现

`pptfi.chart_builder` 现在是兼容层，会把图表导入转发到 `pptchartengine`。

你仍然可以这样导入：

```python
from pptfi.chart_builder import create_combo_chart
```

但底层实际实现来自 `pptchartengine`。

## 当前已接通的图表能力

### 通过 `pptchartengine`

- combo：`bar / line / area`
- grouping：`clustered / stacked / percent_stacked`
- waterfall
- scatter
- bubble
- round-trip parse

### 通过 `pptfi`

- 报告编排中的普通图表页
- `waterfall` composer 布局
- `scatter` composer 布局
- `bubble` composer 布局
- standalone chart-family CLI

## GTM 页面编排（Flow G）

提炼自 J.P. Morgan《Guide to the Markets》的页面骨架，面向 **模型结构化输出**：
LLM 只需产出一个 job JSON 即可编排整本 GTM 风格报告。

```bash
pptfi render job_gtm_demo.json     # 5 页演示：GDP/通胀/劳动力/估值/贸易
```

- 布局 `gtm_panels`：章节箭头 + 页标题分隔线 + [GTM|市场|页码] 角标 +
  左侧竖向章节签 + 来源行 + 品牌字
- 面板编排：1 图整页 / 双栏 / 左一右二（1+2）
- 面板内 `chart` 字段就是 **pptchartengine 的声明式 spec**（data 支持
  内联 dict / CSV 路径），贡献分解、估值区间、注释层等全部能力直接可用
- 面板内可叠加迷你数据表（`table`，行标签可按系列着色）

页面 JSON 形如：

```jsonc
{"layout": "gtm_panels", "data": {
  "title": "通货膨胀", "section": "宏观", "market": "CN", "page_num": 5,
  "source": "来源：...", "brand": "...",
  "panels": [
    {"title": "CPI与核心CPI", "subtitle": "同比",
     "chart": {"chart": "line", "data": "data/gtm/cpi.csv",
               "annotations": [{"type": "band", "from": 0.02, "to": 0.03}]},
     "table": {"columns": ["", "均值", "最新"], "rows": [["CPI同比", "2.1%", "2.4%"]],
               "row_colors": ["#29ABE2"]}},
    {"title": "通胀分项贡献", "subtitle": "百分点",
     "chart": {"chart": "contribution", "data": "data/gtm/cpi_parts.csv", "total": "CPI同比"}}
  ]}}
```

## 工作流总览

### Flow A — 模板替换

适合：

- 已有模板
- 只需要填文本和图表
- 双轴图较多

入口：

```bash
pptfi parse-template aim/aim03.pptx
pptfi generate aim/aim03.pptx config.json output/demo.pptx
```

### Flow B — Job JSON 编排

适合：

- 多数据源
- 多页报告
- 需要 layout / theme / datasource / transform 一体配置

入口：

```bash
pptfi validate-job job.json --dry-run
pptfi render job.json
```

### Flow C — 解析 → 编辑 → 重建

适合：

- 已有 PPT 的结构化微调
- 文本、表格、页面结构处理

入口：

```bash
python scripts/parse_ppt.py input.pptx parsed.json
python scripts/rebuild_ppt.py parsed.json output.pptx
```

### Flow D — Standalone 图表页

适合：

- 单张 waterfall / scatter / bubble
- 快速验证图表能力
- 作为后续页面嵌入前的独立验证

入口：

```bash
pptfi render-waterfall waterfall_demo.json output/waterfall-demo.pptx
pptfi render-scatter scatter_demo.json output/scatter-demo.pptx
pptfi render-bubble bubble_demo.json output/bubble-demo.pptx
```

## 仓库里的现成示例

### 报告 Job

- `job_hikvision.json`
- `job_gigadevice.json`
- `job_waterfall_demo.json`
- `job_scatter_demo.json`
- `job_bubble_demo.json`

### Standalone 图表 spec

- `waterfall_demo.json`
- `scatter_demo.json`
- `bubble_demo.json`

### 数据样例

- `data/waterfall_attribution.csv`
- `data/risk_return_points.csv`
- `data/hikvision_*.csv`
- `data/gigadevice_*.csv`

### 输出目录

- `output/`

这里默认忽略生成产物，不进 git。

## 目录结构

```text
pptfi/
├── pptfi/               # Python package
├── scripts/             # wrapper scripts
├── reference/           # docs
├── tests/               # contract tests
├── data/                # sample data
├── aim/                 # sample templates / source PPTs
├── *.json               # sample jobs / specs
└── output/              # generated artifacts (gitignored)
```

## 测试

### 系统合同测试

```bash
python -m pytest tests/test_system_contract.py
```

### CLI / SDK 合同测试

```bash
python -m pytest tests/test_cli_sdk_contract.py
```

### 当前验证重点

- CLI 能否正常工作
- SDK 导出面是否稳定
- chart engine compatibility layer 是否仍然正确指向 `pptchartengine`
- waterfall / scatter / bubble 是否能 standalone 生成并反向解析
- composer demo jobs 是否能渲染出 PPT

## 约束

1. `merge` transform 仍未实现
2. 复杂图表能力应优先在 `pptchartengine` 中扩展，再接回 `pptfi`
3. `pptfi` 不应重新复制一套 chart engine

## 相关仓库

- `pptchartengine`：底层图表引擎

推荐协作方式：

- 图表家族、parser、round-trip → 改 `pptchartengine`
- CLI、SDK、layout、workflow、docs、samples → 改 `pptfi`
