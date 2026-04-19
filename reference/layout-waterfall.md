# Layout: `waterfall` — 瀑布图/归因分析

> 幻灯片尺寸: 13.333 × 7.5 英寸 | 边距: 0.6 英寸 | 内容宽: 12.133 英寸

> 当前状态:
> - `pptfi` 已提供 standalone waterfall CLI / SDK：`pptfi render-waterfall waterfall_demo.json output.pptx`
> - composer `LAYOUT_REGISTRY` 已注册 `waterfall`
> - 这是当前布局约定与数据接口说明

---

## 用途

收益归因、成本分解、利润桥图（Profit Bridge）、组合贡献分析。
展示"从起点 → 各因素贡献 → 终点"的累积变化过程。

---

## ASCII 线框图

```
┌─────────────────────────────────────────────────────────────┐
│ [标题]                                          y=0.25       │
│ ▬▬ (accent 装饰线 2.0")                         y=0.90       │
│                                                              │
│  起始值        增加项    增加项    减少项    最终值           │
│  ┌──────┐      ┌──────┐                                     │
│  │      │      │ +██  │ +██      │      │                   │
│  │ 基础 │      │      │          │ -██  │ ┌──────┐          │
│  │      │      │      │          │      │ │ 合计 │          │
│  └──────┘      └──────┘          └──────┘ └──────┘          │
│   8.50%        +2.10%  +1.30%   -1.80%   10.10%            │
│  [期初收益]   [权益贡献] [债券贡献] [汇率拖累] [期末收益]   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 数据结构说明

瀑布图数据包含：
- **start** — 起始值（期初，作为第一个完整柱）
- **items** — 各贡献因素（浮动柱，正向或负向）
- **end** — 终止值（期末，作为最后一个完整柱，可自动计算）

---

## 精确坐标标注

### 固定元素

| 元素 | x | y | w | h | 字号 | 颜色 | 对齐 |
|------|---|---|---|---|------|------|------|
| 页面标题 | 0.60 | 0.25 | 12.133 | 0.60 | title_size-2 | text_dark | 左 |
| 装饰线 | 0.60 | 0.90 | 2.00 | 0.04 | — | accent | — |
| 零基准线 | 0.60 | 图表区中心 | 12.133 | 0.02 | — | text_muted | — |

### 图表区域

| 参数 | 值 | 说明 |
|------|---|------|
| chart_x | 0.60 | 图表左边界 |
| chart_y | 1.30 | 图表顶部（内容区起始） |
| chart_w | 12.133 | 图表宽度 |
| chart_h | 5.50 | 图表高度（到 y=6.80） |
| bar_area_h | 4.00 | 柱体绘制区高度（y=1.50 ~ y=5.50） |
| label_y | 5.60 | 标签行 y（柱下方） |
| value_y | 1.20 | 数值标注 y（柱上方，浮动） |
| footer_y | 6.20 | 数据来源行 |

### 柱体尺寸计算

```
N = len(items) + 2    # 总柱数（start + items + end）
bar_gap = 0.20        # 柱间距（英寸）
bar_w = (chart_w - bar_gap * (N - 1)) / N   # 每柱宽

# N=5: bar_w = (12.133 - 0.80) / 5 = 2.267"
# N=6: bar_w = (12.133 - 1.00) / 6 = 1.856"
# N=7: bar_w = (12.133 - 1.20) / 7 = 1.562"
# N=8: bar_w = (12.133 - 1.40) / 8 = 1.342"

bar_x[i] = chart_x + i * (bar_w + bar_gap)
```

### 柱体高度计算

```
# 图表坐标系
y_axis_max = max(所有累积值的最大值) * 1.15    # 留 15% 上边距
y_axis_min = min(所有累积值的最小值) * 1.15    # 留 15% 下边距（负值时）
y_range = y_axis_max - y_axis_min

# 将数据值映射到像素（英寸）
def value_to_y(v):
    return chart_y + bar_area_h * (1 - (v - y_axis_min) / y_range)

# 起始柱（完整柱，从0到start_value）
start_bar_top = value_to_y(start_value)
start_bar_bottom = value_to_y(0)
start_bar_h = start_bar_bottom - start_bar_top

# 贡献柱（浮动柱，从累积值到累积值+delta）
for item in items:
    bar_top = value_to_y(max(cumsum, cumsum + item.value))
    bar_bottom = value_to_y(min(cumsum, cumsum + item.value))
    bar_h = bar_bottom - bar_top
    cumsum += item.value

# 连接虚线（前一柱的浮动底部 → 当前柱底部）
连接线: w=bar_gap, h=0.01, 颜色=text_muted, 虚线样式
```

### 颜色规则

| 柱类型 | 条件 | 颜色变量 |
|--------|------|---------|
| 起始柱 | — | primary |
| 正向贡献柱 | item.value > 0 | positive |
| 负向贡献柱 | item.value < 0 | negative |
| 终止柱 | — | primary |
| 连接虚线 | — | text_muted |

### 数值标注（柱顶/底 + 数值）

| 元素 | 位置 | 字号 | 颜色 | 格式 |
|------|------|------|------|------|
| 起始/终止数值 | 柱顶上方 0.10" | body_size | text_dark | "X.XX%" |
| 正向贡献值 | 柱顶上方 0.10" | body_size | positive | "+X.XX%" |
| 负向贡献值 | 柱底下方 0.10" | body_size | negative | "-X.XX%" |
| 柱体内标注（高柱时） | 柱体垂直居中 | body_size-1 | text_light | 同上 |

### 底部标签行

| 元素 | x | y | w | h | 字号 | 颜色 | 对齐 |
|------|---|---|---|---|------|------|------|
| 柱体标签 | bar_x[i] | 5.60 | bar_w | 0.45 | caption_size | text_muted | 中 |

---

## 数据接口

```python
data = {
    "title": str,                    # 页面标题
    "subtitle": str,                 # 可选，如 "2024年全年收益归因分析"
    "start": {
        "label": str,                # 如 "期初收益"
        "value": float,              # 如 8.50
        "value_fmt": str,            # 如 "8.50%" 或 "850亿"
    },
    "items": [
        {
            "label": str,            # 贡献因素名称（8字以内）
            "value": float,          # 数值（正=向上，负=向下）
            "value_fmt": str,        # 显示文字（如 "+2.10%"）
            "direction": "up" | "down",  # 可选，若不传则根据 value 符号判断
        },
        ...
    ],
    "end": {
        "label": str,                # 如 "期末收益"
        "value": float | None,       # None则自动计算(start + sum(items))
        "value_fmt": str | None,
    },
    "unit": str,                     # 可选，如 "%" 或 "亿元"，用于Y轴标注
    "show_connector": bool,          # 是否显示连接虚线，默认 True
}
```

---

## 实现伪代码

```python
def layout_waterfall(slide, data, theme):
    m = theme["margin"]
    sw = 13.333
    cw = sw - 2 * m    # 12.133

    set_slide_bg(slide, theme["bg_light"])
    add_text(slide, data["title"],
             x=m, y=0.25, w=cw, h=0.60,
             font_size=theme["title_size"]-2, color=theme["text_dark"],
             bold=True, font_name=theme["header_font"])
    add_rect(slide, m, 0.90, 2.0, 0.04, fill=theme["accent"])

    # 计算柱体布局
    all_bars = [data["start"]] + data["items"] + [data["end"]]
    N = len(all_bars)
    bar_gap = 0.20
    bar_w = (cw - bar_gap * (N - 1)) / N

    chart_y = 1.50
    bar_area_h = 4.00

    # 计算值域
    cumsum = data["start"]["value"]
    all_values = [0, cumsum]
    for item in data["items"]:
        cumsum += item["value"]
        all_values.append(cumsum)
    end_val = data["end"].get("value") or cumsum
    all_values.append(end_val)

    y_max = max(all_values) * 1.15
    y_min = min(all_values) * 1.15 if min(all_values) < 0 else 0
    y_range = y_max - y_min

    def val_to_y(v):
        return chart_y + bar_area_h * (1 - (v - y_min) / y_range)

    # 绘制零线
    zero_y = val_to_y(0)
    add_rect(slide, m, zero_y, cw, 0.015, fill=theme["text_muted"])

    # 绘制柱体
    cumsum = 0
    prev_top_y = None
    for i, bar in enumerate(all_bars):
        bx = m + i * (bar_w + bar_gap)
        is_total = (i == 0 or i == N - 1)

        if is_total:
            v = bar.get("value", cumsum)
            top_y = val_to_y(max(v, 0))
            bot_y = val_to_y(min(v, 0))
            color = theme["primary"]
        else:
            v = bar["value"]
            base = cumsum
            top_y = val_to_y(max(base, base + v))
            bot_y = val_to_y(min(base, base + v))
            color = theme["positive"] if v >= 0 else theme["negative"]
            cumsum += v

        bar_h = bot_y - top_y
        add_rect(slide, bx, top_y, bar_w, bar_h, fill=color)

        # 连接线
        if prev_top_y is not None and data.get("show_connector", True) and not is_total:
            add_rect(slide, bx - bar_gap, prev_top_y, bar_gap, 0.01,
                     fill=theme["text_muted"])
        prev_top_y = bot_y if v >= 0 else top_y

        # 数值标注
        fmt = bar.get("value_fmt", f"{v:+.2f}%")
        label_y = top_y - 0.30 if v >= 0 else bot_y + 0.05
        add_text(slide, fmt,
                 x=bx, y=label_y, w=bar_w, h=0.28,
                 font_size=theme["body_size"], color=color,
                 bold=True, align="center", font_name=theme["body_font"])

        # 底部标签
        add_text(slide, bar["label"],
                 x=bx, y=5.60, w=bar_w, h=0.45,
                 font_size=theme["caption_size"], color=theme["text_muted"],
                 align="center", font_name=theme["body_font"])
```

---

## 设计要点

1. **柱间连接虚线** 从前一柱的"累积底部"水平延伸到当前柱，帮助读者追踪累积过程
2. **数值标注位置**: 正向柱标在顶部上方，负向柱标在底部下方（避免遮挡柱体）
3. **起始/终止柱**（汇总柱）用 `primary` 色，与贡献柱颜色形成视觉区分
4. **最多 8 个柱**（含起始和终止）；超过时建议合并小贡献项为"其他"
5. **含负值时**：零线显示并加粗（0.02"），负值柱延伸到零线以下

---

## 测试数据示例

```python
data = {
    "title": "2024年组合收益归因分析",
    "subtitle": "单位: 百分点（%）",
    "start": {"label": "期初基准", "value": 0, "value_fmt": "0%"},
    "items": [
        {"label": "权益资产", "value": 3.20, "value_fmt": "+3.20%"},
        {"label": "债券资产", "value": 1.80, "value_fmt": "+1.80%"},
        {"label": "另类资产", "value": 0.90, "value_fmt": "+0.90%"},
        {"label": "汇率影响", "value": -0.60, "value_fmt": "-0.60%"},
        {"label": "费用扣除", "value": -0.30, "value_fmt": "-0.30%"},
    ],
    "end": {"label": "期末收益", "value": None, "value_fmt": None},  # 自动计算=5.00%
}
```

---

## 与 投行级研报 GTM 的对应

投行级研报 P4（GDP分解）、P44（EPS贡献）等页面均使用堆叠柱变体。
真正的"利润桥"瀑布图（浮动柱）在收益归因报告中极为常见，需单独布局支持。
