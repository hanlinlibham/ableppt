# Layout: `timeline` — 水平时间线

> 幻灯片尺寸: 13.333 × 7.5 英寸 | 边距: 0.6 英寸 | 内容宽: 12.133 英寸

---

## 用途

投资历程、项目进度、公司发展史、基金成立以来大事记。

---

## ASCII 线框图

```
┌─────────────────────────────────────────────────────────────┐
│ [标题]                                          y=0.25       │
│ ▬▬ (accent 装饰线 2.0")                         y=0.90       │
│                                                              │
│    ●━━━━━━━━━━━━━━━●━━━━━━━━━━━━━━━●━━━━━━━━━━━●           │
│    │               │               │               │         │
│  [date]          [date]          [date]          [date]      │
│  [title]         [title]         [title]         [title]     │
│  [desc]          [desc]          [desc]          [desc]      │
│                                                              │
│ ──────────────────────────────────────────────────          │
└─────────────────────────────────────────────────────────────┘
```

---

## 精确坐标标注

### 固定元素

| 元素 | x | y | w | h | 字号 | 颜色 | 对齐 |
|------|---|---|---|---|------|------|------|
| 页面标题 | 0.60 | 0.25 | 12.133 | 0.60 | title_size-2 | text_dark | 左 |
| 装饰线 | 0.60 | 0.90 | 2.00 | 0.04 | — | accent | — |

### 时间线主轴

| 元素 | x | y | w | h | 颜色 |
|------|---|---|---|---|------|
| 水平连接线 | 0.60 | 3.10 | 12.133 | 0.04 | secondary |

> 连接线 y = 3.10，恰好穿过所有节点圆圈中心。

### 节点计算（以 N 个节点为例）

```
node_gap = 12.133 / N          # 节点间距
node_x[i] = 0.60 + node_gap * i + node_gap / 2   # 节点圆圈中心 x
```

| N | node_gap | 示例节点中心 x（N=4） |
|---|----------|---------------------|
| 3 | 4.044 | 2.622 / 6.666 / 10.711 |
| 4 | 3.033 | 2.117 / 5.150 / 8.183 / 11.217 |
| 5 | 2.427 | 1.813 / 4.240 / 6.667 / 9.093 / 11.520 |
| 6 | 2.022 | 1.611 / 3.633 / 5.656 / 7.678 / 9.700 / 11.722 |

### 单个节点元素（以节点中心 cx 为基准）

| 元素 | x | y | w | h | 字号 | 颜色 | 对齐 |
|------|---|---|---|---|------|------|------|
| 节点圆圈（实心） | cx-0.15 | 2.95 | 0.30 | 0.30 | — | primary | — |
| 节点编号（可选） | cx-0.10 | 2.97 | 0.20 | 0.20 | body_size-1 | text_light | 中 |
| 日期文字 | cx-1.0 | 3.50 | 2.00 | 0.35 | caption_size | accent | 中 |
| 节点标题 | cx-1.2 | 3.90 | 2.40 | 0.45 | body_size | text_dark | 中 |
| 节点描述 | cx-1.2 | 4.40 | 2.40 | 1.50 | caption_size | text_muted | 中 |

> **连接线竖杆**（圆圈到日期间的短竖线，可选）:
> x=cx-0.01, y=3.25, w=0.02, h=0.25, fill=secondary

### 变体：交替上下布局（推荐用于 5-6 个节点，避免文字拥挤）

奇数节点：文字在线**上方**；偶数节点：文字在线**下方**

```
奇数节点（上方）:
  日期: y=1.30, 节点标题: y=1.70, 节点描述: y=2.15
  竖杆: y=2.65, h=0.45（向下连到主轴）

偶数节点（下方）:
  日期: y=3.50, 节点标题: y=3.90, 节点描述: y=4.35
  竖杆: y=3.10, h=0.40（从主轴向下延伸，节点y=2.95不变）
```

---

## 数据接口

```python
data = {
    "title": str,                    # 页面标题
    "items": [                        # 3-6 个时间节点
        {
            "date": str,             # 日期文字（如 "2020年", "Q3 2023"）
            "title": str,            # 节点标题（10字以内）
            "desc": str,             # 描述（30字以内）
            "highlight": bool,       # 可选，True时节点圆圈用 accent 色
        },
        ...
    ],
    "variant": "standard" | "alternating",  # 布局变体，默认 standard
}
```

---

## 实现伪代码

```python
def layout_timeline(slide, data, theme):
    m = theme["margin"]          # 0.6
    sw = 13.333
    cw = sw - 2 * m             # 12.133
    N = len(data["items"])

    set_slide_bg(slide, theme["bg_light"])

    # 固定元素
    add_text(slide, data["title"],
             x=m, y=0.25, w=cw, h=0.60,
             font_size=theme["title_size"]-2, color=theme["text_dark"],
             bold=True, font_name=theme["header_font"])
    add_rect(slide, m, 0.90, 2.0, 0.04, fill=theme["accent"])

    # 水平主轴线
    line_y = 3.10
    add_rect(slide, m, line_y, cw, 0.04, fill=theme["secondary"])

    node_gap = cw / N

    for i, item in enumerate(data["items"]):
        cx = m + node_gap * i + node_gap / 2

        # 节点圆圈
        circle_color = theme["accent"] if item.get("highlight") else theme["primary"]
        add_circle(slide, cx-0.15, line_y-0.15, 0.30, 0.30, fill=circle_color)

        # 文字（标准布局：全部在轴下方）
        add_text(slide, item["date"],
                 x=cx-1.0, y=3.50, w=2.0, h=0.35,
                 font_size=theme["caption_size"], color=theme["accent"],
                 align="center", font_name=theme["body_font"])
        add_text(slide, item["title"],
                 x=cx-1.2, y=3.90, w=2.4, h=0.45,
                 font_size=theme["body_size"], color=theme["text_dark"],
                 bold=True, align="center", font_name=theme["header_font"])
        add_text(slide, item["desc"],
                 x=cx-1.2, y=4.40, w=2.4, h=1.50,
                 font_size=theme["caption_size"], color=theme["text_muted"],
                 align="center", font_name=theme["body_font"])
```

---

## 设计要点

1. **节点圆圈直径** 固定 0.30 英寸，不随 N 缩放，保证可见性
2. **节点文字宽度** 设为 `node_gap * 0.80`（当 N=6 时约 1.62 英寸），避免相邻节点文字重叠
3. **最多 6 个节点**；超过 6 个时建议改用表格布局
4. **高亮节点**（如"当前阶段"）用 `accent` 色，其余用 `primary`
5. **连接线**用 `secondary`（浅色），节点圆圈用 `primary`（深色），形成层次对比

---

## 测试数据示例

```python
data = {
    "title": "基金成立以来重要里程碑",
    "items": [
        {"date": "2015年", "title": "基金成立", "desc": "初始规模 50 亿元，首批认购完成"},
        {"date": "2017年", "title": "规模突破百亿", "desc": "资产规模达 120 亿，纳入养老金第二支柱"},
        {"date": "2019年", "title": "国际化布局", "desc": "QDII 额度批准，开始配置境外资产"},
        {"date": "2022年", "title": "ESG 认证", "desc": "获得 UN PRI 签署认证，ESG 比例达 40%"},
        {"date": "2024年Q4", "title": "当前状态", "desc": "规模 380 亿，年化收益 8.7%",
         "highlight": True},
    ],
}
```
