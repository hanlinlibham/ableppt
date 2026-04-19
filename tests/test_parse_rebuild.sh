#!/bin/bash
# 测试 parse_ppt.py + rebuild_ppt.py - 解析重建流程
set -e

PYTHON=$(which python || which python3)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJ_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PARSE_SCRIPT="$SCRIPT_DIR/../scripts/parse_ppt.py"
REBUILD_SCRIPT="$SCRIPT_DIR/../scripts/rebuild_ppt.py"

TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

echo "=== 测试 parse_ppt.py + rebuild_ppt.py ==="
echo "输入: $PROJ_DIR/aim/aim01.pptx"

# Step 1: 解析
echo "Step 1: 解析 PPT → JSON"
$PYTHON "$PARSE_SCRIPT" "$PROJ_DIR/aim/aim01.pptx" "$TMPDIR/parsed.json" 2>/dev/null

if [ ! -f "$TMPDIR/parsed.json" ]; then
    echo "FAIL: parsed.json 未生成"
    exit 1
fi

SIZE=$(wc -c < "$TMPDIR/parsed.json")
echo "  parsed.json 大小: ${SIZE} bytes"

if [ "$SIZE" -lt 100 ]; then
    echo "FAIL: parsed.json 太小"
    exit 1
fi

# Step 2: 重建
echo "Step 2: 重建 JSON → PPT"
$PYTHON "$REBUILD_SCRIPT" "$TMPDIR/parsed.json" "$TMPDIR/rebuilt.pptx" 2>/dev/null

if [ ! -f "$TMPDIR/rebuilt.pptx" ]; then
    echo "FAIL: rebuilt.pptx 未生成"
    exit 1
fi

SIZE=$(wc -c < "$TMPDIR/rebuilt.pptx")
echo "  rebuilt.pptx 大小: ${SIZE} bytes"

if [ "$SIZE" -lt 1000 ]; then
    echo "FAIL: rebuilt.pptx 太小"
    exit 1
fi

echo "PASS: parse + rebuild 流程正常"
