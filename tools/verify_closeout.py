"""Verify the closeout deliverables myself: coverage service must COMPUTE, not restate.

Checks
  A. coverage-service.ts exists, imports the real loaders, and contains no hard-coded totals
  B. it really computes: adjacency/union-find over edges, substring test against chunk text
  C. Test Q asserts every number and is non-vacuous (counts assertions)
  D. the panel is wired into the app (App.tsx imports + NavPane entry)
"""
import json, re
from pathlib import Path

HERE = Path(r"C:\Users\Gershon\.cline\data\workspaces\chat\hi5-graph-supervisor")
APP = HERE / "_app_files"
OUT = HERE / "_w23_verify_closeout.txt"


def decode(*names):
    for name in names:
        p = APP / ("src__" + name)
        if not p.exists():
            p = APP / name
        if not p.exists():
            continue
        raw = p.read_text(encoding="utf-8", errors="replace")
        m = re.match(r'\s*export default\s+(".*")\s*;?\s*$', raw, re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                return raw
        return raw
    return ""


L, P = [], []
def say(s=""):
    L.append(s)
def bad(s):
    P.append(s)


svc = decode("services__coverage-service.ts")
panel = decode("components__CoveragePanel.tsx")
app = decode("App.tsx")
nav = decode("components__NavPane.tsx")
tests = decode("tests__phase3-tests.ts")

say("== A. coverage-service.ts  chars=%d" % len(svc))
if not svc:
    bad("coverage-service.ts missing from the dump")
for token in ("getSeedGraph", "getMergedGraph", "getExpansionRegistry", "chunks"):
    say("   imports/uses %-22s %s" % (token, token in svc))
    if token not in svc:
        bad("coverage-service does not use %s" % token)

HARD = {"69": 0, "63": 0, "152": 0}
for num in HARD:
    hits = [m.start() for m in re.finditer(r"\b%s\b" % num, svc)]
    HARD[num] = len(hits)
    if hits:
        bad("coverage-service.ts hard-codes %s (%d occurrence(s)) -> %s"
            % (num, len(hits), [svc[max(0, i - 60):i + 40].replace("\n", " ") for i in hits[:2]]))
say("   hard-coded 69/63/152 totals: %s" % HARD)
say("   evidence chunk text used for the byte test: %s" % bool(re.search(r"chunks?\b", svc)))
say("   substring comparison present: %s" % ("includes(" in svc or "indexOf(" in svc))

say()
say("== B. it computes connectivity (not a stored number)")
for token in ("adjacency", "adj", "components", "visited", "Set(", "queue", "stack"):
    say("   %-12s %s" % (token, token in svc))

say()
say("== C. Test Q in the suite  chars=%d" % len(tests))
tq = tests.find("Test Q")
say("   present: %s" % (tq > 0))
if tq <= 0:
    bad("Test Q missing")
else:
    block = tests[tq:]
    n_if = len(re.findall(r"qErrors\.push", block))
    say("   qErrors.push assertions: %d" % n_if)
    if n_if < 8:
        bad("Test Q has only %d assertions - check it is not vacuous" % n_if)
    for num in ("69", "63", "152", "104", "48", "36", "35", "7"):
        ok = bool(re.search(r"!==\s*%s\b" % num, block)) or bool(re.search(r"===\s*%s\b" % num, block))
        say("   pins %-4s %s" % (num, ok))
        if not ok:
            bad("Test Q does not pin %s" % num)
    say("   calls computeCoverageReport(): %s" % ("computeCoverageReport(" in block))

say()
say("== D. wiring")
say("   App.tsx imports CoveragePanel: %s" % ("CoveragePanel" in app))
say("   App.tsx renders <CoveragePanel: %s" % ("<CoveragePanel" in app))
say("   NavPane mentions coverage: %s" % (bool(re.search(r"coverage", nav, re.I))))
say("   NavPane chars=%d" % len(nav))
say("   CoveragePanel chars=%d, uses report props: %s" % (
    len(panel), bool(re.search(r"coverage|report", panel, re.I))))
if "CoveragePanel" not in app:
    bad("App.tsx does not import the panel")
if "<CoveragePanel" not in app:
    bad("App.tsx does not render the panel")
if not re.search(r"coverage", nav, re.I):
    bad("NavPane has no coverage entry")

say()
say("PROBLEMS: %d" % len(P))
for x in P:
    say("  - " + x)
OUT.write_text("\n".join(L), encoding="utf-8")
print("PROBLEMS=%d" % len(P))
