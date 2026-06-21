# pptfi

`pptfi` 是一套面向金融场景的 **PowerPoint 自动化解决方案**。它负责把：

- 结构化数据
- 模板与布局
- 图表引擎
- 报告编排
- 解析 / 重建
- QA 审计

组合成一条可执行的工作流，最终输出 **原生可编辑 `.pptx`**。

底层图表能力由独立仓库 `ablechart` 提供；本仓库负责系统层能力和对外工作流。

## 你可以拿它做什么

- 用模板 + 数据快速生成金融汇报
- 用 Job JSON 声明式地生成整套报告
- 解析已有 PPT，做结构化编辑，再重建
- 生成 standalone 图表页：
  - waterfall
  - scatter
  - bubble
  - range snapshot（支持 `orientation=horizontal`）
  - semantic families（`performance_compare`、`distribution_plus_history`、`score_overlay`、`event_timeline`、`style_box` 等）
  - matrix/tile families（`ranked_tile_matrix`、`heatmap_matrix`）
  - composite page family（`table_plus_chart_composite`）
  - attribution panel family（`factor_attribution_panel`）
  - regime panel family（`regime_table_panel`）
  - people/info families（`manager_timeline_profile`、`award_timeline_panel`）
  - judgment families（`selection_timing_grid`）
  - detail panel families（`holding_detail`）
  - dual chart panel family（`dual_chart_panel`）
  - page shells（`research_shell_4_3`、`dashboard_shell_16_9`）
  - advanced page shells（`factsheet_shell_4_3`、`summary_shell_16_9`）
  - shell variants（`section_cover_4_3`、`chapter_divider_16_9`、`profile_factsheet_4_3`）
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
pptfi validate-job job_demo_company_a.json
pptfi render job_demo_company_a.json
pptfi validate-ppt output/样例公司A竞争壁垒分析.pptx --json
```

### Tushare -> SQLite 数据准备

```bash
python scripts/build_tushare_sqlite.py --output pptfi/data/tushare_market.sqlite
python scripts/fetch_data.py --config tushare_sqlite_datasources.json --output output/sqlite_exports
```

### 模板工作流

```bash
pptfi parse-template aim/aim00.pptx
pptfi generate aim/aim00.pptx config.json output/demo.pptx
```

### Standalone 图表家族

```bash
pptfi render-waterfall waterfall_demo.json output/waterfall-demo.pptx
pptfi parse-waterfall output/waterfall-demo.pptx

pptfi render-scatter scatter_demo.json output/scatter-demo.pptx
pptfi parse-scatter output/scatter-demo.pptx

pptfi render-bubble bubble_demo.json output/bubble-demo.pptx
pptfi parse-bubble output/bubble-demo.pptx

pptfi render-range-snapshot range_snapshot_demo.json output/range-snapshot-demo.pptx
pptfi parse-range-snapshot output/range-snapshot-demo.pptx

pptfi render-range-snapshot range_snapshot_sector_demo.json output/range-snapshot-sector-demo.pptx

pptfi render-family performance_compare_demo.json output/performance-compare-demo.pptx
pptfi render-family distribution_history_demo.json output/distribution-history-demo.pptx
pptfi render-family score_overlay_demo.json output/score-overlay-demo.pptx
pptfi render-family event_timeline_demo.json output/event-timeline-demo.pptx
pptfi render-family style_box_demo.json output/style-box-demo.pptx
pptfi render-family ranked_tile_matrix_demo.json output/ranked-tile-matrix-demo.pptx
pptfi render-family heatmap_matrix_demo.json output/heatmap-matrix-demo.pptx
pptfi render-family table_plus_chart_composite_demo.json output/table-plus-chart-composite-demo.pptx
pptfi render-family factor_attribution_panel_demo.json output/factor-attribution-panel-demo.pptx
pptfi render-family regime_table_panel_demo.json output/regime-table-panel-demo.pptx
pptfi render-family manager_timeline_profile_demo.json output/manager-timeline-profile-demo.pptx
pptfi render-family award_timeline_panel_demo.json output/award-timeline-panel-demo.pptx
pptfi render-family selection_timing_grid_demo.json output/selection-timing-grid-demo.pptx
pptfi render-family holding_detail_demo.json output/holding-detail-demo.pptx
pptfi render-family dual_chart_panel_demo.json output/dual-chart-panel-demo.pptx

pptfi render job_research_shell_demo.json
pptfi render job_dashboard_shell_demo.json
pptfi render job_factsheet_shell_demo.json
pptfi render job_summary_shell_demo.json
pptfi render job_section_cover_demo.json
pptfi render job_chapter_divider_demo.json
pptfi render job_profile_factsheet_demo.json
```

### Composer 页面示例

```bash
pptfi render job_waterfall_demo.json
pptfi render job_scatter_demo.json
pptfi render job_bubble_demo.json
pptfi render job_range_snapshot_demo.json
pptfi render job_range_snapshot_sector_demo.json
```

## SDK Quickstart

```python
from pptfi import (
    render_job,
    render_family,
    render_waterfall,
    render_scatter,
    render_bubble,
    render_range_snapshot,
)

render_job("job_demo_company_a.json")
render_waterfall("waterfall_demo.json", "output/waterfall-demo.pptx")
render_scatter("scatter_demo.json", "output/scatter-demo.pptx")
render_bubble("bubble_demo.json", "output/bubble-demo.pptx")
render_range_snapshot("range_snapshot_demo.json", "output/range-snapshot-demo.pptx")
render_family("performance_compare_demo.json", "output/performance-compare-demo.pptx")
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

`pptfi.chart_builder` 现在是兼容层，会把图表导入转发到 `ablechart`。

你仍然可以这样导入：

```python
from pptfi.chart_builder import create_combo_chart
```

但底层实际实现来自 `ablechart`。

## 当前已接通的图表能力

### 通过 `ablechart`

- combo：`bar / line / area`
- grouping：`clustered / stacked / percent_stacked`
- waterfall
- scatter
- bubble
- range snapshot（当前 vertical / horizontal 都可）
- semantic families:
  - `performance_compare`
  - `distribution_plus_history`
  - `style_box`
  - `style_allocation`
  - `factor_exposure`
  - `score_overlay`
  - `concentration`
  - `event_timeline`
  - `attribution_decomposition`
- round-trip parse

### 通过 `pptfi`

- 报告编排中的普通图表页
- `waterfall` composer 布局
- `scatter` composer 布局
- `bubble` composer 布局
- `range_snapshot` composer 布局
- standalone chart-family CLI

## GTM 页面编排（Flow G）

提炼自国际投行市场指南类报告版式（GTM：General Theme for Markets），面向 **模型结构化输出**：
LLM 只需产出一个 job JSON 即可编排整本 GTM 风格报告。

```bash
pptfi render job_gtm_demo.json     # 5 页演示：GDP/通胀/劳动力/估值/贸易
```

- 布局族：`gtm_cover`（封面）/ `gtm_toc`（目录，items 可自动生成）/
  `gtm_panels`（面板页）/ `gtm_chart_text`（左图右点评）/ `gtm_quilt`（资产收益排序矩阵）
- 页面骨架：章节箭头 + 页标题分隔线 + [GTM|市场|页码] 角标 +
  左侧竖向章节签 + 来源行 + 品牌字
- 面板编排：1 图整页 / 双栏 / 左一右二（1+2）/ 2×2 四面板
- **deck 级工作流**：`"deck": {"brand": ..., "market": ..., "start_page": 1}` →
  品牌/市场/来源自动注入每页、页码自增、章节延续、目录按后续页面自动生成
- few-shot：`gtm_page_examples()` 返回 8 个场景的最小页面 spec（拼进 LLM 提示词）
- **结构化输出**：`gtm_job_schema()` 返回 deck job 的 JSON Schema（内联图表 schema），
  做模型的约束解码；`pptfi validate-job job.json --deep` 深度校验闭环——
  加载真实数据源逐面板校验列名/类型（带 did-you-mean），错误喂回模型自修正
- **提示词工具包**：`pptfi describe-data <目录|job>` 生成数据列清单（列名/类型/样例/范围）；
  `pptfi prompt-kit <job|目录>` 一键组装 规则+页面示例+图表示例+数据清单 的完整提示词
- **原子安全渲染**：`pptfi render job.json --validate` 先深度校验，有错只输出报告不渲染——
  agent 的"产出→校验→修正→渲染"循环可全黑盒调用
- 面板内 `chart` 字段就是 **ablechart 的声明式 spec**（data 支持
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
pptfi parse-template aim/aim00.pptx
pptfi generate aim/aim00.pptx config.json output/demo.pptx
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

- 单张 waterfall / scatter / bubble / range snapshot
- 单张 semantic family 图表
- 快速验证图表能力
- 作为后续页面嵌入前的独立验证

入口：

```bash
pptfi render-waterfall waterfall_demo.json output/waterfall-demo.pptx
pptfi render-scatter scatter_demo.json output/scatter-demo.pptx
pptfi render-bubble bubble_demo.json output/bubble-demo.pptx
pptfi render-range-snapshot range_snapshot_demo.json output/range-snapshot-demo.pptx
```

## 仓库里的现成示例

### 报告 Job

- `job_demo_company_a.json`
- `job_demo_company_b.json`
- `job_waterfall_demo.json`
- `job_scatter_demo.json`
- `job_bubble_demo.json`
- `job_range_snapshot_demo.json`
- `job_range_snapshot_sector_demo.json`
- `job_research_shell_demo.json`
- `job_dashboard_shell_demo.json`
- `job_factsheet_shell_demo.json`
- `job_summary_shell_demo.json`
- `job_section_cover_demo.json`
- `job_chapter_divider_demo.json`
- `job_profile_factsheet_demo.json`

### Standalone 图表 spec

- `waterfall_demo.json`
- `scatter_demo.json`
- `bubble_demo.json`
- `range_snapshot_demo.json`
- `range_snapshot_sector_demo.json`
- `performance_compare_demo.json`
- `distribution_history_demo.json`
- `style_allocation_demo.json`
- `factor_exposure_demo.json`
- `score_overlay_demo.json`
- `concentration_demo.json`
- `event_timeline_demo.json`
- `style_box_demo.json`
- `attribution_decomposition_demo.json`
- `ranked_tile_matrix_demo.json`
- `heatmap_matrix_demo.json`
- `table_plus_chart_composite_demo.json`
- `factor_attribution_panel_demo.json`
- `regime_table_panel_demo.json`
- `manager_timeline_profile_demo.json`
- `award_timeline_panel_demo.json`
- `selection_timing_grid_demo.json`
- `holding_detail_demo.json`
- `dual_chart_panel_demo.json`

### 数据样例

- `data/waterfall_attribution.csv`
- `data/risk_return_points.csv`
- `data/range_snapshot_valuation.csv`
- `data/range_snapshot_sector_valuation.csv`
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

## 参考 deck 建模

`jp_demo.pdf` 已经被抽象为一份可校验的 chart-family catalog，用来定义后续 `ablechart` / `composer` 的覆盖目标，而不是把 PDF 当成一次性的视觉参考。

- 说明文档：`reference/jp-demo-chart-model.md`
- machine-readable catalog：`reference/jp_demo_chart_catalog.json`
- HTML atlas：`reference/jp-demo-chart-atlas.html`
- atlas 生成脚本：`scripts/render_chart_catalog_atlas.py`
- SDK loader：`from pptfi import load_jp_demo_chart_catalog`

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
- chart engine compatibility layer 是否仍然正确指向 `ablechart`
- waterfall / scatter / bubble 是否能 standalone 生成并反向解析
- composer demo jobs 是否能渲染出 PPT

## 约束

1. `merge` transform 仍未实现
2. 复杂图表能力应优先在 `ablechart` 中扩展，再接回 `pptfi`
3. `pptfi` 不应重新复制一套 chart engine

## 相关仓库

- `ablechart`：底层图表引擎

推荐协作方式：

- 图表家族、parser、round-trip → 改 `ablechart`
- CLI、SDK、layout、workflow、docs、samples → 改 `pptfi`
