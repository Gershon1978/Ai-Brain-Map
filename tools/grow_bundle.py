"""Grow src/data/seed-evidence.json from 36 to 44 chunks, byte-for-byte from kb.db.

Dry by default; --write saves _fixed/seed-evidence-44.json (never touches the app yet).
The existing 36 records must be byte-identical to what is already there.
"""
import json, re, sqlite3, sys
from pathlib import Path

HERE = Path(r"C:\Users\Gershon\.cline\data\workspaces\chat\hi5-graph-supervisor")
LIVE = HERE / "_app_files" / "src__data__seed-evidence.json"
DB = r"C:\Users\Gershon\Desktop\WORKSPACE\hi5-andrey-server\live\app\data\kb.db"
OUT44 = HERE / "_fixed" / "seed-evidence-43.json"

NEW = [
    "big_blue_book_p0663_c00",
    "big_blue_book_p0693_c00",
    "bike_repair_manual_chris_p0088_c00",
    "bike_repair_manual_chris_p0089_c00",
    "bike_repair_manual_chris_p0071_c05",
    "bike_repair_manual_chris_p0148_c00",
    "bike_repair_manual_chris_p0003_c00",
]

live = json.loads(LIVE.read_text(encoding="utf-8"))
chunks = live["chunks"]
print("live bundle: %d chunks; top-level keys=%s" % (len(chunks), list(live.keys())))
first = next(iter(chunks.values()))
print("record keys: %s" % sorted(first.keys()))
print("sample record: %s" % {k: (str(v)[:60]) for k, v in first.items()})

con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
cur = con.cursor()

# the 36 must be unchanged: compare to kb.db now
same = diff = missing = 0
for cid, rec in chunks.items():
    row = cur.execute("select text, book, page from chunks where chunk_id=?", (cid,)).fetchone()
    if not row:
        missing += 1
        print("  ! %s no longer in kb.db" % cid)
        continue
    if rec.get("text") == row[0] and rec.get("book") == row[1] and rec.get("page") == row[2]:
        same += 1
    else:
        diff += 1
        print("  ! %s differs from kb.db (book/page/text)" % cid)
print("existing 36 vs kb.db: same=%d diff=%d missing=%d" % (same, diff, missing))

added, problems = 0, []
for cid in NEW:
    if cid in chunks:
        problems.append("%s already in the bundle" % cid)
        continue
    row = cur.execute("select text, book, page, section_title, has_visual_data from chunks where chunk_id=?",
                      (cid,)).fetchone()
    if not row:
        problems.append("%s NOT in kb.db" % cid)
        continue
    text, book, page, section, visual = row
    if not text or len(text) < 40:
        problems.append("%s has empty/short text" % cid)
        continue
    # copy the shape of an existing record from the same book, then coerce types to match
    tpl = next((r for r in chunks.values() if r.get("book") == book), first)
    def like(val, sample):
        try:
            return type(sample)(val) if not isinstance(sample, bool) else bool(val)
        except Exception:
            return val
    rec = {}
    for k, v in tpl.items():
        rec[k] = v
    rec["chunk_id"] = cid
    rec["book"] = book
    rec["page"] = like(page, tpl.get("page"))
    rec["section"] = section or ""
    rec["has_visual_data"] = like(visual, tpl.get("has_visual_data"))
    rec["text"] = text
    chunks[cid] = rec
    added += 1

out = dict(live)
out["chunks"] = chunks
out["chunk_count"] = len(chunks)
if "note" in out:
    out["note"] = (str(out["note"]).split(" | GREW-2026-10-25")[0]
                   + " | GREW-2026-10-25: +7 chunks (43 total) approved by the owner to join the last 6 islands"
                   + " - p0663_c00, p0693_c00, p0088_c00, p0089_c00, p0071_c05, p0148_c00, p0003_c00")
print()
print("chunk_count -> %s" % out.get("chunk_count"))
print("added=%d total=%d problems=%s" % (added, len(chunks), problems or "none"))

if "--write" in sys.argv and not problems:
    OUT44.parent.mkdir(exist_ok=True)
    OUT44.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote %s (%d bytes, %d chunks)" % (OUT44.name, OUT44.stat().st_size, len(chunks)))
else:
    print("dry run - nothing written")
