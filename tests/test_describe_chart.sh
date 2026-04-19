#!/bin/bash
# 测试 describe_chart.py - 描述已有图表
set -e

PYTHON=$(which python || which python3)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJ_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SCRIPT="$SCRIPT_DIR/../scripts/describe_chart.py"

echo "=== 测试 describe_chart.py ==="
echo "输入: $PROJ_DIR/aim/aim00.pptx"

OUTPUT=$($PYTHON "$SCRIPT" "$PROJ_DIR/aim/aim00.pptx" 2>/dev/null)

# 验证输出是合法 JSON
echo "$OUTPUT" | $PYTHON -m json.tool > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "FAIL: 输出不是合法 JSON"
    exit 1
fi

# 验证包含 slides 键
echo "$OUTPUT" | $PYTHON -c "
import sys, json
d = json.load(sys.stdin)
assert 'slides' in d, 'missing slides key'
slide_count = len(d['slides'])
chart_count = sum(len(s['charts']) for s in d['slides'])
print(f'  幻灯片数: {slide_count}')
print(f'  图表总数: {chart_count}')
for s in d['slides']:
    for c in s['charts']:
        print(f'  - Slide {s[\"slide_index\"]}: {c.get(\"title\", \"无标题\")} ({len(c.get(\"series\", []))} 系列)')
" 2>/dev/null

echo "PASS: describe_chart.py 输出正确"
