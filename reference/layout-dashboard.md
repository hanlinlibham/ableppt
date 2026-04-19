# 布局标注：`dashboard`（仪表盘页）

> 设计师交付物 · v1.0 · 2026-02-20
> 参考来源：投行级研报 图表页设计语言 + 现有 kpi.py / chart.py 实现规范

---

## 设计意图

一页内同时展示**核心数字 + 趋势图表**。金融场景典型用途：
- 组合季报首页：年化收益 / 夏普比率 / 最大回撤 / 规模 + 净值曲线图
- 宏观月报：GDP / CPI / PMI / 利率 + 经济指标走势图
- 基金评价：超额收益 / 信息比率 / 跟踪误差 / Calmar + 比较图

---

## 变体 A（主变体）：顶部 KPI 条 + 下方大图

### ASCII 线框图

```
┌─────────────────────────────────────────────────────────────┐  y=0
│ ▌ 页面标题（bold, title_size-2, text_dark）                   │  y=0.25~0.85
│   ████████ accent 装饰线（2.0w × 0.04h）                     │  y=0.90
│                                                              │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐          │  y=1.10
│ │ ▌▌▌▌▌▌▌▌▌▌▌ │ │ ▌▌▌▌▌▌▌▌▌▌▌ │ │ ▌▌▌▌▌▌▌▌▌▌▌ │          │  (顶部色条 h=0.05)
│ │  指标名       │ │  指标名       │ │  指标名       │          │  y=1.42
│ │              │ │              │ │              │          │
│ │   12.3%      │ │   1.87       │ │  -4.2%      │          │  y=1.72 大数字
│ │              │ │              │ │              │          │
│ │  +2.1% ↑    │ │  +0.15 ↑    │ │  本期最低     │          │  y=2.50 变化/注释
│ └──────────────┘ └──────────────┘ └──────────────┘          │  y=2.80
│                                                              │
│  图表区副标题（可选，body_size, text_muted）                   │  y=3.05
│                                                              │
│ ┌────────────────────────────────────────────────────────┐  │  y=3.35
│ │                                                        │  │
│ │              大图表（full width）                        │  │  h=3.90
│ │                                                        │  │
│ └────────────────────────────────────────────────────────┘  │  y=7.25
└─────────────────────────────────────────────────────────────┘  y=7.50
```

### 精确元素标注（英寸，m = theme["margin"] = 0.6）

#### 全局常量
```
sw = 13.333          # 幻灯片宽度
sh = 7.5             # 幻灯片高度
m  = theme["margin"] # 默认 0.6
content_w = sw - 2*m # = 12.133
```

#### 页面标题区

| 元素 | x | y | w | h | 样式 |
|------|---|---|---|---|------|
| 背景 | 0 | 0 | 13.333 | 7.5 | `bg_light` |
| 页面标题 | `m` | 0.25 | `content_w` | 0.6 | `text_dark`, bold, `title_size-2`, left, header_font |
| accent 装饰线 | `m` | 0.90 | 2.0 | 0.04 | `accent` fill |

#### KPI 卡片区（3 张卡片）

```
n       = len(cards)           # 3 或 4
gap     = 0.30                 # 卡片间距
card_w  = (content_w - gap*(n-1)) / n
card_h  = 1.70
start_y = 1.10
```

**3 张卡片时**：`card_w = (12.133 - 0.60) / 3 = 3.844`
**4 张卡片时**：`card_w = (12.133 - 0.90) / 4 = 2.808`

每张卡片（以第 i 张为例，`cx = m + i*(card_w+gap)`）：

| 元素 | x（相对卡片左边） | y（相对幻灯片） | w | h | 样式 |
|------|----------------|---------------|---|---|------|
| 卡片背景 | `cx` | `start_y` = 1.10 | `card_w` | 1.70 | `card_bg` fill, `border` 边框 1pt, 圆角 0.08" |
| 顶部色条 | `cx + 0.12` | 1.10 + 0.10 = **1.20** | `card_w - 0.24` | 0.05 | `primary` fill |
| 指标名（label） | `cx + 0.20` | **1.40** | `card_w - 0.40` | 0.28 | `text_muted`, `body_size`, center, body_font |
| 大数字（value） | `cx + 0.20` | **1.72** | `card_w - 0.40` | 0.72 | `primary`, **`kpi_size`**, bold, center+middle, header_font |
| 变化值（change） | `cx + 0.20` | **2.50** | `card_w - 0.40` | 0.25 | `positive`/`negative`, `body_size+1`, bold, center, body_font |

> **change 颜色判断**：以 `+` 开头 → `positive`；以 `-` 开头 → `negative`

#### 图表区

| 元素 | x | y | w | h | 样式 |
|------|---|---|---|---|------|
| 图表区副标题（可选） | `m` | **3.05** | `content_w` | 0.25 | `text_muted`, `body_size-1`, left, body_font |
| 图表 | `m` | **3.35** | `content_w` | **3.90** | ChartBuilder |

> 有副标题时图表上移 0 px（副标题和图表不重叠，副标题占 3.05~3.30，图表从 3.35 开始）
> 底部安全区：3.35 + 3.90 = **7.25**，留 0.25 底部安全边距 ✓

---

## 变体 B（次变体）：左图 60% + 右侧 KPI 竖排

用于 KPI 较多（4-5 个）且图表更重要的场景。

### ASCII 线框图

```
┌──────────────────────────────────────────────────────────┐
│ 页面标题                                                   │  y=0.25
│ ▌▌ accent 线                                             │  y=0.90
│                                                          │
│ ┌─────────────────────────────┐  ┌────────────────────┐  │  y=1.10
│ │                             │  │ 指标名              │  │
│ │                             │  │  12.3%             │  │  KPI card 1
│ │                             │  │ +2.1% ↑           │  │
│ │                             │  └────────────────────┘  │
│ │         大图表               │  ┌────────────────────┐  │
│ │        (60% 宽)              │  │ 指标名              │  │  KPI card 2
│ │                             │  │  1.87              │  │
│ │                             │  └────────────────────┘  │
│ │                             │  ┌────────────────────┐  │
│ │                             │  │ 指标名              │  │  KPI card 3
│ │                             │  │  -4.2%             │  │
│ └─────────────────────────────┘  └────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### 精确标注

```
chart_w   = content_w * 0.60   # = 7.280
right_w   = content_w * 0.38   # = 4.611  (留 0.02 给中间分隔)
gap_lr    = content_w - chart_w - right_w  # ≈ 0.242 居中分隔
right_x   = m + chart_w + gap_lr  # ≈ 8.122

chart_top = 1.20
chart_h   = 7.5 - chart_top - 0.25  # = 6.05
```

| 元素 | x | y | w | h |
|------|---|---|---|---|
| 大图表 | `m`=0.6 | 1.20 | 7.280 | 6.05 |
| KPI 卡片（竖排，n张） | 8.122 | 见下方计算 | 4.611 | 见下方 |

**竖排 KPI 卡片高度计算**：
```
total_h   = 6.05          # 与图表等高
n         = len(cards)    # 通常 3-5 张
gap_v     = 0.20          # 纵向间距
card_h    = (total_h - gap_v*(n-1)) / n
start_y   = 1.20
# 第 i 张 y = start_y + i*(card_h + gap_v)
```

竖排卡片内部布局（card_h 可变）：
- 左侧竖色条（而非顶部色条）：`right_x`, `card_y+0.1`, `0.05`, `card_h-0.2`, `primary` fill
- 指标名：`right_x+0.25`, `card_y+0.15`, `right_w-0.45`, `0.28`, `text_muted`, body_size
- 大数字：`right_x+0.25`, `card_y+0.45`, `right_w-0.45`, `card_h*0.45`, `primary`, kpi_size*0.85, bold
- 变化值：底部 0.28 高度区域，positive/negative

---

## 数据接口

### 变体 A（top_kpi 模式）

```python
data = {
    # 必须
    "title": "组合运行情况",           # 页面标题
    "cards": [                          # 3-4 个 KPI 卡片
        {
            "label": "年化收益率",       # 指标名
            "value": "12.3%",           # 已格式化数值（大数字）
            "change": "+2.1%",          # 可选：变化值（+开头→绿，-开头→红）
        },
        {
            "label": "夏普比率",
            "value": "1.87",
            "change": "+0.15",
        },
        {
            "label": "最大回撤",
            "value": "-4.2%",
            # change 省略时不显示变化行
        },
    ],
    # 图表（同 chart_full 的图表参数）
    "df": df,                           # DataFrame
    "categories_col": "日期",
    "series_config": [...],
    "style_config": None,               # 可选
    "layout_config": None,              # 可选

    # 可选
    "subtitle": None,                   # 页面副标题（accent 线后）
    "chart_label": "净值走势",          # 图表区左上方小标题
    "variant": "top_kpi",              # "top_kpi"（默认）| "side_kpi"
}
```

### 变体 B（side_kpi 模式）

同上，改 `"variant": "side_kpi"`，图表和 cards 含义相同。

---

## 实现伪代码

```python
def layout_dashboard(slide, data, theme):
    m = theme["margin"]
    sw = 13.333
    content_w = sw - 2 * m
    variant = data.get("variant", "top_kpi")

    set_slide_bg(slide, theme["bg_light"])

    # ── 标题区 ──────────────────────────────────────
    add_text(slide, data["title"],
             x=m, y=0.25, w=content_w, h=0.6,
             font_size=theme["title_size"] - 2, color=theme["text_dark"],
             bold=True, font_name=theme["header_font"])
    add_rect(slide, m, 0.90, 2.0, 0.04, fill=theme["accent"])

    if data.get("subtitle"):
        add_text(slide, data["subtitle"],
                 x=m, y=1.00, w=content_w, h=0.30,
                 font_size=theme["body_size"] - 1, color=theme["text_muted"],
                 font_name=theme["body_font"])

    # ── 分支：变体 A（顶部 KPI + 下方图表）────────────
    if variant == "top_kpi":
        cards = data["cards"]
        n = len(cards)
        gap = 0.30
        card_w = (content_w - gap * (n - 1)) / n
        card_h = 1.70
        start_y = 1.10

        for i, card in enumerate(cards):
            cx = m + i * (card_w + gap)
            # 卡片背景（圆角）
            add_rounded_rect(slide, cx, start_y, card_w, card_h,
                             fill=theme["card_bg"], line_color=theme["border"],
                             line_width=1)
            # 顶部色条
            add_rect(slide, cx + 0.12, start_y + 0.10, card_w - 0.24, 0.05,
                     fill=theme["primary"])
            # 指标名
            add_text(slide, card["label"],
                     x=cx + 0.20, y=start_y + 0.30, w=card_w - 0.40, h=0.28,
                     font_size=theme["body_size"], color=theme["text_muted"],
                     align="center", font_name=theme["body_font"])
            # 大数字
            add_text(slide, card["value"],
                     x=cx + 0.20, y=start_y + 0.62, w=card_w - 0.40, h=0.72,
                     font_size=theme["kpi_size"], color=theme["primary"],
                     bold=True, align="center", valign="middle",
                     font_name=theme["header_font"])
            # 变化值
            if card.get("change"):
                change = card["change"]
                color = theme["positive"] if not change.startswith("-") else theme["negative"]
                add_text(slide, change,
                         x=cx + 0.20, y=start_y + 1.40, w=card_w - 0.40, h=0.25,
                         font_size=theme["body_size"] + 1, color=color,
                         bold=True, align="center", font_name=theme["body_font"])

        # 图表区副标题
        if data.get("chart_label"):
            add_text(slide, data["chart_label"],
                     x=m, y=3.05, w=content_w, h=0.25,
                     font_size=theme["body_size"] - 1, color=theme["text_muted"],
                     font_name=theme["body_font"])
        # 大图表
        _add_chart_to_slide(
            slide, data,
            position=(Inches(m), Inches(3.35)),
            size=(Inches(content_w), Inches(3.90)),
        )

    # ── 分支：变体 B（左图 + 右侧竖排 KPI）───────────
    elif variant == "side_kpi":
        chart_w = content_w * 0.60      # 7.280
        right_w = content_w * 0.38      # 4.611
        gap_lr = content_w - chart_w - right_w
        right_x = m + chart_w + gap_lr
        chart_top = 1.20
        chart_h = 7.5 - chart_top - 0.25

        _add_chart_to_slide(
            slide, data,
            position=(Inches(m), Inches(chart_top)),
            size=(Inches(chart_w), Inches(chart_h)),
        )

        cards = data["cards"]
        n = len(cards)
        gap_v = 0.20
        card_h = (chart_h - gap_v * (n - 1)) / n

        for i, card in enumerate(cards):
            cy = chart_top + i * (card_h + gap_v)
            add_rounded_rect(slide, right_x, cy, right_w, card_h,
                             fill=theme["card_bg"], line_color=theme["border"], line_width=1)
            # 左侧竖色条
            add_rect(slide, right_x, cy + 0.10, 0.05, card_h - 0.20,
                     fill=theme["primary"])
            # 指标名
            add_text(slide, card["label"],
                     x=right_x + 0.25, y=cy + 0.15, w=right_w - 0.45, h=0.28,
                     font_size=theme["body_size"], color=theme["text_muted"],
                     font_name=theme["body_font"])
            # 大数字（自适应 card_h）
            add_text(slide, card["value"],
                     x=right_x + 0.25, y=cy + 0.45, w=right_w - 0.45,
                     h=card_h * 0.45,
                     font_size=int(theme["kpi_size"] * 0.85), color=theme["primary"],
                     bold=True, valign="middle", font_name=theme["header_font"])
            # 变化值
            if card.get("change"):
                change = card["change"]
                color = theme["positive"] if not change.startswith("-") else theme["negative"]
                add_text(slide, change,
                         x=right_x + 0.25, y=cy + card_h - 0.35, w=right_w - 0.45, h=0.28,
                         font_size=theme["body_size"], color=color,
                         bold=True, font_name=theme["body_font"])
```

---

## 设计决策说明

### 为什么 KPI 大数字用 `kpi_size` 而不是固定字号？
卡片数量影响卡片宽度（3张→3.84英寸 vs 4张→2.81英寸），字号应跟随卡片宽度变化。`kpi_size` 是主题全局设置，开发者可按主题调整（建议：3张卡时 kpi_size=36pt，4张时=28pt）。

### 为什么顶部色条而非圆角变化？
参考 投行级研报 和现有 kpi.py 的一致性。色条 `primary` 颜色给卡片一个品牌锚点，同时避免全彩卡片在报告中过于抢眼。

### 变体 A 的图表起始 y=3.35 而非 3.10？
- KPI 区结束：1.10 + 1.70 = 2.80
- 分隔 gap：0.25 → y=3.05
- 副标题区：3.05~3.30（高度 0.25）
- 图表内边距：0.05
- 图表起始：3.35
- 这样即使没有副标题，图表也在 y=3.35 开始（不因 `chart_label` 有无而跳动）

### 变体 B 的图表比例为 60%？
投行级研报 中"1大+2小"布局中大图约占 60%。60% 给图表足够面积展示时间序列细节，40% 给右侧 KPI 仍有约 5 英寸宽度，足够显示 2-3 位小数的数值。

---

## 与现有布局的区别

| 布局 | 与 dashboard 的区别 |
|------|-------------------|
| `kpi_cards` | 只有数字卡片，没有图表 |
| `chart_full` | 只有图表，没有 KPI 数字 |
| `two_charts` | 两个图表，没有 KPI 数字 |
| `dashboard` | **唯一** 在一页内同时显示 KPI + 趋势图的布局 |

---

## 测试用 data 示例

```python
import pandas as pd

df = pd.DataFrame({
    "日期": pd.date_range("2024-01-01", periods=12, freq="ME"),
    "组合净值": [1.00, 1.02, 1.05, 1.08, 1.07, 1.10, 1.12, 1.09, 1.13, 1.15, 1.18, 1.21],
    "基准净值": [1.00, 1.01, 1.03, 1.05, 1.04, 1.06, 1.07, 1.06, 1.08, 1.10, 1.12, 1.14],
})

data = {
    "title": "组合2024年运行情况",
    "subtitle": "截至2024年12月31日",
    "cards": [
        {"label": "年化收益率", "value": "21.0%", "change": "+9.0% vs 基准"},
        {"label": "夏普比率",   "value": "1.87",   "change": "+0.23"},
        {"label": "最大回撤",   "value": "-2.8%",  "change": "-1.4% vs 基准"},
    ],
    "df": df,
    "categories_col": "日期",
    "series_config": [
        {"key": "组合净值", "name": "组合净值", "type": "line", "axis": "primary"},
        {"key": "基准净值", "name": "基准净值", "type": "line", "axis": "primary"},
    ],
    "chart_label": "净值走势（2024年）",
    "variant": "top_kpi",
}
```
