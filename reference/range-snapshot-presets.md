# Range Snapshot Presets

这份文档专门服务于 `jp_demo` 中几页 **vertical valuation** 页的复现，不再讨论普通折线/组合图。

目标是把这些页沉淀成一套稳定的 preset / layout 参数模板，后续只要换数据，不需要重新试布局。

## 适用页面

- `Global valuations`
- `ASX 200 valuation`
- `S&P 500 valuation`
- `MSCI EMU valuation`
- `MSCI Japan valuation`

这些页面虽然标题不同，但视觉语法是一致的：

1. 一组竖版 range snapshot bars
2. 每个 bar 表达历史区间 `min -> max`
3. 一条平均线 `average`
4. 一个当前值 marker `current`
5. 某些页面需要 `axis_break`

## 预设函数

可直接从顶层 SDK 或 `pptchartengine` 使用：

```python
from pptfi import (
    get_vertical_global_valuation_snapshot_preset,
    get_vertical_sector_valuation_snapshot_preset,
    get_asx200_sector_valuation_snapshot_preset,
    get_sp500_sector_valuation_snapshot_preset,
    get_msci_emu_sector_valuation_snapshot_preset,
    get_msci_japan_sector_valuation_snapshot_preset,
)
```

### 1. 全市场 valuation 预设

```python
cfg = get_vertical_global_valuation_snapshot_preset(df)
```

要求列：

- `market`
- `range_min`
- `range_max`
- `average`
- `current`

适合：

- 全球市场估值对比
- 国家/市场 buckets 不多，且不需要 axis break

### 2. 行业 valuation 预设

```python
cfg = get_vertical_sector_valuation_snapshot_preset(
    df,
    title="S&P 500 valuation",
)
```

要求列：

- `sector`
- `range_min`
- `range_max`
- `average`
- `current`

默认行为：

- `orientation="vertical"`
- `axis_break` 自动开启
- 当 `range_max > 30` 时，自动把超出项标记为需要 break
- 默认 `compress_ratio=0.22`
- 默认 lower tick 节奏按 `5x` 生成
- 默认 upper tick 只保留 outlier 段的关键刻度，形成更接近样张的 `tick_values`
- 默认会生成 `tick_values`，而不是只靠连续 `tick_step`

适合：

- sector valuation
- range 上界差异很大
- 需要保住主流行业的阅读密度，同时容纳极端高值

## 4 个 page-specific presets

这些是对 `jp_demo` 样张进一步收敛后的页面级入口：

### `get_asx200_sector_valuation_snapshot_preset(df)`

- 标题：`ASX 200 valuation`
- subtitle：`Forward price-to-earnings ratio`
- 默认 `axis_break.value = 50`
- 默认 `tick_values = [0, 10, 20, 30, 40, 50]`
- 适合极高 outlier 很少、主轴仍以 10x 为节奏的澳股样张

### `get_sp500_sector_valuation_snapshot_preset(df)`

- 标题：`S&P 500 valuation`
- subtitle：`Forward price-to-earnings ratio`
- 默认 `axis_break.value = 30`
- 默认 `tick_values` 采用 `0..30` 的 5x 节奏，另追加高区关键刻度
- 适合 `Energy` 这类明显离群的美股 sector valuation

### `get_msci_emu_sector_valuation_snapshot_preset(df)`

- 标题：`MSCI EMU valuation`
- subtitle：`Forward price-to-earnings ratio`
- 默认不启用 `axis_break`
- 适合欧洲行业估值页

### `get_msci_japan_sector_valuation_snapshot_preset(df)`

- 标题：`MSCI Japan valuation`
- subtitle：`Trailing price-to-book ratio`
- 默认不启用 `axis_break`
- 适合日本估值页，纵轴语义偏 `price-to-book`

## 推荐 composer data 模板

### Global valuations

```json
{
  "layout": "range_snapshot",
  "data": {
    "title": "Global valuations",
    "subtitle": "Current and historical price-to-earning valuations",
    "source": "valuation",
    "categories_col": "market",
    "min_col": "range_min",
    "max_col": "range_max",
    "average_col": "average",
    "current_col": "current",
    "orientation": "vertical",
    "range_color": "5F6772",
    "average_color": "87A330",
    "current_color": "1E88E5",
    "number_format": "0.0x"
  }
}
```

### Sector valuation with axis break

```json
{
  "layout": "range_snapshot",
  "data": {
    "title": "S&P 500 valuation",
    "subtitle": "Forward price-to-earnings ratio",
    "source": "sector_valuation",
    "categories_col": "sector",
    "min_col": "range_min",
    "max_col": "range_max",
    "average_col": "average",
    "current_col": "current",
    "orientation": "vertical",
    "range_color": "5F6772",
    "average_color": "87A330",
    "current_color": "1E88E5",
    "number_format": "0.0x",
    "axis_break": {
      "value": 30.0,
      "compress_ratio": 0.22,
      "tick_values": [0, 5, 10, 15, 20, 25, 30, 50],
      "categories": ["Energy"]
    }
  }
}
```

仓库内现成样例：

- standalone spec: [range_snapshot_sector_demo.json](/Users/jameslee/pension_plan/ppt-project/pptfi/range_snapshot_sector_demo.json)
- composer job: [job_range_snapshot_sector_demo.json](/Users/jameslee/pension_plan/ppt-project/pptfi/job_range_snapshot_sector_demo.json)
- sample data: [range_snapshot_sector_valuation.csv](/Users/jameslee/pension_plan/ppt-project/pptfi/data/range_snapshot_sector_valuation.csv)

## DataFrame 语义约束

### `range_min`

- 历史区间下界
- 必须是数值
- 必须 `<= range_max`

### `range_max`

- 历史区间上界
- 如果显著高于大多数类别，就建议用 `axis_break`

### `average`

- 长期均值
- 必须落在 `range_min ~ range_max` 内

### `current`

- 当前观测值
- 可以落在区间内，也可以靠近上沿

## 什么时候开 axis break

建议满足下列任一条件时开启：

- `max(range_max)` 明显高于第二大值
- 不开 break 时，主流类别都被压缩到图下半段
- 页面目标是“比较多数类别”，不是强调极端值本身

不建议开启的情况：

- 所有类别的 range 上界比较接近
- 你的重点就是展示异常高值的真实跨度

## 当前实现边界

- 已支持 `vertical` / `horizontal`
- 已支持真实分段压缩，不只是 break 符号
- 已支持 axis labels / gridlines 的自定义 overlay
- `axis_break` 仍然是 piecewise compression，不是 PowerPoint 原生分段轴

这已经足够覆盖 `jp_demo` 里的 valuation grammar，并且比继续手工调 shape 更可维护。
