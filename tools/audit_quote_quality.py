"""Evidence-quality audit: finds weak citations that the existing gates cannot see.

Existing checks verify that a quote IS a substring of its chunk. They do not notice that the quote is
a table of contents, is truncated mid-word, is a handful of words, or is reused verbatim by several
entities (copy-paste evidence). This tool looks for exactly those.

Run: python tools/audit_quote_quality.py   (read-only; exit 0 always - findings are for adjudication)
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data"
OUT = ROOT / "docs" / "evidence_quality_audit.txt"

FILES = ["seed_graph.json"] + sorted(p.name for p in DATA.glob("expansion-*.json"))
chunks = json.loads((DATA / "seed-evidence.json").read_text(encoding="utf-8"))["chunks"]
texts = {k: (v["text"] if isinstance(v, dict) else str(v)) for k, v in chunks.items()}

findings = []          # (severity, kind, entity, chunk, detail)
quote_owners = {}      # quote -> [entity ids]

for name in FILES:
    doc = json.loads((DATA / name).read_text(encoding="utf-8"))
    for kind in ("nodes", "edges"):
        for ent in doc.get(kind) or []:
            for ev in ent.get("evidence") or []:
                q, cid = ev.get("quote") or "", ev.get("chunk_id") or ""
                if not q or cid not in texts:
                    continue
                text = texts[cid]
                eid = "%s:%s" % (kind[:-1], ent.get("id"))
                quote_owners.setdefault(q, []).append(eid)

                words = len(q.split())
                upper = re.sub(r"[^A-Za-z ]", "", q).strip()
                headingish = (
                    (upper.isupper() and words >= 2)
                    or "CHAPTER" in q.upper()
                    or re.search(r"\bTypes\b.*\bService\b", q) is not None
                )
                if headingish:
                    findings.append(("HIGH", "heading-or-toc", eid, cid, q[:80]))

                # truncated mid-word: the chunk continues with a letter right after the quote ends
                i = text.find(q)
                if i >= 0:
                    after = text[i + len(q): i + len(q) + 1]
                    if after and after.isalpha():
                        findings.append(("HIGH", "truncated-mid-word", eid, cid,
                                         "%r ...next char %r" % (q[-60:], after)))

                if words <= 4:
                    findings.append(("MED", "very-short-quote", eid, cid, "%r (%d words)" % (q[:60], words)))

for q, owners in quote_owners.items():
    if len(owners) > 1:
        findings.append(("MED", "reused-quote", ", ".join(owners), "-", "%r shared by %d entities"
                         % (q[:60], len(owners))))

order = {"HIGH": 0, "MED": 1}
findings.sort(key=lambda f: (order[f[0]], f[1]))

L = ["== evidence quality audit (read-only)", ""]
L.append("%d findings: %d high, %d medium"
         % (len(findings), sum(1 for f in findings if f[0] == "HIGH"),
            sum(1 for f in findings if f[0] == "MED")))
L.append("")
for sev, kind, ent, cid, detail in findings:
    L.append("%-4s %-20s %-46s %-24s %s" % (sev, kind, ent[:46], cid[:24], detail))
out = "\n".join(L)
print(out)
OUT.write_text(out + "\n", encoding="utf-8")
