# 整本规划 · 页型路由 playbook（导演层）

> 给"规划整本 deck"的 agent 读的提示。可移植：Claude Code 和 ablemind 的
> ppt-specialist agent 同源消费。**核心病根：ableppt 是 chart-first 引擎，不加
> 约束就会把每页都做成图表。这份文件就是治"满本是图"的纪律。**
>
> 它本身有 ~36 个 layout（远不止图表），缺的不是渲染能力，是**先派页型再渲染**
> 的判断。先做这一步，再去 `ableppt render`。

## 一条总规则（每页都先问）

> **这页的论点，有没有"支撑数据 + 需要看趋势/对比/分布/构成"？**
> - **没有** → 用**文字/逻辑/表格**版式，别上图。
> - **有，但一句话/一个数能说清** → KPI 卡 / 一行强调，别上图。
> - **有，且图能让论点更有力**（趋势、对比、分布、桥接、占比）→ 才升级成图表。

默认是文字，**图表是"被论点挣来的"，不是默认**。

## 三条硬规则（借鉴成熟实践，治"满本是图"＋"标题只是主题词"）

1. **Action Title（行动式标题）**：每页内容页标题是**一句完整结论句**，不是主题词。
   "营收三年翻倍但毛利率承压" ✅ ／ "营收情况" ❌。〔借鉴 academic-pptx-skill〕
2. **Ghost Deck Test（幽灵稿测试）**：把所有页的 action title **顺序读下来，必须讲得出完整论证**。读不通 → 先改 outline，别急着渲染。**这是治"满本是图/大杂烩"的根本自检。**〔借鉴 academic-pptx-skill〕
3. **每个 exhibit 配 "So what" 标注**：每张图/表必须有**一句结论标注**直接点出要点——映射到 ableppt 的 `insight` / `subtitle` 槽位，**chart 页必填**。〔借鉴 academic-pptx-skill〕

> 优先级顺序，别本末倒置：**论证结构 → 数据 → 版式 → 美化**。
> 内容纪律：选**这个时长内能讲服的那一个论点**，其余进附录。〔借鉴 academic-pptx-skill「Structured Argument Mode」〕

## 页型 taxonomy（意图 → 页型 → ableppt layout）

| 论点意图 | 页型 | 推荐 layout | 何时用 / 反面 |
|---|---|---|---|
| 开场 / 收尾品牌页 | cover | `title_dark` / `title_light` | 第 1 页、致谢页 |
| 分章过渡 | section | `section_divider` / `chapter_divider_16_9` | 每个大节前 1 页 |
| 目录 / 议程 | agenda | `gtm_toc` / `bullet_points` | 长 deck 第 2 页 |
| 执行摘要 / 关键数 | summary + KPI | `summary_shell_16_9` / `kpi_cards` | 摘要页；3–5 个核心数字 |
| **逻辑论证 / 观点**（最容易被误图表化） | argument | `bullet_points` / `pyramid` / `process_flow` | 讲"为什么/怎么做/三点理由"——**没数据就别上图** |
| 并列对比 | comparison | `comparison_table` / `comparison` / `matrix` | 方案 A vs B、维度打分 |
| 流程 / 时间线 | flow | `process_flow` / `timeline` | 步骤、里程碑 |
| 图文混排 | image+text | `image_text` / `chart_text` | 一张图 + 一段解读 |
| **复杂数据图** | chart | `chart_full` / `two_charts` / `waterfall` / `scatter` / `bubble` / `range_snapshot` | **趋势/对比/分布/桥接/区间**——ableppt 的主场 |
| 仪表盘 / 多图 | dashboard | `dashboard_shell_16_9` / `two_charts` / `composite` | 一页多指标总览 |
| 结论 / 行动项 | conclusion | `conclusion_dark` | 末页 |

> 完整 layout 名以 `ableppt`（render 时 `未知布局` 报错会列全部）或 composer 源为准。

## 图表预算（硬约束，治满本是图）

- **chart 页 ≤ 全本 40%**（投研类可放宽到 ~50%，但不该过半还全是图）。
- **连续 chart 页 ≤ 2**：第 3 页强制换文字/表格/section 喘口气。
- **一个论点一张图**：别为了"显得专业"给同一观点堆 3 张图。
- **逻辑页默认文字**：理由/框架/流程优先 `bullet_points` / `pyramid` / `process_flow`。
- **能用表就别硬画图**：精确数值对比用 `comparison_table`，不用柱状图。

## 规划配方（plan → 派型 → 预算 → 自检）

1. **outline**：把 brief 拆成"叙事弧"——开场 → 背景/问题 → 论证若干节 → 数据证据 → 结论。
2. **逐页派型**：每页套"总规则"判定页型，落到上表的 layout。
3. **过预算**：数 chart 页占比、查连续图、查"逻辑页是否被误判成图表页"。超了就降级。
4. **再渲染**：把 typed outline 翻成 Job JSON 的 `pages[]`（chart 页才带 `series_config`/`layout_config`），`ableppt render`。
5. **自检**（见下）→ 不过就改版重排。

## `plan_deck` 机器契约：typed outline schema

规划阶段**先产出这个结构化 outline**（而不是直接生 Job JSON），便于校验纪律、跑预算、再确定性地展开成 `pages[]`。弱 agent 照着填槽即可。

```jsonc
// JSON Schema (draft 2020-12，精简)
{
  "title": "DeckOutline",
  "type": "object",
  "required": ["meta", "pages"],
  "properties": {
    "meta": {
      "type": "object",
      "required": ["title", "aspect_ratio"],
      "properties": {
        "title":           { "type": "string" },
        "audience":        { "type": "string" },
        "aspect_ratio":    { "enum": ["16:9", "4:3"] },
        "theme":           { "type": "string" },          // ableppt 主题；写错自动回退默认
        "max_chart_ratio": { "type": "number", "default": 0.4 }
      }
    },
    "pages": { "type": "array", "minItems": 1, "items": { "$ref": "#/$defs/page" } }
  },
  "$defs": {
    "page": {
      "type": "object",
      "required": ["n", "type", "layout", "action_title", "has_data"],
      "properties": {
        "n":            { "type": "integer", "minimum": 1 },
        "type":         { "enum": ["cover","agenda","section","summary","argument",
                                   "comparison","flow","image_text","chart","dashboard","conclusion"] },
        "layout":       { "type": "string" },             // 须 ∈ 该 type 允许集（见下表）
        "action_title": { "type": "string" },             // 完整结论句，非主题词；cover/section 可为标签
        "has_data":     { "type": "boolean" },            // 本页论点是否依赖数据
        "so_what":      { "type": "string" },             // 图/表结论标注 → ableppt insight/subtitle
        "data_ref":     { "type": ["string","null"] },    // datasource 句柄名
        "body":         { "type": ["array","object","null"] }, // 逻辑页内容：bullets/表行/流程节点
        "notes":        { "type": "string" }              // 备注/演讲提示
      },
      "allOf": [
        { "if":   { "properties": { "type": { "enum": ["chart","dashboard"] } } },
          "then": { "required": ["so_what","data_ref"],
                    "properties": { "data_ref": { "type": "string" } } } }
      ]
    }
  }
}
```

**Schema 管不了的跨字段/全局规则（compose 前必须过）：**

- **R1 layout∈type**：`page.layout` 必须在该 `type` 的允许集内（下表）。
- **R2 逻辑页≠图表**：`type ∈ {argument, comparison, flow, agenda}` ⇒ `layout` **不得**是图表版式（治"满本是图"）。
- **R3 图表需数据+sowhat**：`type ∈ {chart, dashboard}` ⇒ `data_ref` 与 `so_what` 必填（schema 已 enforce）。
- **R4 预算**：`count(chart|dashboard) / len(pages) ≤ meta.max_chart_ratio`；**连续 chart/dashboard ≤ 2**。
- **R5 Ghost Deck**：`pages[].action_title` 顺读成完整论证（LLM 判，非 schema）。〔借鉴 academic-pptx-skill〕
- **R6 收尾**：末页 `type=conclusion`；>15 页含 ≥1 个 `section`。

**type → 允许 layout 集：**

| type | 允许 layout |
|---|---|
| cover | `title_dark` `title_light` `section_cover_4_3` |
| agenda | `gtm_toc` `bullet_points` |
| section | `section_divider` `chapter_divider_16_9` |
| summary | `summary_shell_16_9` `kpi_cards` |
| argument | `bullet_points` `pyramid` `process_flow` |
| comparison | `comparison_table` `comparison` `matrix` |
| flow | `process_flow` `timeline` |
| image_text | `image_text` `chart_text` |
| chart | `chart_full` `two_charts` `two_charts_vertical` `chart_table` `waterfall` `scatter` `bubble` `range_snapshot` |
| dashboard | `dashboard_shell_16_9` `composite` `two_charts` |
| conclusion | `conclusion_dark` |

**实例（节选 3 页）：**

```json
{
  "meta": { "title": "宁德时代盈利能力", "audience": "投研", "aspect_ratio": "16:9",
            "theme": "dashboard_shell_16_9", "max_chart_ratio": 0.4 },
  "pages": [
    { "n": 1, "type": "cover", "layout": "title_dark",
      "action_title": "宁德时代：盈利能力深度复盘", "has_data": false },
    { "n": 2, "type": "argument", "layout": "bullet_points",
      "action_title": "营收三年翻倍但毛利率持续承压，是本篇核心矛盾",
      "has_data": false,
      "body": ["营收 2021→2024 翻倍", "毛利率 27%→24%", "净利率靠规模摊薄维稳"] },
    { "n": 3, "type": "chart", "layout": "chart_full",
      "action_title": "营收高增下毛利率逐年下行，剪刀差扩大",
      "has_data": true, "data_ref": "fin", "so_what": "毛利率三年降 3pct，规模红利见顶" }
  ]
}
```

**展开成 Job JSON `pages[]`（确定性映射，compose 节点做）：**

| outline 字段 | → Job JSON `data.*` |
|---|---|
| `layout` | `pages[].layout` |
| `action_title` | `data.title` |
| `so_what` | `data.insight`（chart）/ `data.subtitle` |
| `data_ref` | `data.source` |
| `body` | bullets / 表行 / 流程节点（逻辑页） |
| chart 页另补 | `data.categories_col` / `series_config` / `layout_config`（取数据 schema 时填） |

→ `plan_deck` 出 `DeckOutline` → 过 R1–R6 → `compose_job` 确定性展开 → `ableppt render`。正好落进 A2A 图的 `plan_deck → compose → render → critique`。

## 自检 rubric（借 PPTEval 三维 + Ghost Deck + 防滥图）

- **Ghost Deck**：action title 顺序读下来，能否独立讲通全论证？〔借鉴 academic-pptx-skill〕
- **Content**：每页一个明确论点？数字有出处（页内标注）？无凑数页？
- **Design**：版式跟内容匹配（没把文字论点硬塞进图表页）？同节风格一致？
- **Coherence**：页序成叙事弧（不是图表大杂烩）？有过渡/章节？〔三维借 PPTEval〕
- **防滥图**：chart 占比 ≤ 预算？有没有"本该文字却上了图"的页？逐页回答。
- **收尾纪律**：末页是**结论页**不是 "Thank You"；>15 页加 section divider；借用图表/数据**页内注源**。〔借鉴 academic-pptx-skill〕
- **渲染回看（可选，补 DeckLinter）**：把 deck 转成图，**派子 agent** 查 overlap/文字溢出/边距/对齐，**修-验循环到干净一遍**再交付（"别盯着代码看，会看成你以为的样子"）。〔借鉴 anthropics/skills·pptx 的 visual-inspection loop〕

## 一个范例 outline（8 页投研 deck）

| # | 页型 | layout | 说明 |
|---|---|---|---|
| 1 | cover | `title_dark` | 标题 + 标的 + 日期 |
| 2 | agenda | `gtm_toc` | 4 节目录 |
| 3 | argument | `bullet_points` | 投资逻辑三点（**纯文字，不上图**） |
| 4 | chart | `chart_full` | 营收/毛利双轴组合（数据证据） |
| 5 | chart | `waterfall` | 利润桥（连续第 2 张图，到顶） |
| 6 | comparison | `comparison_table` | 可比公司估值表（**换口气，不是图**） |
| 7 | argument | `pyramid` | 风险/催化剂框架（文字逻辑） |
| 8 | conclusion | `conclusion_dark` | 评级 + 目标价 |

→ 8 页里 chart 仅 2 页（25%），逻辑页用文字版式,叙事有起伏——而不是"8 张图"。

## 反模式（金融/研究 content 页别犯）

- ❌ **标题下加 accent 横线** —— AI 生成的典型痕迹。〔借鉴 anthropics/skills·pptx〕
- ❌ 装饰性 icon / 剪贴画 / 配图 / 渐变；content 页满版背景图。〔借鉴 academic-pptx-skill〕
- ❌ 正文堆字（content 页正文 ≤ ~40 字）、居中正文（应**左对齐**，仅标题/轴标签居中）。
- ❌ **"每页都得有个视觉元素"** —— 官方 pptx skill 这条偏营销向，**金融/研究 deck 不采纳**：它正是"满本是图"的病根。逻辑页就该是干净文字。

> 可借的版式纪律：**版式别逐页雷同、定一个视觉母题(motif)重复、一种字体配对、一个主色占 60–70% 视觉重量**。〔借鉴 anthropics/skills·pptx〕——但 content 页"视觉优先"在金融场景**让位于"论证优先"**（取 academic 派）。

## 来源 / 引用（借鉴出处）

本 playbook 的判断纪律融合了三处成熟实践，正文已就近 〔标注〕：

- **academic-pptx-skill** (Gabberflast) — Action Titles、Ghost Deck Test、One-Insight-Per-Slide、"So what" 标注、Structured-Argument 优先级、内容纪律、页内注源、反装饰原则、结论页收尾。
  https://github.com/Gabberflast/academic-pptx-skill
- **anthropics/skills · pptx**（官方）— 视觉母题/版式多样性/主色 60–70% 纪律、"标题别加 accent 线"反模式、**渲染回看式 QA 循环**。
  https://github.com/anthropics/skills/blob/main/skills/pptx/SKILL.md
- **PPTAgent** (icip-cas) — slide 功能类型化思路 + **PPTEval（Content / Design / Coherence）**评分三维。
  https://github.com/icip-cas/PPTAgent

> **关键取舍**：金融/研究 deck 以 academic 派"**论证优先、克制装饰**"为主干，仅借官方 pptx skill 的**版式多样性 + 渲染 QA 循环**；**明确不采纳其"每页都要有视觉元素"**——那正是你这次"满本是图"的根源。
