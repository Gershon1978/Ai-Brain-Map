"""Reconstruct a TABULAR page from OCR boxes, using geometry instead of reading order.

RapidOCR returns text in the order it finds boxes, which on a three-column table interleaves
SYMPTOM / CAUSE / SOLUTION cells. Quoting from that order produces cross-column garbage such as
"Wheel moves laterally back\\nadjustment\\n2. Loose skewer or thru axle". This tool clusters boxes into
columns by x-centre and rows by y-centre, then emits each CELL as clean text, which is what a citation
of a table cell needs.

  python tools/ocr_table.py <pdf> 254 [--json out.json] [--min-gap 40]
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import pymupdf


def centres(box):
    xs = [p[0] for p in box]
    ys = [p[1] for p in box]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def cluster(values: list[float], gap: float) -> list[float]:
    """Split sorted 1-D values into clusters wherever the gap exceeds `gap`; return cluster centres."""
    if not values:
        return []
    vals = sorted(values)
    groups = [[vals[0]]]
    for v in vals[1:]:
        if v - groups[-1][-1] > gap:
            groups.append([v])
        else:
            groups[-1].append(v)
    return [sum(g) / len(g) for g in groups]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("page", type=int)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--json", default=None)
    ap.add_argument("--min-gap", type=float, default=40.0, help="px gap that separates columns")
    ap.add_argument("--row-gap", type=float, default=55.0, help="px gap that separates rows/cells")
    args = ap.parse_args()
    if not args.pdf.exists():
        print(f"no such pdf: {args.pdf}", file=sys.stderr)
        return 2

    from rapidocr_onnxruntime import RapidOCR

    doc = pymupdf.open(args.pdf)
    page = doc.load_page(args.page - 1)
    png = Path(tempfile.gettempdir()) / f"table_{args.pdf.stem}_p{args.page}.png"
    page.get_pixmap(dpi=args.dpi).save(png)
    doc.close()

    engine = RapidOCR()
    res = engine(str(png))
    rows = (res[0] if isinstance(res, tuple) else res) or []
    boxes = []
    for r in rows:
        if len(r) < 3:
            continue
        box, text = r[0], str(r[1])
        cx, cy = centres(box)
        boxes.append({"x": cx, "y": cy, "text": text, "conf": float(r[2])})

    col_centres = cluster([b["x"] for b in boxes], args.min_gap)
    print(f"page {args.page}: {len(boxes)} boxes, {len(col_centres)} columns detected")

    def nearest(v, centres_):
        return min(range(len(centres_)), key=lambda i: abs(v - centres_[i]))

    # group into cells by (column, row-cluster within that column)
    by_col: dict[int, list[dict]] = {}
    for b in boxes:
        by_col.setdefault(nearest(b["x"], col_centres), []).append(b)

    table_rows = []
    cells_by_col: dict[int, list[str]] = {}
    for ci, items in by_col.items():
        row_centres = cluster([it["y"] for it in items], args.row_gap)
        cells = [[] for _ in row_centres]
        for it in items:
            cells[nearest(it["y"], row_centres)].append(it)
        cells_by_col[ci] = [
            " ".join(x["text"] for x in sorted(cell, key=lambda x: x["x"])).strip()
            for cell in cells
        ]

    width = max(len(v) for v in cells_by_col.values())
    for ri in range(width):
        parts = [(cells_by_col.get(ci) or [""] * width)[ri] if ri < len(cells_by_col.get(ci, [])) else ""
                 for ci in range(len(col_centres))]
        if any(parts):
            table_rows.append(parts)
            print(" | ".join(p[:46].ljust(46) for p in parts))

    # Column-wise linearisation: each column's lines in reading order, joined with single spaces, so a
    # table CELL becomes one contiguous string that can be quoted byte-exactly. Reading order across
    # columns would interleave them, which is what produced cross-column quotes.
    columns_text = []
    for ci in range(len(col_centres)):
        lines = cells_by_col.get(ci, [])
        columns_text.append(" ".join(l for l in lines if l).strip())
    linear = " | ".join(columns_text)
    print("-" * 60)
    for ci, col in enumerate(columns_text):
        print(f"col{ci + 1}: {col[:200]}")

    if args.json:
        Path(args.json).write_text(json.dumps({"page": args.page, "columns": len(col_centres),
                                               "rows": table_rows, "columns_text": columns_text,
                                               "text": linear}, ensure_ascii=False, indent=1),
                                   encoding="utf-8")
        print(f"wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
