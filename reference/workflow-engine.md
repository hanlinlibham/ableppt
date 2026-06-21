# Flow B — Job JSON 声明式编排

使用 PptEngine 引擎，通过一个 Job JSON 文件声明全部数据源、变换、幻灯片渲染逻辑。

## 端到端流程

> 当前主入口已经切到包 CLI：`ableppt validate-job` / `ableppt render`。`scripts/run_job.py` 和 `scripts/render_ppt.py` 仍然是兼容包装。

### Step 1: 编写 job.json

参考 [job-schema.md](job-schema.md) 了解完整结构。

最小示例:

```json
{
  "template": {"path": "aim/aim00.pptx"},
  "datasources": {},
  "slides": [
    {
      "id": "cover",
      "texts": [{"target": "标题", "value": "年度报告"}]
    }
  ],
  "output": {"path": "/tmp/output.pptx"}
}
```

### Step 2: 验证（可选）

```bash
ableppt validate-job job.json --dry-run
```

输出: `{"status": "ok", "message": "schema 验证通过", "slides": 1, "datasources": []}`

### Step 3: 渲染

```bash
ableppt render job.json
```

输出: `{"status": "ok", "output": "/tmp/output.pptx"}`

引擎日志输出到 stderr。

## Flow A vs Flow B 选择矩阵

| 维度 | Flow A (generate_ppt) | Flow B (run_job) |
|------|----------------------|------------------|
| 配置格式 | config.json + CSV | job.json（含数据源声明）|
| 数据来源 | 本地 CSV | CSV/Excel/Tushare |
| 数据变换 | 手动预处理 | 声明式 ops |
| 图表创建 | 通过占位符替换 | 通过 ChartSpec |
| 文本替换 | 通过 text_data | 通过 SlideSpec.texts |
| 适用场景 | 模板已有占位符 | 从零编排 |

## 完整 job.json 示例

```json
{
  "template": {"path": "aim/aim00.pptx"},
  "datasources": {
    "ytd": {
      "type": "csv",
      "path": "/tmp/ytd_chart.csv"
    }
  },
  "transforms": {
    "ytd_sorted": {
      "from": "ytd",
      "ops": [
        {"type": "sort", "sort_by": ["日期"]}
      ]
    }
  },
  "slides": [
    {
      "id": "cover",
      "texts": [
        {"target": "标题", "value": "2024年度报告"},
        {"target": "日期", "value": "2024-12-31"}
      ]
    },
    {
      "id": "chart_page",
      "charts": [
        {
          "mode": "update",
          "target": "当年收益率走势图",
          "source": "ytd_sorted",
          "categories": "日期",
          "series": [
            {"key": "沪深300指数", "name": "沪深300", "axis": "secondary"},
            {"key": "组合收益率", "name": "收益率", "axis": "primary"}
          ]
        }
      ]
    }
  ],
  "output": {
    "path": "/tmp/report.pptx",
    "overwrite": true,
    "add_metadata": true
  }
}
```

## 已知限制

1. **图表渲染分支不完整**: engine.py 中的图表渲染仅传递基础参数（slide, data, shape_name），不传递 series_config/style_config/layout_config。复杂图表（双轴、自定义样式）建议用 Flow A。
2. **瀑布图现已支持 composer 布局**: 可直接使用 `layout: "waterfall"`，也可以继续用 `ableppt render-waterfall ...` 走单页 chart-engine 路径。
3. 图表渲染异常会被 catch 为 warning，不会导致整个任务失败。
4. `validate-job --dry-run` 仅验证 JSON schema，不检查数据源是否可访问。
