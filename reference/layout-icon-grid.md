# Layout: `icon_grid` — 图标网格

> 幻灯片尺寸: 13.333 × 7.5 英寸 | 边距: 0.6 英寸 | 内容宽: 12.133 英寸

---

## 用途

能力矩阵、特征展示、产品功能清单、投资策略要素、风险因素分类。

---

## ASCII 线框图

### 2×3 网格（6格，每行2列）

```
┌─────────────────────────────────────────────────────────────┐
│  [标题]                                     y=0.25          │
│  ▬▬ (accent 装饰线)                         y=0.90          │
│                                                              │
│  ┌──────────────────────────┐  ┌──────────────────────────┐ │
│  │  [图标] [标题]            │  │  [图标] [标题]            │ │
│  │  一行描述文字...          │  │  一行描述文字...          │ │
│  └──────────────────────────┘  └──────────────────────────┘ │
│                                                              │
│  ┌──────────────────────────┐  ┌──────────────────────────┐ │
│  │  [图标] [标题]            │  │  [图标] [标题]            │ │
│  │  一行描述文字...          │  │  一行描述文字...          │ │
│  └──────────────────────────┘  └──────────────────────────┘ │
│                                                              │
│  ┌──────────────────────────┐  ┌──────────────────────────┐ │
│  │  [图标] [标题]            │  │  [图标] [标题]            │ │
│  │  一行描述文字...          │  │  一行描述文字...          │ │
│  └──────────────────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 3×3 网格（9格，每行3列）

```
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ [图] [标题]  │  │ [图] [标题]  │  │ [图] [标题]  │        │
│  │ 描述文字...  │  │ 描述文字...  │  │ 描述文字...  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ... ×3 行                                                   │
```

### 3×2 网格（6格，每行3列，2行——较常用）

与 3×3 相同列数，仅 2 行，格内内容更多。

---

## 网格尺寸计算

### 2列布局（N=4,6）

```
cols = 2
col_gap = 0.30
cell_w = (12.133 - col_gap) / 2 = 5.917"

rows = ceil(N / cols)  # 4→2行, 6→3行
row_gap = 0.20
grid_start_y = 1.15
available_h = 7.5 - 1.15 - 0.30 = 6.05"
cell_h = (available_h - (rows-1)*row_gap) / rows

rows=2: cell_h = (6.05 - 0.20) / 2 = 2.925"
rows=3: cell_h = (6.05 - 0.40) / 3 = 1.883"
```

### 3列布局（N=6,9）

```
cols = 3
col_gap = 0.25
cell_w = (12.133 - 2*col_gap) / 3 = 3.878"

rows = ceil(N / 3)  # 6→2行, 9→3行
row_gap = 0.20
cell_h: rows=2→2.925", rows=3→1.883"（与2列相同）
```

---

## 精确坐标标注

### 固定元素

| 元素 | x | y | w | h | 字号 | 颜色 |
|------|---|---|---|---|------|------|
| 页面标题 | 0.60 | 0.25 | 12.133 | 0.60 | title_size-2 | text_dark |
| 装饰线 | 0.60 | 0.90 | 2.00 | 0.04 | — | accent |

### 单格内部结构（以 3列×2行, cell_w=3.878", cell_h=2.925" 为例）

**格内元素（横向图标+标题排列）**:

| 元素 | x（相对 cell_x） | y（相对 cell_y） | w | h | 字号 | 颜色 | 对齐 |
|------|----------------|----------------|---|---|------|------|------|
| 格背景（圆角矩形） | +0 | +0 | cell_w | cell_h | — | card_bg | — |
| 左侧 accent 竖条 | +0 | +0 | 0.06 | cell_h | — | accent | — |
| 图标 | +0.20 | +0.30 | 0.60 | 0.60 | 28pt | primary | 中 |
| 格标题 | +0.90 | +0.30 | cell_w-1.10 | 0.55 | subtitle_size | text_dark | 左 |
| 描述正文 | +0.20 | +1.00 | cell_w-0.40 | cell_h-1.20 | body_size | text_muted | 左 |

> **格标题 y 对齐图标垂直居中**: 图标高 0.60"，标题高 0.55"，图标从 +0.30 开始，
> 标题从 +0.33 开始，视觉上与图标垂直居中。

**替代排列：图标置顶（更适合 2列×3行 的高格）**:

| 元素 | x（相对 cell_x） | y（相对 cell_y） | w | h | 字号 | 颜色 | 对齐 |
|------|----------------|----------------|---|---|------|------|------|
| 格背景 | +0 | +0 | cell_w | cell_h | — | card_bg | — |
| 顶部 accent 色带 | +0 | +0 | cell_w | 0.06 | — | accent | — |
| 图标（居中大图标） | +0 | +0.15 | cell_w | 0.80 | 40pt | primary | 中 |
| 格标题 | +0.15 | +1.05 | cell_w-0.30 | 0.50 | subtitle_size | text_dark | 中 |
| 描述正文 | +0.20 | +1.65 | cell_w-0.40 | cell_h-1.85 | body_size | text_muted | 中 |

---

## 数据接口

```python
data = {
    "title": str,                      # 页面标题
    "subtitle": str,                   # 可选
    "cols": int,                       # 列数（2 或 3），默认自动根据 N 判断
    "icon_position": "left" | "top",   # 图标位置，默认 "left"
    "items": [
        {
            "icon": str,               # Unicode 图标或文字（如 "📊", "①", "AI"）
            "title": str,              # 格标题（12字以内）
            "desc": str,               # 描述（40字以内，超出自动换行）
            "color": str,              # 可选，左侧竖条/顶部色带的颜色变量名
        },
        ...  # 4-9 个
    ],
}
```

---

## 列数自动判断规则

```
N <= 4: cols=2
N == 5: cols=3（5格：2×3网格中5格填满，最后一格空白或用"敬请期待"）
N == 6: cols=2（2×3，格高1.88"，推荐）或 cols=3（3×2，格高2.93"，推荐）
N == 7,8: cols=4（推荐改用4列）
N == 9: cols=3（3×3）
```

> **推荐最多 9 格**；超过 9 格时内容过于拥挤，建议拆成多页。

---

## 实现伪代码

```python
def layout_icon_grid(slide, data, theme):
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
    cols = data.get("cols", 2 if N <= 4 else 3)
    rows = (N + cols - 1) // cols
    icon_pos = data.get("icon_position", "left")

    col_gap = 0.30 if cols == 2 else 0.25
    row_gap = 0.20
    cell_w = (cw - (cols-1) * col_gap) / cols
    grid_y = 1.15
    available_h = sh - grid_y - 0.30
    cell_h = (available_h - (rows-1) * row_gap) / rows

    for idx, item in enumerate(items):
        row_i = idx // cols
        col_i = idx % cols
        cx = m + col_i * (cell_w + col_gap)
        cy = grid_y + row_i * (cell_h + row_gap)

        item_color = theme.get(item.get("color", "accent"), theme["accent"])

        # 格背景
        add_rounded_rect(slide, cx, cy, cell_w, cell_h,
                         fill=theme["card_bg"], border=theme["border"], radius=0.08)

        if icon_pos == "left":
            # 左侧 accent 竖条
            add_rect(slide, cx, cy, 0.06, cell_h, fill=item_color)
            # 图标
            add_text(slide, item["icon"],
                     x=cx+0.15, y=cy+0.25, w=0.65, h=0.65,
                     font_size=28, color=theme["primary"],
                     align="center", font_name=theme["body_font"])
            # 标题
            add_text(slide, item["title"],
                     x=cx+0.90, y=cy+0.28, w=cell_w-1.10, h=0.55,
                     font_size=theme["subtitle_size"], color=theme["text_dark"],
                     bold=True, font_name=theme["header_font"])
            # 描述
            add_text(slide, item["desc"],
                     x=cx+0.20, y=cy+0.95, w=cell_w-0.40, h=cell_h-1.15,
                     font_size=theme["body_size"], color=theme["text_muted"],
                     font_name=theme["body_font"])
        else:  # top
            add_rect(slide, cx, cy, cell_w, 0.06, fill=item_color)
            add_text(slide, item["icon"],
                     x=cx, y=cy+0.10, w=cell_w, h=0.80,
                     font_size=40, color=theme["primary"],
                     align="center", font_name=theme["body_font"])
            add_text(slide, item["title"],
                     x=cx+0.15, y=cy+0.95, w=cell_w-0.30, h=0.50,
                     font_size=theme["subtitle_size"], color=theme["text_dark"],
                     bold=True, align="center", font_name=theme["header_font"])
            add_text(slide, item["desc"],
                     x=cx+0.20, y=cy+1.55, w=cell_w-0.40, h=cell_h-1.75,
                     font_size=theme["body_size"], color=theme["text_muted"],
                     align="center", font_name=theme["body_font"])
```

---

## 设计要点

1. **左侧竖条** 0.06 英寸宽，等于格高，颜色可每格不同（对应不同类别）
2. **图标** 建议 Emoji 或 Unicode 符号，字号 28-40pt，颜色用 `primary`
3. **描述** 左对齐（icon_pos=left）/ 居中（icon_pos=top），字号 body_size
4. **列间距** 3列时用 0.25"（更紧凑），2列时用 0.30"
5. **空格处理**（N=5 时 3×2 网格有一空格）：最后空格留白或填"敬请期待"占位

---

## 测试数据示例

```python
data = {
    "title": "养老金投资管理核心能力",
    "cols": 3,
    "icon_position": "left",
    "items": [
        {"icon": "📊", "title": "量化风险管理", "desc": "基于 VaR/CVaR 的实时风险监控，覆盖市场、信用、流动性三类风险"},
        {"icon": "🌐", "title": "全球资产配置", "desc": "覆盖 30+ 个市场，QDII 额度 120 亿元，海外资产占比 20%"},
        {"icon": "🤖", "title": "AI 辅助决策", "desc": "机器学习因子模型，月度再平衡信号生成，提升组合效率"},
        {"icon": "📋", "title": "ESG 整合", "desc": "UN PRI 签署机构，ESG 评分纳入选股模型，覆盖全部持仓"},
        {"icon": "⚖️", "title": "合规风控", "desc": "独立风控部门，三重审批机制，满足银保监会全部监管要求"},
        {"icon": "💬", "title": "投资者服务", "desc": "7×24 小时客服，季度投资报告，专属客户经理 1 对 1 服务"},
    ],
}
```
