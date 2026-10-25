"""Enforce the rules in docs/RESEARCH_BRIEF.md on a returned data sheet.

A research model returns JSON that looks authoritative. This decides which rows may enter the graph:

  REJECT  a value that does not appear in its own quote; a missing quote / retrieved_at / URL;
          a domain outside the allowlist; a mismatched min/max; a duplicate row.
  PENDING a row whose source_url is a hub page (e.g. /en/service), because it cannot be re-checked.
  ACCEPT  everything else - still not ingested automatically, but eligible.

  python tools/validate_research_datasheet.py <datasheet.json> [--accepted out.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ALLOWED_DOMAINS = {
    "www.sram.com", "sram.com", "www.parktool.com", "parktool.com",
    "si.shimano.com", "www.giant-bicycles.com", "giant-bicycles.com",
    "www.trekbikes.com", "trekbikes.com",
    "www.iso.org", "iso.org", "www.etrto.org", "etrto.org",
}
REQUIRED = ["gap", "component", "fastener_or_part", "field", "value", "unit", "applies_to",
            "source_id", "source_title", "source_url", "page", "quote", "retrieved_at",
            "confidence", "notes"]
FIELDS = {"torque", "dimension", "test_threshold", "tool", "symptom", "cause", "fix", "standard_name"}
NUMERIC_FIELDS = {"torque", "dimension", "test_threshold"}
HUB_PATHS = {"/en/service", "/service", "/en-us/blog/repair-help", "/", "/global/manuals"}


def numbers_in(text: str) -> list[float]:
    out = []
    for m in re.finditer(r"\d+(?:[.,]\d+)?", text or ""):
        try:
            out.append(float(m.group(0).replace(",", ".")))
        except ValueError:
            pass
    return out


def repair_json(raw: str) -> tuple[str, list[str]]:
    """Escape stray quotes inside string VALUES and drop trailing commas. Returns (fixed, notes).

    Research output routinely contains inch marks ("1-1/8\"") that it failed to escape. That is a data
    defect worth recording, not hiding, so the caller prints the repairs.
    """
    notes = []
    out = []
    pair = re.compile(r'^(\s*"[A-Za-z_]+"\s*:\s*")(.*)("\s*,?\s*)$')
    for lineno, line in enumerate(raw.splitlines(), 1):
        m = pair.match(line)
        if m and '"' in m.group(2):
            inner = m.group(2).replace('\\"', '"').replace('"', '\\"')
            notes.append(f"line {lineno}: escaped {m.group(2).count(chr(34))} stray quote(s) in a value")
            line = m.group(1) + inner + m.group(3)
        out.append(line)
    fixed = "\n".join(out)
    fixed = re.sub(r",(\s*[}\]])", r"\1", fixed)   # trailing commas are invalid JSON
    return fixed, notes


def load_rows(path: Path) -> list:
    raw = path.read_text(encoding="utf-8").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\n", "", raw)
        raw = re.sub(r"\n```$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as first:
        fixed, notes = repair_json(raw)
        for n in notes[:12]:
            print(f"repair: {n}")
        if len(notes) > 12:
            print(f"repair: ... {len(notes) - 12} more")
        try:
            rows = json.loads(fixed)
            print(f"note: JSON repaired ({first.msg} at line {first.lineno}) -> {len(rows)} rows")
            return rows
        except json.JSONDecodeError as second:
            start, end = raw.find("["), raw.rfind("]")
            if start < 0 or end < 0:
                raise SystemExit(f"NOT JSON and not repairable: {second}")
            print(f"note: salvaged array bounds, still malformed: {second}")
            raise SystemExit(f"NOT JSON: {second}")



def check_row(row: dict) -> tuple[list[str], list[str]]:
    """Return (reasons_to_reject, warnings)."""
    reasons, warns = [], []
    for k in REQUIRED:
        if k not in row:
            reasons.append(f"missing key {k}")
    if reasons:
        return reasons, warns

    url = str(row["source_url"] or "")
    host = re.sub(r"^https?://", "", url).split("/")[0].lower()
    path = "/" + "/".join(re.sub(r"^https?://", "", url).split("/")[1:])
    if host not in ALLOWED_DOMAINS:
        reasons.append(f"domain not allowed: {host}")
    if path.rstrip("/") in HUB_PATHS:
        warns.append("hub_url: source_url is a landing page, cannot be re-checked")
    if row["field"] not in FIELDS:
        reasons.append(f"bad field {row['field']}")
    if not str(row["quote"] or "").strip():
        reasons.append("empty quote")
    if not str(row["retrieved_at"] or "").strip():
        reasons.append("missing retrieved_at")
    if row["confidence"] == "high" and not str(row["page"] or "").strip():
        reasons.append("confidence high without page")

    value = row["value"]
    if value is not None:
        if not isinstance(value, (int, float)):
            reasons.append("value is not numeric")
        elif not any(abs(n - float(value)) < 1e-6 for n in numbers_in(str(row["quote"]))):
            reasons.append(f"value {value} does not appear in its own quote")
        if row["field"] in NUMERIC_FIELDS and not str(row["unit"] or "").strip():
            reasons.append("numeric row without unit")
    lo, hi = row["min"], row["max"]
    if lo is not None and hi is not None and isinstance(value, (int, float)):
        if not (float(lo) <= float(value) <= float(hi)):
            reasons.append(f"value {value} outside min/max {lo}..{hi}")
    return reasons, warns


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("datasheet", type=Path)
    ap.add_argument("--accepted", default=None)
    args = ap.parse_args()

    rows = load_rows(args.datasheet)
    accept, pending, reject = [], [], []
    seen = set()
    for i, row in enumerate(rows, 1):
        reasons, warns = check_row(row)
        key = (row.get("gap"), row.get("component"), row.get("fastener_or_part"),
               row.get("field"), row.get("value"), row.get("applies_to"), row.get("source_url"))
        if key in seen:
            reasons.append("duplicate row")
        seen.add(key)
        if reasons:
            reject.append((i, row, reasons))
        elif warns:
            pending.append((i, row, warns))
        else:
            accept.append((i, row, []))

    print(f"rows in sheet: {len(rows)}")
    print(f"  ACCEPT  {len(accept)}")
    print(f"  PENDING {len(pending)}")
    print(f"  REJECT  {len(reject)}")

    if accept:
        print("\nACCEPTED:")
        for i, row, _ in accept:
            print(f"  #{i:3d} {row['gap']} {str(row['component'])[:18]:18s} "
                  f"{str(row['fastener_or_part'])[:34]:34s} {row['value']} {row['unit']}  [{row['source_id']}]")
    if pending:
        print("\nPENDING (not ingestible yet):")
        for i, row, w in pending:
            print(f"  #{i:3d} {row['gap']} {str(row['fastener_or_part'])[:40]:40s} {w[0]}")
    if reject:
        print("\nREJECTED:")
        for i, row, r in reject:
            print(f"  #{i:3d} {str(row.get('fastener_or_part'))[:40]:40s} {'; '.join(r)}")

    if args.accepted:
        Path(args.accepted).write_text(
            json.dumps([r for _, r, _ in accept], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nwrote {args.accepted} ({len(accept)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

