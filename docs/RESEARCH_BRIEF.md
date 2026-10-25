# Research brief: closing five measured gaps in a bicycle knowledge graph

This file is the input to a research model (Gemini / AI Studio). Everything it asks for was derived
mechanically by `tools/weak_links.py` from an 87-node graph, not guessed. Read the RULES first — a row
that breaks them is worse than no row.

## What the graph already has (so you do not re-research it)

- 87 nodes: 19 components, 25 subcomponents, 12 standards, 4 properties, 4 symptoms, 4 failure modes,
  5 procedures, 2 measurements, 4 compatibility rules, 2 safety constraints.
- Citations are verbatim quotes tied to a page or URL. Claims without a verbatim quote cannot be added.
- Existing torque values: crank bolt 25–38 Nm (Big Blue Book p349); Center Lock ring (grade B,
  unconfirmed). That is the entire numeric record.

## The five gaps, as questions

**G1 — NUMBERS.** The graph has 2 measurements for 44 components. For each fastener below, what is the
specified tightening torque, with the exact wording and the brand/model scope it applies to?
`stem clamp bolts` · `handlebar clamp` · `seatpost clamp` · `saddle rail clamp` · `6-bolt rotor bolts` ·
`Center Lock ring` · `caliper mounting bolts` · `cassette lockring` · `bottom bracket cups` ·
`pedal spindles` · `crank bolts` · `derailleur clamp` · `brake lever clamp` · `headset top cap`.
Also: rotor minimum thickness, brake pad minimum thickness, chain wear limit (% elongation).

**G2 — TOOLS.** The graph has 0 tool nodes. For each procedure — hydraulic brake bleed (DOT and
mineral), threadless headset adjustment, hub bearing adjustment, hub bearing replacement, cassette
removal — which specific tools are required? Name the tool type; a manufacturer's own part number is
acceptable only if the source states it.

**G3 — DIAGNOSTIC TESTS.** The graph has 0 `diagnostic_test` nodes. For each check, what is the exact
test and its pass/fail threshold? `chain wear` · `rotor wear` · `brake pad wear` · `hub bearing play` ·
`headset play` · `spoke tension` · `rim wear` · `tyre pressure by tyre width`.

**G4 — STANDARDS CURRENTLY MARKED "UNCONFIRMED" IN THE GRAPH.** Give the exact value and the document
that states it: `chain pitch` · `XDR driver spline dimensions / added length vs XD` · `steerer tube
diameters (1", 1-1/8", 1.5", tapered) and their SHIS names` · `thru-axle thread pitch and length
standards` · `Center Lock ring torque`.

**G5 — SYMPTOM LIBRARY.** The graph has 4 symptoms, all from one grade-C OCR chart. For each symptom,
give the distinguishing test that separates the competing causes, and the fix for each cause:
`creak from bottom bracket under load` · `ghost shifting under power` · `brake rub after wheel
refit` · `soft/spongy lever` · `wheel wobble` · `chain suck` · `disc rotor rub when hot` ·
`suspension fork stiction`.

## ALLOWED SOURCES — nothing else counts

| id | source | what it is authoritative for | caveat |
|---|---|---|---|
| S1 | `si.shimano.com` | Shimano dealer manuals, SHIS naming, torque tables | automated fetch returns **HTTP 403**; if you cannot open it, emit UNKNOWN — do not substitute another site |
| S2 | `sram.com` (incl. `/en/service` PDFs) | SRAM/RockShox/Zipp manuals, torque, service intervals, DOT vs mineral bleed | PDFs must be opened, not summarised from memory |
| S3 | `parktool.com/en-us/blog/repair-help` | diagnostics, procedures, tool requirements, some torque | article pages are dated; record the date |
| S4 | `giant-bicycles.com` manuals library | owner/component manuals, per-model torque tables | model-year specific |
| S5 | `trekbikes.com` (correct manual path — the old `/owners_manuals/` URL 404s) | owner manuals with torque tables | model-year specific |
| S6 | ISO 4210 / ETRTO / SHIS documents **only if you can open the document itself** | safety requirements, tyre/rim sizing, headset naming | secondary summaries are NOT allowed |

**FORBIDDEN as sources:** forums, Reddit, Wikipedia, retailer or marketplace listings, YouTube,
review sites, aggregator blogs, AI-generated pages, or any domain not in the table above. Do not infer a
value from a similar model. Do not average two brands into one number.

## RULES — a row that breaks one of these must be omitted

1. **One row = one source.** Never merge two documents into one value.
2. **Every value needs a verbatim quote containing that value**, copied character-for-character from the
   source, plus the page number or URL section it came from. No quote → no row.
3. **Scope is a field, not an assumption.** If a value is brand- or model-specific, emit one row per
   brand/model and put the scope in `applies_to` ("SRAM G2 2023+", "Shimano 11-speed HG", "all").
4. **If the allowed sources do not state it, say so**: `"value": null, "notes": "not stated in allowed
   sources"`. Emitting a null is a success; estimating is a failure.
5. **No unit conversion** unless you give the original value and unit in `quote`.
6. **No source outside the table.** If the only source you find is forbidden, the answer is null.
7. **Record `retrieved_at`** (YYYY-MM-DD) for every row; a web page changes, a manual page does not.
8. **Output JSON only** — no preamble, no prose, no markdown fences. An array of row objects.

## OUTPUT SCHEMA (all keys required; use null rather than omitting a key)

```json
[
  {
    "gap": "G1",
    "component": "stem",
    "fastener_or_part": "stem clamp bolts",
    "field": "torque",
    "value": 5.5,
    "unit": "Nm",
    "min": 5.0,
    "max": 6.0,
    "applies_to": "SRAM G2 brake levers, 2023+",
    "source_id": "S2",
    "source_title": "SRAM MTB Disc Brake Hose Shortening and Bleed Manual",
    "source_url": "https://www.sram.com/...",
    "page": "p.7",
    "quote": "exact sentence from the document containing 5.5 Nm",
    "retrieved_at": "2026-10-25",
    "confidence": "high",
    "notes": null
  }
]
```

`field` must be one of: `torque`, `dimension`, `test_threshold`, `tool`, `symptom`, `cause`, `fix`,
`standard_name`. For `field: "tool"` put the tool name in `notes` and the procedure in
`fastener_or_part`. For `field: "symptom"|"cause"|"fix"` put the prose in `notes` and keep `value` null.

## What happens to your output

Each row is checked by `tools/validate_research_datasheet.py`, which rejects: a `source_url` whose domain
is not in the allowed table, a numeric `value` whose `quote` does not contain that number, a missing
`quote`, a missing `retrieved_at`, and `confidence: high` without a `page`. Surviving rows are ingested
as **grade A** citations (web rows carry `retrieved_at`); a null row becomes an explicit
`unknown_requirement` node, which the graph already has a type for.

Priority if you cannot fill everything: **G1 torque for rotor bolts, caliper bolts, stem clamp and
cassette lockring → G4 chain pitch and steerer diameters → G3 chain wear % → G2 bleed tools → G5.**

