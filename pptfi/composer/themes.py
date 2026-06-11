"""主题配置 — 配色、字体、间距、结构几何"""


# ── 新增 tokens 的默认值（供旧主题/自定义主题 fallback） ──────────────
_LAYOUT_DEFAULTS = {
    # 字号层级
    "cover_title_size": 36,
    "page_title_size": 16,
    "chart_subtitle_size": 11,
    "footer_size": 8,
    # 幻灯片尺寸 (inches)
    "slide_w": 13.333,   # 16:9 default
    "slide_h": 7.5,
    # 结构几何 (inches)
    "header_y": 0.25,
    "divider_y": 0.80,
    "divider_h": 0.015,
    "content_y": 1.00,
    "content_h": 5.80,
    "footer_y": 7.10,
    # content_w 由 _theme() 自动计算: slide_w - 2 * margin
    # 表格样式
    "table_header_bg": "1F4E79",
    "table_zebra_even": "F8FAFC",
    "table_zebra_odd": "FFFFFF",
    # 图表默认
    "chart_default_scheme": "default",
}


def _theme(base: dict) -> dict:
    """合并 layout defaults，保证每个 theme 都有完整 tokens"""
    merged = {**_LAYOUT_DEFAULTS, **base}
    # table_header_bg 默认跟随 primary
    if "table_header_bg" not in base:
        merged["table_header_bg"] = base.get("primary", _LAYOUT_DEFAULTS["table_header_bg"])
    # content_w = slide_w - 2 * margin（自动派生）
    if "content_w" not in base:
        merged["content_w"] = merged["slide_w"] - 2 * merged.get("margin", 0.6)
    return merged


THEMES = {
    "midnight": _theme({
        "name": "Midnight Executive",
        "primary": "1E2761",
        "secondary": "CADCFC",
        "accent": "E8B931",
        "bg_dark": "1E2761",
        "bg_light": "F5F7FA",
        "card_bg": "FFFFFF",
        "text_dark": "1E2761",
        "text_light": "FFFFFF",
        "text_muted": "8896AB",
        "border": "E2E8F0",
        "positive": "10B981",
        "negative": "EF4444",
        "header_font": "微软雅黑",
        "body_font": "微软雅黑",
        "margin": 0.6,
        "title_size": 28,
        "subtitle_size": 18,
        "body_size": 14,
        "caption_size": 10,
        "kpi_size": 44,
        "chart_default_scheme": "midnight",
    }),
    "charcoal": _theme({
        "name": "Charcoal Minimal",
        "primary": "36454F",
        "secondary": "F2F2F2",
        "accent": "E8B931",
        "bg_dark": "36454F",
        "bg_light": "F8F8F8",
        "card_bg": "FFFFFF",
        "text_dark": "212121",
        "text_light": "FFFFFF",
        "text_muted": "808080",
        "border": "E0E0E0",
        "positive": "10B981",
        "negative": "EF4444",
        "header_font": "微软雅黑",
        "body_font": "微软雅黑",
        "margin": 0.6,
        "title_size": 28,
        "subtitle_size": 18,
        "body_size": 14,
        "caption_size": 10,
        "kpi_size": 44,
        "chart_default_scheme": "charcoal",
    }),
    # ── 新主题（设计源自投行级研报分析 + 行业报告研究） ──────────────
    "able_finance": _theme({
        "name": "IB Finance",
        "primary": "1B3D6E",
        "secondary": "00A5BD",
        "accent": "C9A84C",
        "bg_dark": "0F2340",
        "bg_light": "F4F6FA",
        "card_bg": "FFFFFF",
        "text_dark": "1A2744",
        "text_light": "FFFFFF",
        "text_muted": "6B7C93",
        "border": "C8D6E5",
        "positive": "0B7B3E",
        "negative": "C0392B",
        "header_font": "微软雅黑",
        "body_font": "微软雅黑",
        "margin": 0.6,
        "title_size": 28,
        "subtitle_size": 18,
        "body_size": 12,
        "caption_size": 9,
        "kpi_size": 44,
        # IB-specific overrides
        "table_header_bg": "1B3D6E",
        "chart_default_scheme": "able_finance",
    }),
    "pension_warm": _theme({
        "name": "Pension Warm",
        "primary": "2E5FA3",
        "secondary": "7BA7BC",
        "accent": "D4903F",
        "bg_dark": "1C3557",
        "bg_light": "F7F4F0",
        "card_bg": "FDFAF7",
        "text_dark": "2C3E50",
        "text_light": "FAFAFA",
        "text_muted": "7F8C8D",
        "border": "D5C9B8",
        "positive": "27AE60",
        "negative": "E74C3C",
        "header_font": "微软雅黑",
        "body_font": "微软雅黑",
        "margin": 0.6,
        "title_size": 28,
        "subtitle_size": 18,
        "body_size": 12,
        "caption_size": 9,
        "kpi_size": 44,
        "chart_default_scheme": "pension_warm",
    }),
    "tech_blue": _theme({
        "name": "Tech Blue",
        "primary": "1565C0",
        "secondary": "29B6F6",
        "accent": "00BFA5",
        "bg_dark": "0A1628",
        "bg_light": "F0F4FF",
        "card_bg": "FFFFFF",
        "text_dark": "102040",
        "text_light": "E8F1FF",
        "text_muted": "7A8CA8",
        "border": "C0D0E8",
        "positive": "00C896",
        "negative": "FF4B5C",
        "header_font": "微软雅黑",
        "body_font": "微软雅黑",
        "margin": 0.6,
        "title_size": 28,
        "subtitle_size": 18,
        "body_size": 12,
        "caption_size": 9,
        "kpi_size": 44,
        "chart_default_scheme": "tech_blue",
    }),
    "state_red": _theme({
        "name": "State Red",
        "primary": "8B0000",
        "secondary": "B8860B",
        "accent": "DAA520",
        "bg_dark": "5C0000",
        "bg_light": "FDF8F0",
        "card_bg": "FFFFFF",
        "text_dark": "2C1810",
        "text_light": "FFF8E7",
        "text_muted": "8C7B6B",
        "border": "E0CFAA",
        "positive": "2E6B30",
        "negative": "8B0000",
        "header_font": "微软雅黑",
        "body_font": "微软雅黑",
        "margin": 0.6,
        "title_size": 28,
        "subtitle_size": 18,
        "body_size": 12,
        "caption_size": 9,
        "kpi_size": 44,
        "chart_default_scheme": "state_red",
    }),
    "esg_green": _theme({
        "name": "ESG Green",
        "primary": "1A5C2A",
        "secondary": "4CAF50",
        "accent": "8BC34A",
        "bg_dark": "0D3318",
        "bg_light": "F1F8F2",
        "card_bg": "FFFFFF",
        "text_dark": "1B2B1C",
        "text_light": "E8F5E9",
        "text_muted": "5C7A5E",
        "border": "B8D8BA",
        "positive": "2E7D32",
        "negative": "C62828",
        "header_font": "微软雅黑",
        "body_font": "微软雅黑",
        "margin": 0.6,
        "title_size": 28,
        "subtitle_size": 18,
        "body_size": 12,
        "caption_size": 9,
        "kpi_size": 44,
        "chart_default_scheme": "esg_green",
    }),
    # ── 研究级主题（研究报告风格） ──────────────────────
    "daybreak": _theme({
        "name": "Daybreak Research",
        "primary": "1D2B3A",      # 深石板灰
        "secondary": "5A9BD5",    # 中蓝
        "accent": "E67E22",       # 暖橙
        "bg_dark": "1A1A2E", "bg_light": "FAFBFC", "card_bg": "FFFFFF",
        "text_dark": "2C3E50", "text_light": "F8F9FA", "text_muted": "7B8794",
        "border": "DEE2E6", "positive": "28A745", "negative": "DC3545",
        "header_font": "微软雅黑", "body_font": "微软雅黑",
        "margin": 0.6, "title_size": 28, "subtitle_size": 18,
        "body_size": 11, "caption_size": 9, "kpi_size": 36,
        "chart_default_scheme": "daybreak",
    }),
    "macro_research": _theme({
        "name": "Macro Research",
        "primary": "2C3E50",      # 深藏蓝灰
        "secondary": "3498DB",    # 净蓝
        "accent": "95A5A6",       # 中性灰（低调）
        "bg_dark": "1A252F", "bg_light": "F7F9FB", "card_bg": "FFFFFF",
        "text_dark": "2C3E50", "text_light": "ECF0F1", "text_muted": "95A5A6",
        "border": "D5D8DC", "positive": "27AE60", "negative": "E74C3C",
        "header_font": "微软雅黑", "body_font": "微软雅黑",
        "margin": 0.6, "title_size": 28, "subtitle_size": 18,
        "body_size": 11, "caption_size": 9, "kpi_size": 36,
        "chart_default_scheme": "macro_research",
    }),
    "dark_pro": _theme({
        "name": "Dark Pro",
        "primary": "00BFFF",
        "secondary": "7B68EE",
        "accent": "FFD700",
        "bg_dark": "080808",
        "bg_light": "141820",
        "card_bg": "1E2430",
        "text_dark": "E0E8F0",
        "text_light": "FFFFFF",
        "text_muted": "6880A0",
        "border": "2A3848",
        "positive": "00E676",
        "negative": "FF1744",
        "header_font": "微软雅黑",
        "body_font": "微软雅黑",
        "margin": 0.6,
        "title_size": 30,
        "subtitle_size": 20,
        "body_size": 13,
        "caption_size": 10,
        "kpi_size": 48,
        "chart_default_scheme": "dark_pro",
    }),
}

DEFAULT_THEME = THEMES["midnight"]

# ── 比例预设 ──────────────────────────────────────────────────────────
ASPECT_4_3 = {"slide_w": 10.0, "slide_h": 7.5}
ASPECT_16_9 = {"slide_w": 13.333, "slide_h": 7.5}


def resolve_theme(theme, aspect_ratio=None) -> dict:
    """解析主题参数，确保所有 tokens 都有值

    Args:
        theme: 主题名称(str) 或主题字典(dict) 或 None
        aspect_ratio: 可选比例 "4:3" 或 "16:9"

    Returns:
        完整的主题字典（包含所有 layout tokens）
    """
    if isinstance(theme, str):
        result = dict(THEMES.get(theme, DEFAULT_THEME))
    elif isinstance(theme, dict):
        result = {**DEFAULT_THEME, **theme}
    else:
        result = dict(DEFAULT_THEME)
    if aspect_ratio == "4:3":
        result.update(ASPECT_4_3)
        result["content_w"] = result["slide_w"] - 2 * result.get("margin", 0.6)
    return result
