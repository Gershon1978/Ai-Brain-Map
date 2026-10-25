"""Find the brain's weak links, mechanically, so the questions asked of a research model are real.

Reports:
  * node-type census vs the types the schema allows (what the graph has never recorded)
  * edge-type census vs the relations the ontology defines (which relations are never used)
  * failure modes with no `resolves` procedure   -> "how is this fixed?"
  * symptoms with no `indicates` edge            -> "what does this point to?"
  * procedures with no tool and no component     -> "what do I need / what does it touch?"
  * nodes whose best evidence is grade C/B, or that rest on the frozen seed only
  * subsystems with thin coverage
  * measurements present vs components that need them

  python tools/weak_links.py [--json out.json]
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Users\Gershon\Desktop\WORKSPACE\Ai-Brain-Map")
DATA = ROOT / "src" / "data"
GRADE_ORDER = {"A": 0, "B+": 1, "B": 2, "C": 3, "D": 4}


def load():
    nodes, edges = [], []
    for path in [DATA / "seed_graph.json"] + sorted(DATA.glob("expansion-*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        for n in doc.get("nodes") or []:
            n["_file"] = path.name
            nodes.append(n)
        for e in doc.get("edges") or []:
            e["_file"] = path.name
            edges.append(e)
    onto = json.loads((DATA / "relation-ontology.json").read_text(encoding="utf-8"))["relations"]
    return nodes, edges, onto


def best_grade(item) -> str:
    grades = [ev.get("evidence_grade", "D") for ev in item.get("evidence") or []]
    return min(grades, key=lambda g: GRADE_ORDER.get(g, 9)) if grades else "none"


def main() -> int:
    nodes, edges, onto = load()
    by_id = {n["id"]: n for n in nodes}
    out = defaultdict(list)

    print(f"nodes {len(nodes)}  edges {len(edges)}\n")

    ntypes = Counter(n["type"] for n in nodes)
    print("NODE TYPES")
    for t in ["component", "subcomponent", "symptom", "failure_mode", "procedure", "measurement",
              "standard", "property", "diagnostic_test", "tool", "compatibility_rule", "safety_constraint",
              "material", "interface", "unknown_requirement"]:
        print(f"  {t:20s} {ntypes.get(t, 0)}")

    etypes = Counter(e["type"] for e in edges)
    print("\nEDGE TYPES")
    for t, c in etypes.most_common():
        print(f"  {t:28s} {c}")
    print("\n  ontology relations never used: "
          + ", ".join(r for r in onto if r not in etypes))

    indeg, outdeg = Counter(), Counter()
    for e in edges:
        outdeg[e["src"]] += 1
        indeg[e["dst"]] += 1
    has_resolves = {e["dst"] for e in edges if e["type"] == "resolves"}

    print("\nFAILURE MODES WITH NO FIX RECORDED")
    for n in nodes:
        if n["type"] == "failure_mode" and n["id"] not in has_resolves:
            incoming = [(e["src"], e["type"]) for e in edges if e["dst"] == n["id"]]
            print(f"  {n['id']:34s} deg_in={len(incoming)}  best_grade={best_grade(n)}")
            out["failure_mode_no_fix"].append(n["id"])

    print("\nSYMPTOMS WITH NO OUTGOING EDGE (cannot be used to diagnose anything)")
    for n in nodes:
        if n["type"] == "symptom" and outdeg[n["id"]] == 0:
            print(f"  {n['id']}")
            out["symptom_no_outgoing"].append(n["id"])

    print("\nPROCEDURES (what do they need / what do they touch?)")
    for n in nodes:
        if n["type"] == "procedure":
            print(f"  {n['id']:34s} out={outdeg[n['id']]} in={indeg[n['id']]}")

    print("\nNODES WHOSE BEST EVIDENCE IS NOT GRADE A")
    for n in nodes:
        g = best_grade(n)
        if g in {"B+", "B", "C", "D"}:
            print(f"  {n['id']:34s} {n['type']:14s} grade={g} file={n['_file']}")
            out["weak_evidence_node"].append(n["id"])

    print("\nSUBSYSTEM COVERAGE (components/subcomponents per subsystem)")
    per_sub = Counter(n.get("subsystem", "(none)") for n in nodes
                      if n["type"] in {"component", "subcomponent"})
    for sub, c in per_sub.most_common():
        print(f"  {sub:20s} {c}")

    print("\nMEASUREMENTS RECORDED")
    for n in nodes:
        if n["type"] == "measurement":
            print(f"  {n['id']:34s} {n['name']}")

    if "--json" in __import__("sys").argv:
        i = __import__("sys").argv.index("--json")
        Path(__import__("sys").argv[i + 1]).write_text(
            json.dumps(dict(out), indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
