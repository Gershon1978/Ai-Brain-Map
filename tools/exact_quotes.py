"""For each planned quote, print the EXACT substring of the chunk, newlines included.

A quote that only matches after whitespace collapse is not a literal quote; this turns each planned
sentence into the byte-exact text the batch must copy.
"""
import json, re
from pathlib import Path

REPO = Path(r"C:\Users\Gershon\Desktop\WORKSPACE\Ai-Brain-Map")
bundle = json.loads((REPO / "src/data/seed-evidence.json").read_text(encoding="utf-8"))["chunks"]
OUT = Path(r"C:\Users\Gershon\.cline\data\workspaces\chat\hi5-graph-supervisor\_exact_quotes.txt")

PLAN = [
    ("8a pad->rotor", "big_blue_book_p0663_c00",
     "Brake pads are housed in the caliper and are forced against the rotor"),
    ("8a caliper->pad", "big_blue_book_p0663_c00",
     "Brake pads are housed in the caliper"),
    ("8a dot->caliper", "big_blue_book_p0710_c00",
     "Hayes® offers brakes in both mineral oil and hydraulic brakes using DOT 3 or DOT 4 brake fluid."),
    ("8b headset->fork", "bike_repair_manual_chris_p0088_c00",
     "both hold the front fork securely in the head tube"),
    ("8b steerer->fork", "bike_repair_manual_chris_p0088_c00",
     "the part of the fork known as the steerer tube"),
    ("8b fork->wheels", "bike_repair_manual_chris_p0089_c00",
     "turns the fork and the front wheel"),
    ("8c rear-triangle", "bike_repair_manual_chris_p0148_c00",
     "The rear triangle of the frame, which connects the rear wheel to the shock absorber"),
    ("8c crank->bb", "bike_repair_manual_chris_p0002_c02",
     "Tighten crank puller to extract crank arm from bottom bracket spindle."),
    ("8c chainring->crank", "bike_repair_manual_chris_p0003_c00",
     "countersunk bolt holes for chainring attachment"),
]

L = []
for label, cid, quote in PLAN:
    text = bundle[cid]["text"]
    if quote in text:
        L.append("%-22s %-38s EXACT as written" % (label, cid))
        L.append("    %s" % json.dumps(quote, ensure_ascii=False))
        continue
    # find the span, allowing any whitespace where the sentence has a space
    parts = [re.escape(p) for p in quote.split()]
    rx = re.compile(r"\s+".join(parts))
    m = rx.search(text)
    if not m:
        L.append("%-22s %-38s *** NOT FOUND ***" % (label, cid))
        continue
    exact = m.group(0)
    L.append("%-22s %-38s needs %d line break(s)" % (label, cid, exact.count("\n")))
    L.append("    %s" % json.dumps(exact, ensure_ascii=False))
L.append("")
L.append("Copy the string on the indented line into the JSON quote field verbatim. \\n stays a real")
L.append("newline inside the JSON string (written as the two characters backslash-n).")

OUT.write_text("\n".join(L), encoding="utf-8")
print("\n".join(L))
