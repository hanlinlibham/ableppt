"""GTM 页面布局合同测试。"""

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def test_gtm_panels_registered():
    from ableppt.composer.layouts import LAYOUT_REGISTRY
    assert "gtm_panels" in LAYOUT_REGISTRY


def test_gtm_two_panel_page_renders():
    from ableppt.composer.page_composer import PageComposer

    composer = PageComposer(theme="able_finance")
    composer.add_page("gtm_panels", {
        "title": "测试页",
        "section": "宏观",
        "market": "CN",
        "page_num": 1,
        "source": "来源：测试",
        "brand": "PPT·FI",
        "panels": [
            {"title": "面板一", "subtitle": "同比",
             "chart": {"data": {"年": ["23", "24"], "v": [1, 2]}, "legend": "none"}},
            {"title": "面板二",
             "chart": {"chart": "line",
                       "data": {"年": ["23", "24"], "v": [0.1, 0.2]}, "legend": "none"},
             "table": {"columns": ["", "均值"], "rows": [["指标", "1.5"]],
                       "row_colors": ["#29ABE2"]}},
        ],
    })
    slide = composer.prs.slides[0]
    charts = [s for s in slide.shapes if s.has_chart]
    tables = [s for s in slide.shapes if s.has_table]
    assert len(charts) == 2
    assert len(tables) == 1
    assert len(slide.shapes) >= 14


def test_gtm_one_plus_two_layout():
    from ableppt.composer.layouts.gtm import _panel_rects
    rects = _panel_rects(3)
    assert len(rects) == 3
    assert rects[0][3] > rects[1][3]      # 左面板全高
    assert rects[1][0] == rects[2][0]     # 右侧两面板同 x
    assert rects[2][1] > rects[1][1]      # 上下排


def test_gtm_demo_job_renders():
    import os
    job_path = REPO / "job_gtm_demo.json"
    if not job_path.exists():
        pytest.skip("demo job missing")
    cwd = os.getcwd()
    os.chdir(REPO)
    try:
        from ableppt.operations import render_job
        result = render_job(str(job_path))
        assert result.get("status") == "ok"
        assert Path(result["output"]).exists()
    finally:
        os.chdir(cwd)


def test_new_layouts_registered():
    from ableppt.composer.layouts import LAYOUT_REGISTRY
    for name in ("gtm_cover", "gtm_toc", "gtm_quilt", "gtm_chart_text"):
        assert name in LAYOUT_REGISTRY


def test_panel_rects_2x2():
    from ableppt.composer.layouts.gtm import _panel_rects
    rects = _panel_rects(4)
    assert len(rects) == 4
    assert rects[0][1] == rects[1][1]   # 上排同 y
    assert rects[2][1] == rects[3][1]   # 下排同 y
    assert rects[2][1] > rects[0][1]


def test_deck_workflow_defaults_and_toc():
    from ableppt.models.job import Job
    from ableppt.engine import PptEngine

    job = Job(**{
        "mode": "composer",
        "deck": {"brand": "测试品牌", "market": "CN", "start_page": 1},
        "pages": [
            {"layout": "gtm_cover", "data": {"title": "封面"}},
            {"layout": "gtm_toc", "data": {}},
            {"layout": "gtm_panels", "data": {"title": "宏观页", "section": "宏观", "panels": []}},
            {"layout": "gtm_panels", "data": {"title": "权益页", "section": "权益", "panels": []}},
        ],
        "output": {"path": "x.pptx"},
    })
    staged = PptEngine._apply_deck_workflow(job)
    datas = [s[1] for s in staged]
    assert datas[2]["page_num"] == 3 and datas[3]["page_num"] == 4
    assert datas[2]["brand"] == "测试品牌"
    toc_items = datas[1]["items"]
    assert [g["section"] for g in toc_items] == ["宏观", "权益"]
    assert toc_items[0]["entries"][0]["page"] == 3


def test_quilt_layout_renders():
    import pandas as pd
    from ableppt.composer.page_composer import PageComposer

    df = pd.DataFrame({
        "年份": ["2024", "2024", "2025", "2025"],
        "资产": ["A股", "黄金", "A股", "黄金"],
        "收益率": [0.05, 0.12, 0.18, 0.07],
    })
    composer = PageComposer(theme="able_finance")
    composer.add_page("gtm_quilt", {"title": "矩阵", "df": df, "source": "来源：测试"})
    slide = composer.prs.slides[0]
    tables = [s for s in slide.shapes if s.has_table]
    assert len(tables) == 1
    # 2025 年列（第 2 列）收益最高的 A股 应排首行
    assert "A股" in tables[0].table.cell(1, 1).text_frame.text


def test_gtm_chart_text_renders():
    from ableppt.composer.page_composer import PageComposer

    composer = PageComposer(theme="able_finance")
    composer.add_page("gtm_chart_text", {
        "title": "观点页", "section": "权益",
        "panel": {"title": "面板",
                  "chart": {"data": {"年": ["23", "24"], "v": [1, 2]}, "legend": "none"}},
        "bullets": ["要点一", "要点二"],
    })
    slide = composer.prs.slides[0]
    assert any(s.has_chart for s in slide.shapes)


def test_gtm_page_examples():
    from ableppt.composer.layouts.gtm_examples import gtm_page_examples
    assert gtm_page_examples().count("```json") >= 8
    assert "gtm_quilt" in gtm_page_examples("quilt")


class TestStructuredOutputAlignment:
    """结构化输出对齐：job schema（语法）+ 深度校验（语义）。"""

    def test_gtm_job_schema_valid_and_accepts_demo(self):
        import json
        import jsonschema
        from ableppt.composer.layouts.gtm_schema import gtm_job_schema

        schema = gtm_job_schema()
        jsonschema.Draft7Validator.check_schema(schema)
        job = json.loads((REPO / "job_gtm_demo.json").read_text())
        assert not list(jsonschema.Draft7Validator(schema).iter_errors(job))

    def test_schema_rejects_unknown_layout(self):
        import jsonschema
        from ableppt.composer.layouts.gtm_schema import gtm_job_schema

        bad = {"mode": "composer", "pages": [{"layout": "gtm_pie", "data": {}}],
               "output": {"path": "x.pptx"}}
        assert list(jsonschema.Draft7Validator(gtm_job_schema()).iter_errors(bad))

    def test_deep_validation_passes_demo_job(self):
        import os
        from ableppt.composer.layouts.gtm_schema import validate_gtm_job
        cwd = os.getcwd()
        os.chdir(REPO)
        try:
            report = validate_gtm_job(REPO / "job_gtm_demo.json")
        finally:
            os.chdir(cwd)
        assert report["ok"] is True and report["pages"] == 10

    def test_deep_validation_locates_column_typo(self):
        import os
        from ableppt.composer.layouts.gtm_schema import validate_gtm_job
        bad = {"mode": "composer",
               "pages": [{"layout": "gtm_panels", "data": {"title": "P", "panels": [
                   {"chart": {"chart": "contribution", "total": "GDP同笔",
                              "data": "data/gtm/gdp_contrib.csv"}}]}}],
               "output": {"path": "x.pptx"}}
        cwd = os.getcwd()
        os.chdir(REPO)
        try:
            report = validate_gtm_job(bad)
        finally:
            os.chdir(cwd)
        assert report["ok"] is False
        assert any("pages[1]" in e and "GDP同比" in e for e in report["errors"])

    def test_chart_spec_schema_exported(self):
        import jsonschema
        from ablechart import chart_spec_schema
        schema = chart_spec_schema()
        jsonschema.Draft7Validator.check_schema(schema)
        v = jsonschema.Draft7Validator(schema)
        assert not list(v.iter_errors({"chart": "range", "low": "l", "high": "h"}))
        assert list(v.iter_errors({"chart": "pie"}))


class TestPromptKitAndSafeRender:
    """提示词工具包 + 自修正循环（agent 工作流的两块拼图）。"""

    def test_datasource_manifest_from_dir(self):
        from ableppt.composer.layouts.gtm_prompt import datasource_manifest
        md = datasource_manifest(REPO / "data" / "gtm")
        assert "asset_returns.csv" in md
        assert "| 年份 | 数值 |" in md
        assert "收益率" in md

    def test_datasource_manifest_from_job(self):
        from ableppt.composer.layouts.gtm_prompt import datasource_manifest
        md = datasource_manifest(REPO / "job_gtm_demo.json")
        # 注册的 datasource 和 pages 内直接引用的 CSV 都应收录
        assert "asset_returns" in md
        assert "gdp_contrib.csv" in md

    def test_prompt_kit_assembles_all_parts(self):
        from ableppt.composer.layouts.gtm_prompt import gtm_prompt_kit
        kit = gtm_prompt_kit(job=REPO / "job_gtm_demo.json")
        assert "产出规则" in kit          # 规则
        assert "gtm_quilt" in kit         # 页面示例
        assert "contribution" in kit      # 图表示例
        assert "可用数据源清单" in kit     # 数据清单

    def test_self_correction_loop(self):
        """模拟 agent 流程：产出含错 job → 深度校验 → 按建议修正 → 校验通过。"""
        import json
        import os
        from ableppt.composer.layouts.gtm_schema import validate_gtm_job

        job = json.loads((REPO / "job_gtm_demo.json").read_text())
        job["pages"][2]["data"]["panels"][0]["chart"]["total"] = "GDP同笔"  # 模型拼错

        cwd = os.getcwd()
        os.chdir(REPO)
        try:
            report = validate_gtm_job(job)
            assert not report["ok"]
            # 错误里带修正建议
            err = next(e for e in report["errors"] if "GDP同笔" in e)
            assert "GDP同比" in err
            # 按建议修正后通过
            job["pages"][2]["data"]["panels"][0]["chart"]["total"] = "GDP同比"
            assert validate_gtm_job(job)["ok"] is True
        finally:
            os.chdir(cwd)
