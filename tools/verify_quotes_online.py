"""Does a citation's quote ACTUALLY appear on the page it cites?

This is the gate the first data sheet walked straight through. `validate_research_datasheet.py` checks
that a value appears in its own quote; it cannot know the quote was invented. The only defence is to
fetch the source and look.

  python tools/verify_quotes_online.py <rows.json> [--report out.json] [--max 25]

Verdicts per row:
  FOUND          quote present in the fetched document text (whitespace-normalised)
  NOT_FOUND      fetched the page, quote absent  -> the citation is fabricated or paraphrased
  UNFETCHABLE    the page could not be retrieved (403/404/timeout) -> unproven, not disproven
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36")


def fetch(url: str, timeout: int = 25) -> tuple[str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        charset = resp.headers.get_content_charset() or "utf-8"
    text = raw.decode(charset, errors="replace")
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = html.unescape(text)
    return text, "skipped"


def norm(s: str) -> str:
    s = s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u00a0", " ").replace("\u2013", "-").replace("\u2014", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("rows", type=Path)
    ap.add_argument("--report", default=None)
    ap.add_argument("--max", type=int, default=25)
    args = ap.parse_args()

    rows = json.loads(args.rows.read_text(encoding="utf-8"))
    cache: dict[str, str] = {}
    results = []
    counts = {"FOUND": 0, "NOT_FOUND": 0, "UNFETCHABLE": 0}

    for i, row in enumerate(rows[: args.max], 1):
        url = row.get("source_url") or ""
        quote = norm(str(row.get("quote") or ""))
        if url not in cache:
            try:
                text, _ = fetch(url)
                cache[url] = norm(text)
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, Exception) as exc:  # noqa: BLE001
                cache[url] = f"__ERROR__{exc}"
        page = cache[url]
        if page.startswith("__ERROR__"):
            verdict = "UNFETCHABLE"
        elif not quote or quote == "not stated in allowed sources":
            verdict = "NOT_FOUND"
        elif quote in page:
            verdict = "FOUND"
        else:
            # allow the quote to be present with different dash/quote characters already normalised,
            # but not to be "close": close means paraphrased, which is still a fabrication.
            verdict = "NOT_FOUND"
        counts[verdict] += 1
        results.append({"row": i, "verdict": verdict, "url": url,
                        "fastener": row.get("fastener_or_part"), "quote": row.get("quote")})
        flag = {"FOUND": "ok  ", "NOT_FOUND": "FAIL", "UNFETCHABLE": "????"}[verdict]
        print(f"{flag} #{i:2d} {str(row.get('fastener_or_part'))[:36]:36s} {url[:70]}")

    print(f"\nFOUND {counts['FOUND']}  NOT_FOUND {counts['NOT_FOUND']}  UNFETCHABLE {counts['UNFETCHABLE']}")
    if args.report:
        Path(args.report).write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {args.report}")
    return 0 if counts["NOT_FOUND"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
