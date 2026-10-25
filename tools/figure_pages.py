"""Map a PDF's FIGURES: which pages carry illustrations, what they are captioned, and which of
those captions are diagnostic (inspect / check / test / measure / replace).

Why: a big service manual's value to a mechanic is not only prose. Figures carry (a) exploded views
whose labels may live in the image rather than the text layer, (b) torque/diagnostic tables, and
(c) the captions that say what the mechanic is looking for. This tool finds them before any OCR is
spent, so OCR is aimed at pages where the text layer genuinely cannot see the text.

  python tools/figure_pages.py <pdf> [--json out.json] [--min-images 1]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pymupdf

FIGURE_RX = re.compile(r"(?:FIGURE|Figure)\s+\d+[\.\-]\d+[^\n]{0,110}")
DIAGNOSTIC_RX = re.compile(
    r"\b(inspect|check|test|measure|verify|examine|feel for|look for|replace if|if the|worn|worn out)\b",
    re.IGNORECASE,
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--json", default=None)
    ap.add_argument("--min-images", type=int, default=1, help="images per page to count as illustrated")
    args = ap.parse_args()
    if not args.pdf.exists():
        print(f"no such pdf: {args.pdf}", file=sys.stderr)
        return 2

    doc = pymupdf.open(args.pdf)
    rows = []
    for i in range(doc.page_count):
        page = doc.load_page(i)
        text = page.get_text("text")
        images = page.get_images(full=True)
        captions = FIGURE_RX.findall(text)
        rows.append({
            "page": i + 1,
            "chars": len(text.strip()),
            "images": len(images),
            "vector_ops": len(page.get_drawings()),
            "captions": [re.sub(r"\s+", " ", c).strip() for c in captions],
        })
    doc.close()

    no_text = [r["page"] for r in rows if r["chars"] == 0]
    thin = [r["page"] for r in rows if 0 < r["chars"] < 200]
    illustrated = [r for r in rows if r["images"] >= args.min_images]
    with_captions = [r for r in rows if r["captions"]]
    total_captions = sum(len(r["captions"]) for r in with_captions)
    caption_no_text = [r["page"] for r in with_captions if r["chars"] < 200]
    diag = [r for r in rows if r["captions"] and any(DIAGNOSTIC_RX.search(c) for c in r["captions"])]

    print(f"{args.pdf.name}: {len(rows)} pages, {len(args.pdf.name)} bytes-name")
    print(f"  pages with NO text layer      : {len(no_text)}  {no_text[:30]}{' ...' if len(no_text) > 30 else ''}")
    print(f"  pages with <200 chars        : {len(thin)}  {thin[:30]}{' ...' if len(thin) > 30 else ''}")
    print(f"  pages with >= {args.min_images} embedded image : {len(illustrated)}")
    print(f"  pages carrying a FIGURE caption: {len(with_captions)}  ({total_captions} captions)")
    print(f"  ...of those, text-poor (<200 ch): {len(caption_no_text)}  {caption_no_text[:30]}")
    print(f"  captions that are DIAGNOSTIC  : {len(diag)} pages")
    for r in diag[:25]:
        for c in r["captions"]:
            if DIAGNOSTIC_RX.search(c):
                print(f"    p{r['page']:4d}  {c[:100]}")
    print(f"  OCR candidates (illustrated AND text-poor): "
          f"{len([r for r in rows if r['images'] >= args.min_images and r['chars'] < 200])}")

    if args.json:
        Path(args.json).write_text(json.dumps(rows, indent=1), encoding="utf-8")
        print(f"  wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
