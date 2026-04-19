基于提供的 Morningstar（晨星）市场观察报告（PDF）和现有的 `skill` 工具包规范（如 JP Morgan GTM 设计语言），我提取了该报告的核心特征，并为你提供针对性的 Layout 配置方案以及对 `skill` 的底层优化建议。

### 核心要点概括

1. **视觉与排版特征**：Morningstar 高度依赖**上下双图（Vertical Two Charts）**展示长周期时间序列，且具有强烈的**“结论先行（Insights-first）”**特征（每页图表上方必有 2-3 行分析结论段落）。
2. **Layout 配置映射**：需要基于现有的 `dashboard` 和 `chart_table` 衍生出 `two_charts_vertical`（上下双图）和 `chart_table_horizontal`（左图右表）。
3. **Skill 工具包优化方向**：扩展 `ChartBuilder` 以支持基准带（Reference Bands）和范围条形图（Floating/Range Bar）；在页面级元数据中增加标准的 `insight_text` 插槽；在 `DeckLinter` 中加入对 X 轴强制对齐的校验。

---

### 一、 Morningstar 报告特征提取与 Layout 配置映射

现有的 `skill` 规范（受 JP Morgan 启发）主推左右 50/50 的双图布局。然而，Morningstar 报告在处理宏观数据时，展现了不同的专业偏好。

#### 1. 宏观长周期对比：上下双图 (Vertical Two Charts)

* **特征分析**：如报告 P16（市盈率与估值）、P17（大小盘相对估值）、P19（美股七雄与大盘）、P26（信用利差）。当两个图表共享相同的日期 X 轴时，Morningstar 绝对优先使用上下布局，而非左右布局。这样能最大化横向空间，展现更长的时间周期和更细腻的波动。
* **Layout 配置定义 (`two_charts_vertical`)**：
```python
# 适用场景：汇率与利率、宏观指标对比、估值与价格
layout_config = {
    "header_y": 0.25,
    "insight_text_y": 0.65,      # 给结论文本留出 0.5" 的高度
    "chart_top": {
        "x": 0.60, "y": 1.25, "w": 12.133, "h": 2.75
    },
    "chart_bottom": {
        "x": 0.60, "y": 4.15, "w": 12.133, "h": 2.75
    },
    "sync_x_axis": True          # 关键：下发指令强制上下图的X轴范围对齐
}

```



#### 2. 走势 + 截面数据切片：左图右表 (Chart & Table Horizontal)

* **特征分析**：如 P23（左侧为不同时期的收益率曲线，右侧为各期限收益率和利差明细表）。这弥补了纯折线图无法精确读取当期快照数据的缺陷。
* **Layout 配置定义 (`chart_table_horizontal`)**：
```python
# 对已有 layout-chart-table.md 的横向衍生
layout_config = {
    "chart_area": {
        "x": 0.60, "y": 1.20, "w": 8.0, "h": 5.5  # 图表占据左侧约 65%
    },
    "table_area": {
        "x": 8.90, "y": 1.20, "w": 3.833, "h": "auto" # 表格占据右侧 35%
    },
    "table_config": {
        "ib_style": True,        # 无垂直边框
        "zebra": False           # 数据少于 10 行时可关闭斑马纹，更显清爽
    }
}

```



#### 3. 极简区间数据表达：范围条形图 (Range Bar Chart)

* **特征分析**：如 P24（各类固定收益资产的 5 年收益率高低点区间 vs 当前值）。这种图表信息密度极高，摒弃了传统折线图的杂乱，直接给出“水位”位置。
* **Layout 映射**：属于 `chart_full` 布局，但严重依赖 `ChartBuilder` 的深层能力。

---

### 二、 对 `skill` 工具包的可执行优化建议

基于上述特征，当前的 `skill` 工具包（特别是 `ppt_station` 组件）存在一些空白，建议进行以下架构和功能优化：

#### 1. 强化页面结构：引入标准的 `insight_text` 插槽

* **问题**：当前的 Job JSON schema (如 `layout-dashboard.md`) 中只有 `subtitle`，往往被渲染为单行浅色文本。但金融报告要求“结论先行”。
* **优化建议**：在基础页面数据模型中新增 `insight` 或 `takeaways` 字段。
* **渲染逻辑**：位于 `page_header`（分隔线）下方，占据全宽，支持最多 3 行文本自动折行。字体设定为 `body_font`，字号 `body_size`，颜色 `text_dark` 或 `text_muted`。图表的 `start_y` 应根据该文本块的实际高度自适应下推。



#### 2. 升级图表引擎 (`ChartBuilder`): 支持高级投行图表类型

* **增加范围条形图（Floating/Range Bar）支持**：
* **实现方式**：在 `series_config` 的 `type` 枚举中新增 `range_bar`。API 需接受 `min_col`, `max_col`, `current_col`。在 python-pptx 中可通过不可见的底层柱子做堆叠，或使用具有误差线的自定义散点/折线组合来实现。


* **增加基准线/参考带（Reference Lines & Bands）支持**：
* 如报告 P17 中的历史均值线及标准差区间。
* **实现方式**：扩展 `ChartLayoutConfig`，允许传入 `y_axis_reference_lines: [{"value": 1.2, "label": "均值", "color": "accent", "dash": "dash"}]`。在底层渲染时叠加不带标记点的辅助线序列。



#### 3. 升级自动化规则与审计 (`ChartJunkCleaner` & `DeckLinter`)

* **自动轴对齐校验 (Axis Synchronization)**：
* 当渲染 `two_charts_vertical` 布局且判断两图的 `categories_col` 均为时间序列时，在 `render_ppt.py` 环节自动提取最大/最小日期，强制将两图的 X 轴 bounds 设为一致。


* **Linter 规则增强**：
* 增加 `WARN: insight_missing`。对于分析类布局（如 `chart_full`, `two_charts`），如果在 JSON 中未提供 `insight`（或长度小于 20 个字符），抛出警告。目标是纠正分析师“只贴图、不写结论”的坏习惯，强制提高决策信息密度。