# Layout: `image_text` — 图片+文字（左右可切换）

> 幻灯片尺寸: 13.333 × 7.5 英寸 | 边距: 0.6 英寸 | 内容宽: 12.133 英寸

---

## 用途

产品展示、团队介绍、案例分析、公司介绍、基金经理简介。

---

## ASCII 线框图

### 变体 A：左图右文（image_side="left"）

```
┌─────────────────────────────────────────────────────────────┐
│  [标题]                                     y=0.25          │
│  ▬▬ (accent 装饰线)                         y=0.90          │
│                                                              │
│  ┌──────────────────────────┐  ┌──────────────────────────┐ │
│  │                          │  │  [副标题/小标签]          │ │
│  │      [ 图 片 ]           │  │                          │ │
│  │                          │  │  [正文段落...]            │ │
│  │   (fill=bg_dark或图片)   │  │  正文继续...              │ │
│  │                          │  │                          │ │
│  │                          │  │  ● 要点一                 │ │
│  │                          │  │  ● 要点二                 │ │
│  │                          │  │  ● 要点三                 │ │
│  └──────────────────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 变体 B：右图左文（image_side="right"）

镜像翻转，文字在左，图片在右。

### 变体 C：无实际图片（用色块+数据代替图片区）

```
│  ┌──────────────────────────┐  ┌──────────────────────────┐ │
│  │   bg_dark 深色区域        │  │  [文字内容]               │ │
│  │                          │  │                          │ │
│  │      大数字强调           │  │                          │ │
│  │     "380亿"               │  │                          │ │
│  │   [规模标签]              │  │                          │ │
│  │                          │  │                          │ │
│  └──────────────────────────┘  └──────────────────────────┘ │
```

---

## 精确坐标标注

### 固定元素

| 元素 | x | y | w | h | 字号 | 颜色 |
|------|---|---|---|---|------|------|
| 页面标题 | 0.60 | 0.25 | 12.133 | 0.60 | title_size-2 | text_dark |
| 装饰线 | 0.60 | 0.90 | 2.00 | 0.04 | — | accent |

### 左右分栏（50/50 分割）

```
image_side = "left"（默认）

分割线 x = 0.60 + 12.133 * 0.50 + 0.15 = 7.167（以图片区右边界为准）

图片区（左侧）:
  img_x = 0.60
  img_y = 1.10
  img_w = 5.667   # 12.133 * 0.50 - 0.40（间距）
  img_h = 6.00    # 7.5 - 1.10 - 0.40（底部留白）

文字区（右侧）:
  text_x = 7.067  # img_x + img_w + 0.80（间距）
  text_y = 1.10
  text_w = 5.667  # 对称
  text_h = 6.00
```

> **间距**: 图片区与文字区之间固定留 0.80" 间距（分别各 0.40"）

### 图片区内容（当无实际图片文件，用深色背景 + 大文字代替）

| 元素 | x | y | w | h | 字号 | 颜色 | 对齐 |
|------|---|---|---|---|------|------|------|
| 图片背景块 | img_x | img_y | img_w | img_h | — | bg_dark | — |
| 大数字（可选） | img_x | img_y+1.50 | img_w | 1.50 | 72pt | accent | 中 |
| 数字标签（可选） | img_x | img_y+3.10 | img_w | 0.50 | body_size+2 | text_light | 中 |
| 来源标注（可选） | img_x | img_y+3.70 | img_w | 0.40 | caption_size | text_muted | 中 |

### 文字区内部结构

| 元素 | x | y（相对 text_y） | w | h | 字号 | 颜色 | 对齐 |
|------|---|----------------|---|---|------|------|------|
| 小标签/类型 | text_x | +0 | text_w | 0.35 | caption_size | accent | 左 |
| 副标题 | text_x | +0.40 | text_w | 0.65 | subtitle_size | text_dark | 左 |
| accent 短横线 | text_x | +1.10 | 1.50 | 0.04 | — | accent | — |
| 正文段落 | text_x | +1.25 | text_w | 2.20 | body_size | text_dark | 左 |
| 要点列表起始 y | text_x | +3.55 | text_w | — | body_size | text_dark | 左 |
| 底部标注/签名 | text_x | +5.50 | text_w | 0.40 | caption_size | text_muted | 左 |

**要点列表行（每行）**:
```
add_rect(slide, text_x, bullet_y+0.12, 0.08, 0.08, fill=accent)  # 小方块bullet
add_text(slide, bullet_text, x=text_x+0.20, y=bullet_y, w=text_w-0.20, h=0.45,
         font_size=body_size, color=text_dark)
```

---

## 宽度变体（非严格50/50）

| 变体名 | 图片区 | 文字区 | 适用场景 |
|--------|--------|--------|---------|
| 50/50 | 5.667" | 5.667" | 默认，图文均衡 |
| 40/60 | 4.453" | 7.080" | 文字内容多时 |
| 60/40 | 7.080" | 4.453" | 图片内容丰富时 |

---

## 数据接口

```python
data = {
    "title": str,                        # 页面标题
    "image_side": "left" | "right",      # 图片在哪侧，默认 "left"
    "image_path": str | None,            # 图片文件路径，None 则用色块代替
    "image_fill_color": str,             # 当 image_path=None 时，色块颜色变量名，默认 "bg_dark"
    # 图片区（无实际图片时）的内容
    "image_number": str | None,          # 大数字（如 "380亿"），可选
    "image_number_label": str | None,    # 数字标签（如 "资产规模"），可选
    # 文字区内容
    "tag": str | None,                   # 小标签文字（如 "团队介绍"），可选
    "text_title": str,                   # 副标题（如人名或章节小标题）
    "text_body": str,                    # 正文段落
    "bullets": list[str] | None,        # 要点列表，可选
    "footnote": str | None,             # 底部小注，可选
    # 布局
    "split_ratio": float,               # 图片区占内容宽比例，默认 0.50
    "variant": "default" | "dark_image", # 默认变体或深色图片区变体
}
```

---

## 实现伪代码

```python
def layout_image_text(slide, data, theme):
    from pptx.util import Inches
    m = theme["margin"]
    sw, sh = 13.333, 7.5
    cw = sw - 2 * m

    set_slide_bg(slide, theme["bg_light"])
    add_text(slide, data["title"],
             x=m, y=0.25, w=cw, h=0.60,
             font_size=theme["title_size"]-2, color=theme["text_dark"],
             bold=True, font_name=theme["header_font"])
    add_rect(slide, m, 0.90, 2.0, 0.04, fill=theme["accent"])

    ratio = data.get("split_ratio", 0.50)
    inner_gap = 0.40    # 每侧留出的间距
    img_w = cw * ratio - inner_gap
    txt_w = cw * (1 - ratio) - inner_gap
    area_y = 1.10
    area_h = sh - area_y - 0.40

    img_side = data.get("image_side", "left")
    if img_side == "left":
        img_x = m
        txt_x = m + img_w + inner_gap * 2
    else:
        txt_x = m
        img_x = m + txt_w + inner_gap * 2

    # 图片区
    if data.get("image_path"):
        # 插入实际图片
        from pptx.util import Inches
        slide.shapes.add_picture(
            data["image_path"],
            Inches(img_x), Inches(area_y),
            Inches(img_w), Inches(area_h)
        )
    else:
        # 深色色块代替
        img_color = theme.get(
            data.get("image_fill_color", "bg_dark"), theme["bg_dark"])
        add_rect(slide, img_x, area_y, img_w, area_h, fill=img_color)
        if data.get("image_number"):
            add_text(slide, data["image_number"],
                     x=img_x, y=area_y+1.50, w=img_w, h=1.50,
                     font_size=72, color=theme["accent"],
                     bold=True, align="center", font_name=theme["header_font"])
        if data.get("image_number_label"):
            add_text(slide, data["image_number_label"],
                     x=img_x, y=area_y+3.10, w=img_w, h=0.50,
                     font_size=theme["body_size"]+2, color=theme["text_light"],
                     align="center", font_name=theme["body_font"])

    # 文字区
    ty = area_y
    if data.get("tag"):
        add_text(slide, data["tag"],
                 x=txt_x, y=ty, w=txt_w, h=0.35,
                 font_size=theme["caption_size"], color=theme["accent"],
                 font_name=theme["body_font"])
        ty += 0.40
    if data.get("text_title"):
        add_text(slide, data["text_title"],
                 x=txt_x, y=ty, w=txt_w, h=0.65,
                 font_size=theme["subtitle_size"], color=theme["text_dark"],
                 bold=True, font_name=theme["header_font"])
        ty += 0.70
        add_rect(slide, txt_x, ty, 1.50, 0.04, fill=theme["accent"])
        ty += 0.15
    if data.get("text_body"):
        add_text(slide, data["text_body"],
                 x=txt_x, y=ty, w=txt_w, h=2.20,
                 font_size=theme["body_size"], color=theme["text_dark"],
                 font_name=theme["body_font"])
        ty += 2.30
    if data.get("bullets"):
        for bullet in data["bullets"]:
            add_rect(slide, txt_x, ty+0.12, 0.08, 0.08, fill=theme["accent"])
            add_text(slide, bullet,
                     x=txt_x+0.20, y=ty, w=txt_w-0.20, h=0.45,
                     font_size=theme["body_size"], color=theme["text_dark"],
                     font_name=theme["body_font"])
            ty += 0.50
    if data.get("footnote"):
        add_text(slide, data["footnote"],
                 x=txt_x, y=area_y+area_h-0.40, w=txt_w, h=0.40,
                 font_size=theme["caption_size"], color=theme["text_muted"],
                 font_name=theme["body_font"])
```

---

## 设计要点

1. **图片区与文字区** 各占约 50%，左右可切换，保持视觉多样性
2. **无图片时** 用 `bg_dark` 深色色块代替，加大数字，效果与图片一样震撼
3. **文字区左上角小标签**（"团队介绍"/"案例分析"）用 `accent` 色，比副标题小一级
4. **文字区 accent 短横线** 位于副标题与正文之间，宽 1.50"，与页面标准装饰线一致
5. **图片填充方式**: 用 `add_picture` 时建议 `fill` 模式（拉伸填满），保持比例

---

## 测试数据示例

```python
# 示例1：基金经理介绍（无实际图片，用深色块代替）
data = {
    "title": "投资管理团队",
    "image_side": "left",
    "image_path": None,
    "image_fill_color": "bg_dark",
    "image_number": "26年",
    "image_number_label": "平均投资经验",
    "tag": "首席投资官",
    "text_title": "张明远",
    "text_body": "毕业于北京大学经济学院，CFA持证人，具有26年资本市场投资经验。历任多家顶级资产管理机构投资总监。",
    "bullets": [
        "主导管理资产规模超 3,800 亿元",
        "年化超额收益 4.2%（2015-2024）",
        "荣获中国养老金投资十佳基金经理",
    ],
    "footnote": "截至 2024 年 12 月 31 日",
}

# 示例2：实际图片（如产品截图或场景照片）
data = {
    "title": "养老社区实地调研",
    "image_side": "right",
    "image_path": "/path/to/community_photo.jpg",
    "tag": "案例分析",
    "text_title": "北京·夕阳红养老社区",
    "text_body": "项目总建筑面积 12 万平方米，设计床位 1,200 张，配套医疗、康复、餐饮全覆盖。",
    "bullets": [
        "入住率 94%，位居北京市前三",
        "REITs 上市，估值 35 亿元",
        "年化租金回报率 5.8%",
    ],
}
```
