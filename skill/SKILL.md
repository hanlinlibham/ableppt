---
name: ableppt
description: >
  Financial PowerPoint automation system built on the `ablechart` editable
  chart engine. Supports template placeholder replacement, Job JSON
  orchestration, PPT parse-edit-rebuild (round-trip), data connectors
  (CSV/Excel/Tushare), dataframe transforms, composer layouts/themes, and
  DeckLinter QA — emitting native, fully editable .pptx. Charts cover dual-axis
  combos, waterfall/scatter/bubble/range, with fine-grained styling: axis
  titles, tick-label rotation, per-axis number formats, min/max, gridlines, and
  legend position. Use when the task is to create, edit, analyze, or generate
  finance-oriented PowerPoint reports from structured data.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
user-invocable: true
---

# ableppt

`ableppt` 是当前工作区里的金融类 PPT 整体解决方案，不只是图表引擎。

定位：

- 数据优先的金融 PPT 自动化系统
- 输出原生可编辑 `.pptx`
- 支持整套报告生成，而不只是单图
- 适合投研、资管、养老金、风控、财务分析场景

项目根目录：

`/Users/jameslee/pension_plan/ppt-project/ableppt`

## 快速上手（最常用，照抄即可）

在项目根目录执行。下面是端到端最短路径（自带 demo 试手）：

```bash
# Job JSON / 单图 → 可编辑 PPT
ableppt render-waterfall waterfall_demo.json output/demo.pptx
# 质检（DeckLinter）
ableppt validate-ppt output/demo.pptx
# 回读校验（把原生图表读回数据，证明可编辑/round-trip）
ableppt parse-waterfall output/demo.pptx
```

> `validate-ppt` 报的 `WARN`/`footer_missing` 等是**内容样式建议**，不是执行失败。
> 其它入口见「核心工作流」表；细粒度图表精修（轴标题/旋转/双轴）见「图表精修」节。

## 生成整本 deck 前：先当"导演"派页型（别满本是图）

⚠️ ableppt 是 **chart-first** 引擎，不加约束会把**每页都做成图表**。生成多页 deck
前**必须先规划页型**——它本身有 ~36 个 layout，逻辑/文字页有现成版式，缺的是判断：

> **每页先问**：这页论点有没有"支撑数据 + 需要看趋势/对比/分布"？
> **没有 → 文字/逻辑/表格版式**（`bullet_points` / `pyramid` / `process_flow` /
> `comparison_table` / `section_divider`）；**有且图能加强 → 才上 chart 版式**。
> 默认文字，图表是论点"挣来"的。**硬约束**：chart 页 ≤ 全本 ~40%、连续 ≤ 2 张。

两条王牌纪律（借鉴 academic-pptx-skill）:**Action Title**(每页标题是结论句不是主题词)、**Ghost Deck Test**(标题顺读能讲通全论证,否则先改 outline)。

完整页型 taxonomy、图表预算、规划配方、**`plan_deck` typed outline schema(机器契约,可结构化输出+校验)**、自检 rubric、反模式、范例 outline、**借鉴出处引用**：见 **`references/deck-planning.md`**（规划整本时先读它）。

## 解决范围

- 模板占位符替换生成 PPT
- Job JSON 声明式编排
- 数据连接器：CSV / Excel / Tushare
- DataFrame 变换
- 图表生成：双轴组合图、日期轴、金融预设、瀑布图、散点图、气泡图
- 页面编排：主题、布局、页眉页脚、结论页
- PPT 解析 → 编辑 → 重建
- DeckLinter 质量审计

## 图表精修（细粒度控制）

**首选 Job JSON：直接照抄下面结构改字段，再 `ableppt render your_job.json`。** 精修放进 page 的 `data.layout_config`（同名旋钮在 Python config 类里等价，见末尾）：

```json
{
  "mode": "composer",
  "theme": "dashboard_shell_16_9",
  "datasources": { "d": { "type": "csv", "path": "your.csv" } },
  "pages": [{
    "layout": "chart_full",
    "data": {
      "title": "标题",
      "source": "d",
      "categories_col": "月份",
      "series_config": [
        { "key": "销量", "name": "销量", "type": "bar",  "axis": "primary" },
        { "key": "增速", "name": "增速", "type": "line", "axis": "secondary" }
      ],
      "style_config": { "color_scheme": "categorical" },
      "layout_config": {
        "value_axis_config":           { "axis_title": "RMB bn", "number_format": "#,##0", "tick_label_rotation": -45 },
        "secondary_value_axis_config": { "axis_title": "增速 %",  "number_format": "0.0%" },
        "category_axis_config":        { "tick_label_rotation": -45 }
      }
    }
  }],
  "output": { "path": "out.pptx" }
}
```

可调旋钮（`value_axis_config` / `secondary_value_axis_config` / `category_axis_config` 通用）：

- **轴标题** `axis_title`、**标签旋转** `tick_label_rotation`（如 `-45`）
- `number_format`（如 `"#,##0"` / `"0.0%"`）、`font_name` / `font_size_pt`
- 值轴量程 `min_value` / `max_value`、`major_unit`、网格线 `has_major_gridlines`
- 图例 `legend_config`：`position`、`font_size_pt`

> **容错边界（弱 agent 必读）**：
> - **配色名 / 主题名**写错或不认识 → **自动回退默认、不报错**，照常出图（`color_scheme` 回退 `default`，`theme` 回退默认主题；想选对就 `ableppt list-presets` 查 `color_schemes`）。
> - 但 **列名 / 布局名**写错会**明确报错且不出图**（有意为之——瞎猜数据列会产出"静默错图"，比报错更糟）：`categories_col` 和 `series_config[].key` 必须是数据里真实存在的列。报错信息会**列出可用列 / 可用布局**（如 `列 ['打错的列'] 不在数据中。可用列：[...]`），照着改即可。

**范例可直接照抄改**：`job_combo_gallery_demo.json`（双轴组合）、`job_waterfall_demo.json`、`job_range_snapshot_demo.json`。

需要写 Python 时（等价底层接口）：`from ableppt.chart_builder import ChartLayoutConfig, CategoryAxisConfig, ValueAxisConfig, LegendConfig, StyleConfig`；隐藏单条系列图例项：`from ablechart.annotations import delete_legend_entry`（facade 未透传，直接从引擎取）。

**尚不支持**：对数轴、原生 display units（×1000/百万角标）、图例手动 XY 定位。

## 核心工作流

| 场景 | 推荐入口 |
|------|----------|
| 模板 + 数据 → 报告 | `ableppt generate` / `scripts/generate_ppt.py` |
| Job JSON → 报告 | `ableppt render` / `scripts/render_ppt.py` |
| 多数据源抓取 + 编排 | `ableppt fetch-data` + `ableppt validate-job` + `ableppt render` |
| 查看 chart engine 兼容层 | `ableppt chart-engine-info` |
| 单页瀑布图 | `ableppt render-waterfall waterfall_demo.json output/demo.pptx` |
| Composer 瀑布图页 | `ableppt render job_waterfall_demo.json` |
| 单页散点图 | `ableppt render-scatter scatter_demo.json output/scatter_demo.pptx` |
| 单页气泡图 | `ableppt render-bubble bubble_demo.json output/bubble_demo.pptx` |
| 解析已有 PPT | `scripts/parse_ppt.py` |
| JSON → 重建 PPT | `scripts/rebuild_ppt.py` |
| 审计输出 PPT | `scripts/validate_ppt.py` |

## 原子脚本

- `scripts/fetch_data.py`
- `scripts/validate_job.py`
- `scripts/render_ppt.py`
- `scripts/generate_ppt.py`
- `scripts/parse_template.py`
- `scripts/describe_chart.py`
- `scripts/parse_ppt.py`
- `scripts/rebuild_ppt.py`
- `scripts/list_presets.py`
- `scripts/render_waterfall.py`
- `scripts/render_scatter.py`
- `scripts/render_bubble.py`
- `scripts/add_placeholders.py`
- `scripts/validate_ppt.py`

## 关键包层级

- `ableppt.engine`：系统调度入口
- `ableppt.connectors`：数据源连接器
- `ableppt.transformers`：数据变换
- `ableppt.chart_builder`：兼容层入口，实际实现路由到 `ablechart`
- `ableppt.template`：模板替换与金融图表预设
- `ableppt.composer`：页面编排与主题
- `ableppt.parsers` / `ableppt.renderers`：解析与重建
- `ableppt.qa`：PPT 合规检查
- `ableppt.advisors` / `ableppt.extractors`：推荐与风格提取

## 适用判断

优先使用 `ableppt` 的情况：

- 任务核心是“从数据生成金融 PPT”
- 需要多页报告，不只是单页图
- 需要模板、编排、解析、重建、审计中的任意一环
- 需要保留 PowerPoint 中的可编辑性

如果任务只是底层双轴图表能力本身，可降到 `ablechart`。

如果任务是：

- 只需要验证 `chart_builder` 兼容层是否已正确连到 `ablechart`
- 只需要生成或回读单页瀑布图
- 只是在完善 chart engine 的 CLI / 帮助 / 文档 / 样例 / 合同测试

仍然优先在 `ableppt` 范围内完成，因为这是当前对外兼容入口。

## 已知边界

- 当前最成熟：金融时间序列、双轴组合图、模板替换、报告型页面编排、瀑布/散点/气泡图
- `merge` 变换未实现
- 图表精修尚缺：对数轴、原生 display units（×1000/百万角标）、图例手动 XY 定位（详见「图表精修」节）
- 某些极复杂图表类型仍不属于当前稳定范围

> 引擎版本：依赖 `ablechart>=0.1.0,<0.2`（当前 0.1.1，含轴标题 / 标签旋转 / 按 axId 认轴）。
