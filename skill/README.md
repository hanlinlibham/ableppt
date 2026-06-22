# ableppt — 会先讲逻辑、再画图的金融 PPT 引擎

> 把数据变成**原生可编辑**的 `.pptx`。重点是：**它不会把你的 deck 做成一摞图表。**

---

AI 生成的 PPT 你大概见过那个味儿：**每页一张图、配色花哨、读完不知道在讲啥**。
ableppt 反着来——它先当**导演**把逻辑捋顺，再让引擎去画那几张*真正需要*的图。

图表是底层强项（`ablechart` 引擎，原生 OOXML、可双击编辑、能把图读回数据）；
但上面压着一套**纪律**，逼着"逻辑页用文字、对比用表格、只有数据能加强论点时才上图"。

## 30 秒上手

在 `ableppt/` 目录里：

```bash
ableppt render-waterfall waterfall_demo.json output/demo.pptx   # Job JSON → 可编辑 PPT
ableppt validate-ppt     output/demo.pptx                       # DeckLinter 质检
ableppt parse-waterfall  output/demo.pptx                       # 把原生图表读回数据(证明可编辑)
```

出来的是 PowerPoint 里能直接双击改的原生图表 —— 不是截图贴上去的。

## 它最擅长两件事

| | 干啥 | 北极星 |
|---|---|---|
| **模板更新** | 上传现成 `.pptx`，原位把图表/表格数据换掉，**样式、位置、可编辑性全保留** | ⭐ 主场 |
| **整本生成** | 从 brief + 数据 → 多页 deck，**但有导演纪律**，不满本是图 | 第二批 |

## 不让你"满本是图"：导演纪律

这是 ableppt 跟"一键生成"工具最不一样的地方。生成整本前，它先派页型、定预算：

- **Action Title** — 每页标题是**结论句**，不是主题词。
  "营收三年翻倍但毛利率承压" ✅ ／ "营收情况" ❌
- **Ghost Deck Test** — 所有标题顺读下来，得能**独立讲通整个论证**；讲不通，先改大纲。
- **图表预算** — chart 页 ≤ 全本 ~40%、连续不超过 2 张；逻辑页默认走文字/表格版式。
- **每张图配 "So what"** — 图上必须有一句话点出要点。

> 完整 playbook（页型 taxonomy、`plan_deck` 机器契约 schema、自检 rubric）见
> [`references/deck-planning.md`](references/deck-planning.md)。

## 引擎底子（图为什么能编辑）

底层是 [`ablechart`](https://github.com/hanlinlibham/ablechart) 引擎（已上 PyPI）：

- **原生可编辑 + round-trip**：图表是真 OOXML，带内嵌工作簿；还能 `parse` 读回 DataFrame。
- **细粒度精修**：双轴组合 / 瀑布 / 散点 / 气泡 / 区间；轴标题、刻度旋转、逐轴数字格式、量程、网格、图例位置。
- **fail-loud 但友好**：列名写错不会甩一句天书，而是
  `列 ['打错的列'] 不在数据中。可用列：['月份','销量','增速']` —— 照着改即可。
- **手滑也不崩**：配色名 / 主题名写错 → **自动回退默认、照常出图**（装饰类容错；数据类才严管）。

## 想深入看哪儿

- [`SKILL.md`](SKILL.md) — 给 agent 看的操作手册（快速上手 / 工作流 / 图表精修 / 容错边界）
- [`references/deck-planning.md`](references/deck-planning.md) — 导演 playbook + `plan_deck` schema
- 代码仓：`ableppt`（上层方案） · `ablechart`（图表内核）

## 诚实的边界

- 最成熟：金融时间序列、双轴组合、模板替换、报告型编排、瀑布/散点/气泡。
- 图表精修暂缺：对数轴、原生 display units（×1000/百万角标）、图例手动 XY 定位。
- `merge` 变换未实现；极复杂图表类型尚不在稳定范围。

## 站在前人肩上

导演纪律融合了几处成熟实践，playbook 里逐条标了出处：

- [academic-pptx-skill](https://github.com/Gabberflast/academic-pptx-skill) — Action Title、Ghost Deck Test、克制装饰
- [anthropics/skills · pptx](https://github.com/anthropics/skills/blob/main/skills/pptx/SKILL.md) — 版式纪律、渲染回看式 QA
- [PPTAgent](https://github.com/icip-cas/PPTAgent) — slide 功能类型化 + PPTEval 三维评分

---

*一句话：ablechart 负责把图画得能编辑，ableppt 负责让整本 deck 像个有逻辑的人做的。*
