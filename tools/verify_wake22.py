"""Wake-22 verification of the reply to _msg20_connectors3.txt.

Independent of the app's own test suite: reads the dumped app files + kb.db,
recomputes every number the reply claimed, and checks every citation.

Claims under test (reply, 23:17:42):
  expansion-connectors.json: 0 nodes, 9 edges (9 verified)
  8 expansion files: 42 nodes, 51 edges
  merged map: 69 nodes (61 verified / 1 candidate / 7 needs_review)
              63 edges (53 verified / 10 needs_review)
  connectivity: 7 components, largest 35, sizes [35,16,8,6,2,1,1]
  suite 14/14, tsc clean, build succeeded -> NOT re-runnable from here, reported unverified
"""
import json, hashlib, sqlite3, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
APP = HERE / "_app_files"
DB = r"C:\Users\Gershon\Desktop\WORKSPACE\hi5-andrey-server\live\app\data\kb.db"
OUT = HERE / "_verify_wake22.txt"

L, P, N = [], [], []
def say(s=""):
    L.append(s)
def bad(s):
    P.append(s)
def note(s):
    N.append(s)

def af(name):
    p = APP / ("src__" + name)
    return p if p.exists() else APP / name

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]

def flat(t):
    return re.sub(r"\s+", " ", t or "")

def cite_ok(quote, cid, texts):
    """byte-literal: the quote, newlines and all, must sit inside the chunk text"""
    t = texts.get(cid, "")
    return bool(quote) and quote in t

# ---------------------------------------------------------------- A. frozen files
FROZEN = {
    "seed":         ("data__seed_graph.json",           "63ac51261765d930"),
    "brake-1":      ("data__expansion-brakes.json",     "a384a15fb5581f0c"),
    "cockpit-2":    ("data__expansion-cockpit.json",    "13f28204569156e1"),
    "drivetrain-3": ("data__expansion-drivetrain.json", "62442afcf5e63529"),
    "rearshock-4":  ("data__expansion-rearshock.json",  "ace4858b7de6fd83"),
    "quillstem-5":  ("data__expansion-quillstem.json",  "69526d23b6be5725"),
    "cassette-6":   ("data__expansion-cassette.json",   "0a15c41866388782"),
    "hubfit-7":     ("data__expansion-hubfit.json",     "2e86bcd491646ba3"),
}
say("== A. frozen files (hash must equal the one recorded before wake-20 was sent)")
for label, (f, want) in FROZEN.items():
    got = sha(af(f))
    say("  %-13s %s vs %s %s" % (label, got, want, "UNCHANGED" if got == want else "*** MOVED ***"))
    if got != want:
        bad("%s moved (%s -> %s)" % (label, want, got))

for f in ("data__seed_graph.json", "data__seed-evidence.json"):
    p_fixed = HERE / "_fixed" / f.split("__")[-1]
    if p_fixed.exists():
        same = p_fixed.read_bytes() == af(f).read_bytes()
        say("  %-30s identical to _fixed: %s" % (f, same))
        if not same:
            bad("%s differs from the _fixed copy" % f)
    else:
        note("no _fixed copy of %s to compare" % f)

# ---------------------------------------------------------------- B. seed
seed = json.loads(af("data__seed_graph.json").read_text(encoding="utf-8"))
evf = json.loads(af("data__seed-evidence.json").read_text(encoding="utf-8"))
bundle = evf.get("chunks", {})
btext = {cid: (rec.get("text") or "") for cid, rec in bundle.items()}
say()
say("== B. seed must still be 27 / 12 / 59 with 20/20 + 39/39 literal")
say("  nodes=%d edges=%d bundle chunks=%d" % (len(seed["nodes"]), len(seed["edges"]), len(bundle)))
if len(seed["nodes"]) != 27: bad("seed nodes %d != 27" % len(seed["nodes"]))
if len(seed["edges"]) != 12: bad("seed edges %d != 12" % len(seed["edges"]))
if len(bundle) != 36: bad("bundle chunks %d != 36" % len(bundle))

node_c = sum(len(n.get("evidence") or []) for n in seed["nodes"])
edge_c = sum(len(e.get("evidence") or []) for e in seed["edges"])
say("  node citations=%d edge citations=%d total=%d" % (node_c, edge_c, node_c + edge_c))
if node_c != 39 or edge_c != 20:
    bad("seed citation count changed: %d node / %d edge (want 39/20)" % (node_c, edge_c))
braw = sum(1 for n in seed["nodes"] for d in (n.get("evidence") or [])
           if d.get("chunk_id") in btext and cite_ok(d.get("quote", ""), d["chunk_id"], btext))
eraw = sum(1 for e in seed["edges"] for d in (e.get("evidence") or [])
           if d.get("chunk_id") in btext and cite_ok(d.get("quote", ""), d["chunk_id"], btext))
def nz(s):
    return re.sub(r"\s+", " ", s or "").strip()
bnz = {c: nz(t) for c, t in btext.items()}
bnorm_n = sum(1 for n in seed["nodes"] for d in (n.get("evidence") or [])
              if d.get("chunk_id") in bnz and nz(d.get("quote", "")) in bnz[d["chunk_id"]])
bnorm_e = sum(1 for e in seed["edges"] for d in (e.get("evidence") or [])
              if d.get("chunk_id") in bnz and nz(d.get("quote", "")) in bnz[d["chunk_id"]])
say("  byte-exact in bundle (newlines kept): node %d/%d  edge %d/%d" % (braw, node_c, eraw, edge_c))
say("  exact after whitespace collapse   : node %d/%d  edge %d/%d" % (bnorm_n, node_c, bnorm_e, edge_c))
if bnorm_n != node_c or bnorm_e != edge_c:
    bad("seed citations no longer match the bundle, even after whitespace collapse")
elif braw != node_c or eraw != edge_c:
    note("frozen seed: %d of %d citations differ from the chunk in whitespace only "
         "(e.g. '* DOT FLUID' vs '*   DOT FLUID'); the word sequence is identical. Not edited - "
         "the seed is frozen and I do not rewrite evidence by hand." % ((node_c + edge_c) - (braw + eraw), node_c + edge_c))


# ---------------------------------------------------------------- C. kb.db cross-check
con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
cur = con.cursor()
kb = {cid: (t or "") for cid, t in cur.execute("select chunk_id, text from chunks")}
say()
say("== C. bundle vs kb.db (anti-circularity)")
same = diff = ghost = 0
for cid, rec in bundle.items():
    if cid not in kb:
        ghost += 1
        bad("bundle chunk %s does not exist in kb.db" % cid)
    elif rec.get("text", "") == kb[cid]:
        same += 1
    else:
        diff += 1
        bad("bundle text for %s differs from kb.db" % cid)
say("  chunks=%d identical=%d differs=%d nonexistent=%d" % (len(bundle), same, diff, ghost))

# ---------------------------------------------------------------- D. connectors file
con_f = json.loads(af("data__expansion-connectors.json").read_text(encoding="utf-8"))
ce = con_f.get("edges") or []
say()
say("== D. src/data/expansion-connectors.json")
say("  top-level batch = %s ; nodes = %d ; edges = %d" % (con_f.get("batch"),
                                                          len(con_f.get("nodes") or []), len(ce)))
if con_f.get("batch") != "phase6-connectors-3":
    bad("top-level batch is %r, expected phase6-connectors-3" % con_f.get("batch"))
if len(con_f.get("nodes") or []) != 0:
    bad("connectors file now carries %d nodes (must stay 0)" % len(con_f.get("nodes")))
if len(ce) != 9:
    bad("connectors file holds %d edges, expected 9" % len(ce))

EXPECT_BATCH = {
    "comp-rotor-6bolt|comp-rear-hub|mounted_on": "phase6-connectors-1",
    "comp-stem-quill|comp-steerer|mounted_on": "phase6-connectors-1",
    "rule-hub-135mm|comp-rear-hub|constrains": "phase6-connectors-1",
    "comp-headset-threadless|comp-headset|part_of": "phase6-connectors-2",
    "comp-ebike-motor|comp-rear-hub|fits_into": "phase6-connectors-2",
    "ec-xiaomi-table|comp-ebike-motor|indicates": "phase6-connectors-2",
    "rule-brake-fluid-contamination|comp-caliper-hydraulic|constrains": "phase6-connectors-2",
    "comp-cassette|prop-chainline|has_property": "phase6-connectors-3",
    "comp-freewheel|comp-cassette|interfaces_with": "phase6-connectors-3",
}
DICTATED = {
    "comp-cassette|prop-chainline|has_property": (
        "edge-conn3-cassette-has-chainline",
        "Chainline is the relation of the front and rear sprockets to the center plane, so chainline is a property of the cassette's sprocket stack.",
        "big_blue_book_p0585_c00",
        "Chainline is the relation of the front and rear sprockets to the center plane"),
    "comp-freewheel|comp-cassette|interfaces_with": (
        "edge-conn3-freewheel-interfaces-cassette",
        "A cassette and a freewheel are the two rear-sprocket systems: both let the rear wheel turn while the pedals stay still.",
        "bike_repair_manual_chris_p0066_c00",
        "The cassette and freewheel allow the rear\nwheel to rotate while the pedals remain"),
}

seen = set()
for e in ce:
    key = "%s|%s|%s" % (e.get("src"), e.get("dst"), e.get("type"))
    if key in seen:
        bad("duplicate edge %s" % key)
    seen.add(key)
    line = "  %-48s %-20s" % (key[:48], e.get("batch"))
    if EXPECT_BATCH.get(key) != e.get("batch"):
        bad("edge %s batch=%r want %r" % (key, e.get("batch"), EXPECT_BATCH.get(key)))
        line += " *** BATCH ***"
    if e.get("status") != "verified":
        bad("edge %s status=%r" % (key, e.get("status")))
    if e.get("evidence_type") != "service_manual":
        bad("edge %s evidence_type=%r" % (key, e.get("evidence_type")))
    ev = e.get("evidence") or []
    if len(ev) != 1:
        bad("edge %s has %d evidence objects, expected 1" % (key, len(ev)))
    for d in ev:
        cid, q = d.get("chunk_id"), d.get("quote", "")
        want_keys = {"chunk_id", "book", "page", "section", "quote",
                     "evidence_grade", "linked_to_chunk", "confidence"}
        if set(d.keys()) != want_keys:
            note("edge %s evidence keys = %s" % (key, sorted(d.keys())))
        if d.get("evidence_grade") != "A":
            bad("edge %s grade=%r" % (key, d.get("evidence_grade")))
        if d.get("linked_to_chunk") is not True:
            bad("edge %s linked_to_chunk=%r" % (key, d.get("linked_to_chunk")))
        in_bundle = cid in bundle
        lit_bundle = in_bundle and cite_ok(q, cid, btext)
        lit_kb = cid in kb and cite_ok(q, cid, kb)
        meta_ok = (in_bundle and d.get("book") == bundle[cid].get("book")
                   and d.get("page") == bundle[cid].get("page"))
        line += " | %-38s bundle=%s literal=%s kb=%s meta=%s" % (
            str(cid)[:38], in_bundle, lit_bundle, lit_kb, meta_ok)
        if not in_bundle:
            bad("edge %s cites %s which is NOT in the bundled 36" % (key, cid))
        if in_bundle and not lit_bundle:
            bad("edge %s quote not byte-literal in bundle %s -> %r" % (key, cid, q[:110]))
        if not lit_kb:
            bad("edge %s quote not byte-literal in kb.db %s" % (key, cid))
        if not meta_ok:
            bad("edge %s book/page mismatch for %s" % (key, cid))
    if key in DICTATED:
        want_id, want_claim, want_cid, want_quote = DICTATED[key]
        if e.get("id") != want_id:
            bad("edge %s id=%r want %r" % (key, e.get("id"), want_id))
        if e.get("claim") != want_claim:
            bad("edge %s claim text differs from what was dictated" % key)
        if ev and (ev[0].get("chunk_id") != want_cid or ev[0].get("quote") != want_quote):
            bad("edge %s chunk/quote differ from what was dictated (line-break rule)" % key)
    say(line)

missing = set(EXPECT_BATCH) - seen
extra = seen - set(EXPECT_BATCH)
say("  approved but missing: %s" % (sorted(missing) or "none"))
say("  present but not approved: %s" % (sorted(extra) or "none"))
if missing: bad("connectors file lost approved edges: %s" % sorted(missing))
if extra: bad("connectors file carries unapproved edges: %s" % sorted(extra))

# ---------------------------------------------------------------- E. merged map
FILES = [("seed_graph.json", "seed"),
         ("expansion-brakes.json", "phase5-brake-1"),
         ("expansion-cockpit.json", "phase5-cockpit-2"),
         ("expansion-drivetrain.json", "phase5-drivetrain-3"),
         ("expansion-rearshock.json", "phase5-rearshock-4"),
         ("expansion-quillstem.json", "phase5-quillstem-5"),
         ("expansion-cassette.json", "phase5-cassette-6"),
         ("expansion-hubfit.json", "phase5-hubfit-7"),
         ("expansion-connectors.json", "phase6-connectors-3")]
all_nodes, all_edges = [], []
say()
say("== E. merged map, recomputed from the files")

def comp(items):
    out = {}
    for x in items:
        out[x.get("status")] = out.get(x.get("status"), 0) + 1
    return out

for fn, label in FILES:
    d = json.loads(af("data__" + fn).read_text(encoding="utf-8"))
    ns_, es_ = d.get("nodes") or [], d.get("edges") or []
    all_nodes += ns_
    all_edges += es_
    say("  %-20s nodes=%-3d %-40s edges=%-3d %s" % (label, len(ns_), comp(ns_), len(es_), comp(es_)))

ids = [n["id"] for n in all_nodes]
dups = sorted({i for i in ids if ids.count(i) > 1})
say("  merged nodes=%d edges=%d" % (len(all_nodes), len(all_edges)))
say("  node statuses: %s" % comp(all_nodes))
say("  edge statuses: %s" % comp(all_edges))
if len(all_nodes) != 69: bad("merged nodes %d != 69" % len(all_nodes))
if len(all_edges) != 63: bad("merged edges %d != 63" % len(all_edges))
if dups: bad("duplicate node ids after merge: %s" % dups)
exp_nodes, exp_edges = len(all_nodes) - 27, len(all_edges) - 12
say("  expansion contribution: nodes=%d edges=%d (reply said 42 / 51)" % (exp_nodes, exp_edges))
if exp_nodes != 42 or exp_edges != 51:
    bad("expansion contribution %d/%d != 42/51" % (exp_nodes, exp_edges))

node_ids = set(ids)
dangling = [(e.get("src"), e.get("dst")) for e in all_edges
            if e.get("src") not in node_ids or e.get("dst") not in node_ids]
say("  dangling endpoints: %s" % (dangling or "none"))
if dangling: bad("dangling endpoints: %s" % dangling)
ek = ["%s|%s|%s" % (e.get("src"), e.get("type"), e.get("dst")) for e in all_edges]
dupe = sorted({k for k in ek if ek.count(k) > 1})
say("  duplicate edges: %s" % (dupe or "none"))
if dupe: bad("duplicate edges after merge: %s" % dupe)

# ---------------------------------------------------------------- F. connectivity
adj = {i: set() for i in node_ids}
for e in all_edges:
    if e.get("src") in adj and e.get("dst") in adj:
        adj[e["src"]].add(e["dst"])
        adj[e["dst"]].add(e["src"])
seen_c, comps = set(), []
for i in node_ids:
    if i in seen_c:
        continue
    stack, comp_list = [i], []
    seen_c.add(i)
    while stack:
        v = stack.pop()
        comp_list.append(v)
        for w in adj[v]:
            if w not in seen_c:
                seen_c.add(w)
                stack.append(w)
    comps.append(comp_list)
comps.sort(key=len, reverse=True)
say()
say("== F. connectivity")
say("  components=%d largest=%d (%d%%)" % (len(comps), len(comps[0]),
                                           round(100.0 * len(comps[0]) / len(node_ids))))
say("  sizes %s" % [len(c) for c in comps])
say("  still separate: %s" % [[c[0], len(c)] for c in comps[1:]])
if len(comps) != 7: bad("component count %d != 7" % len(comps))
if len(comps[0]) != 35: bad("largest component %d != 35" % len(comps[0]))

# ---------------------------------------------------------------- G. ontology legality, new edges
raw = None
onto_path = af("data__relation-ontology.json")
if onto_path.exists():
    onto_doc = json.loads(onto_path.read_text(encoding="utf-8"))
    raw = onto_doc.get("relations") or onto_doc.get("types") or []
say()
say("== G. ontology: do the connectors-3 relations allow these endpoint types")
ont = {}
for r in (raw or []):
    if isinstance(r, dict):
        ont[r.get("id") or r.get("name")] = r
    else:
        ont[r] = {}
say("  ontology entries: %d  (first keys: %s)" % (len(ont), list(ont)[:6]))
nodes_by_id = {n["id"]: n for n in all_nodes}
for e in ce:
    if not str(e.get("batch", "")).endswith("-3"):
        continue
    r = ont.get(e.get("type")) or {}
    st = (nodes_by_id.get(e.get("src")) or {}).get("type")
    dt = (nodes_by_id.get(e.get("dst")) or {}).get("type")
    src_ok = (not r.get("source_types")) or st in r["source_types"]
    dst_ok = (not r.get("target_types")) or dt in r["target_types"]
    say("  %-16s %s(%s) -> %s(%s)  src_ok=%s dst_ok=%s" % (e.get("type"), e.get("src"), st,
                                                           e.get("dst"), dt, src_ok, dst_ok))
    if not (src_ok and dst_ok):
        bad("ontology violation on %s|%s|%s" % (e.get("src"), e.get("type"), e.get("dst")))

# ---------------------------------------------------------------- H. grade rules, catalog-wide
say()
say("== H. edge status=verified with digits but only sub-A evidence (all 63 edges)")
n_num = 0
for e in all_edges:
    if e.get("status") == "verified" and re.search(r"\d", e.get("claim") or ""):
        grades = [d.get("evidence_grade") or d.get("grade") for d in (e.get("evidence") or [])]
        if grades and all(g in ("B", "C", "D") for g in grades):
            n_num += 1
            bad("edge %s is verified but its numbers rest only on grade %s" % (e.get("id"), grades))
say("  flagged: %d" % n_num)
lowb = [e for e in all_edges if e.get("status") != "verified"
        and re.search(r"\d", e.get("claim") or "")
        and all((d.get("evidence_grade") or d.get("grade")) in ("B", "C", "D")
                for d in (e.get("evidence") or [])) and (e.get("evidence") or [])]
say("  digit claims correctly held at needs_review on grade B: %d" % len(lowb))
for e in lowb:
    say("     %-56s %s" % (e.get("id")[:56], e.get("status")))


# ---------------------------------------------------------------- I. properties verified without citation
say()
say("== I. properties marked verified without a citation (all 69 nodes)")
n_u = 0
for n in all_nodes:
    for k, p in (n.get("properties") or {}).items():
        if isinstance(p, dict) and p.get("status") == "verified" \
                and not (p.get("evidence_chunk") or p.get("evidence")):
            n_u += 1
            bad("node %s property %s marked verified without an evidence chunk" % (n["id"], k))
say("  flagged: %d" % n_u)

# ---------------------------------------------------------------- J. every citation in all 9 files
say()
say("== J. every citation in all 9 files, checked against bundle and kb.db")
tot = ok_exact = ok_norm = bad_ = 0
kb_nz = {c: nz(t) for c, t in kb.items()}
for fn, label in FILES:
    d = json.loads(af("data__" + fn).read_text(encoding="utf-8"))
    fe = ff = ftot = 0
    for kind, items in (("node", d.get("nodes") or []), ("edge", d.get("edges") or [])):
        for it in items:
            for ev_ in it.get("evidence") or []:
                tot += 1
                ftot += 1
                cid, q = ev_.get("chunk_id"), ev_.get("quote") or ""
                if cid not in btext:
                    bad_ += 1
                    fe += 1
                    bad("%s %s(%s) cites %s - NOT in the bundled 36" % (fn, kind, it.get("id"), cid))
                elif q in btext[cid]:
                    ok_exact += 1
                elif nz(q) and nz(q) in bnz[cid]:
                    ok_norm += 1
                    ff += 1
                else:
                    bad_ += 1
                    fe += 1
                    bad("%s %s(%s) quote not found in %s -> %r" % (fn, kind, it.get("id"), cid, q[:80]))
                if cid in kb and not (nz(q) in kb_nz[cid]):
                    bad_ += 1
                    fe += 1
                    bad("%s %s(%s): quote not in kb.db text of %s" % (fn, kind, it.get("id"), cid))
    say("  %-24s citations=%3d  whitespace-only diffs=%d  problems=%d" % (fn, ftot, ff, fe))
say("  TOTAL citations=%d  byte-exact=%d  whitespace-only=%d  problems=%d" % (tot, ok_exact, ok_norm, bad_))
if tot != 152:
    note("total citations across the 9 files = %d (the app's Test P declared 93 for the expansion files "
         "alone: %d nodes + %d edges)" % (tot, tot - 59, 0))


say()
say("PROBLEMS: %d" % len(P))
for x in P:
    say("  - " + x)
say()
say("NOTES: %d" % len(N))
for x in N:
    say("  - " + x)
OUT.write_text("\n".join(L), encoding="utf-8")
print("PROBLEMS=%d NOTES=%d -> %s" % (len(P), len(N), OUT.name))
