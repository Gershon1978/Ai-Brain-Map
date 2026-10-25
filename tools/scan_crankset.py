"""Prove the crankset island is evidence-starved, not mis-built.

Scans the bundle for sentences that mention the crankset and classify them as INSTALLED-relationship
("threads into", "presses in", "mounted on", "shell") vs REMOVAL ("extract", "puller", "remove").
The rule that demoted comp-crank-arm -> comp-bb-threaded is applied literally here: a removal step
never counts as an installed state.

Run: python tools/scan_crankset.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data"
OUT = ROOT / "docs" / "crankset_evidence_scan.txt"

SUBJ = re.compile(r"crank|chainring|chain set|chainset|bottom bracket|\bbb\b|spindle", re.I)
INSTALL = re.compile(r"\bthread(?:s|ed)?\b|\binstall|\bpress(?:es|ed)?\b|\bmount(?:s|ed)?\b|\bfits?\b|"
                     r"\bheld\b|\bshell\b|\bsecure|\bbolted\b|\battached\b", re.I)
REMOVE = re.compile(r"\bextract|\bremov|\bpuller\b|\bloosen|\bunscrew|\bundo\b|\bdisassembl", re.I)
# A sentence can name the shell/threading without asserting any relationship ("confirm shell width").
PROCEDURAL = re.compile(r"^\s*(confirm|check|measure|ensure|verify|select|choose|note)\b", re.I)


def main():
    chunks = json.loads((DATA / "seed-evidence.json").read_text(encoding="utf-8"))["chunks"]
    installed, removal, procedural = [], [], []
    for cid, c in chunks.items():
        text = c["text"] if isinstance(c, dict) else str(c)
        for m in re.finditer(r"[^.\n]{0,200}[.!?]", text):
            s = m.group(0).strip()
            if not s or not SUBJ.search(s):
                continue
            if REMOVE.search(s):
                removal.append((cid, s))
            elif INSTALL.search(s):
                (procedural if PROCEDURAL.match(s) else installed).append((cid, s))

    L = ["== crankset attachment evidence scan", ""]
    L.append("sentences asserting an installed relationship: %d" % len(installed))
    for cid, s in installed:
        L.append("  CANDIDATE %s | %s" % (cid, s[:200]))
    L.append("")
    L.append("sentences naming shell/threading but only asking the mechanic to confirm a spec: %d" % len(procedural))
    for cid, s in procedural:
        L.append("  PROCEDURAL %s | %s" % (cid, s[:200]))
    L.append("")
    L.append("removal / service steps (do not count as installed state): %d" % len(removal))
    for cid, s in removal:
        L.append("  REMOVAL   %s | %s" % (cid, s[:200]))
    L.append("")
    L.append("VERDICT: %s" % ("NO installed-relationship sentence exists in the bundle. The 3-node "
                              "crankset island is evidence-starved, not mis-modelled; closing it "
                              "requires a bottom-bracket interface source, not more inference."
                              if not installed else
                              "%d candidate(s) require review before any edge is created" % len(installed)))
    out = "\n".join(L)
    print(out)
    OUT.write_text(out + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
