"""Guard: every src/data/expansion-*.json must be registered in src/services/graph-loader.ts.

The independent verifier GLOBS the data directory; the app imports statically through a registry.
That asymmetry let a new batch be counted by the verifier while the app silently served an older
graph — the suite passed against the old numbers. This check removes the asymmetry.

Usage: python tools/verify_registry.py     (exit 1 on any mismatch)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data"
LOADER = ROOT / "src" / "services" / "graph-loader.ts"


def main():
    files = sorted(p.name for p in DATA.glob("expansion-*.json"))
    src = LOADER.read_text(encoding="utf-8")
    imported = set(re.findall(r"from '\.\./data/(expansion-[a-z0-9-]+\.json)'", src))
    registered = set(re.findall(r"^\s+(expansion[A-Za-z]+Json) as unknown as ExpansionFile", src, re.M))

    problems = []
    for f in files:
        if f not in imported:
            problems.append("NOT IMPORTED: %s (verifier will count it, the app will not)" % f)
    for f in sorted(imported):
        if f not in files:
            problems.append("IMPORTED BUT MISSING: %s" % f)
        elif not re.search(r"import expansion\w+Json from '\.\./data/%s';" % re.escape(f), src):
            problems.append("IMPORT WITHOUT REGISTRY USE: %s" % f)

    # each import's local symbol must appear in the registry array
    reg_block = src.split("const expansionRegistry", 1)[-1]
    for m in re.finditer(r"import (expansion\w+Json) from '\.\./data/(expansion-[a-z0-9-]+\.json)';", src):
        symbol, fname = m.group(1), m.group(2)
        if symbol not in reg_block:
            problems.append("IMPORTED BUT NOT REGISTERED: %s (%s)" % (fname, symbol))

    print("expansion files on disk: %d" % len(files))
    print("imported: %d   registry symbols: %d" % (len(imported), len(registered)))
    if problems:
        print("\nPROBLEMS: %d" % len(problems))
        for p in problems:
            print("  - " + p)
        return 1
    print("\nOK - every expansion file is imported and registered; app and verifier agree on the file set")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
