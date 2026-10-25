"""Sweep a PDF's text layer for NUMERIC SPECIFICATIONS and report page + sentence.

A bicycle factory manual states torque, clearances, wear limits and dimensions in prose. This finds
them, so a gap like "the graph has 2 measurements for 44 components" can be attacked from a source we
already own at grade A, without waiting on any external service.

  python tools/find_specs.py <pdf> [--kind torque|wear|dimension|pressure] [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pymupdf

KINDS = {
    "torque": r"(?:\d+(?:\.\d+)?\s*(?:to|-|–)\s*)?\d+(?:\.\d+)?\s*(?:Nm|N·m|N m|inch-?pounds?|in-?lbs?)",
    "wear": r"\d+(?:\.\d+)?\s*(?:%|percent)\b|\d+(?:\.\d+)?\s*mm\s*(?:minimum|min\.|thickness)",
    "dimension": r"\d+(?:\.\d+)?\s*(?:mm|in\.|inch|tpi)\b",
    "pressure": r"\d+(?:\.\d+)?\s*(?:psi|bar)\b",
}


def squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--kind", default="torque", choices=sorted(KINDS))
    ap.add_argument("--max", type=int, default=120)
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    if not args.pdf.exists():
        print(f"no such pdf: {args.pdf}", file=sys.stderr)
        return 2

    rx = re.compile(KINDS[args.kind])
    doc = pymupdf.open(args.pdf)
    rows, seen = [], set()
    for i in range(doc.page_count):
        flat = squash(doc.load_page(i).get_text("text"))
        if not flat:
            continue
        for m in rx.finditer(flat):
            lo = max(0, m.start() - 150)
            hi = min(len(flat), m.end() + 120)
            # sentence-ish context around the match
            ctx = flat[lo:hi]
            key = (i + 1, m.group(0).lower())
            if key in seen:
                continue
            seen.add(key)
            rows.append({"page": i + 1, "match": m.group(0), "context": ctx})
    doc.close()

    print(f"{args.pdf.name}: {len(rows)} {args.kind} hits over {doc.page_count if hasattr(doc, 'page_count') else '?'} pages")
    for r in rows[: args.max]:
        print(f"  p{r['page']:4d}  [{r['match']}]  ...{r['context'][140:280]}...")
    if len(rows) > args.max:
        print(f"  ... {len(rows) - args.max} more")
    if args.json:
        Path(args.json).write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
