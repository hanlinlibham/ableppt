"""SQL connector with sqlite-first support."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from ableppt.connectors.base import BaseConnector, ConnectorFactory
from ableppt.models.job import DataSource
from ableppt.config import settings


class SqlConnector(BaseConnector):
    """Run SQL queries against a sqlite database."""

    def load(self, spec: DataSource) -> pd.DataFrame:
        if not spec.query:
            raise ValueError("SQL connector requires 'query'")

        conn_str = spec.conn or spec.path
        if not conn_str:
            raise ValueError("SQL connector requires 'conn' or 'path'")

        db_path = _resolve_sqlite_path(conn_str)
        if not db_path.exists():
            raise FileNotFoundError(f"SQLite database not found: {db_path}")

        with sqlite3.connect(str(db_path)) as conn:
            return pd.read_sql_query(spec.query, conn)


def _resolve_sqlite_path(raw: str) -> Path:
    if raw.startswith("sqlite:///"):
        return Path(raw.replace("sqlite:///", "/", 1)).expanduser().resolve()

    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate

    cwd_candidate = Path.cwd() / candidate
    if cwd_candidate.exists():
        return cwd_candidate

    base_candidate = settings.base_dir / candidate
    if base_candidate.exists():
        return base_candidate

    if candidate.parts and candidate.parts[0] != "data":
        data_candidate = settings.data_dir / candidate
        if data_candidate.exists():
            return data_candidate

    return base_candidate


ConnectorFactory.register("sql", SqlConnector)
