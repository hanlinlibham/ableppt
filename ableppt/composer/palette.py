"""ableppt 侧配色单一来源（fi color hub）。

职责：
1. ``BRANDED_SCHEMES`` —— fi 自有的品牌/场景图表系列盘。import 本模块时
   通过引擎公开 API ``register_schemes`` 注入引擎注册表，使
   ``style.theme: "able_finance"`` 等在渲染时可解析。引擎自身只自带
   default/categorical/diverging/gtm/aim00 等通用默认，品牌盘全在这里。
2. ``GTM_CHROME`` —— GTM 页面骨架（箭头/角标/章节签/quilt/中性墨）的配色 token。
   过去硬编码在 ``layouts/gtm.py``，现集中到此，由 ``themes.py`` 注入各主题，
   ``gtm.py`` 改从 theme 读 → 骨架跟随主题。

设计师改 fi 配色只动这一个文件：品牌盘改 ``BRANDED_SCHEMES``，骨架色改
``GTM_CHROME``，页面语义色（primary/accent…）在 ``themes.py``。
"""

from ablechart import register_schemes  # noqa: E402

# ============================================================================
# 品牌 / 场景图表系列盘（每套 8 色）—— 注入引擎注册表
# ============================================================================

BRANDED_SCHEMES = {
    "advisory":       ["1F3864", "2E9BD6", "00A398", "8C8C8C", "9DC3E6", "C9A84C", "5C7A93", "404040"],
    "midnight":       ["CADCFC", "1E2761", "E8B931", "4A6FA5", "9BB5D6", "B08C28", "8896AB", "484E5C"],
    "charcoal":       ["A8B4BE", "36454F", "E8B931", "607D8B", "B0BEC5", "C4A035", "78909C", "4A565E"],
    "able_finance":   ["A8D5DC", "1B3D6E", "C9A84C", "4A8FB8", "7FBFCF", "A07840", "8FA8C0", "505868"],
    "able_warm":      ["A8C4D4", "2E5FA3", "D4903F", "7BA7BC", "B0C9B0", "9C7B48", "8A9DB8", "606870"],
    "tech_blue":      ["90CAF9", "1565C0", "00BFA5", "7E57C2", "29B6F6", "FF7043", "90A4AE", "546E7A"],
    "state_red":      ["CDAC60", "8B0000", "B8860B", "4A6FA5", "C07840", "507050", "907878", "585048"],
    "esg_green":      ["A5D6A7", "1A5C2A", "8BC34A", "00838F", "C8E6C9", "795548", "78909C", "607D8B"],
    "dark_pro":       ["00BFFF", "FFD700", "00E676", "7B68EE", "FF6D00", "E040FB", "A0B0C0", "4A5868"],
    "daybreak":       ["A4C2D8", "1D2B3A", "E67E22", "5A9BD5", "95C8D8", "B87333", "7B8794", "495057"],
    "macro_research": ["AED6F1", "2C3E50", "3498DB", "95A5A6", "85C1E9", "1ABC9C", "BDC3C7", "566573"],
}

# import 即注册（幂等：再次 import 只是覆盖同名同值）
register_schemes(BRANDED_SCHEMES)

# ============================================================================
# GTM 页面骨架配色 token（过去硬编码在 layouts/gtm.py）
# ============================================================================

# 章节签配色（GTM：每章一色，中英别名都给）
GTM_SECTION_COLORS = {
    "宏观": "00A0DF", "经济": "00A0DF", "local": "00A0DF",
    "全球": "0072CE", "global": "0072CE",
    "权益": "7F9C3D", "equities": "7F9C3D",
    "固收": "C9A84C", "fixed income": "C9A84C",
    "另类": "7B5EA7", "alternatives": "7B5EA7",
    "资产配置": "1F3864", "principles": "1F3864",
}

# 资产收益矩阵 quilt 默认配色（按资产固定着色）
GTM_QUILT_PALETTE = ["1F3864", "29ABE2", "7F9C3D", "C9A84C", "7B5EA7",
                     "00838F", "B0413E", "595959", "8C8C8C", "5C7A93"]

# GTM 骨架 token 默认（主题可逐项 override；默认值保持现状观感）
GTM_CHROME = {
    "chart_accent": "00A0DF",          # 箭头/角标/章节签默认强调蓝
    "cover_chevrons": ["B3E0F5", "5BC2EC", "00A0DF"],  # 封面三段箭头由浅到深
    "section_colors": GTM_SECTION_COLORS,
    "quilt_palette": GTM_QUILT_PALETTE,
    # 中性墨
    "ink": "1A1A1A",                   # 标题/正文近黑
    "ink_muted": "595959",             # 副标/页码灰
    "source": "7F7F7F",                # 来源行灰
    "hairline": "BFBFBF",              # 细分隔线
    "rule": "404040",                  # 页眉粗分隔线
    "paper": "FFFFFF",                 # 卡片/角标/色块上的留白底与反白字
}
