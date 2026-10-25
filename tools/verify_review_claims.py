"""Machine-audit an external reviewer's claims against src/data.

Written after a Gemini review returned 15 confident per-edge verdicts on 15 edge ids that did not
exist. The claims below are the ones that review actually made; edit them to audit a new review.

Usage:  python tools/verify_review_claims.py
Output: prints, per claim, EXISTS / DOES NOT EXIST and VERBATIM / NORMALISED / NOT FOUND.
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "src" / "data"

# --- claims made by the reviewer (Gemini, 2026-10-25, pass 1) ---
CLAIM_EDGES = [
    "edge-cassette-on-freehub", "edge-rotor-on-hub-6bolt", "edge-rotor-centerlock-fit",
    "edge-quill-stem-in-steerer", "edge-hub-motor-in-wheel", "edge-chain-drives-cassette",
    "edge-freewheel-allows-rotation", "edge-remover-tool-engages-lockring",
    "edge-shift-wire-retention", "edge-top-cap-compresses-spacers",
    "edge-brake-pad-thickness-inspection", "edge-star-nut-setter-drive",
    "edge-frame-bushing-play", "edge-shock-air-chamber-extension", "edge-bms-cutoff-controller",
]
CLAIM_QUOTES = [
    "chainline... front crankset and/or front derailleur might be designed to have a chainline of 50mm...",
    "MAINTAINING YOUR TRANSMISSION \u2022 CHAIN, CASSETTE, AND CHAINSET",
    "uses six bolts on a flange built into the hub shell",
    "is designed with splined fittings to accept rotors made with a matching internal pattern. "
    "The rotor is held tight with a lockring.",
    "vertical post that inserts inside of a threaded steering column",
    "electric motor built into the hub of a wheel, directly driving the wheel",
    "allow the rear wheel to rotate while the pedals remain stationary",
    "Insert the cassette remover into the teeth of the lockring",
    "plugs into the body, and is held in by a pinch screw.",
    "The stem presses on spacers below the stem and the spacers put pressure on the bearing races and bearings.",
    "Measure brake pad thickness and replace as needed",
    "sits between battery cells and controller",
    "uses six bolts on a flange",
]


def load_chunks():
    ev = json.loads((DATA / "seed-evidence.json").read_text(encoding="utf-8"))
    chunks = ev.get("chunks", ev)
    if isinstance(chunks, dict):
        return {k: (v.get("text") if isinstance(v, dict) else str(v)) for k, v in chunks.items()}
    return {c["chunk_id"]: c["text"] for c in chunks}


def load_ids():
    edges, nodes = set(), set()
    for f in sorted(DATA.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for e in d.get("edges", []) or []:
            if isinstance(e, dict) and (e.get("id") or e.get("edge_id")):
                edges.add(e.get("id") or e.get("edge_id"))
        for n in d.get("nodes", []) or []:
            if isinstance(n, dict) and (n.get("id") or n.get("node_id")):
                nodes.add(n.get("id") or n.get("node_id"))
    return edges, nodes


def norm(s):
    s = (s.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
          .replace("\u2022", "*").replace("\u2013", "-").replace("\u2014", "-"))
    return re.sub(r"\s+", " ", s).strip().lower()


def main():
    texts = load_chunks()
    edges, nodes = load_ids()
    print("REAL DATA: %d chunks, %d edges, %d nodes" % (len(texts), len(edges), len(nodes)))

    hit = sum(1 for e in CLAIM_EDGES if e in edges)
    print("\nEDGE IDS: %d of %d claimed exist" % (hit, len(CLAIM_EDGES)))
    for e in CLAIM_EDGES:
        if e not in edges:
            print("   DOES NOT EXIST  %s" % e)

    normed = {k: norm(v or "") for k, v in texts.items()}
    print("\nQUOTES:")
    supported = 0
    for q in CLAIM_QUOTES:
        exact = [k for k, v in texts.items() if q in v]
        near = [] if exact else [k for k, v in normed.items() if norm(q).replace("...", "") in v]
        if exact:
            supported += 1
            print("   VERBATIM    %s  <- %s" % (exact[0], q[:70]))
        elif near:
            supported += 1
            print("   NORMALISED  %s  <- %s" % (near[0], q[:70]))
        else:
            print("   NOT FOUND   %s" % q[:80])
    print("\n%d of %d quotes are supported by a chunk" % (supported, len(CLAIM_QUOTES)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
