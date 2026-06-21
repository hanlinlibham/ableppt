"""
数据转换器
"""

from typing import Dict, List
import pandas as pd
from ableppt.models.job import Transform, TransformOp


class DataFrameTransformer:
    """DataFrame 转换器"""

    @staticmethod
    def apply_transforms(
        dfs: Dict[str, pd.DataFrame], transforms: Dict[str, Transform]
    ) -> Dict[str, pd.DataFrame]:
        """应用所有转换"""
        result = dict(dfs)

        for name, transform in (transforms or {}).items():
            # 获取源数据
            if isinstance(transform.from_, str):
                source_df = result[transform.from_].copy()
            elif isinstance(transform.from_, list):
                # 多个数据源需要合并
                source_dfs = [result[src].copy() for src in transform.from_]
                source_df = source_dfs[0]
                for df in source_dfs[1:]:
                    # 默认按索引合并
                    source_df = pd.concat([source_df, df], axis=1)
            else:
                raise ValueError(f"Invalid 'from' type: {type(transform.from_)}")

            # 应用操作
            for op in transform.ops:
                source_df = DataFrameTransformer._apply_op(source_df, op)

            result[name] = source_df

        return result

    @staticmethod
    def _apply_op(df: pd.DataFrame, op: TransformOp) -> pd.DataFrame:
        """应用单个转换操作"""
        if op.type == "groupby":
            if not op.by or not op.agg:
                raise ValueError("groupby requires 'by' and 'agg' parameters")
            return df.groupby(op.by).agg(op.agg).reset_index()

        elif op.type == "pivot":
            if not op.index or not op.columns or not op.values:
                raise ValueError("pivot requires 'index', 'columns', and 'values'")
            return df.pivot(index=op.index, columns=op.columns, values=op.values)

        elif op.type == "merge":
            # merge 需要两个 DataFrame，这里暂不实现
            raise NotImplementedError("merge operation should be handled at higher level")

        elif op.type == "compute":
            if not op.expr or not op.output_col:
                raise ValueError("compute requires 'expr' and 'output_col'")
            # 使用 eval 计算表达式
            df[op.output_col] = df.eval(op.expr)
            return df

        elif op.type == "filter":
            if not op.condition:
                raise ValueError("filter requires 'condition'")
            return df.query(op.condition)

        elif op.type == "sort":
            if not op.sort_by:
                raise ValueError("sort requires 'sort_by'")
            return df.sort_values(op.sort_by, ascending=op.ascending)

        elif op.type == "rename":
            if not op.map:
                raise ValueError("rename requires 'map'")
            return df.rename(columns=op.map)

        else:
            raise ValueError(f"Unknown operation type: {op.type}")

