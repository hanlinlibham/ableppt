"""
数据连接器基类和工厂
"""

from abc import ABC, abstractmethod
from typing import Dict
import pandas as pd
from pptfi.models.job import DataSource


class BaseConnector(ABC):
    """数据连接器基类"""

    @abstractmethod
    def load(self, spec: DataSource) -> pd.DataFrame:
        """加载数据并返回 DataFrame"""
        pass


class ConnectorFactory:
    """连接器工厂"""

    _connectors: Dict[str, type[BaseConnector]] = {}

    @classmethod
    def register(cls, connector_type: str, connector_class: type[BaseConnector]):
        """注册连接器"""
        cls._connectors[connector_type] = connector_class

    @classmethod
    def create(cls, connector_type: str) -> BaseConnector:
        """创建连接器实例"""
        connector_class = cls._connectors.get(connector_type)
        if not connector_class:
            raise ValueError(f"Unknown connector type: {connector_type}")
        return connector_class()

    @classmethod
    def load_data(cls, name: str, spec: DataSource) -> pd.DataFrame:
        """加载数据的便捷方法"""
        connector = cls.create(spec.type)
        return connector.load(spec)

