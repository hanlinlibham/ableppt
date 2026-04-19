"""
CSV 数据连接器
"""

import pandas as pd
from pathlib import Path
from pptfi.connectors.base import BaseConnector, ConnectorFactory
from pptfi.models.job import DataSource
from pptfi.config import settings


class CsvConnector(BaseConnector):
    """CSV 文件连接器"""

    def load(self, spec: DataSource) -> pd.DataFrame:
        """从 CSV 文件加载数据"""
        if not spec.path:
            raise ValueError("CSV connector requires 'path' parameter")

        # 支持相对路径和绝对路径（相对路径优先 CWD，回退 data_dir）
        file_path = Path(spec.path)
        if not file_path.is_absolute():
            cwd_path = Path.cwd() / file_path
            if cwd_path.exists():
                file_path = cwd_path
            else:
                file_path = settings.data_dir / file_path

        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        return pd.read_csv(file_path, encoding=spec.encoding or "utf-8")


class XlsxConnector(BaseConnector):
    """Excel 文件连接器"""

    def load(self, spec: DataSource) -> pd.DataFrame:
        """从 Excel 文件加载数据"""
        if not spec.path:
            raise ValueError("XLSX connector requires 'path' parameter")

        # 相对路径优先 CWD，回退 data_dir
        file_path = Path(spec.path)
        if not file_path.is_absolute():
            cwd_path = Path.cwd() / file_path
            if cwd_path.exists():
                file_path = cwd_path
            else:
                file_path = settings.data_dir / file_path

        if not file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")

        return pd.read_excel(file_path, sheet_name=spec.sheet_name or 0)


# 注册连接器
ConnectorFactory.register("csv", CsvConnector)
ConnectorFactory.register("xlsx", XlsxConnector)

