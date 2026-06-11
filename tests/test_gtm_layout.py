"""GTM 页面布局合同测试。"""

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def test_gtm_panels_registered():
    from pptfi.composer.layouts import LAYOUT_REGISTRY
    assert "gtm_panels" in LAYOUT_REGISTRY


def test_gtm_two_panel_page_renders():
    from pptfi.composer.page_composer import PageComposer

    composer = PageComposer(theme="jp_finance")
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
    from pptfi.composer.layouts.gtm import _panel_rects
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
        from pptfi.operations import render_job
        result = render_job(str(job_path))
        assert result.get("status") == "ok"
        assert Path(result["output"]).exists()
    finally:
        os.chdir(cwd)
