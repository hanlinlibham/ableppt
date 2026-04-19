# Layout: `agenda` — 议程/目录页

> 幻灯片尺寸: 13.333 × 7.5 英寸 | 边距: 0.6 英寸 | 内容宽: 12.133 英寸

---

## 用途

报告目录、会议议程、章节索引页。当前章节高亮，其余章节降调显示。

---

## ASCII 线框图

### 变体 A：竖向列表（3-6 项）

```
┌─────────────────────────────────────────────────────────────┐
│  [标题：如"报告目录"]                       y=0.25          │
│  ▬▬ (accent 装饰线)                         y=0.90          │
│                                                              │
│  ┌──┐ 01   宏观经济环境分析          p.04 - 15              │
│  │  │      [描述文字，2行，text_muted]                       │
│  └──┘                                                        │
│                                                              │
│  ┌██┐ 02   ▶ 资产配置策略（当前）    p.16 - 27  ←高亮      │
│  │██│      [描述文字，primary色，加粗]                       │
│  └██┘                                                        │
│                                                              │
│  ┌──┐ 03   固定收益市场               p.28 - 39              │
│  └──┘                                                        │
│  ┌──┐ 04   权益资产展望               p.40 - 52              │
│  └──┘                                                        │
│  ┌──┐ 05   风险管理与压力测试         p.53 - 60              │
│  └──┘                                                        │
└─────────────────────────────────────────────────────────────┘
```

### 变体 B：两列布局（5-8 项）

```
┌─────────────────────────────────────────────────────────────┐
│  [标题]                                                      │
│  ▬▬                                                          │
│                                                              │
│  ┌──┐ 01  宏观经济        ┌██┐ 02  ▶资产配置（当前）        │
│  └──┘      p.04-15        └██┘       p.16-27                 │
│                                                              │
│  ┌──┐ 03  固定收益        ┌──┐ 04  权益资产                  │
│  └──┘      p.28-39        └──┘       p.40-52                 │
│                                                              │
│  ┌──┐ 05  风险管理        ┌──┐ 06  附录                      │
│  └──┘      p.53-60        └──┘       p.61-70                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 精确坐标标注

### 变体 A（竖向列表，最多 6 项）

**固定元素**

| 元素 | x | y | w | h | 字号 | 颜色 | 对齐 |
|------|---|---|---|---|------|------|------|
| 页面标题 | 0.60 | 0.25 | 12.133 | 0.60 | title_size-2 | text_dark | 左 |
| 装饰线 | 0.60 | 0.90 | 2.00 | 0.04 | — | accent | — |

**列表项布局计算**

```
list_start_y = 1.20
available_h = 6.00    # 7.5 - 1.20 - 0.30(bottom margin)
item_h = available_h / N  # N=5时 item_h=1.20", N=6时 item_h=1.00"

每项最小高度 = 0.90"（够放2行文字）
建议最多 6 项
```

**单列表项结构（以 N=5, item_h=1.20" 为例）**

| 元素 | x | y（相对本项顶部，`item_y`） | w | h | 字号 | 颜色 | 备注 |
|------|---|---|---|---|------|------|------|
| 编号色块（方形） | 0.60 | item_y+0.15 | 0.40 | 0.40 | — | — | 非激活=secondary，激活=primary |
| 编号文字 | 0.60 | item_y+0.15 | 0.40 | 0.40 | caption_size | text_light / text_dark | 居中 |
| 章节编号文字（"01"） | 1.15 | item_y+0.15 | 0.60 | 0.40 | body_size | text_muted | 左 |
| 章节标题 | 1.80 | item_y+0.15 | 8.50 | 0.45 | subtitle_size | text_dark→primary（激活） | 左，激活时粗体 |
| 页码 | 10.50 | item_y+0.15 | 1.80 | 0.40 | body_size | text_muted | 右 |
| 描述文字 | 1.80 | item_y+0.65 | 9.00 | 0.45 | body_size-1 | text_muted | 左 |
| 分隔细线 | 0.60 | item_y+item_h-0.02 | 12.133 | 0.02 | — | border | — |

**激活项（active_index）额外元素**:
- 色块: `primary`（非激活为 `secondary`）
- 标题: `primary`，bold=True
- 左侧 accent 竖条: x=0.58, y=item_y, w=0.04, h=item_h-0.02, fill=accent
- 行背景: 轻微高亮矩形（x=0.60, y=item_y, w=12.133, h=item_h-0.02, fill=secondary, 透明度低）

### 变体 B（两列布局，4-8 项）

**每列宽计算**

```
col_w = (12.133 - 0.40) / 2 = 5.867"   # 两列各5.867"，中间间距0.40"
col_x[0] = 0.60
col_x[1] = 0.60 + 5.867 + 0.40 = 6.867

row_count = ceil(N / 2)
available_h = 5.80  # 1.20 ~ 7.00
row_h = available_h / row_count
```

**单格结构（以 col_x, row_y 为基准）**

| 元素 | x | y | w | h | 字号 | 颜色 |
|------|---|---|---|---|------|------|
| 格内色块（圆角矩形） | col_x | row_y | 5.867 | row_h-0.20 | — | card_bg / secondary |
| 编号色块 | col_x+0.15 | row_y+0.20 | 0.45 | 0.45 | — | primary / secondary |
| 编号文字 | col_x+0.15 | row_y+0.20 | 0.45 | 0.45 | caption_size | text_light | 居中 |
| 章节标题 | col_x+0.75 | row_y+0.20 | 4.70 | 0.50 | body_size+2 | text_dark / primary | 左 |
| 页码 | col_x+0.75 | row_y+0.75 | 4.70 | 0.35 | caption_size | text_muted | 左 |
| 描述 | col_x+0.75 | row_y+1.10 | 4.70 | 0.40 | caption_size | text_muted | 左，可选 |

---

## 数据接口

```python
data = {
    "title": str,                    # 页面标题，如 "报告目录"
    "active_index": int,             # 当前激活章节（0-indexed），-1 表示无激活
    "variant": "list" | "grid",      # 布局变体
    "items": [
        {
            "number": str,           # 编号，如 "01", "02"（2字符）
            "title": str,            # 章节标题（15字以内）
            "desc": str,             # 可选，描述（25字以内）
            "page_range": str,       # 可选，页码范围，如 "p.04-15"
        },
        ...  # 最多 8 项（list变体最多6项）
    ],
}
```

---

## 实现伪代码

```python
def layout_agenda(slide, data, theme):
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
    active = data.get("active_index", -1)

    if data.get("variant", "list") == "list":
        list_y = 1.20
        item_h = max(0.90, (sh - list_y - 0.30) / N)

        for i, item in enumerate(items):
            iy = list_y + i * item_h
            is_active = (i == active)

            # 激活行高亮背景
            if is_active:
                add_rect(slide, m, iy, cw, item_h-0.02,
                         fill=theme["secondary"], alpha=30)
                # 左侧 accent 竖线
                add_rect(slide, m-0.02, iy, 0.04, item_h-0.02,
                         fill=theme["accent"])

            # 编号色块
            block_color = theme["primary"] if is_active else theme["secondary"]
            add_rect(slide, m, iy+0.15, 0.40, 0.40, fill=block_color)
            add_text(slide, item["number"],
                     x=m, y=iy+0.15, w=0.40, h=0.40,
                     font_size=theme["caption_size"],
                     color=theme["text_light"] if is_active else theme["text_dark"],
                     align="center", bold=True, font_name=theme["body_font"])

            # 章节标题
            title_color = theme["primary"] if is_active else theme["text_dark"]
            add_text(slide, item["title"],
                     x=1.20, y=iy+0.15, w=8.50, h=0.45,
                     font_size=theme["subtitle_size"], color=title_color,
                     bold=is_active, font_name=theme["header_font"])

            # 页码
            if item.get("page_range"):
                add_text(slide, item["page_range"],
                         x=10.50, y=iy+0.15, w=1.80, h=0.40,
                         font_size=theme["body_size"], color=theme["text_muted"],
                         align="right", font_name=theme["body_font"])

            # 描述
            if item.get("desc"):
                add_text(slide, item["desc"],
                         x=1.20, y=iy+0.65, w=9.30, h=0.45,
                         font_size=theme["body_size"]-1, color=theme["text_muted"],
                         font_name=theme["body_font"])

            # 分隔线
            add_rect(slide, m, iy+item_h-0.02, cw, 0.02, fill=theme["border"])
```

---

## 设计要点

1. **激活章节** 用三种视觉手段叠加：左侧 accent 竖线 + 行背景浅色 + 标题 primary 加粗
2. **编号色块** 激活时 `primary`，非激活时 `secondary`（浅色），颜色差异明显
3. **页码** 右对齐，浅色，非核心信息，不抢焦点
4. **分隔线** 很细（0.02"），`border` 色，营造整洁感不显突兀
5. **列表变体** 最多 6 项；超过 6 项改用 `grid` 变体

---

## 测试数据示例

```python
data = {
    "title": "报告目录",
    "active_index": 1,  # 第二章节为当前阅读位置
    "variant": "list",
    "items": [
        {"number": "01", "title": "宏观经济环境分析", "desc": "GDP增长、通胀、货币政策", "page_range": "p.04-15"},
        {"number": "02", "title": "资产配置策略", "desc": "大类资产配置建议与逻辑", "page_range": "p.16-27"},
        {"number": "03", "title": "固定收益市场", "desc": "利率走势与债券策略", "page_range": "p.28-39"},
        {"number": "04", "title": "权益资产展望", "desc": "A股与港股配置机会", "page_range": "p.40-52"},
        {"number": "05", "title": "风险管理与压力测试", "desc": "尾部风险与情景分析", "page_range": "p.53-60"},
    ],
}
```
