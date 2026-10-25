"""Inspect the evidence corpus: which chunks exist for given pages / ids."""
from __future__ import annotations

import json
import sys
from pathlib import Path

DATA = Path(r"C:\Users\Gershon\Desktop\WORKSPACE\Ai-Brain-Map\src\data")


def chunks_of(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(obj, dict):
        for key in ("chunks", "items", "documents"):
            if key in obj and isinstance(obj[key], (list, dict)):
                obj = obj[key]
                break
    if isinstance(obj, list):
        return {c.get("chunk_id") or c.get("id"): c for c in obj}
    return obj


def main() -> int:
    pages = [int(a) for a in sys.argv[1:]] or [35, 141, 146]
    for name in ("seed-evidence.json", "evidence-bundle-2.json"):
        p = DATA / name
        if not p.exists():
            print(f"{name}: MISSING")
            continue
        ch = chunks_of(p)
        print(f"{name}: {len(ch)} chunks")
        for cid, c in ch.items():
            page = c.get("page")
            if cid and (any(f"p{pg:04d}" in cid for pg in pages) or page in pages):
                text = c.get("text", "")
                print(f"  {cid}  page={page}  {len(text)} chars")
                print(f"    text[:120]={text[:120]!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
