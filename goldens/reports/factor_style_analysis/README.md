# factor_style_analysis

- **Analysis type**: 因子风格分析（组合在风格 / 因子上的暴露）
- **Target version**: v0.2.0 (Slice 2)
- **Status**: placeholder
- **Created**: 2026-05-03

## 涉及 family

- `style_box` (scatter) — 二维风格定位（大小盘 × 价值成长）
- `factor_exposure` (combo) — 因子暴露条形对比
- `style_allocation` (combo) — 风格桶配置比例 / 超配比例
- `score_overlay` (combo) — 原值叠加分位或相对得分

## 选作 Slice 2 的理由

引入 scatter family 端到端验证；combo 已经在 Slice 1 跑通可以复用。

## 待办（Slice 1 完成后启动）

- [ ] 输入数据准备（脱敏方案沿用 Slice 1）
- [ ] `job.json` 编写
- [ ] reference.pptx 生成与验收
- [ ] reference_pages/ baseline 渲染
- [ ] `assertions.yaml` 编写
- [ ] L3 fixture 接入

## 输入数据 schema 草案

- 持仓清单（资产类别 / 行业 / 风格桶 / 市值桶 / 估值桶）
- 因子暴露向量（如：market beta, size, value, momentum, quality, low-vol）
- 因子暴露的同期对照（基准 / 同类）
- 历史风格漂移序列（用于 style_allocation 的"超配/低配"图）

## 风险

- scatter 在引擎中是独立 family（不能混入 combo），style_box 必须用独立 chart
- 因子标准化方式（z-score vs percentile）会影响 chart 数值范围，需在 assertions.yaml 固化
