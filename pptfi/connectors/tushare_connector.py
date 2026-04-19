"""
Tushare 数据连接器
"""

import pandas as pd
import tushare as ts
from datetime import datetime, timedelta
from pptfi.connectors.base import BaseConnector, ConnectorFactory
from pptfi.models.job import DataSource
from pptfi.config import settings


class TushareConnector(BaseConnector):
    """Tushare 金融数据连接器"""

    def __init__(self):
        super().__init__()
        self._pro = None

    def _get_pro_api(self):
        """获取 Tushare Pro API 实例"""
        if self._pro is None:
            if not settings.tushare_token:
                raise ValueError(
                    "Tushare token not configured. "
                    "Please set TUSHARE_TOKEN in environment or .env file"
                )
            self._pro = ts.pro_api(settings.tushare_token)
        return self._pro

    def load(self, spec: DataSource) -> pd.DataFrame:
        """从 Tushare 加载数据"""
        pro = self._get_pro_api()

        # 处理日期范围
        start_date = spec.start_date
        end_date = spec.end_date

        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")

        if not start_date:
            # 默认一年前
            one_year_ago = datetime.now() - timedelta(days=365)
            start_date = one_year_ago.strftime("%Y%m%d")

        # 根据 api_name 调用不同的接口
        api_name = spec.api_name or "index_daily"

        if api_name == "index_daily":
            # 获取指数日线数据
            ts_code = spec.ts_code or spec.index_code
            if not ts_code:
                raise ValueError("Tushare index_daily requires 'ts_code' or 'index_code'")

            df = pro.index_daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                fields=",".join(spec.fields) if spec.fields else None,
            )

        elif api_name == "pro_bar":
            # 使用 pro_bar 获取数据（更通用）
            ts_code = spec.ts_code or spec.index_code
            if not ts_code:
                raise ValueError("Tushare pro_bar requires 'ts_code' or 'index_code'")

            df = ts.pro_bar(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                adj="qfq",  # 前复权
            )

        else:
            raise ValueError(f"Unsupported Tushare API: {api_name}")

        # 排序数据（按日期升序）
        if "trade_date" in df.columns:
            df = df.sort_values("trade_date").reset_index(drop=True)

        # 转换日期格式为 datetime
        if "trade_date" in df.columns:
            df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")

        return df


# 注册连接器
ConnectorFactory.register("tushare", TushareConnector)

