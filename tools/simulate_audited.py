"""Verify the re-quoted sentences and SIMULATE the audited batches, in memory, from the real files.

Nothing is written. This is the independent recompute the review asked for: the numbers in
AUDIT_v2.md must come from here, not from arithmetic done by hand.
"""
import json, re
from pathlib import Path

REPO = Path(r"C:\Users\Gershon\Desktop\WORKSPACE\Ai-Brain-Map")
D = REPO / "src" / "data"
bundle = json.loads((D / "seed-evidence.json").read_text(encoding="utf-8"))["chunks"]
OUT = Path(r"C:\Users\Gershon\.cline\data\workspaces\chat\hi5-graph-supervisor\_sim_audited.txt")

def nz(s):
    return re.sub(r"\s+", " ", s or "").strip()

QUOTES = [
    ("big_blue_book_p0663_c00", "Brake pads are housed in the caliper and are forced against the rotor"),
    ("big_blue_book_p0663_c00", "Brake pads are housed in the caliper"),
    ("big_blue_book_p0710_c00", "Hayes® offers brakes in both mineral oil and hydraulic brakes using DOT 3 or DOT 4 brake fluid."),
    ("bike_repair_manual_chris_p0088_c00", "the part of the fork known as the steerer tube"),
    ("bike_repair_manual_chris_p0088_c00", "both hold the front fork securely in the head tube"),
    ("bike_repair_manual_chris_p0089_c00", "turns the fork and the front wheel"),
    ("bike_repair_manual_chris_p0148_c00", "The rear triangle of the frame, which connects the rear wheel to the shock absorber"),
    ("bike_repair_manual_chris_p0002_c02", "Tighten crank puller to extract crank arm from bottom bracket spindle."),
    ("bike_repair_manual_chris_p0003_c00", "countersunk bolt holes for chainring attachment"),
]

L = ["== quoted sentences, byte-literal in the bundle?"]
bad = 0
for cid, q in QUOTES:
    ok = cid in bundle and q in bundle[cid]["text"]
    soft = (not ok) and cid in bundle and nz(q) in nz(bundle[cid]["text"])
    L.append("  %-38s %s%s" % (cid, "OK" if ok else "FAIL", " (whitespace-only)" if soft else ""))
    if not ok:
        bad += 1
L.append("  failures: %d" % bad)

# ---- simulate
FILES = ["seed_graph.json", "expansion-brakes.json", "expansion-cockpit.json",
         "expansion-drivetrain.json", "expansion-rearshock.json", "expansion-quillstem.json",
         "expansion-cassette.json", "expansion-hubfit.json", "expansion-connectors.json"]
nodes, edges = [], []
for f in FILES:
    d = json.loads((D / f).read_text(encoding="utf-8"))
    nodes += d.get("nodes") or []
    edges += d.get("edges") or []

NEW_NODES = [
    ("comp-fork", "component", "bike_repair_manual_chris_p0089_c00", "turns the fork and the front wheel"),
    ("comp-crank-arm", "component", "bike_repair_manual_chris_p0002_c02", "extract crank arm from bottom bracket spindle"),
    ("comp-chainring", "subcomponent", "bike_repair_manual_chris_p0003_c00", "countersunk bolt holes for chainring attachment"),
    ("comp-rear-triangle", "component", "bike_repair_manual_chris_p0148_c00", "connects the rear wheel to the shock absorber"),
]
NEW_EDGES = [
    ("comp-brake-pad", "comp-rotor-6bolt", "interfaces_with", "big_blue_book_p0663_c00", "verified"),
    ("comp-caliper-hydraulic", "comp-brake-pad", "contains", "big_blue_book_p0663_c00", "verified"),
    ("prop-fluid-dot", "comp-caliper-hydraulic", "interfaces_with", "big_blue_book_p0710_c00", "verified"),
    ("comp-headset", "comp-fork", "interfaces_with", "bike_repair_manual_chris_p0088_c00", "verified"),
    ("comp-steerer", "comp-fork", "part_of", "bike_repair_manual_chris_p0088_c00", "verified"),
    ("comp-fork", "sys-wheels", "interfaces_with", "bike_repair_manual_chris_p0089_c00", "needs_review"),
    ("comp-rear-triangle", "comp-rear-shock", "interfaces_with", "bike_repair_manual_chris_p0148_c00", "verified"),
    ("comp-rear-triangle", "sys-wheels", "interfaces_with", "bike_repair_manual_chris_p0148_c00", "verified"),
    ("comp-crank-arm", "comp-bb-threaded", "mounted_on", "bike_repair_manual_chris_p0002_c02", "verified"),
    ("comp-chainring", "comp-crank-arm", "mounted_on", "bike_repair_manual_chris_p0003_c00", "needs_review"),
]

sim_nodes = nodes + [{"id": i, "type": t, "status": "verified",
                      "evidence": [{"chunk_id": c, "quote": q}]} for i, t, c, q in NEW_NODES]
sim_edges = edges + [{"src": s, "dst": d_, "type": t, "status": st,
                      "evidence": [{"chunk_id": c, "quote": ""}]} for s, d_, t, c, st in NEW_EDGES]

ids = {n["id"] for n in sim_nodes}
dangling = [(e["src"], e["dst"]) for e in sim_edges if e["src"] not in ids or e["dst"] not in ids]

cited = set()
ncites = 0
for n in sim_nodes:
    for ev in n.get("evidence") or []:
        cited.add(ev.get("chunk_id"))
        ncites += 1
for e in sim_edges:
    for ev in e.get("evidence") or []:
        cited.add(ev.get("chunk_id"))
        ncites += 1

adj = {i: set() for i in ids}
for e in sim_edges:
    if e["src"] in adj and e["dst"] in adj:
        adj[e["src"]].add(e["dst"])
        adj[e["dst"]].add(e["src"])
seen, comps = set(), []
for i in ids:
    if i in seen:
        continue
    st, comp = [i], []
    seen.add(i)
    while st:
        v = st.pop()
        comp.append(v)
        for w in adj[v]:
            if w not in seen:
                seen.add(w)
                st.append(w)
    comps.append(sorted(comp))
comps.sort(key=len, reverse=True)

L.append("")
L.append("== simulated audited batches")
L.append("  nodes=%d edges=%d citations=%d" % (len(sim_nodes), len(sim_edges), ncites))
L.append("  dangling=%s" % (dangling or "none"))
L.append("  cited distinct=%d of %d ; unused=%d" % (len(cited), len(bundle), len(bundle) - len(cited)))
L.append("  unused ids: %s" % sorted(set(bundle) - cited))
L.append("  components=%d, sizes=%s" % (len(comps), [len(c) for c in comps]))
L.append("  largest=%d (%d%%)" % (len(comps[0]), round(100 * len(comps[0]) / len(ids))))
for c in comps[1:]:
    L.append("    island: %s" % (c if len(c) < 6 else c[:6] + ["..."]))

OUT.write_text("\n".join(L), encoding="utf-8")
print("\n".join(L))
