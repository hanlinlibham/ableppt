"""
CSV 数据连接器
"""

import pandas as pd
from pathlib import Path
from ableppt.connectors.base import BaseConnector, ConnectorFactory
from ableppt.models.job import DataSource
from ableppt.config import settings


class CsvConnector(BaseConnector):
    """CSV 文件连接器"""

    def load(self, spec: DataSource) -> pd.DataFrame:
        """从 CSV 文件加载数据"""
        if not spec.path:
            raise ValueError("CSV connector requires 'path' parameter")

        file_path = _resolve_local_path(spec.path)

        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        return pd.read_csv(file_path, encoding=spec.encoding or "utf-8")


class XlsxConnector(BaseConnector):
    """Excel 文件连接器"""

    def load(self, spec: DataSource) -> pd.DataFrame:
        """从 Excel 文件加载数据"""
        if not spec.path:
            raise ValueError("XLSX connector requires 'path' parameter")

        file_path = _resolve_local_path(spec.path)

        if not file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")

        return pd.read_excel(file_path, sheet_name=spec.sheet_name or 0)


# 注册连接器
ConnectorFactory.register("csv", CsvConnector)
ConnectorFactory.register("xlsx", XlsxConnector)


def _resolve_local_path(raw_path: str) -> Path:
    """Resolve local datasource paths without duplicating the `data/` segment."""

    file_path = Path(raw_path)
    if file_path.is_absolute():
        return file_path

    candidates = [
        Path.cwd() / file_path,
        settings.base_dir / file_path,
    ]

    if file_path.parts and file_path.parts[0] != "data":
        candidates.append(settings.data_dir / file_path)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0] if candidates else file_path
