import json
from pathlib import Path

from ableppt import (
    DEFAULT_JP_DEMO_CHART_CATALOG_PATH,
    ChartCatalog,
    load_jp_demo_chart_catalog,
)


def test_chart_catalog_sdk_exports():
    assert ChartCatalog.__name__ == "ChartCatalog"
    assert DEFAULT_JP_DEMO_CHART_CATALOG_PATH.name == "jp_demo_chart_catalog.json"
    assert callable(load_jp_demo_chart_catalog)


def test_jp_demo_chart_catalog_loads_and_covers_every_page():
    catalog = load_jp_demo_chart_catalog()

    assert catalog.catalog_id == "jp_demo_chart_catalog_v2"
    assert catalog.source_pdf == "jp_demo.pdf"
    assert catalog.source_page_count == 74
    assert len(catalog.pages) == 74
    assert [page.page_number for page in catalog.pages] == list(range(1, 75))


def test_jp_demo_chart_catalog_family_mapping_is_stable():
    catalog = load_jp_demo_chart_catalog()
    by_page = {page.page_number: page for page in catalog.pages}
    by_family = {family.id: family for family in catalog.families}

    assert by_page[9].charts[0].family_id == "line_chart"
    assert by_page[17].charts[0].family_id == "line_chart"
    assert by_page[32].charts[0].family_id == "stacked_contribution_chart"
    assert by_page[32].charts[1].family_id == "range_snapshot_chart"
    assert by_page[15].charts[0].family_id == "heatmap_matrix"
    assert by_page[31].charts[0].family_id == "ranked_tile_matrix"
    assert by_page[50].charts[1].family_id == "scatter_chart"
    assert by_page[54].charts[0].family_id == "bar_marker_overlay"
    assert by_page[61].charts[1].family_id == "waterfall_chart"
    assert by_page[67].charts[0].family_id == "bubble_chart"
    assert by_page[69].charts[0].family_id == "bar_marker_overlay"
    assert by_page[73].charts[0].family_id == "floating_range_bar"

    assert by_family["combo_chart"].current_support == "supported"
    assert by_family["heatmap_matrix"].preferred_render_path == "composer_shapes"
    assert by_family["ranked_tile_matrix"].preferred_render_path == "composer_table"
    assert by_family["range_snapshot_chart"].preferred_render_path == "hybrid"
    assert by_family["waterfall_chart"].current_support == "supported"


def test_raw_chart_catalog_json_validates_against_model():
    payload = json.loads(DEFAULT_JP_DEMO_CHART_CATALOG_PATH.read_text(encoding="utf-8"))
    catalog = ChartCatalog.model_validate(payload)

    sections = {page.section for page in catalog.pages}
    assert sections == {
        "Local economy",
        "Global economy",
        "Equities",
        "Fixed income",
        "Other asset classes",
        "Investing principles",
    }


def test_generated_html_atlas_exists():
    atlas_path = Path(__file__).resolve().parent.parent / "reference" / "jp-demo-chart-atlas.html"
    html = atlas_path.read_text(encoding="utf-8")

    assert "JP Demo Chart Design Framework" in html
    assert "range_snapshot_chart" in html
    assert "waterfall_chart" in html
