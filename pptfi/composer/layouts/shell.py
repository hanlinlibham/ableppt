"""Page shell layouts for research-booklet and dashboard-style decks."""

from __future__ import annotations

from ..helpers import add_rect, add_text, set_slide_bg
from ...utils.semantic_normalize import normalize_semantic_spec


def _t(theme: dict, key: str, default):
    return theme.get(key, default)


def _normalize_family_spec(spec: dict) -> tuple[str, dict]:
    family = spec["family"]
    kwargs = {k: v for k, v in spec.items() if k not in {"family", "area"}}
    return family, normalize_semantic_spec(kwargs, family)


def _render_family(slide, spec: dict, default_area: tuple[float, float, float, float]):
    from pptfi import chart_builder

    family, kwargs = _normalize_family_spec(spec)
    area = spec.get("area", default_area)
    x, y, w, h = area
    kwargs["position"] = (x, y)
    kwargs["size"] = (w, h)
    chart_builder.create_semantic_chart(slide=slide, family=family, **kwargs)


def _add_custom_footer(slide, theme, *, left_text: str = "", right_text: str = ""):
    sw = _t(theme, "slide_w", 13.333)
    footer_y = _t(theme, "footer_y", 7.10)
    margin = _t(theme, "margin", 0.6)
    line_gap = _t(theme, "shell_footer_line_gap", 0.08)
    line_h = _t(theme, "shell_footer_line_h", 0.005)
    add_rect(slide, margin, footer_y - line_gap, sw - 2 * margin, line_h, fill=theme["border"])
    if left_text:
        add_text(
            slide,
            left_text,
            x=margin,
            y=footer_y,
            w=(sw - 2 * margin) * 0.7,
            h=0.18,
            font_size=theme.get("footer_size", 8),
            color=theme["text_muted"],
            font_name=theme["body_font"],
            align="left",
        )
    if right_text:
        add_text(
            slide,
            right_text,
            x=sw * 0.55,
            y=footer_y,
            w=sw * 0.35,
            h=0.18,
            font_size=theme.get("footer_size", 8),
            color=theme["text_muted"],
            font_name=theme["body_font"],
            align="right",
        )


def layout_research_shell_4_3(slide, data, theme):
    """4:3 research booklet shell inspired by institutional market booklets."""

    sw = _t(theme, "slide_w", 10.0)
    sh = _t(theme, "slide_h", 7.5)
    left_rule_x = _t(theme, "shell_left_rule_x", 0.85)
    left_rule_w = _t(theme, "shell_left_rule_w", 0.008)
    inner_left_x = _t(theme, "shell_inner_left_x", 1.10)
    top_rule_y = _t(theme, "research_shell_rule_y", 1.05)
    top_rule_right_margin = _t(theme, "research_shell_rule_right_margin", 1.55)
    kicker_y = _t(theme, "research_shell_kicker_y", 0.56)
    title_y = _t(theme, "research_shell_title_y", 1.20)
    title_w = _t(theme, "research_shell_title_w", 3.4)
    title_h = _t(theme, "research_shell_title_h", 1.15)
    as_of_y = _t(theme, "research_shell_as_of_y", 6.20)
    body_top = _t(theme, "research_shell_body_top", 1.45)
    body_h = _t(theme, "research_shell_body_h", 4.45)

    set_slide_bg(slide, theme["bg_light"])

    # Left rule and top section line
    add_rect(slide, left_rule_x, 0.0, left_rule_w, sh, fill=theme["text_dark"])
    add_rect(slide, inner_left_x, top_rule_y, sw - top_rule_right_margin, left_rule_w, fill=theme["text_dark"])

    if data.get("kicker"):
        add_text(
            slide,
            data["kicker"],
            x=inner_left_x,
            y=kicker_y,
            w=2.0,
            h=0.24,
            font_size=11,
            color=theme["text_dark"],
            font_name=theme["header_font"],
            align="left",
            bold=True,
        )

    add_text(
        slide,
        data["title"],
        x=inner_left_x,
        y=title_y,
        w=title_w,
        h=title_h,
        font_size=_t(theme, "cover_title_size", 34),
        color=theme["text_dark"],
        font_name=theme["header_font"],
        align="left",
        bold=True,
    )

    if data.get("as_of"):
        add_text(
            slide,
            data["as_of"],
            x=inner_left_x,
            y=as_of_y,
            w=3.3,
            h=0.35,
            font_size=12,
            color=theme["text_dark"],
            font_name=theme["body_font"],
            align="left",
            bold=False,
        )

    body = data.get("body")
    if body:
        _render_family(slide, body, (inner_left_x, body_top, sw - top_rule_right_margin, body_h))

    footer_left = data.get("source", "")
    footer_right_parts = [part for part in [data.get("region"), data.get("section"), data.get("page_label")] if part]
    _add_custom_footer(slide, theme, left_text=footer_left, right_text="  ".join(footer_right_parts))


def layout_dashboard_shell_16_9(slide, data, theme):
    """16:9 dashboard shell for family-based analysis pages."""

    sw = _t(theme, "slide_w", 13.333)
    margin = _t(theme, "margin", 0.6)
    title_y = _t(theme, "shell_title_y", 0.26)
    rule_y = _t(theme, "shell_rule_y", 0.78)
    rule_h = _t(theme, "shell_rule_h", 0.015)
    kpi_top = _t(theme, "dashboard_shell_kpi_top", 0.96)
    kpi_card_h = _t(theme, "dashboard_shell_kpi_h", 0.86)
    kpi_gap = _t(theme, "dashboard_shell_kpi_gap", 0.12)
    kpi_bottom_gap = _t(theme, "dashboard_shell_kpi_bottom_gap", 0.16)
    insight_h = _t(theme, "dashboard_shell_insight_h", 0.34)
    insight_gap = _t(theme, "dashboard_shell_insight_gap", 0.42)
    body_h = _t(theme, "dashboard_shell_body_h", 5.65)
    secondary_y = _t(theme, "dashboard_shell_secondary_y", 5.55)
    secondary_h = _t(theme, "dashboard_shell_secondary_h", 1.20)
    set_slide_bg(slide, theme["bg_light"])

    add_text(
        slide,
        data["title"],
        x=margin,
        y=title_y,
        w=sw - 2 * margin,
        h=0.34,
        font_size=_t(theme, "page_title_size", 16),
        color=theme["text_dark"],
        font_name=theme["header_font"],
        align="left",
        bold=True,
    )
    add_rect(slide, margin, rule_y, sw - 2 * margin, rule_h, fill=theme["primary"])

    current_y = kpi_top
    if data.get("insight"):
        add_text(
            slide,
            data["insight"],
            x=margin,
            y=current_y,
            w=sw - 2 * margin,
            h=insight_h,
            font_size=_t(theme, "body_size", 12),
            color=theme["text_muted"],
            font_name=theme["body_font"],
            align="left",
        )
        current_y += insight_gap

    if data.get("body"):
        _render_family(slide, data["body"], (margin, current_y, sw - 2 * margin, body_h))

    for panel in data.get("panels", []):
        _render_family(slide, panel, panel["area"])

    _add_custom_footer(
        slide,
        theme,
        left_text=data.get("source", ""),
        right_text="  ".join(part for part in [data.get("section"), data.get("page_label")] if part),
    )


def layout_factsheet_shell_4_3(slide, data, theme):
    """4:3 factsheet shell with top summary strip and one main analysis block."""

    sw = _t(theme, "slide_w", 10.0)
    sh = _t(theme, "slide_h", 7.5)
    left_rule_x = _t(theme, "shell_left_rule_x", 0.72)
    left_rule_w = _t(theme, "shell_left_rule_w", 0.008)
    inner_left_x = _t(theme, "shell_inner_left_x", 1.00)
    rule_y = _t(theme, "factsheet_shell_rule_y", 0.96)
    right_margin = _t(theme, "factsheet_shell_right_margin", 1.35)
    title_y = _t(theme, "factsheet_shell_title_y", 0.42)
    title_h = _t(theme, "factsheet_shell_title_h", 0.42)
    title_w = _t(theme, "factsheet_shell_title_w", 4.6)
    summary_y = _t(theme, "factsheet_shell_summary_y", 1.12)
    summary_h = _t(theme, "factsheet_shell_summary_h", 0.82)
    summary_gap = _t(theme, "factsheet_shell_summary_gap", 0.10)
    summary_max_card_w = _t(theme, "factsheet_shell_summary_max_card_w", 2.0)
    body_top = _t(theme, "factsheet_shell_body_top", 2.18)
    body_title_gap = _t(theme, "factsheet_shell_body_title_gap", 0.24)
    body_h = _t(theme, "factsheet_shell_body_h", 4.55)
    set_slide_bg(slide, theme["bg_light"])

    # Left guide and title rule
    add_rect(slide, left_rule_x, 0.0, left_rule_w, sh, fill=theme["text_dark"])
    add_rect(slide, inner_left_x, rule_y, sw - right_margin, left_rule_w, fill=theme["text_dark"])

    add_text(
        slide,
        data["title"],
        x=inner_left_x,
        y=title_y,
        w=title_w,
        h=title_h,
        font_size=_t(theme, "page_title_size", 16) + 2,
        color=theme["text_dark"],
        font_name=theme["header_font"],
        align="left",
        bold=True,
    )

    summary = data.get("summary_cards", [])
    if summary:
        card_y = summary_y
        card_h = summary_h
        gap = summary_gap
        card_w = min((sw - right_margin - gap * (len(summary) - 1)) / len(summary), summary_max_card_w)
        for idx, item in enumerate(summary):
            x = inner_left_x + idx * (card_w + gap)
            add_rect(slide, x, card_y, card_w, card_h, fill=item.get("fill", theme["card_bg"]), line_color=theme["border"], line_width=0.5)
            add_text(
                slide,
                item["label"],
                x=x + 0.08,
                y=card_y + 0.10,
                w=card_w - 0.16,
                h=0.18,
                font_size=8,
                color=item.get("label_color", theme["text_muted"]),
                font_name=theme["body_font"],
                align="left",
            )
            add_text(
                slide,
                item["value"],
                x=x + 0.08,
                y=card_y + 0.34,
                w=card_w - 0.16,
                h=0.24,
                font_size=item.get("value_size", 13),
                color=item.get("value_color", theme["text_dark"]),
                font_name=theme["header_font"],
                align="left",
                bold=True,
            )

    if data.get("body_title"):
        add_text(
            slide,
            data["body_title"],
            x=inner_left_x,
            y=body_top - body_title_gap,
            w=sw - (right_margin + 0.10),
            h=0.18,
            font_size=10,
            color=theme["text_muted"],
            font_name=theme["body_font"],
            align="left",
        )

    if data.get("body"):
        _render_family(slide, data["body"], (inner_left_x, body_top, sw - (right_margin + 0.10), body_h))

    _add_custom_footer(
        slide,
        theme,
        left_text=data.get("source", ""),
        right_text="  ".join(part for part in [data.get("region"), data.get("page_label")] if part),
    )


def layout_summary_shell_16_9(slide, data, theme):
    """16:9 summary shell with KPI strip plus main and secondary panels."""

    sw = _t(theme, "slide_w", 13.333)
    margin = _t(theme, "margin", 0.6)
    title_y = _t(theme, "summary_shell_title_y", 0.24)
    rule_y = _t(theme, "summary_shell_rule_y", 0.76)
    rule_h = _t(theme, "summary_shell_rule_h", 0.015)
    kpi_top = _t(theme, "summary_shell_kpi_top", 0.96)
    kpi_gap = _t(theme, "summary_shell_kpi_gap", 0.12)
    kpi_h = _t(theme, "summary_shell_kpi_h", 0.86)
    kpi_bottom_gap = _t(theme, "summary_shell_kpi_bottom_gap", 0.16)
    insight_gap = _t(theme, "summary_shell_insight_gap", 0.36)
    main_h = _t(theme, "summary_shell_main_h", 3.10)
    secondary_y = _t(theme, "summary_shell_secondary_y", 5.55)
    secondary_h = _t(theme, "summary_shell_secondary_h", 1.20)
    set_slide_bg(slide, theme["bg_light"])

    add_text(
        slide,
        data["title"],
        x=margin,
        y=title_y,
        w=sw - 2 * margin,
        h=0.34,
        font_size=_t(theme, "page_title_size", 16),
        color=theme["text_dark"],
        font_name=theme["header_font"],
        align="left",
        bold=True,
    )
    add_rect(slide, margin, rule_y, sw - 2 * margin, rule_h, fill=theme["primary"])

    kpis = data.get("kpis", [])
    current_y = kpi_top
    if kpis:
        gap = kpi_gap
        card_h = kpi_h
        card_w = (sw - 2 * margin - gap * (len(kpis) - 1)) / max(len(kpis), 1)
        for idx, item in enumerate(kpis):
            x = margin + idx * (card_w + gap)
            add_rect(slide, x, current_y, card_w, card_h, fill=item.get("fill", "FFFFFF"), line_color=theme["border"], line_width=0.5)
            add_text(slide, item["label"], x=x + 0.10, y=current_y + 0.10, w=card_w - 0.2, h=0.18,
                     font_size=8, color=item.get("label_color", theme["text_muted"]), font_name=theme["body_font"], align="left")
            add_text(slide, item["value"], x=x + 0.10, y=current_y + 0.34, w=card_w - 0.2, h=0.24,
                     font_size=item.get("value_size", 14), color=item.get("value_color", theme["text_dark"]), font_name=theme["header_font"], align="left", bold=True)
            if item.get("change"):
                add_text(slide, item["change"], x=x + 0.10, y=current_y + 0.62, w=card_w - 0.2, h=0.16,
                         font_size=8, color=item.get("change_color", theme["text_muted"]), font_name=theme["body_font"], align="left")
        current_y += card_h + kpi_bottom_gap

    if data.get("insight"):
        add_text(slide, data["insight"], x=margin, y=current_y, w=sw - 2 * margin, h=0.28,
                 font_size=theme.get("body_size", 12), color=theme["text_muted"], font_name=theme["body_font"], align="left")
        current_y += insight_gap

    if data.get("main"):
        _render_family(slide, data["main"], (margin, current_y, sw - 2 * margin, main_h))

    if data.get("secondary"):
        _render_family(slide, data["secondary"], (margin, secondary_y, sw - 2 * margin, secondary_h))

    _add_custom_footer(
        slide,
        theme,
        left_text=data.get("source", ""),
        right_text="  ".join(part for part in [data.get("section"), data.get("page_label")] if part),
    )


def layout_section_cover_4_3(slide, data, theme):
    """4:3 section cover inspired by research booklet dividers."""

    sw = theme.get("slide_w", 10.0)
    sh = theme.get("slide_h", 7.5)
    set_slide_bg(slide, theme["bg_light"])

    add_rect(slide, 0.72, 0.0, 0.008, sh, fill=theme["text_dark"])
    add_rect(slide, 0.18, 0.62, 0.28, 0.10, fill=theme["secondary"])
    add_text(
        slide,
        data.get("kicker", data.get("section", "")),
        x=1.00,
        y=0.54,
        w=3.0,
        h=0.22,
        font_size=11,
        color=theme["text_dark"],
        font_name=theme["header_font"],
        bold=True,
        align="left",
    )
    add_rect(slide, 1.00, 1.06, sw - 1.35, 0.008, fill=theme["text_dark"])
    add_text(
        slide,
        data["title"],
        x=1.00,
        y=2.35,
        w=4.1,
        h=2.2,
        font_size=theme.get("cover_title_size", 36),
        color=theme["text_dark"],
        font_name=theme["header_font"],
        bold=True,
        align="left",
    )
    if data.get("subtitle"):
        add_text(
            slide,
            data["subtitle"],
            x=1.00,
            y=5.60,
            w=3.6,
            h=0.46,
            font_size=16,
            color=theme["text_dark"],
            font_name=theme["body_font"],
            align="left",
        )
    if data.get("date"):
        add_text(
            slide,
            data["date"],
            x=1.00,
            y=6.42,
            w=3.6,
            h=0.24,
            font_size=10,
            color=theme["text_muted"],
            font_name=theme["body_font"],
            align="left",
        )
    # simple geometric motif on the right
    add_rect(slide, 6.7, 1.7, 2.3, 2.3, fill=theme["secondary"])
    add_rect(slide, 7.25, 3.55, 2.3, 2.3, fill=theme["primary"])
    add_rect(slide, 7.55, 2.45, 1.8, 1.8, fill=theme["bg_light"])


def layout_chapter_divider_16_9(slide, data, theme):
    """16:9 chapter divider with strong banding and chapter metadata."""

    sw = theme.get("slide_w", 13.333)
    sh = theme.get("slide_h", 7.5)
    set_slide_bg(slide, theme["bg_dark"])
    add_rect(slide, 0, 0, sw, 0.18, fill=theme["accent"])
    add_rect(slide, 0.82, 0, 0.012, sh, fill=theme["secondary"])
    add_text(
        slide,
        data.get("chapter_no", ""),
        x=1.05,
        y=1.00,
        w=1.0,
        h=0.40,
        font_size=18,
        color=theme["secondary"],
        font_name=theme["header_font"],
        bold=True,
        align="left",
    )
    add_text(
        slide,
        data["title"],
        x=1.05,
        y=1.55,
        w=6.2,
        h=1.10,
        font_size=30,
        color=theme["text_light"],
        font_name=theme["header_font"],
        bold=True,
        align="left",
    )
    if data.get("subtitle"):
        add_text(
            slide,
            data["subtitle"],
            x=1.05,
            y=2.78,
            w=6.2,
            h=0.42,
            font_size=15,
            color=theme["text_muted"],
            font_name=theme["body_font"],
            align="left",
        )
    add_rect(slide, 8.45, 1.40, 3.35, 3.35, fill=theme["primary"])
    add_rect(slide, 9.00, 2.05, 3.35, 3.35, fill=theme["secondary"])
    if data.get("footer_note"):
        add_text(
            slide,
            data["footer_note"],
            x=1.05,
            y=6.75,
            w=10.8,
            h=0.22,
            font_size=9,
            color=theme["text_muted"],
            font_name=theme["body_font"],
            align="left",
        )


def layout_profile_factsheet_4_3(slide, data, theme):
    """4:3 factsheet page for person/product profile with summary strip plus one main module."""

    sw = theme.get("slide_w", 10.0)
    set_slide_bg(slide, theme["bg_light"])
    add_rect(slide, 0.72, 0.0, 0.008, theme.get("slide_h", 7.5), fill=theme["text_dark"])
    add_text(
        slide,
        data["title"],
        x=1.00,
        y=0.38,
        w=4.0,
        h=0.34,
        font_size=18,
        color=theme["text_dark"],
        font_name=theme["header_font"],
        align="left",
        bold=True,
    )
    add_rect(slide, 1.00, 0.94, sw - 1.35, 0.008, fill=theme["text_dark"])

    # profile strip
    add_rect(slide, 1.00, 1.18, sw - 1.45, 1.02, fill="F6F8FC")
    add_rect(slide, 1.00, 1.18, 0.06, 1.02, fill=theme["primary"])
    add_text(slide, data.get("profile_name", ""), x=1.18, y=1.32, w=1.8, h=0.26,
             font_size=16, color=theme["text_dark"], font_name=theme["header_font"], bold=True, align="left")
    add_text(slide, data.get("profile_meta", ""), x=1.18, y=1.64, w=3.8, h=0.20,
             font_size=9, color=theme["text_muted"], font_name=theme["body_font"], align="left")

    stats = data.get("stats", [])
    sx = 5.20
    for item in stats[:3]:
        add_rect(slide, sx, 1.30, 1.15, 0.72, fill="FFFFFF", line_color=theme["border"], line_width=0.5)
        add_text(slide, item["label"], x=sx + 0.08, y=1.40, w=0.98, h=0.14,
                 font_size=8, color=theme["text_muted"], font_name=theme["body_font"], align="left")
        add_text(slide, item["value"], x=sx + 0.08, y=1.64, w=0.98, h=0.18,
                 font_size=12, color=theme["text_dark"], font_name=theme["header_font"], bold=True, align="left")
        sx += 1.25

    if data.get("body_title"):
        add_text(slide, data["body_title"], x=1.00, y=2.35, w=8.2, h=0.20,
                 font_size=10, color=theme["text_muted"], font_name=theme["body_font"], align="left")
    if data.get("body"):
        _render_family(slide, data["body"], (1.00, 2.58, sw - 1.45, 3.95))

    _add_custom_footer(
        slide,
        theme,
        left_text=data.get("source", ""),
        right_text="  ".join(part for part in [data.get("region"), data.get("page_label")] if part),
    )
