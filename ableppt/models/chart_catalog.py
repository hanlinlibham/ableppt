"""Chart catalog models for reference decks and chart-family coverage planning."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SectionName = Literal[
    "Local economy",
    "Global economy",
    "Equities",
    "Fixed income",
    "Other asset classes",
    "Investing principles",
]

RenderPath = Literal["chart_engine", "composer_shapes", "composer_table", "hybrid"]
SupportStatus = Literal["supported", "partial", "planned"]
PriorityLevel = Literal["high", "medium", "low"]
LayoutPattern = Literal[
    "single_panel",
    "single_panel_with_table",
    "two_panel",
    "three_panel",
    "three_panel_asymmetric",
]


class ChartFamily(BaseModel):
    """Reusable chart family definition for planning engine coverage."""

    model_config = ConfigDict(extra="forbid")

    id: str
    display_name: str
    description: str
    primitives: list[str] = Field(default_factory=list)
    preferred_render_path: RenderPath
    current_support: SupportStatus
    implementation_priority: PriorityLevel = "medium"
    editable_output: bool = True
    representative_pages: list[int] = Field(default_factory=list)
    notes: str | None = None


class PageChart(BaseModel):
    """One chart block or panel on a reference deck page."""

    model_config = ConfigDict(extra="forbid")

    panel: str
    title: str
    family_id: str
    render_path: RenderPath | None = None
    notes: str | None = None


class ReferencePage(BaseModel):
    """Per-page chart-family mapping for a reference deck."""

    model_config = ConfigDict(extra="forbid")

    page_number: int = Field(ge=1)
    section: SectionName
    title: str
    layout_pattern: LayoutPattern
    charts: list[PageChart] = Field(default_factory=list)
    non_chart_elements: list[str] = Field(default_factory=list)
    notes: str | None = None


class ChartCatalog(BaseModel):
    """Machine-readable catalog describing chart coverage for a reference deck."""

    model_config = ConfigDict(extra="forbid")

    catalog_id: str
    source_pdf: str
    source_page_count: int = Field(ge=1)
    modeling_goal: str
    families: list[ChartFamily]
    pages: list[ReferencePage]

    @model_validator(mode="after")
    def validate_catalog(self) -> "ChartCatalog":
        family_ids = {family.id for family in self.families}
        if len(family_ids) != len(self.families):
            raise ValueError("family ids must be unique")

        page_numbers = [page.page_number for page in self.pages]
        if len(set(page_numbers)) != len(page_numbers):
            raise ValueError("page numbers must be unique")
        if len(self.pages) != self.source_page_count:
            raise ValueError("pages length must equal source_page_count")

        expected_pages = set(range(1, self.source_page_count + 1))
        if set(page_numbers) != expected_pages:
            raise ValueError("pages must cover every source page exactly once")

        for family in self.families:
            missing_refs = set(family.representative_pages) - expected_pages
            if missing_refs:
                raise ValueError(
                    f"family {family.id} references missing representative pages: {sorted(missing_refs)}"
                )

        for page in self.pages:
            for chart in page.charts:
                if chart.family_id not in family_ids:
                    raise ValueError(
                        f"page {page.page_number} uses unknown family id {chart.family_id!r}"
                    )

        return self


DEFAULT_JP_DEMO_CHART_CATALOG_PATH = (
    Path(__file__).resolve().parents[2] / "reference" / "jp_demo_chart_catalog.json"
)


def load_jp_demo_chart_catalog(
    path: str | Path | None = None,
) -> ChartCatalog:
    """Load the validated jp_demo reference chart catalog."""

    catalog_path = Path(path) if path is not None else DEFAULT_JP_DEMO_CHART_CATALOG_PATH
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    return ChartCatalog.model_validate(payload)
