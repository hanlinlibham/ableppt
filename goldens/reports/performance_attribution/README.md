# performance_attribution

- **Analysis type**: 业绩归因（基金 / 组合收益来源拆解）
- **Target version**: v0.1.0 (Slice 1)
- **Status**: placeholder
- **Created**: 2026-05-03

## 涉及 family

- `performance_compare` (combo) — 时序业绩比较（基金 vs 基准 vs 同类）
- `attribution_decomposition` (waterfall) — 收益来源拆解（如股票贡献 / 债券贡献 / 汇率贡献 / 择时贡献）
- `regime_table_panel` — 阶段图 + 区间收益表

## 选作 Slice 1 的理由

所有涉及的 family 都是纯 native chart（combo / waterfall / table），视觉质量结构性最强，是稳健的 v0.1.0。

## 待办（Slice 1 启动前必须解决）

- [ ] 决定输入数据来源：脱敏真实组合 vs 全合成 vs 混合
- [ ] 确定脱敏方案（公司名映射、规模缩放、时间窗口锚定）
- [ ] 准备 `input.parquet`
- [ ] 编写 `job.json`
- [ ] 跑 pptfi 生成 `reference.pptx`
- [ ] 人工验收 reference 达到"专业"水准
- [ ] 渲染 `reference_pages/` baseline
- [ ] 编写 `assertions.yaml`
- [ ] 接入 pptchartengine L3 fixture

## 输入数据 schema 草案

字段（具体名称在 PRD 中定）：

- 日期序列（月度或日度）
- 基金 / 组合收益序列
- 基准（benchmark）收益序列
- 同类（peer median 或 peer percentile）收益序列（可选）
- 收益拆分项（资产类别 × 收益贡献），如：
  - 股票贡献 / 债券贡献 / 汇率贡献 / 现金贡献 / 择时贡献
- 阶段划分（如：牛市 / 熊市 / 震荡 / 大幅回撤）

## 风险

- 拆分项的 sign 与 totals 关系容易在 waterfall 里出错，必须在 assertions.yaml 里断言总计与拆分一致
- 阶段划分的边界日期会影响 regime_table 的列构成，应固化在脱敏数据中
