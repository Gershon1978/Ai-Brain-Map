"""OCR a named list of pages and report the yield per page (chars, confidence, first line).

Used to test whether the pages whose text layer is EMPTY actually carry text in the image, before
ingesting anything. Prints a summary line per page; writes JSON when --json is given.

  python tools/ocr_batch_pages.py <pdf> 1 2 5 60 --json out.json
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import pymupdf


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("pages", nargs="+", type=int)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    if not args.pdf.exists():
        print(f"no such pdf: {args.pdf}", file=sys.stderr)
        return 2

    from rapidocr_onnxruntime import RapidOCR

    engine = RapidOCR()
    doc = pymupdf.open(args.pdf)
    out_rows = []
    print(f"{'page':>5} {'chars':>6} {'lines':>6} {'conf':>6}  first line")
    print("-" * 88)
    for page_no in args.pages:
        page = doc.load_page(page_no - 1)
        layer = len(page.get_text("text").strip())
        png = Path(tempfile.gettempdir()) / f"batch_{args.pdf.stem}_p{page_no}.png"
        page.get_pixmap(dpi=args.dpi).save(png)
        res = engine(str(png))
        rows = (res[0] if isinstance(res, tuple) else res) or []
        lines = [(str(r[1]), float(r[2])) for r in rows if len(r) >= 3]
        text = "\n".join(t for t, _ in lines)
        conf = sum(c for _, c in lines) / len(lines) if lines else 0.0
        first = (lines[0][0][:52] if lines else "")
        print(f"{page_no:>5} {len(text):>6} {len(lines):>6} {conf:>6.3f}  {first}")
        out_rows.append({"page": page_no, "layer_chars": layer, "ocr_chars": len(text),
                         "lines": len(lines), "mean_confidence": round(conf, 4),
                         "text": text})
    doc.close()

    useful = [r for r in out_rows if r["ocr_chars"] >= 40]
    print("-" * 88)
    print(f"{len(out_rows)} pages OCR'd; {len(useful)} produced >=40 chars of text "
          f"({sum(r['ocr_chars'] for r in useful)} chars total)")
    for r in useful:
        print(f"  p{r['page']}: {r['ocr_chars']} chars  {r['text'][:90].replace(chr(10), ' / ')}")
    if args.json:
        Path(args.json).write_text(json.dumps(out_rows, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
