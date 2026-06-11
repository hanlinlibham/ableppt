# Layout: `chart_table` — 上图表+下表格

> 幻灯片尺寸: 13.333 × 7.5 英寸 | 边距: 0.6 英寸 | 内容宽: 12.133 英寸

---

## 用途

图表和明细数据一页展示：走势图 + 数据明细、收益图 + 各期收益表、指数图 + 成分股数据。

---

## ASCII 线框图

```
┌─────────────────────────────────────────────────────────────┐
│  [标题]                                     y=0.25          │
│  ▬▬ (accent 装饰线)                         y=0.90          │
│                                                              │
│  ╔══════════════════════════════════════════════════════╗   │
│  ║                                                      ║   │
│  ║              [ 图 表 区 ]                            ║   │
│  ║                                                      ║   │
│  ╚══════════════════════════════════════════════════════╝   │
│                                                              │
│  ┌────────┬─────────┬─────────┬─────────┬─────────────┐    │
│  │ 指标名  │  数值A  │  数值B  │  数值C  │   数值D     │    │ ← 表头行（accent背景）
│  ├────────┼─────────┼─────────┼─────────┼─────────────┤    │
│  │ 行1    │  xx.x%  │  xx.x%  │  xx.x%  │   xx.x%     │    │
│  │ 行2    │  xx.x%  │  xx.x%  │  xx.x%  │   xx.x%     │    │
│  │ 行3    │  xx.x%  │  xx.x%  │  xx.x%  │   xx.x%     │    │
│  └────────┴─────────┴─────────┴─────────┴─────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 分区比例与布局参数

### 高度分配

```
chart_table_ratio: 55/45（默认）、60/40、70/30

chart_start_y = 1.20
chart_end_y   = 1.20 + 7.5 * ratio_chart = 5.325（默认55%）
table_start_y = chart_end_y + 0.15（间距）
table_end_y   = 7.10

实际各值：
  ratio 55/45: chart_h=3.525", table_area_h=1.60"
  ratio 60/40: chart_h=3.900", table_area_h=1.225"
  ratio 70/30: chart_h=4.550", table_area_h=0.575"（仅一行表头+1-2数据行）
```

> **建议比例**: 55/45（图表适中，表格可放3-5行数据）

---

## 精确坐标标注

### 固定元素

| 元素 | x | y | w | h | 字号 | 颜色 | 对齐 |
|------|---|---|---|---|------|------|------|
| 页面标题 | 0.60 | 0.25 | 12.133 | 0.60 | title_size-2 | text_dark | 左 |
| 装饰线 | 0.60 | 0.90 | 2.00 | 0.04 | — | accent | — |

### 图表区

| 参数 | 值（55/45 比例） |
|------|----------------|
| chart_x | 0.60 |
| chart_y | 1.20 |
| chart_w | 12.133 |
| chart_h | 3.525 |

### 表格区（55/45 比例，表格起始 y=4.875）

**表头行**:

| 元素 | x | y | w | h | 字号 | 颜色 | 对齐 |
|------|---|---|---|---|------|------|------|
| 表头背景 | 0.60 | 4.875 | 12.133 | 0.38 | — | primary | — |
| 表头文字（每列） | col_x | 4.875 | col_w | 0.38 | body_size-1 | text_light | 中 |

**数据行（斑马条纹）**:

```
row_h = 0.38
最多行数 = floor((7.10 - 4.875 - 0.38) / 0.38) = floor(1.845 / 0.38) ≈ 4行

偶数行背景: secondary（极淡），奇数行: card_bg（白）
```

| 元素 | x | y（相对 row_y） | w | h | 字号 | 颜色 | 对齐 |
|------|---|----------------|---|---|------|------|------|
| 行背景（偶数行） | 0.60 | +0 | 12.133 | 0.38 | — | secondary（30%透明）| — |
| 第1列（标签） | 0.60 | +0.03 | col_widths[0] | 0.32 | body_size-1 | text_dark | 左 |
| 数据列（对齐右） | col_x[j] | +0.03 | col_widths[j] | 0.32 | body_size-1 | text_dark | 右 |
| 行间细线 | 0.60 | +0.36 | 12.133 | 0.02 | — | border | — |

### 列宽分配（自动计算）

```python
def calc_col_widths(headers, table_w=12.133):
    """
    第1列（标签列）分配 25%，其余等分剩余空间
    或根据 headers 自定义
    """
    n_cols = len(headers)
    label_w = table_w * 0.25   # 3.033"
    data_w = (table_w - label_w) / (n_cols - 1)
    return [label_w] + [data_w] * (n_cols - 1)

# 示例（5列）:
#   label_w = 3.033"，每数据列 = (12.133-3.033)/4 = 2.275"
```

**正负值着色规则**（表格数据）:
- 含 "+" 或正数: `positive` 绿色
- 含 "-" 或负数: `negative` 红色
- 中性/非数字: `text_dark`

---

## 数据接口

```python
data = {
    "title": str,                          # 页面标题
    "subtitle": str,                       # 可选
    # 图表参数（与 layout_chart_full 相同）
    "df": pd.DataFrame,                    # 图表数据
    "categories_col": str,                 # 分类列名（X轴）
    "series_config": list,                 # 系列配置
    "style_config": StyleConfig | None,    # 图表样式
    "layout_config": ChartLayoutConfig | None,
    # 表格参数
    "headers": list[str],                  # 列头（含第一列标签名）
    "rows": list[list[str]],              # 数据行，每行一个列表
    "col_widths": list[float] | None,     # 可选，自定义各列宽（英寸），默认自动分配
    "chart_ratio": float,                  # 可选，图表占高比（0.5-0.75），默认 0.55
    "header_color": str,                   # 可选，表头背景色变量名，默认 "primary"
    "zebra": bool,                         # 是否斑马条纹，默认 True
    "highlight_last_row": bool,            # 是否高亮最后一行（汇总行），默认 False
    "source": str,                         # 可选，数据来源
}
```

---

## 实现伪代码

```python
def layout_chart_table(slide, data, theme):
    from pptfi.chart_builder.api import create_combo_chart
    m = theme["margin"]
    sw, sh = 13.333, 7.5
    cw = sw - 2 * m

    set_slide_bg(slide, theme["bg_light"])
    add_text(slide, data["title"],
             x=m, y=0.25, w=cw, h=0.60,
             font_size=theme["title_size"]-2, color=theme["text_dark"],
             bold=True, font_name=theme["header_font"])
    add_rect(slide, m, 0.90, 2.0, 0.04, fill=theme["accent"])

    ratio = data.get("chart_ratio", 0.55)
    chart_y = 1.20
    chart_h = (sh - chart_y - 0.40) * ratio  # 可用高度的 ratio 给图表
    table_y = chart_y + chart_h + 0.15

    # 图表
    from pptx.util import Inches
    create_combo_chart(
        slide=slide,
        df=data["df"],
        categories_col=data["categories_col"],
        series_config=data["series_config"],
        position=(Inches(m), Inches(chart_y)),
        size=(Inches(cw), Inches(chart_h)),
        style_config=data.get("style_config"),
        layout_config=data.get("layout_config"),
    )

    # 表格
    headers = data["headers"]
    rows = data["rows"]
    n_cols = len(headers)

    col_widths = data.get("col_widths")
    if col_widths is None:
        label_w = cw * 0.25
        data_w = (cw - label_w) / (n_cols - 1)
        col_widths = [label_w] + [data_w] * (n_cols - 1)

    col_xs = [m]
    for w in col_widths[:-1]:
        col_xs.append(col_xs[-1] + w)

    row_h = 0.38
    header_color = theme.get(data.get("header_color", "primary"), theme["primary"])

    # 表头
    add_rect(slide, m, table_y, cw, row_h, fill=header_color)
    for j, (header, cx, cw_j) in enumerate(zip(headers, col_xs, col_widths)):
        align = "left" if j == 0 else "right"
        px = cx + (0.10 if j == 0 else 0)
        add_text(slide, header,
                 x=px, y=table_y+0.04, w=cw_j-0.10, h=row_h-0.08,
                 font_size=theme["body_size"]-1, color=theme["text_light"],
                 bold=True, align=align, font_name=theme["body_font"])

    # 数据行
    for k, row in enumerate(rows):
        ry = table_y + row_h + k * row_h
        if ry + row_h > sh - 0.30:
            break  # 超出页面则停止

        # 斑马背景
        if data.get("zebra", True) and k % 2 == 1:
            add_rect(slide, m, ry, cw, row_h, fill=theme["secondary"], alpha=20)

        # 汇总行高亮
        is_last = (k == len(rows) - 1)
        if is_last and data.get("highlight_last_row", False):
            add_rect(slide, m, ry, cw, row_h, fill=theme["secondary"], alpha=40)

        for j, (cell, cx, cw_j) in enumerate(zip(row, col_xs, col_widths)):
            align = "left" if j == 0 else "right"
            # 正负着色
            cell_str = str(cell)
            if j > 0:
                try:
                    val = float(cell_str.replace("%", "").replace("+", "").replace(",", ""))
                    c = theme["positive"] if val > 0 else (theme["negative"] if val < 0 else theme["text_dark"])
                except ValueError:
                    c = theme["text_dark"]
            else:
                c = theme["text_dark"]
            bold = is_last and data.get("highlight_last_row", False)
            px = cx + (0.10 if j == 0 else 0)
            add_text(slide, cell_str,
                     x=px, y=ry+0.04, w=cw_j-0.10, h=row_h-0.08,
                     font_size=theme["body_size"]-1, color=c,
                     bold=bold, align=align, font_name=theme["body_font"])

        # 行间线
        add_rect(slide, m, ry+row_h-0.01, cw, 0.01, fill=theme["border"])

    if data.get("source"):
        add_text(slide, f"数据来源：{data['source']}",
                 x=m, y=7.10, w=cw, h=0.30,
                 font_size=theme["caption_size"], color=theme["text_muted"],
                 font_name=theme["body_font"])
```

---

## 设计要点

1. **55/45 比例** 是最常用配置：图表够大，表格放得下 3-4 行有效数据
2. **表头用 `primary` 背景 + `text_light` 白字**，与数据行形成强烈对比
3. **斑马条纹** 轻微区分奇偶行（透明度 20% 的 secondary），不喧宾夺主
4. **正负值自动着色** 让数字表格直观传达方向
5. **70/30 比例** 适合图表是核心时，表格仅作辅助参考（仅1-2行数据）
6. **表格列宽** 第1列（标签/日期）固定 25%，其余等分

---

## 测试数据示例

```python
import pandas as pd
from pptfi.chart_builder.models import SeriesConfig

df = pd.DataFrame({
    "日期": ["2024-01", "2024-02", "2024-03", "2024-04",
             "2024-05", "2024-06", "2024-07", "2024-08"],
    "组合收益": [1.2, 2.5, -0.8, 3.1, 2.0, 1.5, 0.7, 2.3],
    "基准收益": [0.8, 1.9, -1.2, 2.4, 1.6, 1.1, 0.5, 1.8],
})

data = {
    "title": "2024年月度收益对比",
    "df": df,
    "categories_col": "日期",
    "series_config": [
        SeriesConfig(key="组合收益", name="本组合", type="bar", axis="primary"),
        SeriesConfig(key="基准收益", name="基准", type="line", axis="primary"),
    ],
    "chart_ratio": 0.55,
    "headers": ["时间段", "1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月"],
    "rows": [
        ["本组合(%)", "+1.2", "+2.5", "-0.8", "+3.1", "+2.0", "+1.5", "+0.7", "+2.3"],
        ["基准(%)", "+0.8", "+1.9", "-1.2", "+2.4", "+1.6", "+1.1", "+0.5", "+1.8"],
        ["超额(%)", "+0.4", "+0.6", "+0.4", "+0.7", "+0.4", "+0.4", "+0.2", "+0.5"],
        ["累计超额(%)", "+0.4", "+1.0", "+1.4", "+2.1", "+2.5", "+2.9", "+3.1", "+3.6"],
    ],
    "highlight_last_row": True,
    "source": "示例数据终端，内部测算",
}
```
