"""Render a standalone HTML atlas for the verified jp_demo chart catalog."""

from __future__ import annotations

from collections import Counter, defaultdict
from html import escape
from pathlib import Path

from ableppt import load_jp_demo_chart_catalog


OUTPUT_PATH = Path(__file__).resolve().parents[1] / "reference" / "jp-demo-chart-atlas.html"


SECTION_META = {
    "Local economy": {"accent": "#0d9dc4", "rail": "Local economy"},
    "Global economy": {"accent": "#1c8cff", "rail": "Global economy"},
    "Equities": {"accent": "#8aa42d", "rail": "Equities"},
    "Fixed income": {"accent": "#1a4f96", "rail": "Fixed income"},
    "Other asset classes": {"accent": "#f27a00", "rail": "Other asset classes"},
    "Investing principles": {"accent": "#0d5b37", "rail": "Investing principles"},
}


RENDER_PATH_COPY = {
    "chart_engine": "Native editable chart",
    "hybrid": "Chart + shape overlay",
    "composer_shapes": "Shape renderer",
    "composer_table": "Grid / tile renderer",
}


LAYOUT_COPY = {
    "single_panel": "Single-panel chart page",
    "single_panel_with_table": "Single chart with supporting table",
    "two_panel": "Two-panel comparison page",
    "three_panel": "Three-panel page",
    "three_panel_asymmetric": "Asymmetric three-panel page",
}


FAMILY_BLUEPRINTS = {
    "line_chart": {
        "layout": "One plot area, one shared time/category axis, 1-n line series, optional endpoint callout.",
        "semantics": "Show continuous trend, co-movement, divergence, or cyclical turning points.",
        "data_shape": {
            "grain": "one row per time period or ordered category",
            "required_fields": ["x", "series_1 ... series_n"],
            "optional_fields": ["event_bands", "callout_points", "target_line"],
        },
        "consumers": {
            "ablechart": [
                "editable multi-series line support",
                "date axis tick management",
                "optional secondary label callout without mutating core data",
            ],
            "ableppt composer": [
                "panel framing, source footnotes, and section rail",
                "annotation arrows and recession bands when needed",
            ],
        },
    },
    "combo_chart": {
        "layout": "Dual-axis comparison panel combining lines, bars, or areas in one plot.",
        "semantics": "Juxtapose level vs. rate, quantity vs. sentiment, or two scales that must stay visually aligned.",
        "data_shape": {
            "grain": "one row per time period or ordered category",
            "required_fields": ["x", "primary_series", "secondary_series"],
            "optional_fields": ["extra_primary_series", "extra_secondary_series", "endpoint_callouts"],
        },
        "consumers": {
            "ablechart": [
                "dual-axis editable combo core",
                "line-line and bar-line variants",
                "stable legend and axis formatting contracts",
            ],
            "ableppt composer": [
                "annotation overlays, vertical splits, and narrative subtitles",
            ],
        },
    },
    "stacked_contribution_chart": {
        "layout": "Stacked positive/negative components with a total overlay line or marker.",
        "semantics": "Explain what drove a headline result by decomposing it into additive components.",
        "data_shape": {
            "grain": "one row per time period or scenario bucket",
            "required_fields": ["x", "component_1 ... component_n"],
            "optional_fields": ["total", "baseline", "group_totals"],
        },
        "consumers": {
            "ablechart": [
                "stacked columns or areas with negative values",
                "overlay total marker/line",
                "semantic preservation of contribution ordering",
            ],
            "ableppt composer": [
                "data-label cleanup and outlier annotations",
            ],
        },
    },
    "bar_chart": {
        "layout": "Clustered or simple bars across ordered categories, sometimes arranged as small multiples.",
        "semantics": "Rank, compare, or summarize discrete categories with minimal interpretive overhead.",
        "data_shape": {
            "grain": "one row per category or one row per grouped category",
            "required_fields": ["category", "value"],
            "optional_fields": ["series", "section", "label"],
        },
        "consumers": {
            "ablechart": [
                "clustered bar/column support",
                "horizontal and vertical orientation",
                "dense category label handling",
            ],
            "ableppt composer": [
                "section captions and micro-headers when bars are grouped into blocks",
            ],
        },
    },
    "stacked_bar_chart": {
        "layout": "Vertical or horizontal segmented bars with category labels and part-of-whole encoding.",
        "semantics": "Show composition, expected add-ons, or before/after segmented states within each category.",
        "data_shape": {
            "grain": "one row per category",
            "required_fields": ["category", "segment_1 ... segment_n"],
            "optional_fields": ["group", "total", "pattern_segment"],
        },
        "consumers": {
            "ablechart": [
                "stacked orientation switch",
                "pattern/hatch handling for forecast or expected segments",
                "label placement inside narrow segments",
            ],
            "ableppt composer": [
                "auxiliary legends and explanatory callouts",
            ],
        },
    },
    "heatmap_matrix": {
        "layout": "Matrix grid with labeled rows/columns, continuous color scale, and optional side summary column.",
        "semantics": "Compress many time-series or country-state comparisons into a single comparative field.",
        "data_shape": {
            "grain": "one row per entity x period cell",
            "required_fields": ["row_key", "column_key", "value"],
            "optional_fields": ["display_value", "group_break", "summary_value"],
        },
        "consumers": {
            "ablechart": [
                "not recommended as a native Office chart primitive",
            ],
            "ableppt composer": [
                "shape/grid renderer",
                "continuous color scale mapping",
                "header and separator logic",
            ],
        },
    },
    "ranked_tile_matrix": {
        "layout": "Dense tile quilt where each period is a column and ranking determines row position.",
        "semantics": "Reveal winner/loser rotation and dispersion without relying on a Cartesian axis.",
        "data_shape": {
            "grain": "one row per period x asset tile",
            "required_fields": ["period", "asset", "value", "rank"],
            "optional_fields": ["group", "annualized_value", "volatility"],
        },
        "consumers": {
            "ablechart": [
                "not a good fit for native chart primitives",
            ],
            "ableppt composer": [
                "editable tile grid",
                "rank-aware row ordering per column",
                "cell background + text contrast logic",
            ],
        },
    },
    "scatter_chart": {
        "layout": "XY scatter with dense markers and optional reference line, crosshair, or current-point highlight.",
        "semantics": "Describe relationships, valuation vs. forward return, or risk-vs-reward tradeoffs.",
        "data_shape": {
            "grain": "one row per observation",
            "required_fields": ["x", "y"],
            "optional_fields": ["series", "is_current", "label", "reference_x", "reference_y"],
        },
        "consumers": {
            "ablechart": [
                "pure XY chart family",
                "current-point highlight rules",
                "reference-line safe extension path",
            ],
            "ableppt composer": [
                "narrative callouts and guide-line overlays",
            ],
        },
    },
    "bubble_chart": {
        "layout": "Scatter layout with bubble size as the third channel and a size explainer inset.",
        "semantics": "Map correlation, return, and size/yield in a single field without collapsing any dimension.",
        "data_shape": {
            "grain": "one row per observation",
            "required_fields": ["x", "y", "size", "label"],
            "optional_fields": ["group", "color_family", "legend_benchmark"],
        },
        "consumers": {
            "ablechart": [
                "editable bubble primitives",
                "bubble-size normalization contract",
                "stable label anchor handling",
            ],
            "ableppt composer": [
                "bubble-size explainer inset",
                "manual label positioning where native labels collide",
            ],
        },
    },
    "bar_marker_overlay": {
        "layout": "Bars as the main body plus markers for revisions, maxima, or alternate outcomes.",
        "semantics": "Compare a headline bar value against a prior estimate, drawdown, or reference benchmark.",
        "data_shape": {
            "grain": "one row per category or year",
            "required_fields": ["category", "bar_value"],
            "optional_fields": ["marker_value", "second_bar_value", "section", "footer_metric"],
        },
        "consumers": {
            "ablechart": [
                "bar primitives plus marker-only overlay",
                "negative-value stability",
                "label formatting for bars and markers separately",
            ],
            "ableppt composer": [
                "footer tables, section dividers, and explicit marker callouts",
            ],
        },
    },
    "range_snapshot_chart": {
        "layout": "Historical range bar, long-run average tick, and current marker; supports vertical and horizontal variants.",
        "semantics": "Answer 'where are we versus history?' without plotting a full time series.",
        "data_shape": {
            "grain": "one row per sector or market bucket",
            "required_fields": ["category", "range_min", "range_max", "average", "current"],
            "optional_fields": ["axis_break", "sort_order", "orientation"],
        },
        "consumers": {
            "ablechart": [
                "first-class range snapshot family",
                "average tick and current marker support",
                "axis-break safe rendering",
            ],
            "ableppt composer": [
                "orientation-aware labels and explanatory legends",
            ],
        },
    },
    "floating_range_bar": {
        "layout": "Floating min/max interval bars around a zero baseline, sometimes grouped by rolling horizon.",
        "semantics": "Communicate dispersion and downside/upside range rather than a single central estimate.",
        "data_shape": {
            "grain": "one row per horizon or category",
            "required_fields": ["category", "range_min", "range_max"],
            "optional_fields": ["series", "baseline", "median"],
        },
        "consumers": {
            "ablechart": [
                "hidden base series plus visible interval bar",
                "positive/negative crossover handling",
            ],
            "ableppt composer": [
                "group headers and simplified legends",
            ],
        },
    },
    "waterfall_chart": {
        "layout": "Ordered bridge from base value through relative contributions to a final total.",
        "semantics": "Explain stepwise build-up from component contributions to an aggregate total.",
        "data_shape": {
            "grain": "one row per bridge step",
            "required_fields": ["step", "value", "measure"],
            "optional_fields": ["step_group", "display_label"],
        },
        "consumers": {
            "ablechart": [
                "semantic waterfall/bridge path",
                "total-category handling",
                "connector visibility and label control",
            ],
            "ableppt composer": [
                "surrounding narrative and source framing",
            ],
        },
    },
}


REVALIDATION_NOTES = [
    "Reclassified valuation panels into a dedicated `range_snapshot_chart` family instead of generic bars.",
    "Promoted `Contribution to global oil production` to `waterfall_chart` after visual verification of bridge semantics.",
    "Corrected several title-based false positives, such as `Exports by type` and `U.S. goods imports by market`, which are multi-line charts rather than stacked compositions.",
    "Split `bar_marker_overlay` from plain bar charts for earnings-revision panels, annual return vs. drawdown charts, and max-yield comparison pages.",
]


def list_to_html(items: list[str]) -> str:
    return "".join(f"<li>{escape(item)}</li>" for item in items)


def render_family_blueprint(family, page_count: int) -> str:
    blueprint = FAMILY_BLUEPRINTS[family.id]
    data_shape = blueprint["data_shape"]
    consumer_blocks = []
    for consumer, needs in blueprint["consumers"].items():
        consumer_blocks.append(
            f"""
            <div class="consumer-block">
              <div class="consumer-name">{escape(consumer)}</div>
              <ul>{list_to_html(needs)}</ul>
            </div>
            """
        )
    return f"""
    <article class="family-card" data-family="{escape(family.id)}">
      <div class="family-head">
        <div>
          <div class="eyebrow">Family</div>
          <h3>{escape(family.display_name)}</h3>
        </div>
        <div class="status-pills">
          <span class="pill support-{escape(family.current_support)}">{escape(family.current_support)}</span>
          <span class="pill path-pill">{escape(RENDER_PATH_COPY[family.preferred_render_path])}</span>
          <span class="pill page-pill">{page_count} pages</span>
        </div>
      </div>
      <p class="family-description">{escape(family.description)}</p>
      <div class="blueprint-grid">
        <section>
          <div class="block-title">Layout</div>
          <p>{escape(blueprint['layout'])}</p>
        </section>
        <section>
          <div class="block-title">Semantic Contract</div>
          <p>{escape(blueprint['semantics'])}</p>
        </section>
        <section>
          <div class="block-title">Data Shape</div>
          <p><strong>Grain:</strong> {escape(data_shape['grain'])}</p>
          <p><strong>Required:</strong> {escape(', '.join(data_shape['required_fields']))}</p>
          <p><strong>Optional:</strong> {escape(', '.join(data_shape['optional_fields']))}</p>
        </section>
        <section>
          <div class="block-title">Consumers</div>
          <div class="consumer-grid">
            {''.join(consumer_blocks)}
          </div>
        </section>
      </div>
      <div class="family-foot">
        <span>Representative pages: {', '.join(str(p) for p in family.representative_pages)}</span>
        <span>Priority: {escape(family.implementation_priority)}</span>
      </div>
    </article>
    """


def render_chart_block(chart, page, section_meta) -> str:
    blueprint = FAMILY_BLUEPRINTS[chart.family_id]
    data_shape = blueprint["data_shape"]
    consumer_summary = "; ".join(
        f"{consumer}: {', '.join(needs[:2])}"
        for consumer, needs in blueprint["consumers"].items()
    )
    notes = f"<p class='chart-notes'>{escape(chart.notes)}</p>" if chart.notes else ""
    return f"""
    <div class="chart-block" data-family="{escape(chart.family_id)}" data-path="{escape(chart.render_path or '')}">
      <div class="chart-meta">
        <span class="panel-tag">{escape(chart.panel.replace('_', ' '))}</span>
        <span class="family-tag">{escape(chart.family_id)}</span>
      </div>
      <h4>{escape(chart.title)}</h4>
      <p><strong>Layout:</strong> {escape(LAYOUT_COPY[page.layout_pattern])}; panel role = {escape(chart.panel.replace('_', ' '))}</p>
      <p><strong>Content:</strong> {escape(chart.title)} on page {page.page_number} under {escape(page.title)}</p>
      <p><strong>Semantics:</strong> {escape(blueprint['semantics'])}</p>
      <p><strong>Data contract:</strong> grain = {escape(data_shape['grain'])}; required = {escape(', '.join(data_shape['required_fields']))}</p>
      <p><strong>Consumer needs:</strong> {escape(consumer_summary)}</p>
      {notes}
    </div>
    """


def render_page_card(page) -> str:
    section_meta = SECTION_META[page.section]
    chart_blocks = "".join(render_chart_block(chart, page, section_meta) for chart in page.charts)
    extras = ""
    if page.non_chart_elements:
        extras = (
            "<div class='page-extras'><strong>Non-chart elements:</strong> "
            + escape(", ".join(page.non_chart_elements))
            + "</div>"
        )
    return f"""
    <article class="page-card" data-section="{escape(page.section)}">
      <div class="page-rail" style="background:{section_meta['accent']}">{escape(section_meta['rail'])}</div>
      <div class="page-shell">
        <div class="page-header">
          <div>
            <div class="page-number">Page {page.page_number}</div>
            <h3>{escape(page.title)}</h3>
          </div>
          <div class="page-badges">
            <span class="pill">{escape(page.section)}</span>
            <span class="pill">{escape(LAYOUT_COPY[page.layout_pattern])}</span>
          </div>
        </div>
        <div class="chart-stack">{chart_blocks}</div>
        {extras}
      </div>
    </article>
    """


def build_html() -> str:
    catalog = load_jp_demo_chart_catalog()
    family_usage = Counter()
    for page in catalog.pages:
        for chart in page.charts:
            family_usage[chart.family_id] += 1

    sections = defaultdict(list)
    for page in catalog.pages:
        sections[page.section].append(page)

    family_cards = "".join(
        render_family_blueprint(family, family_usage[family.id]) for family in catalog.families
    )

    page_sections = []
    for section, pages in sections.items():
        accent = SECTION_META[section]["accent"]
        cards = "".join(render_page_card(page) for page in pages)
        page_sections.append(
            f"""
            <section class="section-block">
              <div class="section-head">
                <div class="section-kicker" style="color:{accent}">{escape(section)}</div>
                <h2>{escape(section)}</h2>
                <p>{len(pages)} pages</p>
              </div>
              <div class="page-grid">{cards}</div>
            </section>
            """
        )

    filter_buttons = "".join(
        f'<button class="filter-button" data-family="{escape(family.id)}">{escape(family.display_name)}</button>'
        for family in catalog.families
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>JP Demo Chart Atlas</title>
  <style>
    :root {{
      --paper: #f3efe6;
      --ink: #141414;
      --muted: #5f635d;
      --line: rgba(20, 20, 20, 0.12);
      --card: rgba(255, 255, 255, 0.82);
      --shadow: 0 18px 60px rgba(20, 20, 20, 0.08);
      --accent: #0b7c6d;
    }}

    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(11, 124, 109, 0.12), transparent 32%),
        radial-gradient(circle at top right, rgba(28, 140, 255, 0.10), transparent 28%),
        linear-gradient(180deg, #f9f6f0 0%, var(--paper) 46%, #f0eadf 100%);
      font-family: "Avenir Next", "Helvetica Neue", "Segoe UI", sans-serif;
    }}

    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(rgba(20, 20, 20, 0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(20, 20, 20, 0.035) 1px, transparent 1px);
      background-size: 32px 32px;
      opacity: 0.25;
    }}

    .shell {{
      position: relative;
      width: min(1500px, calc(100% - 48px));
      margin: 0 auto;
      padding: 28px 0 72px;
    }}

    .hero {{
      display: grid;
      grid-template-columns: 1.4fr 0.8fr;
      gap: 28px;
      align-items: end;
      padding: 42px 0 24px;
      border-bottom: 1px solid var(--line);
    }}

    .eyebrow {{
      font-size: 11px;
      letter-spacing: 0.24em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 10px;
    }}

    .hero h1, .hero h2, .section-head h2, .page-header h3, .family-card h3 {{
      font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Georgia, serif;
      font-weight: 700;
      letter-spacing: -0.04em;
      margin: 0;
    }}

    .hero h1 {{
      font-size: clamp(3rem, 6vw, 5.8rem);
      line-height: 0.95;
      max-width: 9ch;
    }}

    .hero-copy p {{
      font-size: 1.1rem;
      line-height: 1.7;
      max-width: 60ch;
      color: #232421;
    }}

    .hero-panel {{
      background: rgba(255,255,255,0.7);
      border: 1px solid var(--line);
      box-shadow: var(--shadow);
      padding: 18px 20px 20px;
      border-radius: 24px;
      backdrop-filter: blur(12px);
    }}

    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      margin-top: 16px;
    }}

    .metric {{
      padding: 14px 16px;
      border-radius: 18px;
      background: rgba(243, 239, 230, 0.9);
      border: 1px solid rgba(20,20,20,0.08);
    }}

    .metric strong {{
      display: block;
      font-size: 1.8rem;
      letter-spacing: -0.05em;
    }}

    .metric span {{
      color: var(--muted);
      font-size: 0.92rem;
    }}

    .notes-strip {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 26px 0 10px;
    }}

    .note-card {{
      background: rgba(255,255,255,0.66);
      border: 1px solid var(--line);
      padding: 14px 16px;
      border-radius: 18px;
      min-height: 128px;
    }}

    .note-card strong {{
      display: block;
      margin-bottom: 8px;
      font-size: 0.95rem;
    }}

    .sticky-filter {{
      position: sticky;
      top: 0;
      z-index: 20;
      margin: 34px 0 26px;
      padding: 18px;
      border-radius: 22px;
      border: 1px solid var(--line);
      background: rgba(249, 246, 240, 0.88);
      backdrop-filter: blur(14px);
      box-shadow: var(--shadow);
    }}

    .filter-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 12px;
    }}

    .filter-button, .clear-button {{
      border: 1px solid rgba(20,20,20,0.15);
      background: rgba(255,255,255,0.78);
      color: var(--ink);
      padding: 10px 14px;
      border-radius: 999px;
      cursor: pointer;
      font: inherit;
      transition: transform 180ms ease, background 180ms ease, border-color 180ms ease;
    }}

    .filter-button:hover, .clear-button:hover {{
      transform: translateY(-1px);
      background: white;
    }}

    .filter-button.active {{
      background: var(--ink);
      color: white;
      border-color: var(--ink);
    }}

    .section-block {{
      margin-top: 54px;
    }}

    .section-head {{
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 16px;
      border-bottom: 1px solid var(--line);
      padding-bottom: 14px;
      margin-bottom: 20px;
    }}

    .section-kicker {{
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.22em;
      margin-bottom: 6px;
    }}

    .section-head h2 {{
      font-size: 2.1rem;
    }}

    .family-grid, .page-grid {{
      display: grid;
      gap: 18px;
    }}

    .family-grid {{
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}

    .page-grid {{
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}

    .family-card, .page-card {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 28px;
      box-shadow: var(--shadow);
      overflow: hidden;
      backdrop-filter: blur(8px);
    }}

    .family-card {{
      padding: 20px 22px 18px;
    }}

    .family-head, .page-header {{
      display: flex;
      justify-content: space-between;
      gap: 14px;
      align-items: start;
    }}

    .family-head h3 {{
      font-size: 1.7rem;
      line-height: 1;
    }}

    .status-pills, .page-badges {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: flex-end;
    }}

    .pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 7px 10px;
      border-radius: 999px;
      background: rgba(20,20,20,0.06);
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}

    .support-supported {{ background: rgba(11, 124, 109, 0.14); }}
    .support-partial {{ background: rgba(242, 122, 0, 0.16); }}
    .support-planned {{ background: rgba(28, 140, 255, 0.16); }}

    .family-description {{
      margin: 14px 0 18px;
      color: #272925;
      line-height: 1.65;
    }}

    .blueprint-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }}

    .blueprint-grid section {{
      padding: 14px 14px 12px;
      border-radius: 18px;
      background: rgba(243, 239, 230, 0.9);
      border: 1px solid rgba(20,20,20,0.08);
    }}

    .block-title {{
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.18em;
      color: var(--muted);
      margin-bottom: 8px;
    }}

    .blueprint-grid p {{
      margin: 0 0 8px;
      line-height: 1.55;
    }}

    .consumer-grid {{
      display: grid;
      gap: 10px;
    }}

    .consumer-block ul {{
      margin: 8px 0 0 18px;
      padding: 0;
    }}

    .consumer-name {{
      font-weight: 700;
    }}

    .family-foot {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding-top: 14px;
      margin-top: 14px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 0.92rem;
    }}

    .page-card {{
      display: grid;
      grid-template-columns: 84px 1fr;
      min-height: 280px;
    }}

    .page-rail {{
      writing-mode: vertical-rl;
      transform: rotate(180deg);
      color: white;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 14px 0;
    }}

    .page-shell {{
      padding: 18px 18px 18px 20px;
    }}

    .page-number {{
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.18em;
      color: var(--muted);
      margin-bottom: 4px;
    }}

    .page-header h3 {{
      font-size: 1.5rem;
    }}

    .chart-stack {{
      display: grid;
      gap: 14px;
      margin-top: 16px;
    }}

    .chart-block {{
      border-radius: 18px;
      border: 1px solid rgba(20,20,20,0.08);
      background: rgba(255,255,255,0.72);
      padding: 14px 16px;
    }}

    .chart-block h4 {{
      margin: 8px 0 10px;
      font-size: 1.06rem;
    }}

    .chart-block p {{
      margin: 0 0 8px;
      line-height: 1.52;
      color: #252723;
    }}

    .chart-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}

    .panel-tag, .family-tag {{
      display: inline-flex;
      align-items: center;
      padding: 5px 8px;
      border-radius: 999px;
      background: rgba(20,20,20,0.06);
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }}

    .chart-notes {{
      padding-top: 6px;
      border-top: 1px dashed rgba(20,20,20,0.12);
      color: var(--muted);
    }}

    .page-extras {{
      margin-top: 12px;
      padding-top: 12px;
      border-top: 1px solid var(--line);
      color: var(--muted);
    }}

    .hidden {{
      display: none !important;
    }}

    @media (max-width: 1120px) {{
      .hero, .family-grid, .page-grid, .notes-strip {{
        grid-template-columns: 1fr;
      }}
    }}

    @media (max-width: 820px) {{
      .shell {{
        width: min(100% - 28px, 980px);
      }}
      .page-card {{
        grid-template-columns: 1fr;
      }}
      .page-rail {{
        writing-mode: horizontal-tb;
        transform: none;
        min-height: 54px;
      }}
      .blueprint-grid {{
        grid-template-columns: 1fr;
      }}
      .hero h1 {{
        max-width: 100%;
      }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <div class="hero-copy">
        <div class="eyebrow">Verified Chart Atlas</div>
        <h1>JP Demo Chart Design Framework</h1>
        <p>This atlas is the logic-checked bridge between <code>jp_demo.pdf</code> and implementation work. It treats the deck as a system of reusable chart families, not as 74 disconnected screenshots. Each page is mapped to a verified family, and each family is annotated with layout logic, semantic intent, data contract, and consumer needs for <code>ablechart</code> and <code>ableppt</code>.</p>
      </div>
      <aside class="hero-panel">
        <div class="eyebrow">Catalog Metrics</div>
        <div class="metric-grid">
          <div class="metric"><strong>{catalog.source_page_count}</strong><span>verified pages</span></div>
          <div class="metric"><strong>{len(catalog.families)}</strong><span>chart families</span></div>
          <div class="metric"><strong>{sum(len(page.charts) for page in catalog.pages)}</strong><span>chart panels</span></div>
          <div class="metric"><strong>4</strong><span>render paths</span></div>
        </div>
      </aside>
    </section>

    <section class="notes-strip">
      {''.join(f"<div class='note-card'><strong>Logic check {i}</strong><p>{escape(note)}</p></div>" for i, note in enumerate(REVALIDATION_NOTES, 1))}
    </section>

    <section class="sticky-filter">
      <div class="eyebrow">Filter Atlas</div>
      <div>Use the family filters to isolate the page patterns that matter before implementing or refactoring a chart family.</div>
      <div class="filter-row">
        <button class="clear-button active" data-family="all">Show all families</button>
        {filter_buttons}
      </div>
    </section>

    <section class="section-block">
      <div class="section-head">
        <div>
          <div class="section-kicker">Blueprint Layer</div>
          <h2>Family System</h2>
        </div>
        <p>{len(catalog.families)} reusable families</p>
      </div>
      <div class="family-grid">
        {family_cards}
      </div>
    </section>

    {''.join(page_sections)}
  </div>

  <script>
    const filterButtons = Array.from(document.querySelectorAll('.filter-button'));
    const clearButton = document.querySelector('.clear-button');
    const pageCards = Array.from(document.querySelectorAll('.page-card'));
    const familyCards = Array.from(document.querySelectorAll('.family-card'));

    function setActive(button) {{
      [clearButton, ...filterButtons].forEach((btn) => btn.classList.remove('active'));
      button.classList.add('active');
    }}

    function applyFilter(familyId) {{
      familyCards.forEach((card) => {{
        card.classList.toggle('hidden', familyId !== 'all' && card.dataset.family !== familyId);
      }});

      pageCards.forEach((page) => {{
        const blocks = Array.from(page.querySelectorAll('.chart-block'));
        let visibleCount = 0;
        blocks.forEach((block) => {{
          const visible = familyId === 'all' || block.dataset.family === familyId;
          block.classList.toggle('hidden', !visible);
          if (visible) visibleCount += 1;
        }});
        page.classList.toggle('hidden', visibleCount === 0);
      }});
    }}

    clearButton.addEventListener('click', () => {{
      setActive(clearButton);
      applyFilter('all');
    }});

    filterButtons.forEach((button) => {{
      button.addEventListener('click', () => {{
        setActive(button);
        applyFilter(button.dataset.family);
      }});
    }});
  </script>
</body>
</html>
"""


def main() -> None:
    OUTPUT_PATH.write_text(build_html(), encoding="utf-8")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
