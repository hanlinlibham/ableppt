"""
配置管理模块
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    # 项目路径
    base_dir: Path = Path(__file__).parent.parent
    templates_dir: Path = base_dir / "templates"
    output_dir: Path = base_dir / "output"
    data_dir: Path = base_dir / "data"

    # API 配置
    api_title: str = "PPTFI API"
    api_version: str = "0.1.0"
    api_prefix: str = "/api/v1"

    # Tushare 配置
    tushare_token: Optional[str] = None

    # 数据库配置（可选）
    database_url: Optional[str] = None

    # 调试模式
    debug: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保目录存在
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)


# 全局配置实例
settings = Settings()

