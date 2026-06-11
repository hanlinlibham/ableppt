# Layout: `comparison_cards` — 对比卡片（A vs B）

> 幻灯片尺寸: 13.333 × 7.5 英寸 | 边距: 0.6 英寸 | 内容宽: 12.133 英寸

---

## 用途

两家公司对比、方案A vs 方案B、Before/After、两只基金横向比较。

---

## ASCII 线框图

```
┌─────────────────────────────────────────────────────────────┐
│  [标题]                                     y=0.25          │
│  ▬▬ (accent 装饰线)                         y=0.90          │
│                                                              │
│  ┌──────────────────────────┐VS┌──────────────────────────┐ │
│  │  [left_color 顶部色带]   │  │  [right_color 顶部色带]  │ │
│  │                          │  │                          │ │
│  │  [Left Title]            │  │  [Right Title]           │ │
│  │  [Left Subtitle]         │  │  [Right Subtitle]        │ │
│  │ ─────────────────────── │  │ ─────────────────────── │ │
│  │  指标A      3,521点      │  │  指标A      3,089点      │ │
│  │  指标B     +12.3%        │  │  指标B      +8.7%        │ │
│  │  指标C      0.85         │  │  指标C      0.62         │ │
│  │  指标D    2.15%          │  │  指标D      3.40%        │ │
│  │  指标E      AA           │  │  指标E      A            │ │
│  └──────────────────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 精确坐标标注

### 固定元素

| 元素 | x | y | w | h | 字号 | 颜色 | 对齐 |
|------|---|---|---|---|------|------|------|
| 页面标题 | 0.60 | 0.25 | 12.133 | 0.60 | title_size-2 | text_dark | 左 |
| 装饰线 | 0.60 | 0.90 | 2.00 | 0.04 | — | accent | — |

### "VS" 中间分隔

| 元素 | x | y | w | h | 字号 | 颜色 | 对齐 |
|------|---|---|---|---|------|------|------|
| "VS" 文字 | 6.167 | 3.50 | 1.00 | 0.60 | subtitle_size+4 | text_muted | 中 |
| 中央竖线（可选） | 6.617 | 1.10 | 0.01 | 5.80 | — | border | — |

> VS 文字居中于两卡片之间间隙 (x≈6.167，间隙约1.0英寸)

### 卡片尺寸

```
vs_gap = 1.00        # VS 区域宽度
card_w = (12.133 - vs_gap) / 2 = 5.567"
left_x  = 0.60
right_x = 0.60 + 5.567 + 1.00 = 7.167
card_y  = 1.10
card_h  = 5.80  (到 y=6.90)
```

### 左/右卡片内部结构（以左卡片 x=0.60 为例）

| 元素 | x（相对 card_x） | y | w | h | 字号 | 颜色 | 对齐 |
|------|-----------------|---|---|---|------|------|------|
| 卡片背景（圆角矩形） | +0 | 1.10 | 5.567 | 5.80 | — | card_bg | — |
| 顶部色带 | +0 | 1.10 | 5.567 | 0.08 | — | left_color / right_color | — |
| 卡片标题 | +0.20 | 1.28 | 5.167 | 0.55 | subtitle_size+2 | text_dark | 左 |
| 卡片副标题 | +0.20 | 1.88 | 5.167 | 0.40 | body_size | text_muted | 左 |
| 分隔线 | +0.20 | 2.35 | 5.167 | 0.02 | — | border | — |
| 指标区域（起始 y） | +0.20 | 2.50 | 5.167 | — | — | — | — |

**指标行（每行）**:
```
row_start_y = 2.50
row_h = 0.55   # 每行高度
max_rows = floor((6.90 - 2.50) / 0.55) = 8行（最多）
建议 5-7 行
```

| 元素 | x（相对 card_x） | y（相对 row_y） | w | h | 字号 | 颜色 | 对齐 |
|------|-----------------|----------------|---|---|------|------|------|
| 指标名称 | +0.20 | +0 | 2.80 | 0.40 | body_size | text_muted | 左 |
| 指标数值 | +3.00 | +0 | 2.37 | 0.40 | body_size | text_dark | 右 |
| 行间细线 | +0.20 | +0.47 | 5.167 | 0.01 | — | border | — |

**胜出方高亮规则**（当某指标某卡片更优时）:
- 数值颜色改为 `positive`（绿），`bold=True`
- 或在数值前加 ▲ 符号
- 或行背景加极浅的 `positive` 色（透明度 10%）

### 底部注释（可选）

| 元素 | x | y | w | h | 字号 | 颜色 |
|------|---|---|---|---|------|------|
| 来源说明 | 0.60 | 7.10 | 12.133 | 0.30 | caption_size | text_muted |

---

## 颜色约定

| 元素 | 默认值 | 说明 |
|------|--------|------|
| left_color | primary | 左卡片顶部色带 |
| right_color | secondary | 右卡片顶部色带（可自定义） |
| 胜出数值 | positive | 某指标上较优的一方 |
| 劣势数值 | negative | 某指标上较差的一方（可选显示） |
| "VS" 文字 | text_muted | 居中，降调处理 |

---

## 数据接口

```python
data = {
    "title": str,                # 页面标题
    "subtitle": str,             # 可选，如 "截至2024年12月31日"
    "left": {
        "title": str,            # 左卡片主标题（如公司名/方案名）
        "subtitle": str,         # 可选，左卡片副标题
        "color": str,            # 可选，顶部色带颜色（主题变量名，默认 "primary"）
        "items": [
            {
                "label": str,    # 指标名（如 "近一年收益"）
                "value": str,    # 指标值（如 "+12.3%"）
                "better": bool,  # 可选，是否为该指标的优胜方（高亮显示）
            },
            ...
        ],
    },
    "right": {
        # 同上
    },
    "source": str,               # 可选，数据来源
}
```

---

## 实现伪代码

```python
def layout_comparison_cards(slide, data, theme):
    m = theme["margin"]
    sw, sh = 13.333, 7.5
    cw = sw - 2 * m

    set_slide_bg(slide, theme["bg_light"])
    add_text(slide, data["title"],
             x=m, y=0.25, w=cw, h=0.60,
             font_size=theme["title_size"]-2, color=theme["text_dark"],
             bold=True, font_name=theme["header_font"])
    add_rect(slide, m, 0.90, 2.0, 0.04, fill=theme["accent"])

    # "VS"
    add_text(slide, "VS",
             x=6.167, y=3.50, w=1.00, h=0.60,
             font_size=theme["subtitle_size"]+4, color=theme["text_muted"],
             bold=True, align="center", font_name=theme["header_font"])

    vs_gap = 1.00
    card_w = (cw - vs_gap) / 2   # 5.567"
    card_y = 1.10
    card_h = 5.80

    for side, card_x in [("left", m), ("right", m + card_w + vs_gap)]:
        card_data = data[side]
        top_color = theme.get(card_data.get("color", "primary" if side=="left" else "secondary"))

        # 卡片背景
        add_rounded_rect(slide, card_x, card_y, card_w, card_h,
                         fill=theme["card_bg"], border=theme["border"], radius=0.10)
        # 顶部色带
        add_rect(slide, card_x, card_y, card_w, 0.08, fill=top_color)

        # 标题
        add_text(slide, card_data["title"],
                 x=card_x+0.20, y=1.28, w=card_w-0.40, h=0.55,
                 font_size=theme["subtitle_size"]+2, color=theme["text_dark"],
                 bold=True, font_name=theme["header_font"])
        if card_data.get("subtitle"):
            add_text(slide, card_data["subtitle"],
                     x=card_x+0.20, y=1.88, w=card_w-0.40, h=0.40,
                     font_size=theme["body_size"], color=theme["text_muted"],
                     font_name=theme["body_font"])

        # 分隔线
        add_rect(slide, card_x+0.20, 2.35, card_w-0.40, 0.02, fill=theme["border"])

        # 指标行
        row_y = 2.50
        row_h = 0.55
        for item in card_data["items"]:
            val_color = theme["positive"] if item.get("better") else theme["text_dark"]
            add_text(slide, item["label"],
                     x=card_x+0.20, y=row_y, w=3.00, h=0.40,
                     font_size=theme["body_size"], color=theme["text_muted"],
                     font_name=theme["body_font"])
            add_text(slide, item["value"],
                     x=card_x+0.20, y=row_y, w=card_w-0.40, h=0.40,
                     font_size=theme["body_size"], color=val_color,
                     bold=item.get("better", False),
                     align="right", font_name=theme["body_font"])
            add_rect(slide, card_x+0.20, row_y+0.47, card_w-0.40, 0.01, fill=theme["border"])
            row_y += row_h

    if data.get("source"):
        add_text(slide, f"数据来源：{data['source']}",
                 x=m, y=7.10, w=cw, h=0.30,
                 font_size=theme["caption_size"], color=theme["text_muted"],
                 font_name=theme["body_font"])
```

---

## 设计要点

1. **"VS" 居中** 在两卡片之间间隙正中，字号略大，用 `text_muted` 降调，不抢主体
2. **顶部色带** 区分左右卡片身份，通常左用 `primary`，右用 `secondary` 或 `accent`
3. **胜出指标高亮** 用 `positive` 绿色+粗体，对比一目了然
4. **指标行数** 最多 7 行（含卡片标题区后剩余 4.4 英寸 / 0.55 = 8 行，预留间距后7行）
5. **指标名长度** 建议 8 字以内；数值最长 10 个字符（含符号）

---

## 测试数据示例

```python
data = {
    "title": "基金产品横向对比",
    "subtitle": "截至2024年12月31日",
    "left": {
        "title": "示例养老产品稳健型 A",
        "subtitle": "成立日期：2015年3月",
        "items": [
            {"label": "近一年收益", "value": "+12.3%", "better": True},
            {"label": "近三年年化", "value": "+8.7%", "better": True},
            {"label": "最大回撤", "value": "-5.2%", "better": True},
            {"label": "夏普比率", "value": "1.85", "better": True},
            {"label": "管理费率", "value": "0.80%", "better": False},
            {"label": "规模（亿元）", "value": "380"},
            {"label": "评级", "value": "★★★★★"},
        ],
    },
    "right": {
        "title": "同类产品均值",
        "subtitle": "（同类基金平均）",
        "items": [
            {"label": "近一年收益", "value": "+8.9%"},
            {"label": "近三年年化", "value": "+6.2%"},
            {"label": "最大回撤", "value": "-8.1%"},
            {"label": "夏普比率", "value": "1.12"},
            {"label": "管理费率", "value": "0.65%", "better": True},
            {"label": "规模（亿元）", "value": "85"},
            {"label": "评级", "value": "★★★"},
        ],
    },
    "source": "示例数据终端，示例基金管理公司",
}
```
