import copy
import json
import subprocess
import sys
from pathlib import Path

from pptx import Presentation

from pptfi import (
    PageComposer,
    PptEngine,
    chart_engine_info,
    demo_waterfall,
    describe_chart,
    generate_ppt,
    parse_bubble,
    parse_scatter,
    parse_template,
    parse_waterfall,
    render_bubble,
    render_scatter,
    render_waterfall,
    render_job,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pptfi", *args],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_sdk_top_level_exports():
    assert callable(parse_template)
    assert callable(generate_ppt)
    assert callable(chart_engine_info)
    assert callable(render_waterfall)
    assert callable(render_scatter)
    assert callable(render_bubble)
    assert PptEngine.__name__ == "PptEngine"
    assert PageComposer.__name__ == "PageComposer"


def test_cli_help():
    result = run_cli("--help")
    assert result.returncode == 0
    assert "Financial PowerPoint automation CLI with chart-engine compatibility helpers" in result.stdout
    assert "parse-template" in result.stdout
    assert "render" in result.stdout
    assert "chart-engine-info" in result.stdout
    assert "render-waterfall" in result.stdout
    assert "parse-waterfall" in result.stdout
    assert "demo-waterfall" in result.stdout
    assert "render-scatter" in result.stdout
    assert "parse-scatter" in result.stdout
    assert "render-bubble" in result.stdout
    assert "parse-bubble" in result.stdout


def test_cli_chart_engine_info_reports_compatibility_layer():
    result = run_cli("chart-engine-info")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["compatibility_layer"]["enabled"] is True
    assert payload["operations"]["create_combo_chart"]["module"].startswith("pptchartengine")
    assert payload["operations"]["create_waterfall_chart"]["module"].startswith("pptchartengine")
    assert payload["operations"]["create_scatter_chart"]["module"].startswith("pptchartengine")
    assert payload["operations"]["create_bubble_chart"]["module"].startswith("pptchartengine")


def test_cli_parse_template():
    template = PROJECT_ROOT / "aim" / "aim00.pptx"
    result = run_cli("parse-template", str(template))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "pages" in payload
    assert "all_chart" in payload


def test_cli_generate_real_ppt(tmp_path: Path):
    template = PROJECT_ROOT / "aim" / "aim00.pptx"
    config_path = tmp_path / "config.json"
    output_path = tmp_path / "output.pptx"
    config_path.write_text(
        json.dumps({"text_data": {"标题": "CLI 验证"}, "chart_configs": {}}, ensure_ascii=False),
        encoding="utf-8",
    )

    result = run_cli("generate", str(template), str(config_path), str(output_path))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert output_path.exists()
    assert output_path.stat().st_size > 1000


def test_sdk_describe_chart_recovers_categories_col_for_composer_output(tmp_path: Path):
    job_path = PROJECT_ROOT / "job_demo_company_a.json"
    raw_job = json.loads(job_path.read_text(encoding="utf-8"))
    job = copy.deepcopy(raw_job)
    job["output"]["path"] = str(tmp_path / "company_a.pptx")
    local_job_path = tmp_path / "job.json"
    local_job_path.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")

    result = render_job(local_job_path)
    report = describe_chart(result["output"], slide=3)
    charts = report["slides"][0]["charts"]

    assert charts
    assert charts[0]["categories_col"] in {"年份", "日期", "分类"}


def test_sdk_and_cli_waterfall_demo(tmp_path: Path):
    output = tmp_path / "waterfall-demo.pptx"
    sdk_result = demo_waterfall(output)
    assert Path(sdk_result["output"]).exists()

    parsed = parse_waterfall(output)
    assert parsed["categories_col"] == "项目"
    assert parsed["rows"][0]["measure"] == "total"

    cli_output = tmp_path / "waterfall-cli.pptx"
    cli_result = run_cli("demo-waterfall", str(cli_output))
    assert cli_result.returncode == 0, cli_result.stderr
    payload = json.loads(cli_result.stdout)
    assert Path(payload["output"]).exists()

    parsed_cli = run_cli("parse-waterfall", str(cli_output))
    assert parsed_cli.returncode == 0, parsed_cli.stderr
    parsed_payload = json.loads(parsed_cli.stdout)
    assert parsed_payload["categories_col"] == "项目"


def test_sdk_and_cli_render_waterfall_from_spec(tmp_path: Path):
    config = PROJECT_ROOT / "waterfall_demo.json"
    output = tmp_path / "waterfall-spec-sdk.pptx"
    sdk_result = render_waterfall(config, output)
    assert Path(sdk_result["output"]).exists()
    assert sdk_result["summary"]["prepared_rows"] == 6

    prs = Presentation(str(output))
    assert len(prs.slides) == 1
    chart_shapes = [shape for slide in prs.slides for shape in slide.shapes if getattr(shape, "has_chart", False)]
    assert chart_shapes

    cli_output = tmp_path / "waterfall-spec-cli.pptx"
    cli_result = run_cli("render-waterfall", str(config), str(cli_output))
    assert cli_result.returncode == 0, cli_result.stderr
    payload = json.loads(cli_result.stdout)
    assert Path(payload["output"]).exists()
    assert payload["summary"]["total_categories"] == ["期初收益", "期末收益"]


def test_composer_waterfall_layout_round_trip(tmp_path: Path):
    csv_path = tmp_path / "waterfall.csv"
    csv_path.write_text(
        "阶段,贡献,度量\n期初收益,8.5,total\n权益贡献,2.1,relative\n债券贡献,1.3,relative\n汇率拖累,-1.8,relative\n期末收益,10.1,total\n",
        encoding="utf-8",
    )
    output_path = tmp_path / "composer-waterfall.pptx"
    job = {
        "mode": "composer",
        "theme": "able_finance",
        "datasources": {
            "wf": {"type": "csv", "path": str(csv_path)},
        },
        "pages": [
            {
                "layout": "waterfall",
                "data": {
                    "title": "组合收益归因桥",
                    "source": "wf",
                    "categories_col": "阶段",
                    "value_col": "贡献",
                    "measure_col": "度量",
                    "insight": "权益和债券贡献推动收益抬升，但汇率因素构成主要拖累。",
                    "show_connectors": True,
                    "show_value_labels": True,
                },
            }
        ],
        "output": {"path": str(output_path)},
    }
    job_path = tmp_path / "job.json"
    job_path.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")

    result = render_job(job_path)
    assert Path(result["output"]).exists()

    parsed = parse_waterfall(result["output"])
    assert parsed["categories_col"] == "阶段"
    assert parsed["rows"][0]["度量"] == "total"
    assert parsed["rows"][3]["贡献"] == -1.8


def test_packaged_composer_waterfall_job(tmp_path: Path):
    raw_job = json.loads((PROJECT_ROOT / "job_waterfall_demo.json").read_text(encoding="utf-8"))
    raw_job["output"]["path"] = str(tmp_path / "packaged-waterfall.pptx")
    job_path = tmp_path / "job.json"
    job_path.write_text(json.dumps(raw_job, ensure_ascii=False, indent=2), encoding="utf-8")

    result = render_job(job_path)
    assert Path(result["output"]).exists()

    parsed = parse_waterfall(result["output"])
    assert parsed["categories_col"] == "阶段"
    assert parsed["rows"][-1]["度量"] == "total"


def test_packaged_composer_scatter_job(tmp_path: Path):
    raw_job = json.loads((PROJECT_ROOT / "job_scatter_demo.json").read_text(encoding="utf-8"))
    raw_job["output"]["path"] = str(tmp_path / "packaged-scatter.pptx")
    job_path = tmp_path / "job.json"
    job_path.write_text(json.dumps(raw_job, ensure_ascii=False, indent=2), encoding="utf-8")

    result = render_job(job_path)
    assert Path(result["output"]).exists()

    parsed = parse_scatter(result["output"])
    assert parsed["chart_family"] == "scatter"
    assert parsed["x_col"] == "波动率"
    assert parsed["y_col"] == "收益率"


def test_packaged_composer_bubble_job(tmp_path: Path):
    raw_job = json.loads((PROJECT_ROOT / "job_bubble_demo.json").read_text(encoding="utf-8"))
    raw_job["output"]["path"] = str(tmp_path / "packaged-bubble.pptx")
    job_path = tmp_path / "job.json"
    job_path.write_text(json.dumps(raw_job, ensure_ascii=False, indent=2), encoding="utf-8")

    result = render_job(job_path)
    assert Path(result["output"]).exists()

    parsed = parse_bubble(result["output"])
    assert parsed["chart_family"] == "bubble"
    assert parsed["size_col"] == "规模"


def test_sdk_and_cli_render_scatter_and_bubble(tmp_path: Path):
    scatter_config = PROJECT_ROOT / "scatter_demo.json"
    bubble_config = PROJECT_ROOT / "bubble_demo.json"

    scatter_output = tmp_path / "scatter-sdk.pptx"
    scatter_result = render_scatter(scatter_config, scatter_output)
    assert Path(scatter_result["output"]).exists()
    parsed_scatter = parse_scatter(scatter_output)
    assert parsed_scatter["chart_family"] == "scatter"
    assert parsed_scatter["x_col"] == "波动率"
    assert parsed_scatter["y_col"] == "收益率"

    bubble_output = tmp_path / "bubble-sdk.pptx"
    bubble_result = render_bubble(bubble_config, bubble_output)
    assert Path(bubble_result["output"]).exists()
    parsed_bubble = parse_bubble(bubble_output)
    assert parsed_bubble["chart_family"] == "bubble"
    assert parsed_bubble["size_col"] == "规模"

    cli_scatter_output = tmp_path / "scatter-cli.pptx"
    cli_scatter = run_cli("render-scatter", str(scatter_config), str(cli_scatter_output))
    assert cli_scatter.returncode == 0, cli_scatter.stderr
    scatter_payload = json.loads(cli_scatter.stdout)
    assert Path(scatter_payload["output"]).exists()

    cli_parse_scatter = run_cli("parse-scatter", str(cli_scatter_output))
    assert cli_parse_scatter.returncode == 0, cli_parse_scatter.stderr
    parsed_scatter_payload = json.loads(cli_parse_scatter.stdout)
    assert parsed_scatter_payload["chart_family"] == "scatter"

    cli_bubble_output = tmp_path / "bubble-cli.pptx"
    cli_bubble = run_cli("render-bubble", str(bubble_config), str(cli_bubble_output))
    assert cli_bubble.returncode == 0, cli_bubble.stderr
    bubble_payload = json.loads(cli_bubble.stdout)
    assert Path(bubble_payload["output"]).exists()

    cli_parse_bubble = run_cli("parse-bubble", str(cli_bubble_output))
    assert cli_parse_bubble.returncode == 0, cli_parse_bubble.stderr
    parsed_bubble_payload = json.loads(cli_parse_bubble.stdout)
    assert parsed_bubble_payload["chart_family"] == "bubble"
