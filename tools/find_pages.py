"""Search a PDF's own text layer for a regex and report page numbers + snippets.

Used to find where a topic actually lives before deciding to OCR anything: if the
publisher's text layer has it, that is grade A, not grade C.

  python tools/find_pages.py <pdf> "<regex>" [--context 90] [--max 40]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pymupdf


def squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("pattern")
    ap.add_argument("--context", type=int, default=90)
    ap.add_argument("--max", type=int, default=40)
    ap.add_argument("--ignore-case", action="store_true", default=True)
    args = ap.parse_args()

    if not args.pdf.exists():
        print(f"no such pdf: {args.pdf}", file=sys.stderr)
        return 2

    rx = re.compile(args.pattern, re.IGNORECASE if args.ignore_case else 0)
    doc = pymupdf.open(args.pdf)
    hits = 0
    for i in range(doc.page_count):
        raw = doc.load_page(i).get_text("text")
        if not raw.strip():
            continue
        flat = squash(raw)
        for m in rx.finditer(flat):
            hits += 1
            if hits > args.max:
                break
            lo = max(0, m.start() - args.context)
            hi = min(len(flat), m.end() + args.context)
            print(f"p{i + 1:3d}  ...{flat[lo:hi]}...")
        if hits > args.max:
            print(f"... stopped after {args.max} hits")
            break
    doc.close()
    print(f"{hits} hit(s) for /{args.pattern}/")
    return 0 if hits else 1


if __name__ == "__main__":
    raise SystemExit(main())
