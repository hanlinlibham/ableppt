#!/bin/bash
# 测试 generate_ppt.py - 模板替换生成 PPT
# 注意：此测试需要 aim03.pptx 中存在占位符，并准备对应的 config.json 和 CSV
set -e

PYTHON=$(which python || which python3)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJ_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SCRIPT="$SCRIPT_DIR/../scripts/generate_ppt.py"
PARSE_SCRIPT="$SCRIPT_DIR/../scripts/parse_template.py"

TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

echo "=== 测试 generate_ppt.py ==="

# Step 1: 先解析模板看有哪些占位符
echo "Step 1: 解析模板占位符"
PLACEHOLDERS=$($PYTHON "$PARSE_SCRIPT" "$PROJ_DIR/aim/aim03.pptx" 2>/dev/null)
echo "$PLACEHOLDERS" | $PYTHON -c "
import sys, json
d = json.load(sys.stdin)
text = d.get('all_text', [])
chart = d.get('all_chart', [])
print(f'  文本占位符: {text}')
print(f'  图表占位符: {chart}')
" 2>/dev/null

# Step 2: 准备一个最小 config.json（仅文本替换，不含图表）
echo "Step 2: 准备最小配置"
cat > "$TMPDIR/config.json" << 'HEREDOC'
{
  "text_data": {},
  "chart_configs": {}
}
HEREDOC

# Step 3: 生成 PPT
echo "Step 3: 生成 PPT（仅文本替换）"
$PYTHON "$SCRIPT" "$PROJ_DIR/aim/aim03.pptx" "$TMPDIR/config.json" "$TMPDIR/output.pptx" 2>/dev/null

if [ ! -f "$TMPDIR/output.pptx" ]; then
    echo "FAIL: output.pptx 未生成"
    exit 1
fi

SIZE=$(wc -c < "$TMPDIR/output.pptx")
echo "  output.pptx 大小: ${SIZE} bytes"

if [ "$SIZE" -lt 1000 ]; then
    echo "FAIL: output.pptx 太小"
    exit 1
fi

echo "PASS: generate_ppt.py 流程正常"
