# Golden Reference Reports

本目录存放 `ablechart` + `ableppt` 的"金标准"参考报告，用于 [ablechart ADR-0003](../../ablechart/docs/adr/0003-golden-reference-reports.md) 定义的视觉回归与质量验收。

## 命名原则

所有 golden 按**分析类型**命名，不引用任何具体公司名、基金名、机构名、研究品牌。

- ❌ `moutai_quarterly` / `anker_q3` / `jp_demo`
- ✅ `performance_attribution` / `factor_style_analysis` / `valuation_snapshot`

详见 ADR-0003 §1。

## 索引

| Golden | 分析类型 | 目标版本 | 状态 |
|---|---|---|---|
| [performance_attribution](reports/performance_attribution/) | 业绩归因 | v0.1.0 (Slice 1) | placeholder |
| [factor_style_analysis](reports/factor_style_analysis/) | 因子风格分析 | v0.2.0 (Slice 2) | placeholder |
| [valuation_snapshot](reports/valuation_snapshot/) | 估值快照 | v0.3.0 (Slice 3) | placeholder |

## 每份 golden 必须包含

- `input.parquet` — 完整可重跑的脱敏输入数据
- `job.json` — ableppt job spec，引用 input.parquet
- `reference.pptx` — 人工验收过的 PPT
- `reference_pages/` — 每页 PNG baseline，用于视觉 diff
- `assertions.yaml` — 关键质量断言（schema 见 [_template/assertions.yaml](_template/assertions.yaml)）
- `README.md` — 状态、涉及 family、依赖

模板：[_template/](_template/)

## 数据脱敏要求

输入数据必须脱敏：

- **保留**：行业代码、资产类别、时间序列形态、波动率结构、相对强弱关系
- **隐去**：具体公司名、基金代码、基金管理公司名、机构名、第三方研究品牌、可识别的地理标识

脱敏后数据应能让 chart 在视觉上有意义，但不应能通过反查识别出具体标的或来源报告。

## baseline 更新流程

参见 ADR-0003 §4。要点：

- 改动会导致 baseline 变化的 PR 必须显式更新 baseline
- baseline diff 走 PR review，不允许 CI 自动 accept
- 每季度 review 一次
- 更新需要 PM 或资深分析师签字

## 与 ablechart 的关系

- `ableppt/goldens/` 持有数据 + reference + assertions
- `ablechart` 持有 visual diff harness（待 Slice 1 实现）
- L3 测试运行时由 ablechart 的 harness 调用本目录数据

## 状态约定

- `placeholder`：目录与 README 已建，无实际数据
- `in_progress`：输入数据 + job.json 在做，未通过人工验收
- `accepted`：reference.pptx + reference_pages + assertions 完整，已通过验收
- `needs_refresh`：被识别为视觉退化或 baseline 过期，待更新
