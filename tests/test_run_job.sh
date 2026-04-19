#!/bin/bash
# 测试 run_job.py - PptEngine CLI
set -e

PYTHON=$(which python || which python3)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJ_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SCRIPT="$SCRIPT_DIR/../scripts/run_job.py"

TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

echo "=== 测试 run_job.py ==="

# Step 1: 创建最小 job.json
echo "Step 1: 创建最小 job.json"
cat > "$TMPDIR/job.json" << HEREDOC
{
  "template": {"path": "$PROJ_DIR/aim/aim03.pptx"},
  "datasources": {},
  "slides": [
    {
      "id": "cover",
      "texts": [
        {"target": "标题", "value": "测试报告"}
      ]
    }
  ],
  "output": {"path": "$TMPDIR/output.pptx", "overwrite": true}
}
HEREDOC

# Step 2: dry-run 验证
echo "Step 2: dry-run 验证 schema"
DRY_OUTPUT=$($PYTHON "$SCRIPT" "$TMPDIR/job.json" --dry-run 2>/dev/null)
echo "$DRY_OUTPUT" | $PYTHON -c "
import sys, json
d = json.load(sys.stdin)
assert d['status'] == 'ok', f'dry-run failed: {d}'
print(f'  dry-run: {d[\"message\"]}')
print(f'  slides: {d[\"slides\"]}')
" 2>/dev/null

# Step 3: 实际渲染
echo "Step 3: 渲染 PPT"
RENDER_OUTPUT=$($PYTHON "$SCRIPT" "$TMPDIR/job.json" 2>/dev/null)
echo "$RENDER_OUTPUT" | $PYTHON -c "
import sys, json
d = json.load(sys.stdin)
assert d['status'] == 'ok', f'render failed: {d}'
print(f'  output: {d[\"output\"]}')
" 2>/dev/null

# Step 4: 验证输出
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

echo "PASS: run_job.py 流程正常"
