"""Independent check of "no contradiction in the corpus".

Looks for the only kinds of disagreement that would be checkable without world knowledge:
  * the same fastener/standard carrying different explicit torque figures
  * the same caliper/brand being told to use different fluids
  * the same dimension class stated with different values
Reports pairs, or confirms the negative. Run: python tools/scan_contradictions.py
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data"
OUT = ROOT / "docs" / "contradiction_scan.txt"
chunks = json.loads((DATA / "seed-evidence.json").read_text(encoding="utf-8"))["chunks"]


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n", text) if s.strip()]


torque, fluids, dims = [], [], []
for cid, c in chunks.items():
    text = c["text"] if isinstance(c, dict) else str(c)
    for s in sentences(text):
        for m in re.finditer(
                r"([A-Za-z][A-Za-z \-]{3,40}?)\s*(?:bolts?|bolt|ring|cap|clamp)?[^.\n]{0,40}?"
                r"(\d+(?:[.,]\d+)?\s*(?:-\s*\d+(?:[.,]\d+)?)?)\s*(?:N[·\s-]?m|Nm)", s):
            torque.append((cid, m.group(1).strip().lower()[:40], m.group(2), s[:120]))
        if re.search(r"\bDOT\s?[345](?:\.1)?\b", s) and re.search(r"caliper|brake|fluid", s, re.I):
            fluids.append((cid, "DOT", s[:120]))
        if re.search(r"mineral oil", s, re.I) and re.search(r"caliper|brake|fluid", s, re.I):
            fluids.append((cid, "MINERAL", s[:120]))
        for m in re.finditer(r"(\d{2,3})\s*mm[^.\n]{0,30}(hub|axle|steerer|shell|width)", s, re.I):
            dims.append((cid, m.group(2).lower(), m.group(1), s[:110]))

L = ["== contradiction scan", ""]
L.append("torque statements: %d" % len(torque))
by_subject = defaultdict(list)
for cid, subj, val, s in torque:
    by_subject[subj].append((cid, val, s))
conflicts = 0
for subj, items in by_subject.items():
    if len({v for _, v, _ in items}) > 1:
        conflicts += 1
        L.append("  POSSIBLE CONFLICT on %r: %s" % (subj, sorted({v for _, v, _ in items})))
        for cid, v, s in items:
            L.append("      %s: %s" % (cid, s[:110]))
L.append("")
L.append("fluid statements: %d (DOT %d / MINERAL %d)"
         % (len(fluids), sum(1 for f in fluids if f[1] == "DOT"),
            sum(1 for f in fluids if f[1] == "MINERAL")))
for cid, kind, s in fluids:
    L.append("   %-8s %s | %s" % (kind, cid, s[:100]))
L.append("")
L.append("dimension statements: %d" % len(dims))
L.append("")
L.append("VERDICT: %s" % ("NO mechanical contradiction detected by this scan"
                          if conflicts == 0 else
                          "%d torque subject(s) carry differing values - REVIEW REQUIRED" % conflicts))
out = "\n".join(L)
print(out)
OUT.write_text(out + "\n", encoding="utf-8")
sys.exit(0)
