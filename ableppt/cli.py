from __future__ import annotations

import argparse
import json
import sys

from ableppt import operations
from ableppt.qa.deck_linter import DeckLinter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ableppt",
        description="Financial PowerPoint automation CLI with chart-engine compatibility helpers",
        epilog=(
            "Examples:\n"
            "  ableppt chart-engine-info\n"
            "  ableppt render-waterfall waterfall_demo.json output/waterfall_demo.pptx\n"
            "  ableppt parse-waterfall output/waterfall_demo.pptx\n"
            "  ableppt render-scatter scatter_demo.json output/scatter_demo.pptx\n"
            "  ableppt render-bubble bubble_demo.json output/bubble_demo.pptx\n"
            "  ableppt render-range-snapshot range_snapshot_demo.json output/range_snapshot_demo.pptx\n"
            "  ableppt render-family performance_compare_demo.json output/performance_compare_demo.pptx\n"
            "  ableppt render job_hikvision.json\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_template = subparsers.add_parser("parse-template", help="Parse placeholders from a PPT template")
    parse_template.add_argument("template")
    parse_template.add_argument("--flat", action="store_true")

    generate = subparsers.add_parser("generate", help="Generate PPT from template + config JSON")
    generate.add_argument("template")
    generate.add_argument("config")
    generate.add_argument("output")

    describe_data = subparsers.add_parser(
        "describe-data", help="生成数据源清单（markdown，供注入模型提示词）")
    describe_data.add_argument("source", help="job JSON / CSV 目录 / CSV 文件")

    prompt_kit = subparsers.add_parser(
        "prompt-kit", help="组装 GTM 提示词物料：规则+页面示例+图表示例+数据清单")
    prompt_kit.add_argument("source", nargs="?", help="job JSON 或数据目录（可选）")

    validate_job = subparsers.add_parser("validate-job", help="Validate job JSON")
    validate_job.add_argument("--deep", action="store_true",
                              help="GTM deck 深度校验：加载数据源并逐面板校验 chart spec（不渲染）")
    validate_job.add_argument("job_json")
    validate_job.add_argument("--dry-run", action="store_true")

    render = subparsers.add_parser("render", help="Render PPT from job JSON")
    render.add_argument("--validate", action="store_true",
                        help="先做 GTM 深度校验，有错误则输出报告并退出，不渲染")
    render.add_argument("job_json")
    render.add_argument("--data-dir")

    describe = subparsers.add_parser("describe-chart", help="Describe charts inside PPT")
    describe.add_argument("input")
    describe.add_argument("--slide", type=int)

    describe_waterfall = subparsers.add_parser("parse-waterfall", help="Recover waterfall semantics from PPT")
    describe_waterfall.add_argument("input")
    describe_waterfall.add_argument("--slide-idx", type=int, default=0)
    describe_waterfall.add_argument("--shape-idx", type=int, default=0)

    describe_scatter = subparsers.add_parser("parse-scatter", help="Recover scatter semantics from PPT")
    describe_scatter.add_argument("input")
    describe_scatter.add_argument("--slide-idx", type=int, default=0)
    describe_scatter.add_argument("--shape-idx", type=int, default=0)

    describe_bubble = subparsers.add_parser("parse-bubble", help="Recover bubble semantics from PPT")
    describe_bubble.add_argument("input")
    describe_bubble.add_argument("--slide-idx", type=int, default=0)
    describe_bubble.add_argument("--shape-idx", type=int, default=0)

    describe_range_snapshot = subparsers.add_parser(
        "parse-range-snapshot",
        help="Recover range snapshot semantics from PPT",
    )
    describe_range_snapshot.add_argument("input")
    describe_range_snapshot.add_argument("--slide-idx", type=int, default=0)
    describe_range_snapshot.add_argument("--shape-idx", type=int, default=0)

    parse_ppt = subparsers.add_parser("parse-ppt", help="Parse PPT into JSON")
    parse_ppt.add_argument("input")
    parse_ppt.add_argument("output", nargs="?")

    rebuild = subparsers.add_parser("rebuild-ppt", help="Rebuild PPT from parsed JSON")
    rebuild.add_argument("input")
    rebuild.add_argument("output")

    presets = subparsers.add_parser("list-presets", help="List preset charts/colors/date axes")
    presets.add_argument("--color-schemes", action="store_true")
    presets.add_argument("--date-axis", action="store_true")
    presets.add_argument("--chart-presets", action="store_true")

    subparsers.add_parser(
        "chart-engine-info",
        help="Show how ableppt routes chart_builder imports to the chart engine compatibility layer",
    )

    render_waterfall = subparsers.add_parser(
        "render-waterfall",
        help="Render a standalone waterfall chart PPT from a chart-engine JSON spec",
    )
    render_waterfall.add_argument("config", help="Waterfall JSON spec, e.g. waterfall_demo.json")
    render_waterfall.add_argument("output", help="Output PPTX path")

    render_scatter = subparsers.add_parser(
        "render-scatter",
        help="Render a standalone scatter chart PPT from a chart-engine JSON spec",
    )
    render_scatter.add_argument("config", help="Scatter JSON spec, e.g. scatter_demo.json")
    render_scatter.add_argument("output", help="Output PPTX path")

    render_bubble = subparsers.add_parser(
        "render-bubble",
        help="Render a standalone bubble chart PPT from a chart-engine JSON spec",
    )
    render_bubble.add_argument("config", help="Bubble JSON spec, e.g. bubble_demo.json")
    render_bubble.add_argument("output", help="Output PPTX path")

    render_range_snapshot = subparsers.add_parser(
        "render-range-snapshot",
        help="Render a standalone range snapshot chart PPT from a chart-engine JSON spec",
    )
    render_range_snapshot.add_argument("config", help="Range snapshot JSON spec")
    render_range_snapshot.add_argument("output", help="Output PPTX path")

    render_family = subparsers.add_parser(
        "render-family",
        help="Render a standalone semantic chart family PPT from a JSON spec",
    )
    render_family.add_argument("config", help="Semantic family JSON spec")
    render_family.add_argument("output", help="Output PPTX path")

    fetch = subparsers.add_parser("fetch-data", help="Load datasources and export CSVs")
    fetch.add_argument("--config", required=True)
    fetch.add_argument("--output", required=True)
    fetch.add_argument("--transforms")

    lint = subparsers.add_parser("validate-ppt", help="Run DeckLinter on PPT")
    lint.add_argument("pptx")
    lint.add_argument("--json", action="store_true")
    lint.add_argument("--write-notes", action="store_true")

    demo_waterfall = subparsers.add_parser("demo-waterfall", help="Generate a sample waterfall PPT")
    demo_waterfall.add_argument("output")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "parse-template":
            result = operations.parse_template(args.template, flat=args.flat)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if args.command == "generate":
            result = operations.generate_ppt(args.template, args.config, args.output)
            print(json.dumps(result, ensure_ascii=False))
            return 0

        if args.command == "describe-data":
            from ableppt.composer.layouts.gtm_prompt import datasource_manifest
            print(datasource_manifest(args.source))
            return 0

        if args.command == "prompt-kit":
            from ableppt.composer.layouts.gtm_prompt import gtm_prompt_kit
            source = args.source
            if source and str(source).endswith(".json"):
                print(gtm_prompt_kit(job=source))
            elif source:
                print(gtm_prompt_kit(data_dir=source))
            else:
                print(gtm_prompt_kit())
            return 0

        if args.command == "validate-job":
            if args.deep:
                from ableppt.composer.layouts.gtm_schema import validate_gtm_job
                result = validate_gtm_job(args.job_json)
            else:
                result = operations.validate_job(args.job_json, dry_run=args.dry_run)
            print(json.dumps(result, ensure_ascii=False))
            return 0

        if args.command == "render":
            if getattr(args, "validate", False):
                from ableppt.composer.layouts.gtm_schema import validate_gtm_job
                report = validate_gtm_job(args.job_json)
                if not report["ok"]:
                    print(json.dumps({"status": "validation_failed", **report},
                                     ensure_ascii=False, indent=1))
                    return 1
            result = operations.render_job(args.job_json, data_dir=args.data_dir)
            print(json.dumps(result, ensure_ascii=False))
            return 0

        if args.command == "describe-chart":
            result = operations.describe_chart(args.input, slide=args.slide)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if args.command == "parse-waterfall":
            result = operations.parse_waterfall(args.input, slide_idx=args.slide_idx, shape_idx=args.shape_idx)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if args.command == "parse-scatter":
            result = operations.parse_scatter(args.input, slide_idx=args.slide_idx, shape_idx=args.shape_idx)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if args.command == "parse-bubble":
            result = operations.parse_bubble(args.input, slide_idx=args.slide_idx, shape_idx=args.shape_idx)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if args.command == "parse-range-snapshot":
            result = operations.parse_range_snapshot(args.input, slide_idx=args.slide_idx, shape_idx=args.shape_idx)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if args.command == "parse-ppt":
            result = operations.parse_ppt(args.input, output_json=args.output)
            print(json.dumps(result, ensure_ascii=False, indent=2 if args.output is None else None))
            return 0

        if args.command == "rebuild-ppt":
            result = operations.rebuild_ppt(args.input, args.output)
            print(json.dumps(result, ensure_ascii=False))
            return 0

        if args.command == "list-presets":
            result = operations.list_presets(
                color_schemes=args.color_schemes,
                date_axis=args.date_axis,
                chart_presets=args.chart_presets,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if args.command == "chart-engine-info":
            result = operations.chart_engine_info()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if args.command == "render-waterfall":
            result = operations.render_waterfall(args.config, args.output)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if args.command == "render-scatter":
            result = operations.render_scatter(args.config, args.output)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if args.command == "render-bubble":
            result = operations.render_bubble(args.config, args.output)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if args.command == "render-range-snapshot":
            result = operations.render_range_snapshot(args.config, args.output)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if args.command == "render-family":
            result = operations.render_family(args.config, args.output)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if args.command == "fetch-data":
            result = operations.fetch_data(args.config, args.output, transforms_path=args.transforms)
            print(json.dumps(result, ensure_ascii=False))
            return 0

        if args.command == "validate-ppt":
            report = operations.validate_ppt(args.pptx, write_notes=args.write_notes)
            if args.json:
                print(json.dumps(report, ensure_ascii=False, indent=2))
            else:
                DeckLinter(args.pptx).print_summary(report, file=sys.stdout)
            return 1 if report["summary"]["errors"] > 0 else 0

        if args.command == "demo-waterfall":
            result = operations.demo_waterfall(args.output)
            print(json.dumps(result, ensure_ascii=False))
            return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2
