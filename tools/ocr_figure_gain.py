"""Does OCR of a figure page add words the text layer missed?

A diagram's labels are sometimes vector text (already in the layer) and sometimes baked into the
raster. This measures which, on named pages: OCR the page, then report OCR words that do not appear
in the page's own text layer. Those leftovers are the labels/annotations only the image can give.

  python tools/ocr_figure_gain.py <pdf> 77 100 300 --dpi 300
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

import pymupdf

WORD = re.compile(r"[A-Za-z][A-Za-z\-']{2,}")


def words(text: str) -> list[str]:
    return [w.lower() for w in WORD.findall(text)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("pages", nargs="+", type=int)
    ap.add_argument("--dpi", type=int, default=300)
    args = ap.parse_args()
    if not args.pdf.exists():
        print(f"no such pdf: {args.pdf}", file=sys.stderr)
        return 2

    from rapidocr_onnxruntime import RapidOCR

    engine = RapidOCR()
    doc = pymupdf.open(args.pdf)

    print(f"{'page':>5} {'layer':>6} {'ocr':>6} {'new':>5}  sample of words only OCR saw")
    print("-" * 90)
    totals = Counter()
    for page_no in args.pages:
        page = doc.load_page(page_no - 1)
        layer_text = page.get_text("text")
        png = Path(tempfile.gettempdir()) / f"gain_{args.pdf.stem}_p{page_no}.png"
        page.get_pixmap(dpi=args.dpi).save(png)

        out = engine(str(png))
        result = out[0] if isinstance(out, tuple) else out
        ocr_text = "\n".join(str(r[1]) for r in (result or []) if len(r) >= 3)

        layer_words, ocr_words = Counter(words(layer_text)), Counter(words(ocr_text))
        new = ocr_words - layer_words          # multiset difference: words the layer never had
        totals["new"] += sum(new.values())
        totals["ocr"] += sum(ocr_words.values())
        totals["layer"] += sum(layer_words.values())
        sample = ", ".join(list(new)[:14])
        print(f"{page_no:>5} {sum(layer_words.values()):>6} {sum(ocr_words.values()):>6} "
              f"{sum(new.values()):>5}  {sample[:60]}")

    print("-" * 90)
    print(f"TOTAL: layer {totals['layer']} words, OCR {totals['ocr']} words, "
          f"{totals['new']} words ({totals['new'] / max(1, totals['ocr']):.1%} of OCR output) "
          f"exist only in the image")
    doc.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
