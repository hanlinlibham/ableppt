#!/bin/bash
# 测试 parse_template.py - 解析模板占位符
set -e

PYTHON=$(which python || which python3)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJ_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SCRIPT="$SCRIPT_DIR/../scripts/parse_template.py"

echo "=== 测试 parse_template.py ==="
echo "模板: $PROJ_DIR/aim/aim03.pptx"

OUTPUT=$($PYTHON "$SCRIPT" "$PROJ_DIR/aim/aim03.pptx" 2>/dev/null)

# 验证输出是合法 JSON
echo "$OUTPUT" | $PYTHON -m json.tool > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "FAIL: 输出不是合法 JSON"
    exit 1
fi

# 验证包含 pages 键
echo "$OUTPUT" | $PYTHON -c "import sys, json; d=json.load(sys.stdin); assert 'pages' in d, 'missing pages key'" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "FAIL: 输出缺少 pages 键"
    exit 1
fi

echo "PASS: parse_template.py 输出正确"
echo "$OUTPUT" | python -c "
import sys, json
d = json.load(sys.stdin)
print(f'  页数: {len(d[\"pages\"])}')
print(f'  文本占位符: {d.get(\"all_text\", [])}')
print(f'  图表占位符: {d.get(\"all_chart\", [])}')
" 2>/dev/null
