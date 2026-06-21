"""Low-capability-friendly normalization for semantic family specs."""

from __future__ import annotations

import pandas as pd


def normalize_semantic_spec(spec: dict, family: str | None = None) -> dict:
    normalized = dict(spec)

    # Common alias surfaces
    _move(normalized, "data", "df")
    _move(normalized, "records", "rows")
    _move(normalized, "items", "rows")
    _move(normalized, "series", "series_entries")
    _move(normalized, "left_chart_spec", "left_chart_kwargs")
    _move(normalized, "right_chart_spec", "right_chart_kwargs")
    _move(normalized, "chart_spec", "chart_kwargs")
    _move(normalized, "chart", "chart_kwargs")
    _move(normalized, "chart_family_left", "left_chart_family")
    _move(normalized, "chart_family_right", "right_chart_family")
    _move(normalized, "chart_title", "title")
    _move(normalized, "date_col", "categories_col")
    _move(normalized, "category", "categories_col")
    _move(normalized, "category_col", "categories_col")
    _move(normalized, "labels", "categories_col")
    _move(normalized, "x", "x_col")
    _move(normalized, "y", "y_col")
    _move(normalized, "size", "size_col")
    _move(normalized, "row", "row_col")
    _move(normalized, "column", "column_col")
    _move(normalized, "value", "value_col")
    _move(normalized, "table_rows", "rows", overwrite=False)
    _move(normalized, "table_headers", "headers", overwrite=False)
    _move(normalized, "periods", "row_labels", overwrite=False)
    _move(normalized, "levels", "level_labels", overwrite=False)
    _move(normalized, "section_names", "section_titles", overwrite=False)
    _move(normalized, "csv", "csv_path", overwrite=False)
    _move(normalized, "file", "csv_path", overwrite=False)

    # Family-specific conveniences
    if family in {"performance_compare", "factor_exposure"} and "series_entries" not in normalized and "metrics" in normalized:
        normalized["series_entries"] = normalized.pop("metrics")

    if family == "distribution_plus_history" and "series_columns" not in normalized and "metrics" in normalized:
        normalized["series_columns"] = normalized.pop("metrics")

    if family in {"holding_detail", "award_timeline_panel"} and "rows" in normalized and isinstance(normalized["rows"], list) and normalized["rows"] and isinstance(normalized["rows"][0], dict):
        df = pd.DataFrame(normalized["rows"])
        if "headers" not in normalized:
            normalized["headers"] = list(df.columns)
        normalized["rows"] = df[normalized["headers"]].values.tolist()

    if family not in {"holding_detail", "award_timeline_panel", "table_plus_chart_composite", "regime_table_panel", "factor_attribution_panel", "manager_timeline_profile"}:
        if "rows" in normalized and "df" not in normalized:
            normalized["df"] = pd.DataFrame(normalized.pop("rows"))

    if isinstance(normalized.get("df"), list):
        normalized["df"] = pd.DataFrame(normalized["df"])

    for nested_key in ("chart_kwargs", "left_chart_kwargs", "right_chart_kwargs"):
        if nested_key in normalized and isinstance(normalized[nested_key], dict):
            normalized[nested_key] = normalize_semantic_spec(normalized[nested_key])

    return normalized


def _move(data: dict, src: str, dst: str, *, overwrite: bool = False) -> None:
    if src not in data:
        return
    if dst in data and not overwrite:
        return
    data[dst] = data.pop(src)
