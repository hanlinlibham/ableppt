#!/usr/bin/env python3
"""Use desktop PowerPoint to render a PPTX into PDF, with optional PNG previews.

用法:
    python scripts/export_powerpoint_pdf.py input.pptx output.pdf
    python scripts/export_powerpoint_pdf.py input.pptx output.pdf --png-dir out_png
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def _run_applescript(pptx_path: Path, pdf_path: Path) -> None:
    script = f"""
tell application "Microsoft PowerPoint"
  activate
  open POSIX file "{pptx_path}"
  delay 2
  save active presentation in (POSIX file "{pdf_path}") as save as PDF
  close active presentation saving no
end tell
"""
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0 and not pdf_path.exists():
        stderr = result.stderr.strip() or result.stdout.strip() or "Unknown AppleScript failure"
        raise RuntimeError(stderr)


def _export_pngs(pdf_path: Path, png_dir: Path, scale_to: int) -> list[str]:
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        raise RuntimeError("pdftoppm not found in PATH")

    png_dir.mkdir(parents=True, exist_ok=True)
    prefix = png_dir / "slide"
    subprocess.run(
        [pdftoppm, "-png", "-scale-to", str(scale_to), str(pdf_path), str(prefix)],
        check=True,
        capture_output=True,
        text=True,
    )
    return sorted(str(path) for path in png_dir.glob("slide-*.png"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Render PPTX with desktop PowerPoint and export PDF/PNG previews")
    parser.add_argument("input", help="Input PPTX path")
    parser.add_argument("output_pdf", help="Output PDF path")
    parser.add_argument("--png-dir", help="Optional output directory for per-slide PNG previews")
    parser.add_argument("--scale-to", type=int, default=1400, help="PNG long-edge size passed to pdftoppm")
    args = parser.parse_args()

    pptx_path = Path(args.input).expanduser().resolve()
    pdf_path = Path(args.output_pdf).expanduser().resolve()
    if not pptx_path.exists():
        print(json.dumps({"status": "error", "message": f"文件不存在: {pptx_path}"}, ensure_ascii=False))
        return 1

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    if pdf_path.exists():
        pdf_path.unlink()

    try:
        _run_applescript(pptx_path, pdf_path)
        if not pdf_path.exists():
            raise RuntimeError("PowerPoint reported success but output PDF was not created")

        payload = {
            "status": "ok",
            "input": str(pptx_path),
            "pdf": str(pdf_path),
        }
        if args.png_dir:
            png_dir = Path(args.png_dir).expanduser().resolve()
            payload["pngs"] = _export_pngs(pdf_path, png_dir, args.scale_to)

        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
