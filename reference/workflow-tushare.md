# Flow D — Tushare 实时数据→报告

使用 Tushare 金融数据 API 获取 A 股实时数据，通过变换处理后生成投资分析报告。

## 前置条件

1. 安装 tushare: `pip install tushare`
2. 配置 Token（任选一种）:
   - 环境变量: `export TUSHARE_TOKEN=your_token_here`
   - `.env` 文件（ppt-st 目录下）: `TUSHARE_TOKEN=your_token_here`

Token 获取: 注册 https://tushare.pro 后在个人主页获取。

## 方式一: Job JSON + run_job.py

适合声明式编排，数据获取和渲染一步完成。

### 完整 Tushare Job JSON 示例

```json
{
  "template": {"path": "aim/aim03.pptx"},
  "datasources": {
    "stock": {
      "type": "tushare",
      "api_name": "pro_bar",
      "ts_code": "600519.SH",
      "start_date": "20250101",
      "end_date": "20251231"
    },
    "index": {
      "type": "tushare",
      "api_name": "pro_bar",
      "ts_code": "000300.SH",
      "start_date": "20250101",
      "end_date": "20251231"
    }
  },
  "transforms": {
    "chart_data": {
      "from": ["stock", "index"],
      "ops": [
        {"type": "sort", "sort_by": ["trade_date"]},
        {"type": "compute", "expr": "close / close.iloc[0] - 1", "output_col": "累计收益率"}
      ]
    }
  },
  "slides": [
    {
      "id": "cover",
      "texts": [
        {"target": "标题", "value": "贵州茅台2025年度分析报告"},
        {"target": "日期", "value": "2025-12-31"}
      ]
    }
  ],
  "output": {"path": "output/tushare_report.pptx", "overwrite": true}
}
```

```bash
python scripts/run_job.py tushare_job.json
```

### Tushare 数据源字段

| 字段 | 说明 |
|------|------|
| `api_name` | `"pro_bar"`（股票日线）或 `"index_daily"`（指数日线）|
| `ts_code` | 证券代码，如 `"600519.SH"`, `"000300.SH"` |
| `start_date` | 起始日期 `"YYYYMMDD"` |
| `end_date` | 结束日期 `"YYYYMMDD"` |

返回的 DataFrame 已按 `trade_date` 升序排列，`trade_date` 为 datetime 类型。

常用字段: `trade_date`, `open`, `high`, `low`, `close`, `vol`, `amount`

## 方式二: gen_moutai_report.py 示例脚本

独立示例脚本，演示完整的 Tushare 数据获取 + 计算 + 报告生成流程:

```bash
python scripts/gen_moutai_report.py
```

该脚本:
1. 从 Tushare 获取贵州茅台和沪深300的当年及5年数据
2. 计算累计收益率、成交额等指标
3. 生成 CSV 中间文件
4. 通过 Flow A（模板替换）生成包含双轴图表的 PPT

输出目录: `pptfi/output/moutai_report/`

**定位说明**: 此脚本是一个完整的端到端示例，展示了自定义数据处理 + PPT 生成的模式。对于新的报告需求，建议:
- 简单场景: 参考此脚本模式编写自定义脚本
- 声明式场景: 使用 Job JSON + `run_job.py`

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| `Tushare token not configured` | 检查 TUSHARE_TOKEN 环境变量或 .env 文件 |
| API 调用频率限制 | Tushare 有调用频率限制，适当添加延时 |
| `pro_bar` 返回空数据 | 检查 ts_code 格式和日期范围是否有效 |
| 指数数据获取失败 | 使用 `api_name: "pro_bar"` + `asset: "I"` 替代 `index_daily` |
