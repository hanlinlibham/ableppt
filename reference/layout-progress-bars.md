# Layout: `progress_bars` — 进度条/评分页

> 幻灯片尺寸: 13.333 × 7.5 英寸 | 边距: 0.6 英寸 | 内容宽: 12.133 英寸

---

## 用途

评分展示、指标达标率、能力雷达平铺版、投资组合配置完成度、各资产类别评级。

---

## ASCII 线框图

### 变体 A：单列进度条（5-8 行）

```
┌─────────────────────────────────────────────────────────────┐
│  [标题]                                     y=0.25          │
│  ▬▬ (accent 装饰线)                         y=0.90          │
│                                                              │
│  权益资产    ████████████████████░░░░░░░░░░    80%          │
│              [进度条背景(浅色)]                              │
│                                                              │
│  固定收益    █████████████░░░░░░░░░░░░░░░░░░    52%          │
│                                                              │
│  另类资产    ████████░░░░░░░░░░░░░░░░░░░░░░░    32%          │
│                                                              │
│  海外资产    ████████████████░░░░░░░░░░░░░░░    64%          │
│                                                              │
│  货币市场    ██████░░░░░░░░░░░░░░░░░░░░░░░░░    24%          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 变体 B：带目标值的进度条（显示目标线）

```
│  权益资产    ████████████████████░░░░│░░░░░    80% / 目标 90%│
│                                    ↑ 目标线（垂直虚线）
```

### 变体 C：双列进度条（6-10 行，每列3-5行）

```
│  [左列标题]           │   [右列标题]                        │
│  指标一  ████░░░  75% │   指标A  ████████░░  80%            │
│  指标二  ██░░░░   40% │   指标B  █████████░  90%            │
│  指标三  ███████░ 70% │   指标C  ████░░░░░   42%            │
```

---

## 精确坐标标注

### 变体 A（单列，5-8 行）

**固定元素**

| 元素 | x | y | w | h | 字号 | 颜色 | 对齐 |
|------|---|---|---|---|------|------|------|
| 页面标题 | 0.60 | 0.25 | 12.133 | 0.60 | title_size-2 | text_dark | 左 |
| 装饰线 | 0.60 | 0.90 | 2.00 | 0.04 | — | accent | — |

**行高计算**

```
list_start_y = 1.20
available_h = 5.80   # 7.5 - 1.20 - 0.50(bottom)
row_h = available_h / N

N=5: row_h = 1.16"
N=6: row_h = 0.97"
N=7: row_h = 0.83"
N=8: row_h = 0.73"（最密，仍可读）
```

**单行结构（以 row_y 为行顶部）**

| 元素 | x | y（相对 row_y） | w | h | 字号 | 颜色 | 对齐 |
|------|---|----------------|---|---|------|------|------|
| 标签文字 | 0.60 | +0.15 | 2.80 | 0.40 | body_size | text_dark | 左 |
| 进度条背景（轨道） | 3.50 | +0.20 | 7.80 | 0.30 | — | secondary | — |
| 进度条填充 | 3.50 | +0.20 | 7.80 × (value/max) | 0.30 | — | primary | — |
| 数值文字 | 11.45 | +0.15 | 1.28 | 0.40 | body_size | text_dark | 右 |

> **进度条圆角**: radius=0.05"（轨道和填充均为圆角矩形）
> **填充颜色规则**:
> - 默认: `primary`
> - value/max >= 0.8（优秀）: `positive`（绿）
> - value/max <= 0.3（危险）: `negative`（红）
> - 可通过 `item.color` 强制指定颜色变量名

**目标线（变体 B）**:
```
target_x = 3.50 + 7.80 * (target/max)
add_rect(slide, target_x-0.01, row_y+0.15, 0.02, 0.40,
         fill=theme["accent"])
# 目标值文字
add_text(slide, f"目标:{target_fmt}",
         x=target_x-0.40, y=row_y+0.57, w=0.80, h=0.25,
         font_size=theme["caption_size"]-1, color=theme["accent"],
         align="center")
```

**可选副标注**（进度条下方小字）:
```
x=3.50, y=row_y+0.52, w=7.80, h=0.28
font_size=caption_size-1, color=text_muted
示例: "较上季度 +5.2 个百分点"
```

### 变体 C（双列）

```
col_gap = 0.60
col_w = (12.133 - col_gap) / 2 = 5.767"

左列: x_left = 0.60
右列: x_right = 0.60 + 5.767 + 0.60 = 6.967

每列标签宽: 1.80"
进度条宽: 5.767 - 1.80 - 1.00 = 2.967"
数值宽: 1.00"
```

---

## 数据接口

```python
data = {
    "title": str,                    # 页面标题
    "subtitle": str,                 # 可选，如 "投资组合达标情况（满分100）"
    "variant": "single" | "target" | "double",  # 布局变体，默认 "single"
    "max_value": float,              # 统一最大值（如 100），默认 100
    "unit": str,                     # 可选，数值单位（如 "%", "分"），显示在数值旁
    "items": [
        {
            "label": str,            # 行标签（10字以内）
            "value": float,          # 当前值
            "max_value": float,      # 可选，覆盖全局 max_value
            "target": float,         # 可选，目标值（变体 B 专用）
            "value_fmt": str,        # 可选，自定义数值显示文字（如 "80分"）
            "note": str,             # 可选，进度条下方小注
            "color": str,            # 可选，强制指定填充颜色（主题变量名）
        },
        ...  # 最多 8 行（单列）/ 10 行（双列）
    ],
    # 双列变体时（variant="double"）：
    "left_items": [...],             # 左列数据
    "right_items": [...],            # 右列数据
    "left_title": str,               # 可选，左列分组标题
    "right_title": str,              # 可选，右列分组标题
}
```

---

## 实现伪代码

```python
def layout_progress_bars(slide, data, theme):
    m = theme["margin"]
    sw, sh = 13.333, 7.5
    cw = sw - 2 * m

    set_slide_bg(slide, theme["bg_light"])
    add_text(slide, data["title"],
             x=m, y=0.25, w=cw, h=0.60,
             font_size=theme["title_size"]-2, color=theme["text_dark"],
             bold=True, font_name=theme["header_font"])
    add_rect(slide, m, 0.90, 2.0, 0.04, fill=theme["accent"])

    items = data["items"]
    N = len(items)
    global_max = data.get("max_value", 100)

    list_y = 1.20
    row_h = max(0.73, (sh - list_y - 0.50) / N)

    bar_x = 3.50
    bar_total_w = 7.80
    bar_h = 0.30
    bar_radius = 0.05

    for i, item in enumerate(items):
        ry = list_y + i * row_h
        max_v = item.get("max_value", global_max)
        ratio = min(max(item["value"] / max_v, 0), 1)

        # 颜色选择
        if item.get("color"):
            fill_color = theme[item["color"]]
        elif ratio >= 0.8:
            fill_color = theme["positive"]
        elif ratio <= 0.3:
            fill_color = theme["negative"]
        else:
            fill_color = theme["primary"]

        # 标签
        add_text(slide, item["label"],
                 x=m, y=ry+0.15, w=2.80, h=0.40,
                 font_size=theme["body_size"], color=theme["text_dark"],
                 font_name=theme["body_font"])

        # 轨道背景
        add_rounded_rect(slide, bar_x, ry+0.20, bar_total_w, bar_h,
                         fill=theme["secondary"], radius=bar_radius)

        # 填充（仅当 ratio > 0）
        if ratio > 0:
            add_rounded_rect(slide, bar_x, ry+0.20, bar_total_w*ratio, bar_h,
                             fill=fill_color, radius=bar_radius)

        # 目标线
        if item.get("target") and data.get("variant") == "target":
            t_ratio = min(item["target"] / max_v, 1)
            t_x = bar_x + bar_total_w * t_ratio
            add_rect(slide, t_x-0.01, ry+0.12, 0.02, 0.46, fill=theme["accent"])

        # 数值
        val_text = item.get("value_fmt",
                            f"{item['value']:.0f}{data.get('unit','%')}")
        add_text(slide, val_text,
                 x=11.45, y=ry+0.15, w=1.28, h=0.40,
                 font_size=theme["body_size"], color=theme["text_dark"],
                 bold=True, align="right", font_name=theme["body_font"])

        # 小注
        if item.get("note"):
            add_text(slide, item["note"],
                     x=bar_x, y=ry+0.52, w=bar_total_w, h=0.28,
                     font_size=theme["caption_size"]-1, color=theme["text_muted"],
                     font_name=theme["body_font"])
```

---

## 设计要点

1. **进度条高度** 固定 0.30 英寸（够粗，清晰可见），不随行数缩放
2. **标签宽度** 固定 2.80 英寸，给进度条留足 7.80 英寸空间
3. **颜色自动映射**: ≥80% 绿，≤30% 红，中间默认 `primary`，使进度条直观传达状态
4. **圆角** 0.05 英寸，轨道和填充同半径，视觉一致
5. **目标线** 用 `accent` 色细竖线，明显但不抢主体
6. **最多8行**（单列时），超过时用双列变体

---

## 测试数据示例

```python
data = {
    "title": "投资组合各类资产配置达标率",
    "subtitle": "目标配比达成情况（截至2024年12月）",
    "max_value": 100,
    "unit": "%",
    "variant": "target",
    "items": [
        {"label": "国内权益", "value": 82, "target": 85, "note": "较目标低 3 个百分点"},
        {"label": "境外权益", "value": 45, "target": 40, "note": "较目标高 5 个百分点，需减仓"},
        {"label": "利率债", "value": 78, "target": 75},
        {"label": "信用债", "value": 31, "target": 40, "note": "受信用资质收紧影响", "color": "negative"},
        {"label": "REITs", "value": 60, "target": 60},
        {"label": "海外债券", "value": 25, "target": 30},
    ],
}
```
