"""OCR one page of a PDF with the local ONNX engine (RapidOCR / PP-OCR models).

Three modes:

  inventory   list every page that has no usable text layer (i.e. is a scan)
  ocr         render + OCR one page, print the text and per-line confidence
  validate    OCR a page that DOES have a text layer and measure character error
              rate against that layer, so the engine's accuracy is measured on
              this corpus instead of assumed

Anything produced by `ocr` is a MACHINE TRANSCRIPTION and must be ingested at
evidence grade C, never A/B.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import time
import unicodedata
from collections import Counter
from pathlib import Path

import pymupdf  # PyMuPDF >= 1.24 (the fitz alias is deprecated)

LIGATURES = {
    "\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi",
    "\ufb04": "ffl", "\ufb05": "st", "\ufb06": "st",
}
DASHES = "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"
QUOTES = "\u2018\u2019\u201a\u201b\u2032\u00b4"


def normalise(text: str) -> str:
    """Collapse to a comparable form: identical rules applied to OCR and to the layer."""
    for bad, good in LIGATURES.items():
        text = text.replace(bad, good)
    for dash in DASHES:
        text = text.replace(dash, "-")
    for q in QUOTES:
        text = text.replace(q, "'")
    for q in "\u201c\u201d\u201e\u2033":
        text = text.replace(q, '"')
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u00ad", "")          # soft hyphen
    text = re.sub(r"-\s*\n\s*", "", text)      # de-hyphenate across a line break
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def lev(a: str, b: str) -> int:
    """Levenshtein distance, two rows (a page is only a few thousand chars)."""
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def render(pdf: Path, page_no: int, dpi: int) -> tuple[Path, float, int]:
    """Render one page to PNG; also report its width and text-layer length."""
    doc = pymupdf.open(pdf)
    page = doc.load_page(page_no - 1)
    pix = page.get_pixmap(dpi=dpi)
    tmp = Path(tempfile.gettempdir()) / f"ocr_{pdf.stem}_p{page_no:04d}_{dpi}.png"
    pix.save(tmp)
    layer_chars = len(page.get_text("text").strip())
    width = float(page.rect.width)
    doc.close()
    return tmp, width, layer_chars


def run_ocr(png: Path) -> tuple[list[tuple[str, float]], float]:
    from rapidocr_onnxruntime import RapidOCR

    engine = RapidOCR()
    started = time.time()
    out = engine(str(png))
    elapsed = time.time() - started
    result = out[0] if isinstance(out, tuple) else out
    lines: list[tuple[str, float]] = []
    for row in result or []:
        if len(row) >= 3:  # [box, text, score]
            lines.append((str(row[1]), float(row[2])))
    return lines, elapsed


def cmd_inventory(args) -> int:
    doc = pymupdf.open(args.pdf)
    empty, thin = [], []
    for i in range(doc.page_count):
        chars = len(doc.load_page(i).get_text("text").strip())
        if chars == 0:
            empty.append(i + 1)
        elif chars < 120:
            thin.append((i + 1, chars))
    print(f"{args.pdf.name}: {doc.page_count} pages")
    print(f"  no text layer at all : {len(empty)} pages")
    if empty:
        shown = ", ".join(str(p) for p in empty[:60])
        print("    " + shown + (" ..." if len(empty) > 60 else ""))
    print(f"  0 < chars < 120      : {len(thin)} pages")
    for p, c in thin[:20]:
        print(f"    p{p}: {c} chars")
    doc.close()
    return 0


def cmd_ocr(args) -> int:
    print(f"page {args.page} of {args.pdf.name}: rendering @ {args.dpi}dpi ...", flush=True)
    png, width, layer_chars = render(args.pdf, args.page, args.dpi)
    print(f"  png={png} ({png.stat().st_size // 1024} KB) - ocr running ...", flush=True)
    lines, elapsed = run_ocr(png)
    text = "\n".join(t for t, _ in lines)
    conf = [c for _, c in lines]
    mean = sum(conf) / len(conf) if conf else 0.0
    print(f"page {args.page} of {args.pdf.name}  width={width:.0f}pt  dpi={args.dpi}")
    print(f"  text layer: {layer_chars} chars | ocr: {len(text)} chars in {len(lines)} lines")
    print(f"  mean confidence: {mean:.3f}  min: {min(conf) if conf else 0:.3f}  ({elapsed:.1f}s)")
    print(f"  low-confidence lines (<0.80): {sum(1 for c in conf if c < 0.80)}")
    if args.json:
        Path(args.json).write_text(json.dumps(
            {"pdf": str(args.pdf), "page": args.page, "dpi": args.dpi,
             "mean_confidence": round(mean, 4),
             "lines": [{"text": t, "conf": round(c, 4)} for t, c in lines]},
            ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  wrote {args.json}")
    print("-" * 70)
    print(text)
    return 0


def cmd_validate(args) -> int:
    print(f"validate page {args.page} of {args.pdf.name}: rendering @ {args.dpi}dpi ...", flush=True)
    png, _, _ = render(args.pdf, args.page, args.dpi)
    print(f"  png={png} ({png.stat().st_size // 1024} KB) - ocr running ...", flush=True)
    doc = pymupdf.open(args.pdf)
    truth = doc.load_page(args.page - 1).get_text("text")
    doc.close()
    lines, elapsed = run_ocr(png)
    got = "\n".join(t for t, _ in lines)

    ref_n, got_n = normalise(truth), normalise(got)
    dist = lev(ref_n, got_n)
    cer = dist / max(1, len(ref_n))

    ref_words, got_words = ref_n.split(), got_n.split()
    pool = Counter(got_words)  # multiset: how many reference words the OCR reproduced
    hit = 0
    for w in ref_words:
        if pool[w] > 0:
            pool[w] -= 1
            hit += 1
    recall = hit / max(1, len(ref_words))

    print(f"VALIDATION page {args.page} of {args.pdf.name} @ {args.dpi}dpi")
    print(f"  reference (text layer): {len(ref_n)} chars, {len(ref_words)} words")
    print(f"  ocr output            : {len(got_n)} chars, {len(got_words)} words")
    print(f"  edit distance         : {dist}")
    print(f"  CHARACTER ERROR RATE  : {cer:.2%}")
    print(f"  word recall           : {recall:.2%}")
    mean = sum(c for _, c in lines) / max(1, len(lines))
    print(f"  mean confidence       : {mean:.3f}  ({elapsed:.1f}s)")
    if args.show_diff:
        i = next((k for k in range(min(len(ref_n), len(got_n))) if ref_n[k] != got_n[k]), None)
        if i is not None:
            lo, hi = max(0, i - 60), i + 60
            print("  first divergence at char", i)
            print("    ref:", ref_n[lo:hi])
            print("    ocr:", got_n[lo:hi])
    if cer < 0.05:
        verdict = "TRUSTWORTHY for grade C"
    elif cer < 0.15:
        verdict = "USABLE for grade C (wording only, digits unverified)"
    else:
        verdict = "NOT usable - do not ingest"
    print(f"  VERDICT: {verdict}")
    return 0


def cmd_render(args) -> int:
    doc = pymupdf.open(args.pdf)
    page = doc.load_page(args.page - 1)
    pix = page.get_pixmap(dpi=args.dpi)
    out = Path(args.out or f"{args.pdf.stem}_p{args.page:04d}.png")
    pix.save(out)
    print(f"rendered {args.pdf.name} p{args.page} -> {out} ({pix.width}x{pix.height} px)", flush=True)
    return 0


def cmd_text(args) -> int:
    """Print a page's own text layer verbatim (no OCR, no normalisation)."""
    doc = pymupdf.open(args.pdf)
    raw = doc.load_page(args.page - 1).get_text("text")
    doc.close()
    print(f"--- {args.pdf.name} page {args.page} text layer ({len(raw.strip())} chars) ---", flush=True)
    print(raw)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="OCR a PDF page and measure its accuracy.")
    ap.add_argument("mode", choices=["inventory", "ocr", "validate", "render", "text"])
    ap.add_argument("pdf", type=Path)
    ap.add_argument("page", nargs="?", type=int, default=1)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--json", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--show-diff", action="store_true")
    args = ap.parse_args()
    if not args.pdf.exists():
        print(f"no such pdf: {args.pdf}", file=sys.stderr)
        return 2
    modes = {"inventory": cmd_inventory, "ocr": cmd_ocr, "validate": cmd_validate,
             "render": cmd_render, "text": cmd_text}
    return modes[args.mode](args)


if __name__ == "__main__":
    raise SystemExit(main())
