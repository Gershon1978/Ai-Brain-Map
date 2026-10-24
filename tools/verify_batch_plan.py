"""Authoritative checker for a proposed batch: it consumes the EXACT proposed records and verifies
them, instead of counting things that were never validated.

Fails (exit 1) on: a quote that is not byte-exact, an empty/missing quote, a dangling endpoint, an
illegal relation or endpoint type, a duplicate edge/id, a `verified` claim resting on the
[VISUAL DATA] part of a chunk, or disagreement between recomputed totals and CLAIMED.
"""
import json, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data"
FILES = ["seed_graph.json", "expansion-brakes.json", "expansion-cockpit.json",
         "expansion-drivetrain.json", "expansion-rearshock.json", "expansion-quillstem.json",
         "expansion-cassette.json", "expansion-hubfit.json", "expansion-connectors.json"]

A = "big_blue_book_p0663_c00"
BL = "bike_repair_manual_chris_"
PROPOSED_NODES = [
    {"id": "comp-fork", "type": "component", "name": "Fork", "status": "verified",
     "evidence": [{"chunk_id": BL + "p0089_c00", "quote": "turns\nthe fork and the front wheel"}]},
    {"id": "comp-crank-arm", "type": "component", "name": "Crank Arm", "status": "verified",
     "evidence": [{"chunk_id": BL + "p0002_c02",
                   "quote": "Tighten crank puller to extract crank arm from bottom bracket spindle."}]},
    {"id": "comp-chainring", "type": "subcomponent", "name": "Chainring", "status": "needs_review",
     "evidence": [{"chunk_id": BL + "p0003_c00",
                   "quote": "countersunk bolt holes for chainring attachment"}]},
    {"id": "comp-rear-triangle", "type": "component", "name": "Rear Triangle", "status": "verified",
     "evidence": [{"chunk_id": BL + "p0148_c00",
                   "quote": "The rear triangle of the frame,\nwhich connects the rear wheel to the shock\nabsorber"}]},
]

def E(id_, src, dst, type_, status, claim, cid, quote):
    return {"id": id_, "src": src, "dst": dst, "type": type_, "status": status, "claim": claim,
            "evidence": [{"chunk_id": cid, "quote": quote}]}

RT = "The rear triangle of the frame,\nwhich connects the rear wheel to the shock\nabsorber"
PROPOSED_EDGES = [
    E("edge-conn4-pad-against-rotor", "comp-brake-pad", "comp-rotor-6bolt", "interfaces_with",
      "verified", "Brake pads are forced against the rotor to slow the bike.", A,
      "Brake pads are housed in the caliper and are forced against the rotor"),
    E("edge-conn4-caliper-holds-pads", "comp-caliper-hydraulic", "comp-brake-pad", "contains",
      "verified", "The brake pads are housed in the caliper.", A,
      "Brake pads are housed in the caliper"),
    E("edge-conn4-caliper-uses-dot-fluid", "comp-caliper-hydraulic", "prop-fluid-dot",
      "has_property", "needs_review",
      "A hydraulic caliper may use DOT 3 or DOT 4 brake fluid, with mineral oil as the alternative.",
      "big_blue_book_p0710_c00",
      "Hayes\u00ae offers brakes in both mineral oil and hydraulic brakes using DOT\n3 or DOT 4 brake fluid."),
    E("edge-conn4-headset-holds-fork", "comp-headset", "comp-fork", "interfaces_with", "verified",
      "The headset holds the front fork in the head tube.", BL + "p0088_c00",
      "both hold the front fork securely \nin the head tube"),
    E("edge-conn4-steerer-part-of-fork", "comp-steerer", "comp-fork", "part_of", "verified",
      "The steerer tube is the part of the fork that turns in the headset.", BL + "p0088_c00",
      "the part of\nthe fork known as the steerer tube"),
    E("edge-conn4-fork-turns-front-wheel", "comp-fork", "sys-wheels", "affects",
      "needs_review", "Turning the handlebar turns the fork and the front wheel together.",
      BL + "p0089_c00", "turns\nthe fork and the front wheel"),
    E("edge-conn4-reartriangle-holds-shock", "comp-rear-triangle", "comp-rear-shock",
      "interfaces_with", "verified",
      "The rear triangle connects the shock absorber to the frame.", BL + "p0148_c00", RT),
    E("edge-conn4-reartriangle-holds-wheel", "comp-rear-triangle", "sys-wheels", "affects",
      "needs_review",
      "The rear triangle links the rear wheel to the shock absorber.", BL + "p0148_c00", RT),
    E("edge-conn4-crank-on-bb-spindle", "comp-crank-arm", "comp-bb-threaded", "mounted_on",
      "verified", "The crank arm mounts on the bottom bracket spindle.", BL + "p0002_c02",
      "Tighten crank puller to extract crank arm from bottom bracket spindle."),
    E("edge-conn4-chainring-on-crank", "comp-chainring", "comp-crank-arm", "mounted_on",
      "needs_review", "The chainring bolts to the crank arm.", BL + "p0003_c00",
      "countersunk bolt holes for chainring attachment"),
]

CLAIMED = {"nodes": 73, "edges": 73, "citations": 166, "unused": 2, "components": 3,
           "largest": 69, "cited": 41, "bundle": 43,
           "node_split": {"verified": 64, "candidate": 1, "needs_review": 8},
           "edge_split": {"verified": 59, "needs_review": 14}}

# ---------------------------------------------------------------- load the real state
bundle = json.loads((DATA / "seed-evidence.json").read_text(encoding="utf-8"))["chunks"]
onto = json.loads((DATA / "relation-ontology.json").read_text(encoding="utf-8"))["relations"]
nodes, edges = [], []
for f in FILES:
    d = json.loads((DATA / f).read_text(encoding="utf-8"))
    nodes += d.get("nodes") or []
    edges += d.get("edges") or []

P, W = [], []          # problems, warnings


def nz(s):
    return re.sub(r"\s+", " ", s or "").strip()


def check_evidence(label, evs, status):
    """Three-way quote verdict + the visual-boundary rule. Returns count of usable citations."""
    used = 0
    for ev in evs or []:
        cid, q = ev.get("chunk_id"), ev.get("quote")
        if not cid or not q:
            P.append("%s: empty chunk_id or quote" % label)
            continue
        rec = bundle.get(cid)
        if rec is None:
            P.append("%s: chunk %s not in bundle" % (label, cid))
            continue
        text = rec["text"]
        if q in text:
            verdict = "byte-exact"
            used += 1
        elif nz(q) and nz(q) in nz(text):
            verdict = "WHITESPACE-ONLY (not acceptable)"
            P.append("%s: quote matches only after whitespace collapse: %r" % (label, q[:80]))
            used += 1
        else:
            P.append("%s: quote NOT FOUND in %s: %r" % (label, cid, q[:80]))
            continue
        # a verified claim may not rest on the [VISUAL DATA] tail of the chunk
        mark = text.find("[VISUAL DATA]")
        if mark >= 0:
            pos = text.find(q)
            in_visual = pos > mark
            if in_visual and status == "verified":
                P.append("%s: status=verified but the quote sits in the [VISUAL DATA] part of %s"
                         % (label, cid))
            elif in_visual:
                W.append("%s: quote is inside the [VISUAL DATA] part - fine, status is %s"
                         % (label, status))
            else:
                W.append("%s: chunk %s contains a visual section, but the quote is in the prose part"
                         % (label, cid))
    return used


# ---------------------------------------------------------------- 1. evidence, record by record
cites = 0
for n in PROPOSED_NODES:
    cites += check_evidence("node " + n["id"], n.get("evidence"), n.get("status"))
for e in PROPOSED_EDGES:
    cites += check_evidence("edge " + e["id"], e.get("evidence"), e.get("status"))

# ---------------------------------------------------------------- 2. ids, endpoints, relations
existing_ids = {n["id"] for n in nodes}
node_type = {n["id"]: n.get("type") for n in nodes}
for n in PROPOSED_NODES:
    if n["id"] in existing_ids:
        P.append("node id already exists: " + n["id"])
    existing_ids.add(n["id"])
    node_type[n["id"]] = n["type"]

seen_edges = {"%s|%s|%s" % (e["src"], e["type"], e["dst"]) for e in edges}
seen_ids = {e.get("id") for e in edges}
for e in PROPOSED_EDGES:
    for end in (e["src"], e["dst"]):
        if end not in existing_ids:
            P.append("edge %s: dangling endpoint %s" % (e["id"], end))
    key = "%s|%s|%s" % (e["src"], e["type"], e["dst"])
    if key in seen_edges:
        P.append("edge %s duplicates an existing src|type|dst: %s" % (e["id"], key))
    seen_edges.add(key)
    if e["id"] in seen_ids:
        P.append("edge id already exists: " + e["id"])
    seen_ids.add(e["id"])
    spec = onto.get(e["type"])
    if spec is None:
        P.append("edge %s: relation %r is not in the ontology" % (e["id"], e["type"]))
        continue
    st, dt = node_type.get(e["src"]), node_type.get(e["dst"])
    if st not in (spec.get("allowed_source_types") or []):
        P.append("edge %s: source type %r not allowed for %s (allowed %s)"
                 % (e["id"], st, e["type"], spec.get("allowed_source_types")))
    if dt not in (spec.get("allowed_target_types") or []):
        P.append("edge %s: target type %r not allowed for %s (allowed %s)"
                 % (e["id"], dt, e["type"], spec.get("allowed_target_types")))

# ---------------------------------------------------------------- 3. recompute everything
sim_nodes = nodes + PROPOSED_NODES
sim_edges = edges + PROPOSED_EDGES
all_cites = 0
cited = set()
for coll in (sim_nodes, sim_edges):
    for it in coll:
        for ev in it.get("evidence") or []:
            if ev.get("quote"):
                all_cites += 1
                cited.add(ev.get("chunk_id"))

ids = {n["id"] for n in sim_nodes}
adj = {i: set() for i in ids}
for e in sim_edges:
    if e["src"] in adj and e["dst"] in adj:
        adj[e["src"]].add(e["dst"])
        adj[e["dst"]].add(e["src"])
seen, comps = set(), []
for i in ids:
    if i in seen:
        continue
    stack, comp = [i], []
    seen.add(i)
    while stack:
        v = stack.pop()
        comp.append(v)
        for w in adj[v]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    comps.append(sorted(comp))
comps.sort(key=len, reverse=True)

node_split = dict(Counter(n.get("status") for n in sim_nodes))
edge_split = dict(Counter(e.get("status") for e in sim_edges))
got = {"nodes": len(sim_nodes), "edges": len(sim_edges), "citations": all_cites,
       "unused": len(bundle) - len(cited), "components": len(comps),
       "largest": len(comps[0]), "cited": len(cited), "bundle": len(bundle),
       "node_split": node_split, "edge_split": edge_split}

for k, want in CLAIMED.items():
    if got.get(k) != want:
        P.append("CLAIMED %s = %r but recomputed %r" % (k, want, got.get(k)))
if got["citations"] != all_cites:
    P.append("citation count inconsistent")

# ---------------------------------------------------------------- report
L = []
L.append("== proposed nodes: %d, proposed edges: %d, citations in the proposal: %d"
         % (len(PROPOSED_NODES), len(PROPOSED_EDGES), cites))
bundle_c = "%d of %d" % (len(cited), len(bundle))
L.append("== recomputed: nodes=%d edges=%d citations=%d cited=%s unused=%d components=%d largest=%d"
         % (got["nodes"], got["edges"], got["citations"], bundle_c, got["unused"],
            got["components"], got["largest"]))
L.append("   node split: %s" % node_split)
L.append("   edge split: %s" % edge_split)
L.append("   component sizes: %s" % [len(c) for c in comps])
L.append("   unused chunks: %s" % sorted(set(bundle) - cited))
L.append("")
L.append("WARNINGS: %d" % len(W))
for w in W:
    L.append("  - " + w)
L.append("PROBLEMS: %d" % len(P))
for p in P:
    L.append("  - " + p)
L.append("")
L.append("VERDICT: %s" % ("PASS - proposal verified" if not P else "FAIL - do not insert"))

out = "\n".join(L)
print(out)
Path(ROOT / "docs" / "batch_plan_verification.txt").write_text(out + "\n", encoding="utf-8")
sys.exit(1 if P else 0)


