"""Independent application verifier.

Deliberately shares NO code with tools/verify_batch_plan.py: that one validates a *proposal*, this
one validates the *serialized application state*. If the two disagree, the state wins and something
is wrong with the proposal tool.

Checks every entity in the nine data files:
  * evidence chunk exists in the bundle; quote byte-exact, else whitespace-only (warn) or missing (fail)
  * a `verified` entity may not rest on the [VISUAL DATA] part of its chunk
  * edge endpoints exist; node types satisfy the ontology's allowed_source_types/allowed_target_types
  * no duplicate node ids, no duplicate src|type|dst
  * recomputed totals, status splits, citation counts, chunk coverage, components
Prints the numbers that Test Q must pin. Exit 1 on any problem.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data"
# Glob, not a hand-maintained list: a new expansion file must never be silently ignored.
FILES = ["seed_graph.json"] + sorted(p.name for p in DATA.glob("expansion-*.json"))

chunks = json.loads((DATA / "seed-evidence.json").read_text(encoding="utf-8"))["chunks"]
# Bundles 2+: pages ingested from the source PDFs' own text layer. Additive; bundle 1 is frozen.
# Globbed for the same reason FILES is: a new bundle must never be silently ignored by the verifier,
# or the app/suite/verifier trio starts disagreeing about how many chunks exist.
for _bundle in sorted(DATA.glob("evidence-bundle-*.json")):
    chunks.update(json.loads(_bundle.read_text(encoding="utf-8"))["chunks"])
onto = json.loads((DATA / "relation-ontology.json").read_text(encoding="utf-8"))["relations"]

problems, warns = [], []
known_hits, known_msgs = set(), []
# Warnings that are physically confined to the frozen seed. They are counted as a class with an
# expected size, so a NEW one anywhere - or a drift in these - fails instead of printing quietly.
frozen_soft, frozen_section = [], []
EXPECTED_FROZEN = {"whitespace_only_in_seed": 48, "undeclared_section_in_seed": 11}

# Documented exceptions. Each one is printed, never hidden, and the verifier FAILS if an entry here
# stops occurring (so the list can only shrink honestly).
KNOWN = {
    ("node", "comp-bb-threaded", "bike_repair_manual_chris_p0002_c02"):
        "seed_graph.json is frozen; its section string was truncated at ingest. Fixing it would mean "
        "editing the frozen seed for cosmetics, so it is recorded instead.",
}
nodes, edges, per_batch = [], [], []
file_of = {}
for name in FILES:
    doc = json.loads((DATA / name).read_text(encoding="utf-8"))
    nodes.extend(doc.get("nodes") or [])
    edges.extend(doc.get("edges") or [])
    for n in doc.get("nodes") or []:
        file_of[("node", n.get("id"))] = name
    for e in doc.get("edges") or []:
        file_of[("edge", e.get("id"))] = name
    batch = doc.get("batch") or ("seed" if name == "seed_graph.json" else name)
    per_batch.append((batch, len(doc.get("nodes") or []), len(doc.get("edges") or [])))

ids = [n["id"] for n in nodes]
dupe_ids = {i for i in ids if ids.count(i) > 1}
if dupe_ids:
    problems.append("duplicate node ids: %s" % sorted(dupe_ids))
node_type = {n["id"]: n.get("type") for n in nodes}

exact = soft = missing = 0
cited = set()
for kind, coll in (("node", nodes), ("edge", edges)):
    for ent in coll:
        for ev in ent.get("evidence") or []:
            cid, q = ev.get("chunk_id"), ev.get("quote") or ""
            if not cid or not q:
                problems.append("%s %s: empty chunk_id/quote" % (kind, ent.get("id")))
                continue
            rec = chunks.get(cid)
            if rec is None:
                problems.append("%s %s: chunk %s not in bundle" % (kind, ent.get("id"), cid))
                continue
            text = rec["text"]
            cited.add(cid)
            # section metadata must match the bundle record - the app's Test P checks this, and a
            # second, independent check here means the verifier does not depend on that test running.
            want_section = rec.get("section") or ""
            declared = "section" in ev
            got_section = ev.get("section") or ""
            if declared and want_section != got_section:
                key = (kind, ent.get("id"), cid)
                msg = "%s %s: section declared wrongly for %s (got %r, bundle says %r)" % (
                    kind, ent.get("id"), cid, got_section, want_section)
                if key in KNOWN:
                    known_hits.add(key)
                    known_msgs.append("%s  [known: %s]" % (msg, KNOWN[key]))
                else:
                    problems.append(msg)
            elif not declared and want_section:
                # Absence asserts nothing false, but in a batch we control it is still a metadata gap
                # that the app's Test P does not check - so there it is a FAILURE, not a warning.
                msg = ("%s %s: no section declared for %s (bundle says %r)"
                       % (kind, ent.get("id"), cid[:40], want_section[:40]))
                if file_of.get((kind, ent.get("id"))) == "seed_graph.json":
                    frozen_section.append(msg)
                else:
                    problems.append("fixable metadata gap outside the frozen seed -> " + msg)
            if q in text:
                exact += 1
                pos, mark = text.find(q), text.find("[VISUAL DATA]")
                if mark >= 0 and pos > mark and ent.get("status") == "verified":
                    problems.append("%s %s: verified but quote inside [VISUAL DATA] of %s"
                                    % (kind, ent.get("id"), cid))
            elif re.sub(r"\s+", " ", q) in re.sub(r"\s+", " ", text):
                soft += 1
                msg = "%s %s: whitespace-only match on %s" % (kind, ent.get("id"), cid)
                if file_of.get((kind, ent.get("id"))) == "seed_graph.json":
                    frozen_soft.append(msg)
                else:
                    # Every expansion batch has been byte-exact so far. A soft match here is a
                    # regression we can fix in one string, so it is treated as a defect.
                    warns.append(msg)
                    problems.append("fixable whitespace-only citation outside the frozen seed -> " + msg)
            else:
                missing += 1
                problems.append("%s %s: quote not found in %s" % (kind, ent.get("id"), cid))

seen = set()
for e in edges:
    key = "%s|%s|%s" % (e.get("src"), e.get("type"), e.get("dst"))
    if key in seen:
        problems.append("duplicate edge %s" % key)
    seen.add(key)
    for end in (e.get("src"), e.get("dst")):
        if end not in node_type:
            problems.append("edge %s: dangling endpoint %s" % (e.get("id"), end))
    spec = onto.get(e.get("type"))
    if not spec:
        problems.append("edge %s: relation %r not in ontology" % (e.get("id"), e.get("type")))
        continue
    st, dt = node_type.get(e.get("src")), node_type.get(e.get("dst"))
    if st not in (spec.get("allowed_source_types") or []):
        problems.append("edge %s: %r not an allowed source type for %s"
                        % (e.get("id"), st, e.get("type")))
    if dt not in (spec.get("allowed_target_types") or []):
        problems.append("edge %s: %r not an allowed target type for %s"
                        % (e.get("id"), dt, e.get("type")))

# ---------------------------------------------------------------- recomputed numbers
from collections import Counter
node_split = dict(Counter(n.get("status") for n in nodes))
edge_split = dict(Counter(e.get("status") for e in edges))

adj = {i: set() for i in node_type}
for e in edges:
    if e.get("src") in adj and e.get("dst") in adj:
        adj[e["src"]].add(e["dst"])
        adj[e["dst"]].add(e["src"])
seen_c, comps = set(), []
for i in node_type:
    if i in seen_c:
        continue
    stack, comp = [i], []
    seen_c.add(i)
    while stack:
        v = stack.pop()
        comp.append(v)
        for w in adj[v]:
            if w not in seen_c:
                seen_c.add(w)
                stack.append(w)
    comps.append(sorted(comp))
comps.sort(key=len, reverse=True)

unused = sorted(set(chunks) - cited)
report = []
report.append("== application state (independent verifier)")
report.append("  nodes=%d  edges=%d  citations=%d" % (len(nodes), len(edges), exact + soft))
report.append("  quotes: byte-exact=%d  whitespace-only=%d  missing=%d" % (exact, soft, missing))
report.append("  chunks: cited %d of %d, unused %d %s"
              % (len(cited), len(chunks), len(unused), unused))
report.append("  node status: %s" % node_split)
report.append("  edge status: %s" % edge_split)
report.append("  components=%d sizes=%s largest=%d (%d%%)"
              % (len(comps), [len(c) for c in comps], len(comps[0]),
                 round(100 * len(comps[0]) / len(nodes))))
report.append("  batches: %s" % [(b, n, e) for b, n, e in per_batch])
report.append("")
for w in frozen_soft[:6]:
    report.append("  - seed: " + w)
for w in frozen_section[:6]:
    report.append("  - seed: section: " + w)
if len(frozen_soft) + len(frozen_section) > 12:
    report.append("  ... (%d more, all in seed_graph.json)" % (len(frozen_soft) + len(frozen_section) - 12))
stale = [k for k in KNOWN if k not in known_hits]
for k in stale:
    problems.append("stale KNOWN entry, no longer occurring - remove it: %s" % (k,))

# The frozen-seed class has an exact expected size. Drift in either direction is a finding: more
# means new defects, fewer means someone changed the frozen seed and this record is now a lie.
actual_frozen = {"whitespace_only_in_seed": len(frozen_soft),
                 "undeclared_section_in_seed": len(frozen_section)}
if actual_frozen != EXPECTED_FROZEN:
    problems.append("frozen-seed warning drift: expected %s, measured %s"
                    % (EXPECTED_FROZEN, actual_frozen))

report.append("FROZEN-SEED ARTEFACTS, classified (not counted as problems): %d" % len(frozen_soft + frozen_section))
report.append("  whitespace-only citations in seed_graph.json: %d" % len(frozen_soft))
report.append("  undeclared sections in seed_graph.json:        %d" % len(frozen_section))
report.append("  every expansion batch is byte-exact with declared sections (enforced: a soft match or")
report.append("  missing section outside the seed is a PROBLEM, not a warning)")
report.append("")
report.append("FIXABLE WARNINGS OUTSIDE THE SEED: %d" % len(warns))
for w in warns:
    report.append("  - " + w)
report.append("")
report.append("PROBLEMS: %d" % len(problems))
for p in problems:
    report.append("  - " + p)
report.append("")
report.append("KNOWN, DOCUMENTED (printed, not counted): %d" % len(known_msgs))
for k in known_msgs:
    report.append("  - " + k)
report.append("")
report.append("VERDICT: %s" % ("PASS - application state is consistent" if not problems
                               else "FAIL"))

out = "\n".join(report)
print(out)
(ROOT / "docs" / "app_state_verification.txt").write_text(out + "\n", encoding="utf-8")
sys.exit(1 if problems else 0)

