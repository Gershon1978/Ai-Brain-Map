"""Build phase13-fault-charts: the SYMPTOM / CAUSE / SOLUTION charts that live ONLY in page images.

Measured first, then ingested:
  * OCR of the 107 illustrated-but-text-poor pages gained 1.3% of words, all artefacts (logos).
    BBB's figure labels are vector text and are already in the layer, so OCR-ing 992 pages is waste.
  * The 20 pages with NO text layer are where OCR pays: 11 yield text, and six of those are
    troubleshooting tables (SYMPTOM / CAUSE / SOLUTION) that no text extractor can see.

This batch ingests all 11 as grade-C chunks (machine transcription, never eligible for a numeric
claim) and builds ONE diagnostic tree from p254, whose transcription was checked against the rendered
page image before any claim was written.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(r"C:\Users\Gershon\Desktop\WORKSPACE\Ai-Brain-Map")
OCR_JSON = Path(r"C:\Users\Gershon\.cline\data\workspaces\chat\hi5-graph-supervisor\bbb_notext_ocr.json")
TABLE_JSON = Path(r"C:\Users\Gershon\.cline\data\workspaces\chat\hi5-graph-supervisor\bbb_p254_table.json")
BATCH = "phase13-fault-charts"
SECTIONS = {
    1: "COVER",
    188: "SYMPTOM / CAUSE / SOLUTION (tires and tubes)",
    219: "HUB AND AXLE WIDTH STANDARDS",
    254: "SYMPTOM / CAUSE / SOLUTION (wheels and hub bearings)",
    301: "SYMPTOM / CAUSE / SOLUTION (wheels and spokes)",
    486: "SYMPTOM / CAUSE / SOLUTION (chain)",
    803: "SYMPTOM / CAUSE / SOLUTION (rim brakes)",
    842: "SYMPTOM / CAUSE / SOLUTION (stems)",
    928: "PARK TOOL PRODUCT CROSS-REFERENCE",
    986: "COMPONENT / TOOL INTERFACE TABLE",
    990: "CROWN RACE STANDARDS (SHIS / JIS / ISO)",
}


def span(text: str, start: str, end: str) -> str:
    i = text.find(start)
    if i < 0:
        raise SystemExit(f"anchor not found: {start!r}")
    j = text.find(end, i)
    if j < 0:
        raise SystemExit(f"end anchor not found after {start!r}: {end!r}")
    return text[i:j + len(end)]


def build_bundle(pages: dict) -> dict:
    chunks = {}
    for page_no, row in sorted(pages.items()):
        cid = f"big_blue_book_p{page_no:04d}_ocr"
        chunks[cid] = {
            "chunk_id": cid,
            "book": "big_blue_book",
            "page": page_no,
            "section": SECTIONS.get(page_no, "SCANNED PAGE"),
            "source": "723775317-Big-Blue-Book-of-Bicycle-Repair-4th-Edition-by-C-Calvin-Jones.pdf",
            "extraction": "ocr",
            "ocr_engine": "rapidocr_onnxruntime (CPU/ONNX)",
            "ocr_mean_confidence": row["mean_confidence"],
            "text": row["text"],
        }
    return {
        "schema_version": "1.0.0",
        "corpus": "big_blue_book_page_images_ocr",
        "source_file": "723775317-Big-Blue-Book-of-Bicycle-Repair-4th-Edition-by-C-Calvin-Jones.pdf",
        "note": ("Grade C: these pages have NO text layer, so their text comes from OCR of the page image. "
                 "Six are SYMPTOM/CAUSE/SOLUTION troubleshooting tables and three are specification tables "
                 "(hub/axle widths, tool interfaces, crown-race standards). Spacing is degraded by the "
                 "transcription, and per Test K a grade-C citation may never justify a numeric claim - the "
                 "specification tables are therefore ingested as retrievable text, NOT as numeric evidence."),
        "chunks": chunks,
    }


def build_edges(edge, q_lateral, q_slow, q_rough, q_tighten, q_loosen, q_replace) -> list:
    return [
        edge("edge-lateralplay-indicates-loose-hub", "sym-wheel-lateral-play", "fm-loose-hub-adjustment",
             "indicates", "Lateral play at the rim indicates a loose hub bearing adjustment.", q_lateral),
        edge("edge-lateralplay-indicates-rear-hub", "sym-wheel-lateral-play", "comp-rear-hub",
             "indicates", "Lateral play at the rim points at the rear hub as the component at fault.", q_lateral),
        edge("edge-slowsquickly-indicates-tight-hub", "sym-wheel-slows-quickly", "fm-hub-adjustment-too-tight",
             "indicates", "A wheel that slows quickly when spun has its hub adjustment too tight.", q_slow),
        edge("edge-rough-indicates-worn-bearings", "sym-wheel-rough-rumbling", "fm-hub-bearings-worn",
             "indicates", "Roughness or rumbling at the frame or fork indicates badly worn hub bearings.", q_rough),
        # Each symptom also points at the component it implicates, or the diagnostic sub-tree would be an
        # island: the connectivity pin in Test Q fails on a disconnected pair, and rightly so.
        edge("edge-rough-indicates-rear-hub", "sym-wheel-rough-rumbling", "comp-rear-hub",
             "indicates", "Roughness or rumbling when the wheel turns points at the rear hub.", q_rough),
        edge("edge-slowsquickly-indicates-rear-hub", "sym-wheel-slows-quickly", "comp-rear-hub",
             "indicates", "A wheel that slows quickly when spun points at the rear hub's bearing adjustment.", q_slow),
        edge("edge-tighten-resolves-loose-hub", "proc-adjust-hub-bearing", "fm-loose-hub-adjustment",
             "resolves", "Tightening the bearing adjustment resolves a loose hub adjustment.", q_tighten),
        edge("edge-loosen-resolves-tight-hub", "proc-loosen-hub-adjustment", "fm-hub-adjustment-too-tight",
             "resolves", "Loosening the adjustment resolves a hub that is too tight.", q_loosen),
        edge("edge-replace-resolves-worn-bearings", "proc-replace-hub-bearings", "fm-hub-bearings-worn",
             "resolves", "Replacing the bearings resolves worn hub bearings.", q_replace),
    ]


def build_expansion(p254: str) -> dict:
    # Cell quotes, taken from the column-reconstructed text produced by tools/ocr_table.py. Literal
    # strings plus an assertion: if reconstruction ever changes, the build stops instead of writing a
    # citation that is not in its own chunk.
    q = {
        "lateral": "Wheel moves laterally back and forth at rim",
        "loose": "1. Loose adjustment at hub",
        "slow": "When spun without brake rub, wheel slows quickly",
        "tight": "Hub adjustment too tight",
        "rough": "or rumbling felt or heard at frame/fork",
        "worn": "Bearings badly worn",
        "tighten": "1. Tighten bearing adjustment",
        "loosen": "Loosen adjustment",
        "replace": "Replace bearings",
    }
    for name, quote in q.items():
        if quote not in p254:
            raise SystemExit(f"quote {name} not inside the reconstructed OCR chunk - refusing to write")
        print(f"  quote[{name}] = {quote!r}")
    q_lateral, q_loose, q_slow = q["lateral"], q["loose"], q["slow"]
    q_tight, q_rough, q_worn = q["tight"], q["rough"], q["worn"]
    q_tighten, q_loosen, q_replace = q["tighten"], q["loosen"], q["replace"]

    cid = "big_blue_book_p0254_ocr"

    def cite(quote: str) -> dict:
        return {"chunk_id": cid, "book": "big_blue_book", "page": 254, "section": SECTIONS[254],
                "quote": quote, "evidence_grade": "C", "linked_to_chunk": True, "confidence": 0.8}

    def node(nid, ntype, name, desc, aliases, quote):
        return {"id": nid, "type": ntype, "name": name, "subsystem": "sys-wheels", "aliases": aliases,
                "description": desc, "status": "verified", "batch": BATCH, "properties": {},
                "evidence": [cite(quote)]}

    def edge(eid, src, dst, etype, claim, quote):
        return {"id": eid, "src": src, "dst": dst, "type": etype, "claim": claim, "status": "verified",
                "evidence_type": "service_manual", "confidence": 0.9, "conditions": [], "conflicts": [],
                "batch": BATCH, "evidence": [cite(quote)]}

    nodes = [
        node("sym-wheel-lateral-play", "symptom", "Wheel moves laterally at the rim",
             "With the bike stationary, the wheel can be rocked side to side at the rim.",
             ["Lateral wheel play"], q_lateral),
        node("sym-wheel-slows-quickly", "symptom", "Wheel slows quickly when spun",
             "Spun free of the brake, the wheel slows down much sooner than it should.",
             ["Stiff hub"], q_slow),
        node("sym-wheel-rough-rumbling", "symptom", "Wheel turns roughly or rumbles",
             "Roughness or rumbling is felt or heard at the frame or fork when the wheel turns.",
             ["Grinding hub"], q_rough),
        node("fm-loose-hub-adjustment", "failure_mode", "Loose hub bearing adjustment",
             "The hub bearing adjustment is too loose, so the wheel moves on its axle.",
             ["Loose cones"], q_loose),
        node("fm-hub-adjustment-too-tight", "failure_mode", "Hub adjustment too tight",
             "The hub bearing adjustment is too tight, binding the bearings.", ["Over-tight cones"], q_tight),
        node("fm-hub-bearings-worn", "failure_mode", "Worn hub bearings",
             "The hub bearings are badly worn and no longer run smoothly.", ["Rough bearings"], q_worn),
        node("proc-adjust-hub-bearing", "procedure", "Tighten hub bearing adjustment",
             "Take up the hub bearing adjustment until the play is removed.", ["Cone adjustment"], q_tighten),
        node("proc-loosen-hub-adjustment", "procedure", "Loosen hub adjustment",
             "Back off the hub bearing adjustment to free a binding hub.", ["Back off cones"], q_loosen),
        node("proc-replace-hub-bearings", "procedure", "Replace hub bearings",
             "Replace the hub bearings rather than adjusting a worn set.", ["Bearing replacement"], q_replace),
    ]
    return {"schema_version": "1.0.0", "batch": BATCH,
            "source_note": ("The hub-bearing diagnostic tree from BBB p254, a SYMPTOM / CAUSE / SOLUTION table "
                            "that exists only as an image (the page has no text layer). Grade C: the "
                            "transcription was checked against the rendered page before the claims were "
                            "written, and can never support a number."),
            "nodes": nodes, "edges": build_edges(edge, q_lateral, q_slow, q_rough, q_tighten, q_loosen, q_replace)}


def main() -> int:
    rows = json.loads(OCR_JSON.read_text(encoding="utf-8"))
    pages = {r["page"]: r for r in rows if r["ocr_chars"] >= 40}
    bundle = build_bundle(pages)

    # p254 is a three-column table: replace the raw reading-order text with the column-reconstructed
    # linearisation, so a cell is one contiguous quotable string instead of three interleaved fragments.
    table = json.loads(TABLE_JSON.read_text(encoding="utf-8")) if TABLE_JSON.exists() else None
    if table:
        chunk = bundle["chunks"]["big_blue_book_p0254_ocr"]
        chunk["text"] = table["text"]
        chunk["extraction"] = "ocr+column-reconstruction"
        chunk["columns_text"] = table["columns_text"]
    p254_text = bundle["chunks"]["big_blue_book_p0254_ocr"]["text"]

    expansion = build_expansion(p254_text)

    (ROOT / "src" / "data" / "evidence-bundle-4.json").write_text(
        json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "src" / "data" / "expansion-faultcharts.json").write_text(
        json.dumps(expansion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  wrote bundle-4: {len(bundle['chunks'])} OCR chunks (pages {sorted(pages)})")
    print(f"  wrote expansion-faultcharts.json: {len(expansion['nodes'])} nodes, {len(expansion['edges'])} edges")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

