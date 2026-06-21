"""弱 agent 鲁棒性：数据列名写错时 **fail-loud** 且报错可恢复（列出缺失列 + 可用列），
而不是深处甩一个裸 ``KeyError('列名')``。

设计原则：装饰类参数（配色 / 主题）写错会回退默认（见引擎 styles/themes）；但**数据列绑定**
不能静默默认——否则会产出"数据错了却看起来正常"的静默错图。本测试锁定后者的清晰报错。
"""

import json
from pathlib import Path

import pandas as pd
import pytest

from ableppt import render_job
from ableppt.composer.helpers import require_columns

ROOT = Path(__file__).resolve().parents[1]


def test_require_columns_passes_and_skips_none():
    df = pd.DataFrame({"a": [1], "b": [2]})
    require_columns(df, ["a", "b", None])  # 全在 + None(可选未填) → 不抛


def test_require_columns_reports_missing_and_available():
    df = pd.DataFrame({"年份": [1], "销量": [2]})
    with pytest.raises(ValueError) as ei:
        require_columns(df, ["年份", "不存在"], where="combo 图表")
    msg = str(ei.value)
    assert "不存在" in msg      # 指出违规列
    assert "可用列" in msg
    assert "销量" in msg        # 列出可用列，弱 agent 可据此自我修正
    assert "combo 图表" in msg  # 带上下文标签


def test_render_job_bad_column_fails_loud_with_available(tmp_path):
    job = json.loads((ROOT / "job_waterfall_demo.json").read_text(encoding="utf-8"))

    def corrupt(o):
        if isinstance(o, dict):
            if "categories_col" in o:
                o["categories_col"] = "完全不存在的列xyz"
            for v in o.values():
                corrupt(v)
        elif isinstance(o, list):
            for v in o:
                corrupt(v)

    corrupt(job)
    job["output"]["path"] = str(tmp_path / "out.pptx")
    job_path = tmp_path / "job.json"
    job_path.write_text(json.dumps(job, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError) as ei:
        render_job(job_path)
    msg = str(ei.value)
    assert "完全不存在的列xyz" in msg
    assert "可用列" in msg
