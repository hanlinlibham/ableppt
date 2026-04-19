from pathlib import Path

from pptfi import (
    chart_engine_info,
    create_waterfall_chart,
    create_scatter_chart,
    create_bubble_chart,
    parse_scatter_chart,
    parse_scatter_from_pptx,
    parse_bubble_chart,
    parse_bubble_from_pptx,
    parse_waterfall_chart,
    parse_waterfall_from_pptx,
    prepare_waterfall_dataframe,
    render_bubble,
    render_scatter,
    render_waterfall,
)
from pptfi.advisors import ChartAdvisor, ChartRecommendation, DataFrameProfiler
from pptfi.composer import PageComposer
from pptfi.config import settings
from pptfi.connectors import ConnectorFactory
from pptfi.engine import PptEngine
from pptfi.extractors import StyleExtractor, StyleProfile
from pptfi.main import app
from pptfi.models.job import Job
from pptfi.parsers.ppt_parser import PPTParser
from pptfi.qa.deck_linter import DeckLinter
from pptfi.renderers import PPTRenderer, TableRenderer, TextRenderer
from pptfi.template.chart_presets import CHART_PRESET_FUNCTIONS
from pptfi.template.replacer import TemplateReplacer
from pptfi.transformers import DataFrameTransformer


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
    assert callable(prepare_waterfall_dataframe)
    assert callable(create_scatter_chart)
    assert callable(create_bubble_chart)
    assert callable(parse_scatter_chart)
    assert callable(parse_scatter_from_pptx)
    assert callable(parse_bubble_chart)
    assert callable(parse_bubble_from_pptx)
    assert callable(render_scatter)
    assert callable(render_bubble)
    assert callable(parse_waterfall_chart)
    assert callable(parse_waterfall_from_pptx)
    assert callable(chart_engine_info)
    assert callable(render_waterfall)


def test_chart_builder_compatibility_layer_contract():
    info = chart_engine_info()
    assert info["compatibility_layer"]["enabled"] is True
    assert info["compatibility_layer"]["implementation_root_exists"] is True
    assert info["operations"]["create_combo_chart"]["module"].startswith("pptchartengine")
    assert info["operations"]["create_waterfall_chart"]["module"].startswith("pptchartengine")


def test_runtime_directories_exist():
    assert settings.base_dir.name == "pptfi"
    assert settings.data_dir.exists()
    assert settings.output_dir.exists()
    assert settings.templates_dir.exists()


def test_connectors_and_finance_presets_registered():
    assert set(ConnectorFactory._connectors) >= {"csv", "xlsx", "tushare"}
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
    }
    actual = {path.name for path in (root / "scripts").glob("*.py")}
    assert expected <= actual
