# `jp_demo.pdf` 图表建模

这份建模不是为了复刻一份静态 deck，而是为了把 [jp_demo.pdf](/Users/jameslee/pension_plan/ppt-project/jp_demo.pdf) 抽象成一套可执行的图表家族 catalog，作为 `ablechart` 和 `ableppt` 后续实现的目标面。

## 建模原则

1. **先 family，后 page**  
   不把 74 页当成 74 个互不相关的样张，而是先归并为稳定图族，再做逐页映射。

2. **按实现路径建模，不按视觉名字堆标签**  
   每个 family 都带 `preferred_render_path`：
   - `chart_engine`: 走原生可编辑 Office chart
   - `composer_shapes`: 走 shape / text / rect / line 组合
   - `composer_table`: 走 editable table / grid
   - `hybrid`: 图主体走 chart，注释/参考线/说明框走 shape

3. **把“原生 chart 不该做的事”从一开始隔离出来**  
   热力图、quilt、泡泡解释框等，不强行塞进 `create_combo_chart()`。

## 产物

- machine-readable catalog: [jp_demo_chart_catalog.json](/Users/jameslee/pension_plan/ppt-project/ableppt/reference/jp_demo_chart_catalog.json)
- validated loader: [chart_catalog.py](/Users/jameslee/pension_plan/ppt-project/ableppt/ableppt/models/chart_catalog.py)
- HTML atlas: [jp-demo-chart-atlas.html](/Users/jameslee/pension_plan/ppt-project/ableppt/reference/jp-demo-chart-atlas.html)
- atlas renderer: [render_chart_catalog_atlas.py](/Users/jameslee/pension_plan/ppt-project/ableppt/scripts/render_chart_catalog_atlas.py)

加载方式：

```python
from ableppt import load_jp_demo_chart_catalog

catalog = load_jp_demo_chart_catalog()
print(catalog.source_page_count)  # 74
print(catalog.families[0].id)
print(catalog.pages[14].charts[0].family_id)
```

## 图族结论

| family id | 当前状态 | 主路径 | 说明 |
|---|---|---|---|
| `line_chart` | supported | `chart_engine` | 单轴单/多折线，是 deck 中最常见图族 |
| `combo_chart` | supported | `chart_engine` | 双轴 bar/line/area 组合，当前 repo 的强项 |
| `stacked_contribution_chart` | partial | `chart_engine` | 贡献分解、收益分解、yield decomposition 等语义族 |
| `bar_chart` | supported | `chart_engine` | 单值/分组柱条图，含 small-multiple 变体 |
| `stacked_bar_chart` | partial | `chart_engine` | 纵向/横向堆叠、百分比堆叠、分段条 |
| `heatmap_matrix` | planned | `composer_shapes` | 连续色阶矩阵，不建议强行走 Office chart |
| `ranked_tile_matrix` | planned | `composer_table` | quilt / ranked return board，本质是可编辑 tile grid |
| `scatter_chart` | supported | `hybrid` | 纯 XY 已有能力，参考线/说明文字仍需 hybrid |
| `bubble_chart` | supported | `hybrid` | 气泡本体可做，尺寸图例和标签系统还要补 |
| `bar_marker_overlay` | partial | `hybrid` | 年度柱 + 同轴 marker，对标签和 marker-only 行为有要求 |
| `range_snapshot_chart` | planned | `hybrid` | 历史区间 + 均值线 + 当前点，是估值页的独立视觉语法 |
| `floating_range_bar` | partial | `hybrid` | 区间/浮动柱，适合从 stacked 机制上再抽一层 |
| `waterfall_chart` | supported | `chart_engine` | bridge/waterfall 语义，当前已被确认在 deck 中真实出现 |

## 二次校验后的关键修正

这次补做的逻辑校验，重点不是“多看几页”，而是把标题容易误导的页面重新按视觉语法归类。几个重要修正：

- `Exports by type`、`U.S. goods imports by market` 从 `stacked_contribution_chart` 改回 `line_chart`
- 一组 sector valuation 页从普通 `bar_chart` 拆成 `range_snapshot_chart`
- `Contribution to global oil production` 确认为 `waterfall_chart`
- 多组 earnings revision / annual drawdown / fixed-income max-yield 页面收敛到 `bar_marker_overlay`

也就是说，这一版 catalog 比上一版更接近“如何实现”，而不是“标题看起来像什么”。

## 这份 deck 真正要求 repo 补什么

### 1. 继续强化 `chart_engine` 主干

优先补：
- `stacked_contribution_chart`
- `stacked_bar_chart`
- `floating_range_bar`
- `bar_marker_overlay`

原因：
- 它们仍属于“应该保持原生可编辑图表”的范围
- 与现有 `combo/scatter/bubble/waterfall` 内核最接近

### 2. 明确新增一个 `matrix renderer` 支线

不要把下面两类问题继续塞给 `chart_engine`：
- `heatmap_matrix`
- `ranked_tile_matrix`

更合理的方向是：
- 在 `composer` 层增加 matrix/tile/grid 原语
- 输出为 shape/table 组合
- 保持可编辑，但不伪装成 Office chart

### 3. hybrid 应成为一等公民

这份材料里不少图并不是单纯“图表对象”：
- scatter 的 current-yield reference line
- bubble 的 size explainer block
- combo/chart 上的 callout、箭头、强调点

所以长期看，`chart_engine` 负责“数据图主体”，`composer` 负责“解释性覆盖层”，这是正确边界。

## 后续实现建议

建议按 family 而不是按页推进：

1. `line_chart` / `combo_chart` / `bar_chart`  
   这些已基本可用，主要做 API 稳定化和样式抽取。

2. `stacked_contribution_chart` / `stacked_bar_chart`  
   先把所有“贡献/分解/segment”类页面覆盖掉，收益最高。

3. `bar_marker_overlay` / `range_snapshot_chart` / `floating_range_bar`  
   解决估值页、revision 页、区间图、回撤图等剩余异形图。

4. `waterfall_chart`  
   把已有 waterfall 能力正式纳入 deck family，而不是只作为单独 demo。

5. `heatmap_matrix` / `ranked_tile_matrix`  
   以 `composer` 新 renderer 处理，不污染 combo core。

## 为什么这份建模重要

有了这份 catalog，项目目标就从“pptengine 能不能画这页”变成了：

- 这个页面属于哪个 family
- 这个 family 走 `chart_engine`、`composer` 还是 `hybrid`
- 当前状态是 `supported` / `partial` / `planned`
- 下一步该补的是 family，而不是临时 demo

这正是把 `jp_demo.pdf` 从样张库变成产品目标面的关键一步。
