# Layout: `quote` — 引用/金句页

> 幻灯片尺寸: 13.333 × 7.5 英寸 | 边距: 0.6 英寸 | 内容宽: 12.133 英寸

---

## 用途

管理层观点、投资建议语录、风险提示声明、年报核心金句。

---

## ASCII 线框图

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│   ❝                                                         │
│                                                              │
│       在波动的市场中，坚守长期投资原则，                      │
│       比追求短期收益更能实现财富的稳健增长。                  │
│                                                              │
│                                          ❞                  │
│                                                              │
│              ─────────────────                               │
│              王明远  |  首席投资官                            │
│                                                              │
│   [可选：小字来源说明]                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 变体

### 变体 A：深色背景（`bg_dark` 款，强调感强）

```
┌─────────────────────────────────────────────────────────────┐
│  [bg_dark 背景]                                              │
│                                                              │
│   ❝ （accent 色大引号）                                      │
│                                                              │
│       [quote 文字，text_light，居中，大字]                   │
│                                                              │
│                                          ❞                  │
│              ─── accent 色横线 ───                           │
│              [author]  |  [title]  （text_light，较小）     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 变体 B：浅色背景（`bg_light` 款，报告内页用）

```
┌─────────────────────────────────────────────────────────────┐
│  [bg_light 背景]                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  card_bg 卡片（圆角矩形，带 border 边框）             │   │
│  │                                                      │   │
│  │  ❝ （primary 色引号）                                │   │
│  │                                                      │   │
│  │       [quote 文字，text_dark，居中]                  │   │
│  │                                                      │   │
│  │                                    ❞                │   │
│  │       ─── secondary 色横线 ───                       │   │
│  │       [author]  |  [title]                          │   │
│  │                                                      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 精确坐标标注

### 变体 A（深色背景）

| 元素 | x | y | w | h | 字号 | 颜色 | 对齐 | 备注 |
|------|---|---|---|---|------|------|------|------|
| 背景 | 0 | 0 | 13.333 | 7.5 | — | bg_dark | — | 全页背景 |
| 左引号 ❝ | 0.60 | 1.00 | 1.50 | 1.50 | 96pt | accent | 左 | 装饰引号 |
| 右引号 ❞ | 11.40 | 4.20 | 1.30 | 1.20 | 96pt | accent | 右 | 装饰引号 |
| 引文正文 | 1.80 | 2.00 | 9.733 | 2.80 | 28pt | text_light | 中 | 行高 1.5x |
| 分隔线 | 5.167 | 5.00 | 3.00 | 0.04 | — | accent | — | 居中于页面 |
| 作者名 | 1.80 | 5.15 | 9.733 | 0.50 | body_size+2 | text_light | 中 | 粗体 |
| 职衔 | 1.80 | 5.65 | 9.733 | 0.40 | body_size | text_light | 中 | 细体，muted |
| 来源说明 | 0.60 | 6.90 | 12.133 | 0.35 | caption_size | text_muted | 左 | 可选 |

> **引号字号说明**: 96pt 装饰引号实际使用 `❝` `❞` Unicode 字符（U+275D / U+275E），
> 或用中文弯引号 `"` `"` 加大字号模拟。

### 变体 B（浅色卡片）

| 元素 | x | y | w | h | 字号 | 颜色 | 对齐 | 备注 |
|------|---|---|---|---|------|------|------|------|
| 背景 | 0 | 0 | 13.333 | 7.5 | — | bg_light | — | 全页背景 |
| 卡片 | 0.60 | 0.80 | 12.133 | 6.20 | — | card_bg | — | 圆角 0.12", border |
| 左引号 | 0.90 | 1.00 | 1.20 | 1.20 | 72pt | primary | 左 | — |
| 右引号 | 11.20 | 4.40 | 1.10 | 1.10 | 72pt | primary | 右 | — |
| 引文正文 | 1.60 | 2.00 | 10.133 | 2.60 | 24pt | text_dark | 中 | 行高 1.5x |
| 分隔线 | 5.417 | 4.80 | 2.50 | 0.04 | — | secondary | — | — |
| 作者名 | 1.60 | 5.00 | 10.133 | 0.45 | body_size+2 | primary | 中 | 粗体 |
| 职衔 | 1.60 | 5.50 | 10.133 | 0.40 | body_size | text_muted | 中 | — |

---

## 数据接口

```python
data = {
    "quote": str,              # 引文内容（建议 50-120 字，过长则字号自动缩小）
    "author": str,             # 作者姓名
    "title": str,              # 职衔/身份（如 "首席投资官" 或 "投行研报, 2024Q4"）
    "source": str,             # 可选，来源说明（显示在左下角）
    "variant": "dark" | "light",  # 背景变体，默认 "dark"
    "quote_font_size": int,    # 可选，强制引文字号（默认根据文字长度自动）
}
```

---

## 字号自适应规则

```
引文字数 <= 40 字:  quote_font_size = 32pt
引文字数 41-80 字:  quote_font_size = 26pt
引文字数 81-120 字: quote_font_size = 22pt
引文字数 > 120 字:  quote_font_size = 18pt（或换用文字较多的布局）
```

---

## 实现伪代码

```python
def layout_quote(slide, data, theme):
    sw, sh = 13.333, 7.5
    m = theme["margin"]
    cw = sw - 2 * m

    variant = data.get("variant", "dark")
    bg = theme["bg_dark"] if variant == "dark" else theme["bg_light"]
    qt_color = theme["accent"] if variant == "dark" else theme["primary"]
    text_color = theme["text_light"] if variant == "dark" else theme["text_dark"]
    line_color = theme["accent"] if variant == "dark" else theme["secondary"]

    set_slide_bg(slide, bg)

    if variant == "light":
        add_rounded_rect(slide, m, 0.80, cw, 6.20,
                         fill=theme["card_bg"], border=theme["border"],
                         radius=0.12)

    # 自适应字号
    q_len = len(data["quote"])
    if q_len <= 40: qfont = 32
    elif q_len <= 80: qfont = 26
    elif q_len <= 120: qfont = 22
    else: qfont = 18
    qfont = data.get("quote_font_size", qfont)

    # 装饰引号
    add_text(slide, "\u275d",  # ❝
             x=m, y=1.00, w=1.50, h=1.50,
             font_size=96, color=qt_color, bold=True,
             font_name=theme["header_font"])
    add_text(slide, "\u275e",  # ❞
             x=11.40, y=4.20, w=1.30, h=1.20,
             font_size=96, color=qt_color, bold=True,
             font_name=theme["header_font"])

    # 引文
    add_text(slide, data["quote"],
             x=1.80, y=2.00, w=sw-3.60, h=2.80,
             font_size=qfont, color=text_color,
             align="center", font_name=theme["body_font"])

    # 分隔线（居中）
    line_w = 3.00
    add_rect(slide, (sw-line_w)/2, 5.00, line_w, 0.04, fill=line_color)

    # 作者 + 职衔
    add_text(slide, data["author"],
             x=1.80, y=5.15, w=sw-3.60, h=0.50,
             font_size=theme["body_size"]+2, color=text_color,
             bold=True, align="center", font_name=theme["header_font"])
    add_text(slide, data["title"],
             x=1.80, y=5.65, w=sw-3.60, h=0.40,
             font_size=theme["body_size"], color=theme["text_muted"],
             align="center", font_name=theme["body_font"])

    if data.get("source"):
        add_text(slide, f"来源：{data['source']}",
                 x=m, y=6.90, w=cw, h=0.35,
                 font_size=theme["caption_size"], color=theme["text_muted"],
                 font_name=theme["body_font"])
```

---

## 设计要点

1. **装饰引号** 用 Unicode `❝❞` 或 `""` 超大字号（72-96pt），纯作装饰，不参与文字排版
2. **分隔线** 宽 2.5-3.0 英寸，水平居中，比内容区窄，营造"浮雕"感
3. **引文字体** 建议用 `body_font`（更易读），不用 `header_font`（太方正）
4. **深色变体** 适合章节封面、结论页之前的观点陈述页
5. **浅色变体** 适合内容页中间插入的专家观点

---

## 测试数据示例

```python
data = {
    "quote": "长期投资的核心不是预测市场的每一次波动，而是在确定性的复利中耐心等待价值的回归。",
    "author": "李明华",
    "title": "首席投资策略师 | 国投养老基金",
    "source": "2024年度投资策略报告",
    "variant": "dark",
}
```
