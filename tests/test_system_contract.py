from pathlib import Path

from ableppt import (
    DUAL_CHART_PANEL_FAMILY,
    FACTOR_ATTRIBUTION_PANEL_FAMILY,
    AWARD_TIMELINE_PANEL_FAMILY,
    HEATMAP_MATRIX_FAMILY,
    HOLDING_DETAIL_FAMILY,
    MANAGER_TIMELINE_PROFILE_FAMILY,
    PERFORMANCE_COMPARE_FAMILY,
    REGIME_TABLE_PANEL_FAMILY,
    RANKED_TILE_MATRIX_FAMILY,
    SELECTION_TIMING_GRID_FAMILY,
    TABLE_PLUS_CHART_COMPOSITE_FAMILY,
    create_factor_attribution_panel,
    chart_engine_info,
    create_waterfall_chart,
    create_scatter_chart,
    create_bubble_chart,
    create_factor_attribution_panel,
    create_award_timeline_panel,
    create_holding_detail_panel,
    create_dual_chart_panel,
    create_semantic_chart,
    create_heatmap_matrix_chart,
    create_manager_timeline_profile,
    create_ranked_tile_matrix_chart,
    create_range_snapshot_chart,
    create_regime_table_panel,
    create_selection_timing_grid,
    create_table_plus_chart_composite,
    parse_scatter_chart,
    parse_scatter_from_pptx,
    parse_bubble_chart,
    parse_bubble_from_pptx,
    parse_range_snapshot_chart,
    parse_range_snapshot_from_pptx,
    parse_waterfall_chart,
    parse_waterfall_from_pptx,
    list_semantic_families,
    prepare_range_snapshot_dataframe,
    prepare_waterfall_dataframe,
    restore_range_snapshot_dataframe,
    render_family,
    render_bubble,
    render_range_snapshot,
    render_scatter,
    render_waterfall,
)
from ableppt.advisors import ChartAdvisor, ChartRecommendation, DataFrameProfiler
from ableppt.composer import PageComposer
from ableppt.config import settings
from ableppt.connectors import ConnectorFactory
from ableppt.engine import PptEngine
from ableppt.extractors import StyleExtractor, StyleProfile
from ableppt.main import app
from ableppt.models.job import Job
from ableppt.parsers.ppt_parser import PPTParser
from ableppt.qa.deck_linter import DeckLinter
from ableppt.renderers import PPTRenderer, TableRenderer, TextRenderer
from ableppt.template.chart_presets import CHART_PRESET_FUNCTIONS
from ableppt.template.replacer import TemplateReplacer
from ableppt.transformers import DataFrameTransformer


def test_system_core_imports():
    assert PptEngine.__name__ == "PptEngine"
    assert Job.__name__ == "Job"
    assert PageComposer.__name__ == "PageComposer"
    assert TemplateReplacer.__name__ == "TemplateReplacer"
    assert PPTParser.__name__ == "PPTParser"
    assert PPTRenderer.__name__ == "PPTRenderer"
    assert DeckLinter.__name__ == "DeckLinter"
    assert ChartAdvisor.__name__ == "ChartAdvisor"
    assert DataFrameProfiler.__name__ == "DataFrameProfiler"
    assert ChartRecommendation.__name__ == "ChartRecommendation"
    assert StyleExtractor.__name__ == "StyleExtractor"
    assert StyleProfile.__name__ == "StyleProfile"
    assert TextRenderer.__name__ == "TextRenderer"
    assert TableRenderer.__name__ == "TableRenderer"
    assert DataFrameTransformer.__name__ == "DataFrameTransformer"
    assert app.title == "PPTFI API"
    assert callable(create_waterfall_chart)
    assert callable(create_semantic_chart)
    assert callable(create_ranked_tile_matrix_chart)
    assert callable(create_heatmap_matrix_chart)
    assert callable(create_table_plus_chart_composite)
    assert callable(create_dual_chart_panel)
    assert callable(create_factor_attribution_panel)
    assert callable(create_manager_timeline_profile)
    assert callable(create_award_timeline_panel)
    assert callable(create_holding_detail_panel)
    assert callable(create_regime_table_panel)
    assert callable(create_selection_timing_grid)
    assert callable(prepare_waterfall_dataframe)
    assert callable(create_scatter_chart)
    assert callable(create_bubble_chart)
    assert callable(create_range_snapshot_chart)
    assert callable(parse_scatter_chart)
    assert callable(parse_scatter_from_pptx)
    assert callable(parse_bubble_chart)
    assert callable(parse_bubble_from_pptx)
    assert callable(parse_range_snapshot_chart)
    assert callable(parse_range_snapshot_from_pptx)
    assert callable(render_scatter)
    assert callable(render_bubble)
    assert callable(render_range_snapshot)
    assert callable(parse_waterfall_chart)
    assert callable(parse_waterfall_from_pptx)
    assert callable(chart_engine_info)
    assert callable(list_semantic_families)
    assert callable(render_family)
    assert callable(render_waterfall)
    assert callable(prepare_range_snapshot_dataframe)
    assert callable(restore_range_snapshot_dataframe)


def test_chart_builder_compatibility_layer_contract():
    info = chart_engine_info()
    assert info["compatibility_layer"]["enabled"] is True
    assert info["compatibility_layer"]["implementation_root_exists"] is True
    assert info["operations"]["create_combo_chart"]["module"].startswith("ablechart")
    assert info["operations"]["create_waterfall_chart"]["module"].startswith("ablechart")
    assert info["operations"]["create_range_snapshot_chart"]["module"].startswith("ablechart")
    assert PERFORMANCE_COMPARE_FAMILY in info["semantic_families"]
    assert DUAL_CHART_PANEL_FAMILY in info["semantic_families"]
    assert RANKED_TILE_MATRIX_FAMILY in info["semantic_families"]
    assert HEATMAP_MATRIX_FAMILY in info["semantic_families"]
    assert TABLE_PLUS_CHART_COMPOSITE_FAMILY in info["semantic_families"]
    assert FACTOR_ATTRIBUTION_PANEL_FAMILY in info["semantic_families"]
    assert REGIME_TABLE_PANEL_FAMILY in info["semantic_families"]
    assert MANAGER_TIMELINE_PROFILE_FAMILY in info["semantic_families"]
    assert AWARD_TIMELINE_PANEL_FAMILY in info["semantic_families"]
    assert SELECTION_TIMING_GRID_FAMILY in info["semantic_families"]
    assert HOLDING_DETAIL_FAMILY in info["semantic_families"]


def test_runtime_directories_exist():
    assert settings.base_dir.name == "ableppt"
    assert settings.data_dir.exists()
    assert settings.output_dir.exists()
    assert settings.templates_dir.exists()


def test_connectors_and_finance_presets_registered():
    assert set(ConnectorFactory._connectors) >= {"csv", "xlsx", "sql", "tushare"}
    assert set(CHART_PRESET_FUNCTIONS) == {
        "图表1 - 当年收益率走势",
        "图表2 - 成立以来收益率",
        "图表3 - 权益仓位走势",
        "图表4 - 久期走势",
    }


def test_atomic_scripts_present():
    root = Path(__file__).resolve().parent.parent
    expected = {
        "generate_ppt.py",
        "run_job.py",
        "render_ppt.py",
        "fetch_data.py",
        "validate_job.py",
        "validate_ppt.py",
        "parse_template.py",
        "describe_chart.py",
        "parse_ppt.py",
        "rebuild_ppt.py",
        "list_presets.py",
        "add_placeholders.py",
        "render_waterfall.py",
        "render_scatter.py",
        "render_bubble.py",
        "render_range_snapshot.py",
        "render_vertical_valuation_previews.py",
        "export_powerpoint_pdf.py",
        "build_tushare_sqlite.py",
    }
    actual = {path.name for path in (root / "scripts").glob("*.py")}
    assert expected <= actual
