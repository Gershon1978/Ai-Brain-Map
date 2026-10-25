"""Build the phase12-fork-seal batch from the Sidwells text layer.

Why this exists: `comp-fork-seals` was the graph's only island (components [74,1]).
It was assumed unsolvable because "the Sidwells crank pages are scans". Two checks
killed that assumption:

  1. `tools/ocr_page.py inventory` shows Sidwells has a text layer on 158 of 160
     pages; the two image-only pages (2 and 6) are full-page PHOTOGRAPHS with no
     text at all, so OCR has nothing to recover there.
  2. `tools/find_pages.py` finds suspension-fork content on pp.140-147 - the
     publisher's own prose, i.e. evidence grade A.

Quotes are sliced out of the extracted text by anchor, so each citation is
byte-exact by construction and cannot drift from the chunk it cites.
"""
from __future__ import annotations

import json
from pathlib import Path

import pymupdf

ROOT = Path(r"C:\Users\Gershon\Desktop\WORKSPACE\Ai-Brain-Map")
SID = Path(r"C:\Users\Gershon\Downloads\22743195-Bicycle-Repair-Manual-Chris-Sidwells.pdf")
SID_NAME = SID.name
BATCH = "phase12-fork-seal"


def page_text(page_no: int) -> str:
    doc = pymupdf.open(SID)
    text = doc.load_page(page_no - 1).get_text("text")
    doc.close()
    return text


def span(text: str, start_anchor: str, end_anchor: str) -> str:
    """Return text[start:end] located by anchors; raises if either is absent."""
    i = text.find(start_anchor)
    if i < 0:
        raise SystemExit(f"start anchor not found: {start_anchor!r}")
    j = text.find(end_anchor, i)
    if j < 0:
        raise SystemExit(f"end anchor not found after {start_anchor!r}: {end_anchor!r}")
    return text[i:j + len(end_anchor)]


def write_expansion(cite, q_part_of, q_function, q_symptom, q_worn) -> int:
    expansion = {
        "schema_version": "1.0.0",
        "batch": BATCH,
        "source_note": ("Fork seals, from the Sidwells text layer pp.35 and 141 (grade A). Replaces the island's "
                        "reliance on a vision-model description: the manual states what the seal is for, that it is "
                        "on the fork, and that cracked seals are evidence of worn seals."),
        "nodes": [
            {
                "id": "prop-fork-seal-function",
                "type": "property",
                "name": "Fork seal function (contaminant exclusion)",
                "subsystem": "sys-cockpit",
                "aliases": ["Seal function"],
                "description": "The suspension fork's seal keeps dirt out of the fork's interior.",
                "status": "verified",
                "batch": BATCH,
                "properties": {},
                "evidence": [cite("bike_repair_manual_chris_p0141_c00", 141, "AIR/OIL FORK", q_function)],
            },
            {
                "id": "sym-fork-seal-wear",
                "type": "symptom",
                "name": "Cracked or slack fork seals",
                "subsystem": "sys-cockpit",
                "aliases": ["Seal cracks", "Slack seals"],
                "description": "Cracks or slackness visible at the fork or shock seals during a service check.",
                "status": "verified",
                "batch": BATCH,
                "properties": {},
                "evidence": [cite("bike_repair_manual_chris_p0035_c00", 35, "Servicing", q_symptom)],
            },
            {
                "id": "fm-worn-fork-seals",
                "type": "failure_mode",
                "name": "Worn fork seals",
                "subsystem": "sys-cockpit",
                "aliases": ["Worn dust seals"],
                "description": ("Worn fork seals, evidenced by play, absence of visible oil lines on the stanchions, "
                                "or cracked seals; the manual says replacement is a job for a qualified technician."),
                "status": "verified",
                "batch": BATCH,
                "properties": {},
                "evidence": [cite("bike_repair_manual_chris_p0035_c00", 35, "Servicing", q_worn)],
            },
        ],
        "edges": [
            {
                "id": "edge-forkseals-part-of-fork",
                "src": "comp-fork-seals",
                "dst": "comp-fork",
                "type": "part_of",
                "claim": "The fork seals are fitted on the fork and are renewed as part of its bi-annual service.",
                "status": "verified",
                "evidence_type": "service_manual",
                "confidence": 1.0,
                "conditions": [],
                "conflicts": [],
                "batch": BATCH,
                "evidence": [cite("bike_repair_manual_chris_p0035_c00", 35, "Servicing", q_part_of)],
            },
            {
                "id": "edge-forkseals-has-function",
                "src": "comp-fork-seals",
                "dst": "prop-fork-seal-function",
                "type": "has_property",
                "claim": "The fork seal's function is to keep dirt out of the fork's interior.",
                "status": "verified",
                "evidence_type": "service_manual",
                "confidence": 1.0,
                "conditions": [],
                "conflicts": [],
                "batch": BATCH,
                "evidence": [cite("bike_repair_manual_chris_p0141_c00", 141, "AIR/OIL FORK", q_function)],
            },
            {
                "id": "edge-sym-sealwear-indicates-worn",
                "src": "sym-fork-seal-wear",
                "dst": "fm-worn-fork-seals",
                "type": "indicates",
                "claim": "Cracked or slack fork seals indicate worn seals, which should be replaced by a qualified technician.",
                "status": "verified",
                "evidence_type": "service_manual",
                "confidence": 1.0,
                "conditions": [],
                "conflicts": [],
                "batch": BATCH,
                "evidence": [cite("bike_repair_manual_chris_p0035_c00", 35, "Servicing", q_worn)],
            },
            {
                "id": "edge-sym-sealwear-indicates-forkseals",
                "src": "sym-fork-seal-wear",
                "dst": "comp-fork-seals",
                "type": "indicates",
                "claim": "Cracked or slack seals indicate a fault at the fork seals themselves, which the manual says a qualified technician should replace.",
                "status": "verified",
                "evidence_type": "service_manual",
                "confidence": 1.0,
                "conditions": [],
                "conflicts": [],
                "batch": BATCH,
                "evidence": [cite("bike_repair_manual_chris_p0035_c00", 35, "Servicing", q_symptom)],
            },
        ],
    }
    out = ROOT / "src" / "data" / "expansion-forkseal.json"
    out.write_text(json.dumps(expansion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  wrote {out.name}: {len(expansion['nodes'])} nodes, {len(expansion['edges'])} edges")
    return 0


def main() -> int:
    p35 = page_text(35)
    p141 = page_text(141)

    # --- chunks: the page slice each citation lives in -------------------------
    # Spans the service list from "Fork and shock for play" through the bi-annual
    # "Seals on forks and shocks" row, so both quotes below live in one chunk.
    chunk35 = span(p35, "Fork and shock for play", "EVERY SIX MONTHS")
    chunk141 = p141.strip()

    # --- quotes: sliced from the chunk text, never typed ----------------------
    q_part_of = span(p35, "Seals on forks and shocks, as part of bi-annual service", "by qualified technician")
    q_function = span(p141, "Seal\nKeeps dirt out", "interior")
    q_symptom = span(p35, "Fork and shock seals for cracks and slackness", "slackness")
    q_worn = span(p35, "Play, absence of oil lines, and cracked seals are all evidence of",
                  "qualified technician.")

    for name, quote, chunk in (("part_of", q_part_of, chunk35), ("function", q_function, chunk141),
                               ("symptom", q_symptom, chunk35), ("worn", q_worn, chunk35)):
        if quote not in chunk:
            raise SystemExit(f"quote {name} is not inside its chunk - refusing to write")
        print(f"  quote[{name}] = {quote!r}")

    def cite(chunk_id: str, page: int, section: str, quote: str, conf: float = 1.0) -> dict:
        return {
            "chunk_id": chunk_id,
            "book": "bike_repair_manual_chris",
            "page": page,
            "section": section,
            "quote": quote,
            "evidence_grade": "A",
            "linked_to_chunk": True,
            "confidence": conf,
        }

    bundle3 = {
        "schema_version": "1.0.0",
        "corpus": "bike_repair_manual_chris_pdf_textlayer",
        "source_file": SID_NAME,
        "note": ("Pages ingested from the source PDF's own text layer (PyMuPDF), one chunk per cited region. "
                 "Grade A: these are the publisher's words, not a transcription. Ingested because comp-fork-seals "
                 "was an island and the suspension-fork pages carry the sentences that connect it."),
        "chunks": {
            "bike_repair_manual_chris_p0035_c00": {
                "chunk_id": "bike_repair_manual_chris_p0035_c00",
                "book": "bike_repair_manual_chris",
                "page": 35,
                "section": "Servicing",
                "source": SID_NAME,
                "text": chunk35,
            },
            "bike_repair_manual_chris_p0141_c00": {
                "chunk_id": "bike_repair_manual_chris_p0141_c00",
                "book": "bike_repair_manual_chris",
                "page": 141,
                "section": "AIR/OIL FORK",
                "source": SID_NAME,
                "text": chunk141,
            },
        },
    }
    (ROOT / "src" / "data" / "evidence-bundle-3.json").write_text(
        json.dumps(bundle3, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  wrote bundle with {len(bundle3['chunks'])} chunks")
    return write_expansion(cite, q_part_of, q_function, q_symptom, q_worn)


if __name__ == "__main__":
    raise SystemExit(main())

