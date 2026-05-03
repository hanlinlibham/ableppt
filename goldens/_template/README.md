# Golden Template

新建一份 golden 时，复制本目录的结构。

## 文件清单

- `input.parquet` — 输入数据，必须脱敏
- `job.json` — pptfi job spec，引用 input.parquet
- `reference.pptx` — 人工验收过的 PPT 输出
- `reference_pages/` — 每页 PNG baseline，用于视觉 diff
- `assertions.yaml` — 关键质量断言（schema 见 [assertions.yaml](assertions.yaml)）
- `README.md` — 本份 golden 的目标分析类型、涉及 family、状态、依赖

## 命名

目录名 = 分析类型 snake_case（如 `performance_attribution`、`valuation_snapshot`）。

不允许：

- 主题名（公司名 / 基金名 / 行业名 / 国家名）
- 来源名（机构名 / 报告名 / 数据供应商名）

## 添加流程

1. 在上级 README 索引里登记
2. 在 ADR-0003 §2 三份首发表里登记（如果是新增第 4+ 份）
3. 复制本模板建目录
4. 准备脱敏输入数据
5. 跑 pptfi 生成 reference.pptx
6. 人工验收 reference.pptx，确认达到"专业"水准
7. 渲染 `reference_pages/` baseline
8. 写 `assertions.yaml`
9. 提 PR；review 中验证可重跑
10. 把状态从 `placeholder` 改为 `accepted`
