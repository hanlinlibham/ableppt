"""
表格渲染器
"""

from typing import List
import pandas as pd
from pptx.slide import Slide
from pptfi.models.job import TableSpec
from pptfi.utils.template_utils import find_shape_by_name


class TableRenderer:
    """表格渲染器"""

    @staticmethod
    def render(slide: Slide, table_spec: TableSpec, df: pd.DataFrame) -> None:
        """
        渲染表格到幻灯片

        Args:
            slide: 幻灯片对象
            table_spec: 表格配置
            df: 数据 DataFrame
        """
        shape = find_shape_by_name(slide, table_spec.target)

        if not shape:
            print(f"警告: 未找到表格 '{table_spec.target}'")
            return

        if not shape.has_table:
            print(f"警告: '{table_spec.target}' 不是表格")
            return

        table = shape.table
        data = df[table_spec.columns]

        # 写入表头
        row_start = 0
        if table_spec.header:
            for j, header in enumerate(table_spec.header):
                if j < len(table.columns):
                    cell = table.cell(0, j)
                    cell.text = str(header)
            row_start = 1

        # 写入数据
        for i in range(len(data)):
            if i + row_start >= len(table.rows):
                # 如果表格行数不够，需要添加行
                print(f"警告: 表格 '{table_spec.target}' 行数不足，需要 {i + row_start + 1} 行")
                break

            for j in range(len(table_spec.columns)):
                if j < len(table.columns):
                    cell = table.cell(i + row_start, j)
                    value = data.iat[i, j]

                    # 格式化数值
                    if table_spec.number_format and table_spec.columns[j] in table_spec.number_format:
                        fmt = table_spec.number_format[table_spec.columns[j]]
                        if isinstance(value, (int, float)):
                            if "%" in fmt:
                                cell.text = f"{value:.2%}"
                            elif "#,##0" in fmt:
                                cell.text = f"{value:,.0f}"
                            else:
                                cell.text = str(value)
                        else:
                            cell.text = str(value)
                    else:
                        cell.text = str(value)
