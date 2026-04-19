# Layout: `three_columns` — 三栏内容

> 幻灯片尺寸: 13.333 × 7.5 英寸 | 边距: 0.6 英寸 | 内容宽: 12.133 英寸

---

## 用途

三个方案对比、三大优势、三个阶段、三类风险、三维度分析框架。

---

## ASCII 线框图

### 变体 A：标准三栏（图标+标题+正文）

```
┌─────────────────────────────────────────────────────────────┐
│  [标题]                                     y=0.25          │
│  ▬▬ (accent 装饰线)                         y=0.90          │
│                                                              │
│  ┌──────────────┐ │ ┌──────────────┐ │ ┌──────────────┐    │
│  │    [图标]    │ │ │    [图标]    │ │ │    [图标]    │    │
│  │   稳健增值   │ │ │   风险控制   │ │ │   流动管理   │    │
│  │              │ │ │              │ │ │              │    │
│  │  正文内容..  │ │ │  正文内容..  │ │ │  正文内容..  │    │
│  │  正文继续..  │ │ │  正文继续..  │ │ │  正文继续..  │    │
│  └──────────────┘   └──────────────┘   └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 变体 B：三栏卡片（加 card_bg 背景，各栏独立卡片）

```
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │ [顶部色带]     │  │ [顶部色带]     │  │ [顶部色带]     │ │
│  │   [图标]       │  │   [图标]       │  │   [图标]       │ │
│  │   [标题]       │  │   [标题]       │  │   [标题]       │ │
│  │   [要点列表]   │  │   [要点列表]   │  │   [要点列表]   │ │
│  └────────────────┘  └────────────────┘  └────────────────┘ │
```

### 变体 C：三阶段时间线（横向，强调顺序）

```
│  [起点]   →   第一阶段  →  第二阶段  →  第三阶段   [终点]  │
│            ┌────────────┐ ┌────────────┐ ┌────────────┐    │
│            │  图标/编号  │ │  图标/编号  │ │  图标/编号  │    │
│            │   标题      │ │   标题      │ │   标题      │    │
│            │   正文...   │ │   正文...   │ │   正文...   │    │
│            └────────────┘ └────────────┘ └────────────┘    │
```

---

## 精确坐标标注

### 尺寸计算（三等分）

```
col_gap = 0.30                                  # 列间距
col_w = (12.133 - 2 * col_gap) / 3 = 3.844"    # 每列宽（精确）

col_x[0] = 0.60
col_x[1] = 0.60 + 3.844 + 0.30 = 4.744
col_x[2] = 0.60 + 2 * (3.844 + 0.30) = 8.888

col_y = 1.20   # 内容区起始 y
col_h = 5.90   # 内容区高度（到 y=7.10）
```

### 变体 A（标准三栏，无卡片背景）

| 元素（每列，以 col_x[i] 为基准） | x | y | w | h | 字号 | 颜色 | 对齐 |
|-------------------------------|---|---|---|---|------|------|------|
| 图标区（文字/Unicode 图标） | col_x | 1.20 | 3.844 | 0.90 | 36pt | primary | 中 |
| 顶部 accent 横线（图标下方） | col_x | 2.15 | 1.50 | 0.04 | — | accent | — |
| 列标题 | col_x | 2.30 | 3.844 | 0.55 | subtitle_size | text_dark | 中 |
| 列正文 | col_x | 2.95 | 3.844 | 3.80 | body_size | text_dark | 左 |
| 列间竖分隔线 | col_x+3.844+0.15 | 1.20 | 0.01 | 5.90 | — | border | — |

> accent 横线居左对齐于列，宽 1.50"（不满列宽，营造"半线"装饰感）

### 变体 B（卡片三栏）

| 元素（每列） | x | y | w | h | 颜色 | 备注 |
|------------|---|---|---|---|------|------|
| 卡片背景（圆角矩形） | col_x | 1.20 | 3.844 | 5.90 | card_bg | border 边框 |
| 顶部色带 | col_x | 1.20 | 3.844 | 0.08 | 见下方颜色规则 | 每列不同色 |
| 图标 | col_x+0.10 | 1.40 | 3.644 | 0.80 | 36pt | primary / text_light | 居中 |
| 标题 | col_x+0.15 | 2.30 | 3.544 | 0.55 | subtitle_size | text_dark | 居中 |
| 分隔线 | col_x+0.30 | 2.90 | 3.244 | 0.02 | border | — |
| 正文/要点 | col_x+0.20 | 3.10 | 3.444 | 3.70 | body_size | text_dark | 左 |

**三栏顶部色带颜色（建议）**:
- 第1栏: `primary`
- 第2栏: `secondary`
- 第3栏: `accent`
- 或全部使用 `primary`（统一风格）

**要点列表行（每行）**:
```
bullet_y = 3.10 + j * 0.55  (j=0,1,2,3...)
add_text("●", x=col_x+0.20, y=bullet_y, w=0.25, h=0.40, color=accent)
add_text(text, x=col_x+0.50, y=bullet_y, w=3.00, h=0.40, color=text_dark)
```

### 变体 C（三阶段，加箭头）

```
顶部箭头连接线:
  x=0.60, y=2.20, w=12.133, h=0.04, fill=secondary  # 底层横线

各箭头（向右三角形，用文字 "→" 代替）:
  x=col_x[0]+3.844+0.05, y=2.00, w=0.20, h=0.40, color=accent

编号圆圈（替代图标时）:
  x=col_x+1.722, y=1.20, r=0.35  # 水平居中，fill=primary
  text: "01"/"02"/"03", color=text_light, 14pt, bold
```

---

## 固定元素（所有变体通用）

| 元素 | x | y | w | h | 字号 | 颜色 |
|------|---|---|---|---|------|------|
| 页面标题 | 0.60 | 0.25 | 12.133 | 0.60 | title_size-2 | text_dark |
| 装饰线 | 0.60 | 0.90 | 2.00 | 0.04 | — | accent |

---

## 数据接口

```python
data = {
    "title": str,                        # 页面标题
    "subtitle": str,                     # 可选
    "variant": "open" | "card" | "phase",  # 布局变体，默认 "open"
    "columns": [
        {
            "icon": str,                 # Unicode 图标字符（如 "📈" "🛡" "💧"）
                                         # 或自定义文字（如 "01", "A"）
            "title": str,               # 栏标题（8字以内）
            "body": str,                # 正文段落（可含换行 \n）
            "bullets": list[str],       # 可选，要点列表（替代 body）
            "color": str,               # 可选，顶部色带颜色变量名
            "footnote": str,            # 可选，栏底部小注
        },
        ...  # 必须恰好 3 项
    ],
    "show_dividers": bool,              # 是否显示列间竖分隔线，默认 True（open变体）
    "accent_line_per_col": bool,        # 每列图标下是否加 accent 短线，默认 True
}
```

---

## 实现伪代码

```python
def layout_three_columns(slide, data, theme):
    m = theme["margin"]
    sw = 13.333
    cw = sw - 2 * m

    set_slide_bg(slide, theme["bg_light"])
    add_text(slide, data["title"],
             x=m, y=0.25, w=cw, h=0.60,
             font_size=theme["title_size"]-2, color=theme["text_dark"],
             bold=True, font_name=theme["header_font"])
    add_rect(slide, m, 0.90, 2.0, 0.04, fill=theme["accent"])

    col_gap = 0.30
    col_w = (cw - 2 * col_gap) / 3
    col_xs = [m, m + col_w + col_gap, m + 2 * (col_w + col_gap)]
    col_y = 1.20
    col_h = 5.90
    variant = data.get("variant", "open")

    for i, col in enumerate(data["columns"]):
        cx = col_xs[i]

        if variant == "card":
            add_rounded_rect(slide, cx, col_y, col_w, col_h,
                             fill=theme["card_bg"], border=theme["border"], radius=0.10)
            col_colors = ["primary", "secondary", "accent"]
            top_color = theme.get(col.get("color", col_colors[i]), theme["primary"])
            add_rect(slide, cx, col_y, col_w, 0.08, fill=top_color)

        # 图标
        add_text(slide, col["icon"],
                 x=cx, y=col_y+0.20, w=col_w, h=0.80,
                 font_size=36, color=theme["primary"],
                 align="center", font_name=theme["body_font"])

        # 图标下 accent 线
        if data.get("accent_line_per_col", True):
            line_x = cx + (col_w - 1.50) / 2
            add_rect(slide, line_x, col_y+1.05, 1.50, 0.04, fill=theme["accent"])

        # 标题
        add_text(slide, col["title"],
                 x=cx+0.10, y=col_y+1.20, w=col_w-0.20, h=0.55,
                 font_size=theme["subtitle_size"], color=theme["text_dark"],
                 bold=True, align="center", font_name=theme["header_font"])

        # 正文或要点
        body_y = col_y + 1.85
        if col.get("bullets"):
            for j, bullet in enumerate(col["bullets"]):
                add_text(slide, f"● {bullet}",
                         x=cx+0.15, y=body_y+j*0.55, w=col_w-0.30, h=0.50,
                         font_size=theme["body_size"], color=theme["text_dark"],
                         font_name=theme["body_font"])
        else:
            add_text(slide, col.get("body", ""),
                     x=cx+0.15, y=body_y, w=col_w-0.30, h=3.70,
                     font_size=theme["body_size"], color=theme["text_dark"],
                     font_name=theme["body_font"])

        # 列间竖线（open 变体）
        if variant == "open" and i < 2 and data.get("show_dividers", True):
            add_rect(slide, cx+col_w+0.15, col_y, 0.01, col_h, fill=theme["border"])
```

---

## 设计要点

1. **三等分** 精确计算：col_w = (12.133 - 0.60) / 3 = 3.844 英寸
2. **图标** 建议用 Unicode Emoji（如 📈 🛡 💧）或文字数字（"01"）；字号 36pt
3. **accent 短横线** 位于图标与标题之间，宽 1.50"（不满列宽），每列居中对齐
4. **卡片变体** 三栏顶部色带颜色建议不同（视觉区分），或统一用 `primary`
5. **正文** 左对齐（更易读），不居中；标题居中

---

## 测试数据示例

```python
data = {
    "title": "养老投资三大核心策略",
    "variant": "card",
    "columns": [
        {
            "icon": "📈",
            "title": "稳健增值",
            "color": "primary",
            "bullets": [
                "长期年化收益目标 8-10%",
                "权益+债券均衡配置",
                "专注α收益挖掘",
                "低换手率运营",
            ],
        },
        {
            "icon": "🛡",
            "title": "风险控制",
            "color": "secondary",
            "bullets": [
                "最大回撤控制在 8% 以内",
                "多资产类别分散",
                "季度压力测试",
                "动态再平衡机制",
            ],
        },
        {
            "icon": "💧",
            "title": "流动管理",
            "color": "accent",
            "bullets": [
                "保持 15% 以上流动资产",
                "匹配养老金支付节奏",
                "避免集中赎回风险",
                "T+1 快速响应机制",
            ],
        },
    ],
}
```
