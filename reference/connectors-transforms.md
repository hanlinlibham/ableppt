# 连接器与变换操作参考

## ConnectorFactory — 3 种数据连接器

ConnectorFactory 通过 `type` 字段自动路由到对应的连接器。

### csv — CSV 文件连接器

从本地 CSV 文件加载 DataFrame。

```json
{"type": "csv", "path": "data/stock.csv", "encoding": "utf-8"}
```

- `path`: 相对于 `data_dir`（默认 `pptfi/data/`）或绝对路径
- `encoding`: 默认 `utf-8`

### xlsx — Excel 文件连接器

从 Excel 文件加载 DataFrame。

```json
{"type": "xlsx", "path": "data/report.xlsx", "sheet_name": "Sheet1"}
```

- `path`: 同 csv
- `sheet_name`: 工作表名，默认第一个

### tushare — Tushare 金融数据连接器

从 Tushare Pro API 获取 A 股市场数据。

```json
{
  "type": "tushare",
  "api_name": "pro_bar",
  "ts_code": "600519.SH",
  "start_date": "20240101",
  "end_date": "20241231"
}
```

### sql — SQLite / SQL 查询连接器

适合将高频 API 数据先落本地数据库，再通过 SQL 读取绘图。

```json
{
  "type": "sql",
  "conn": "pptfi/data/tushare_market.sqlite",
  "query": "SELECT ts_code, name, trade_date, close FROM index_bars WHERE ts_code = '000300.SH' ORDER BY trade_date"
}
```

支持的 `api_name`:
- `index_daily`: 指数日线数据（需 `ts_code` 或 `index_code`）
- `pro_bar`: 通用日线数据，前复权（需 `ts_code`）

返回的 DataFrame 自动按 `trade_date` 升序排列，`trade_date` 列已转为 datetime。

前置条件: `TUSHARE_TOKEN` 环境变量或 `.env` 文件。

## DataFrameTransformer — 7 种变换操作

变换在 `transforms` 中定义，每个变换指定 `from`（数据源）和 `ops`（有序操作列表）。

### 多源合并

`from` 支持字符串（单源）或数组（多源 concat）:

```json
{"from": ["stock_data", "index_data"], "ops": [...]}
```

多源使用 `pd.concat(axis=1)` 按列合并。

### groupby — 分组聚合

```json
{"type": "groupby", "by": ["year"], "agg": {"close": "mean", "vol": "sum"}}
```

### pivot — 透视表

```json
{"type": "pivot", "index": "trade_date", "columns": "indicator", "values": "value"}
```

### compute — 计算新列

```json
{"type": "compute", "expr": "close / close.iloc[0] - 1", "output_col": "cumulative_return"}
```

使用 `pandas.DataFrame.eval()`，支持列名引用。

### filter — 条件过滤

```json
{"type": "filter", "condition": "close > 100 and vol > 10000"}
```

使用 `pandas.DataFrame.query()`。

### sort — 排序

```json
{"type": "sort", "sort_by": ["trade_date"], "ascending": true}
```

### rename — 重命名列

```json
{"type": "rename", "map": {"trade_date": "日期", "close": "收盘价"}}
```

### merge — 未实现

会抛 `NotImplementedError`。替代方案:

```json
{"from": ["src1", "src2"], "ops": [...]}
```

用 `from` 数组实现 concat，然后用其他 ops 整理。

## 常用组合模式

### 合并两个 Tushare 序列

```json
{
  "datasources": {
    "stock": {"type": "tushare", "api_name": "pro_bar", "ts_code": "600519.SH"},
    "index": {"type": "tushare", "api_name": "pro_bar", "ts_code": "000300.SH"}
  },
  "transforms": {
    "combined": {
      "from": ["stock", "index"],
      "ops": [
        {"type": "rename", "map": {"close": "stock_close"}}
      ]
    }
  }
}
```

### 计算累计收益率

```json
{
  "ops": [
    {"type": "sort", "sort_by": ["trade_date"]},
    {"type": "compute", "expr": "close / close.iloc[0] - 1", "output_col": "累计收益率"}
  ]
}
```

### 过滤后重命名

```json
{
  "ops": [
    {"type": "filter", "condition": "trade_date >= '2024-01-01'"},
    {"type": "rename", "map": {"trade_date": "日期", "close": "收盘价"}},
    {"type": "sort", "sort_by": ["日期"]}
  ]
}
```
