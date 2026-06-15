"""PageComposer: 页面级组合 PPT 生成器"""

from . import palette  # noqa: F401  导入即把品牌盘注册进引擎注册表
from .page_composer import PageComposer
from .template_assembler import TemplateAssembler
from .themes import THEMES, DEFAULT_THEME

__all__ = ["PageComposer", "TemplateAssembler", "THEMES", "DEFAULT_THEME"]
