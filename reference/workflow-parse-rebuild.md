# Flow C — 解析→编辑→重建

适用于微调已有 PPT：将 PPT 解析为 JSON 中间格式，编辑 JSON，再重建为 PPT。

## 端到端流程

### Step 1: 解析 PPT 为 JSON

```bash
python scripts/parse_ppt.py aim/aim01.pptx /tmp/parsed.json
```

不指定输出文件则输出到 stdout:

```bash
python scripts/parse_ppt.py aim/aim01.pptx > /tmp/parsed.json
```

### Step 2: 编辑 JSON

JSON 中间格式包含每张幻灯片的所有形状信息。

```json
{
  "slides": [
    {
      "slide_index": 0,
      "shapes": [
        {
          "shape_id": 2,
          "shape_type": "TEXT_BOX",
          "text": "原始文本",
          "left": 914400,
          "top": 365125,
          "width": 8229600,
          "height": 457200
        }
      ]
    }
  ]
}
```

### Step 3: 重建 PPT

```bash
python scripts/rebuild_ppt.py /tmp/parsed.json /tmp/rebuilt.pptx
```

## JSON 中间格式结构

| 层级 | 字段 | 说明 |
|------|------|------|
| root | `slides[]` | 幻灯片数组 |
| slide | `slide_index` | 页码（0-based）|
| slide | `shapes[]` | 形状数组 |
| shape | `shape_id` | 形状 ID |
| shape | `shape_type` | 形状类型 |
| shape | `text` | 文本内容 |
| shape | `left/top/width/height` | 位置和尺寸（EMU）|

## 安全修改 vs 危险字段

### 安全修改

- `text`: 修改文本内容
- 表格单元格的文本值
- 形状的可见文本属性

### 危险字段（修改可能导致损坏）

- `shape_id`: 内部引用，修改会破坏关联
- `left/top/width/height`: 可修改但需保持 EMU 单位
- 图表的内嵌数据: 结构复杂，建议用 Flow A 替代

## 典型用例

1. **批量文字修改**: 解析 → 搜索替换文本 → 重建
2. **提取内容**: 解析 → 读取所有文本（不重建）
3. **结构检查**: 解析 → 分析形状布局
