# valuation_snapshot

- **Analysis type**: 估值快照（市场 / 行业当前估值在历史区间位置）
- **Target version**: v0.3.0 (Slice 3)
- **Status**: placeholder
- **Created**: 2026-05-03
- **Blocked on**: [PRD-0001](../../../../ablechart/docs/prds/0001-range-snapshot-visual-polish.md) range_snapshot 视觉精修

## 涉及 family

- `range_snapshot` — 区间柱 + 当前值 + 均值 + 可选轴断裂
- `score_overlay` (combo, 复用 Slice 2)
- `heatmap_matrix` — 横向多市场 / 行业 × 多估值指标的热力图

## 前置依赖

`range_snapshot` 当前是 native chart + custom overlay 复合实现，视觉质量低于 combo（详见 PRD-0001）。本 golden 验收前必须完成 PRD-0001 的视觉精修，否则视觉 diff 过不了人工验收。

## 现有原始素材（脱敏前）

`pptfi/data/` 已有 valuation 相关 CSV：

- `asx200_sector_valuation_snapshot.csv`
- `sp500_sector_valuation_snapshot.csv`
- `msci_emu_sector_valuation_snapshot.csv`
- `msci_japan_sector_valuation_snapshot.csv`
- `range_snapshot_valuation.csv`
- `range_snapshot_sector_valuation.csv`

脱敏要求：

- 去掉具体市场名（ASX 200 / S&P 500 / MSCI EMU / MSCI Japan 等）
- 去掉具体行业的可识别命名（必要时映射到 sector code）
- 保留估值指标的相对水平、波动率、当前值与历史区间的相对位置

可考虑合并多份成单一 `input.parquet`，让 golden 同时覆盖"全市场"与"行业"两类页面。

## 待办（Slice 2 完成 + PRD-0001 完成后启动）

- [ ] 等 PRD-0001 视觉精修完成（阻塞条件）
- [ ] 现有 valuation CSV 脱敏整合为 `input.parquet`
- [ ] `job.json` 编写
- [ ] reference.pptx 生成与验收
- [ ] reference_pages/ baseline 渲染
- [ ] `assertions.yaml` 编写
- [ ] L3 fixture 接入

## 风险

- range_snapshot 的轴断裂位置极敏感，pixel diff 容易误报，需要单页阈值放宽
- heatmap_matrix 的颜色映射如果改动会让全图 diff 变红，需要在 assertions.yaml 对色阶做结构断言而不是仅靠 pixel diff
