"""Pre-flight: are the three dictated quotes literal in the (new) bundle and in kb.db?"""
import json, sqlite3
from pathlib import Path

HERE = Path(r"C:\Users\Gershon\.cline\data\workspaces\chat\hi5-graph-supervisor")
b = json.loads((HERE / "_fixed" / "seed-evidence-43.json").read_text(encoding="utf-8"))["chunks"]
DB = r"C:\Users\Gershon\Desktop\WORKSPACE\hi5-andrey-server\live\app\data\kb.db"
cur = sqlite3.connect("file:%s?mode=ro" % DB, uri=True).cursor()

CHECK = [
    ("big_blue_book_p0663_c00", "Brake pads are housed in the caliper and are forced against the rotor"),
    ("big_blue_book_p0663_c00", "Brake pads are housed in the caliper"),
    ("big_blue_book_p0693_c00", "Some manufacturers specify proprietary mineral fluids, while others use\nvarious automotive DOT brake fluid."),
]
bad = 0
for cid, q in CHECK:
    inb = cid in b and q in b[cid]["text"]
    row = cur.execute("select text from chunks where chunk_id=?", (cid,)).fetchone()
    inkb = bool(row) and q in row[0]
    sec = b.get(cid, {}).get("section", "")
    print("%-28s bundle=%-5s kb=%-5s  quote=%r" % (cid, inb, inkb, q[:60]))
    print("    section in bundle: %r" % (sec or "")[:80])
    if not (inb and inkb):
        bad += 1
print("PROBLEMS:", bad)
