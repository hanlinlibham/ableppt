"""
渲染器模块
"""

from pptfi.renderers.text_renderer import TextRenderer
from pptfi.renderers.table_renderer import TableRenderer
from pptfi.renderers.ppt_renderer import PPTRenderer

__all__ = ["TextRenderer", "TableRenderer", "PPTRenderer"]
