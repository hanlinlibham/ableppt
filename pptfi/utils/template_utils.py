"""
模板工具函数
"""

from pptx.presentation import Presentation
from pptx.slide import Slide


def find_shape_by_name(slide: Slide, name: str):
    """
    在幻灯片中查找指定名称的形状

    Args:
        slide: 幻灯片对象
        name: 形状名称

    Returns:
        找到的形状对象，未找到返回 None
    """
    for shape in slide.shapes:
        if shape.name == name:
            return shape
    return None


def get_slide_layouts(prs: Presentation) -> dict:
    """
    获取演示文稿中的所有幻灯片版式

    Args:
        prs: 演示文稿对象

    Returns:
        版式名称到版式对象的映射字典
    """
    return {layout.name: layout for layout in prs.slide_layouts}

