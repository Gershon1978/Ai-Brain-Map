# HANDOFF — three batches that finish the map

Status at handoff (2026-10-25): **69 nodes / 63 edges / 152 citations / 43-chunk bundle,
36 of 43 chunks cited (7 unused), 7 disconnected components (largest 35).**

The bundle was grown from 36 to 43 chunks on 2026-10-25 (owner-approved). The 7 new chunks are
verbatim from the corpus and verified byte-identical. Five of them are not cited yet — batches 8b
and 8c below use them. `p0002_c02` and `p0585_c00` were **already** in the 36.

Goal: **one connected graph, 72 nodes / 74 edges, 43 of 43 chunks cited, 0 unused.**

---

## The six islands to join

| island | size | what it holds |
|---|---|---|
| main | 35 | drivetrain, hubs, rotors, standards, brake rotor side |
| cockpit | 16 | headset, steerer, stem, quill, star nut, top cap |
| brakes | 8 | caliper, lever, hose, pad, bleed, fluid rules |
| rear shock | 6 | shock, damper, spring, air chamber, bushing |
| fluids | 2 | `prop-fluid-dot`, `prop-fluid-mineral` |
| bb | 1 | `comp-bb-threaded` |
| fork seals | 1 | `comp-fork-seals` |

---

## Batch 8a — brakes + fluids  (ready, already sent to AI Studio)

**Target:** append 3 edges to `src/data/expansion-connectors.json` (which holds 0 nodes / 9 edges),
top-level `"batch": "phase8a-brakes"`. Do not touch the existing 9 edges. Still 0 nodes.

| id | src | dst | type | chunk_id | quote (verbatim) |
|---|---|---|---|---|---|
| `edge-conn4-pad-against-rotor` | `comp-brake-pad` | `comp-rotor-6bolt` | `interfaces_with` | `big_blue_book_p0663_c00` | `Brake pads are housed in the caliper and are forced against the rotor` |
| `edge-conn4-caliper-holds-pads` | `comp-caliper-hydraulic` | `comp-brake-pad` | `contains` | `big_blue_book_p0663_c00` | `Brake pads are housed in the caliper` |
| `edge-conn4-dot-fluid-in-caliper` | `prop-fluid-dot` | `comp-caliper-hydraulic` | `interfaces_with` | `big_blue_book_p0693_c00` | `Some manufacturers specify proprietary mineral fluids, while others use\nvarious automotive DOT brake fluid.` |

Claims:
- `Brake pads are forced against the rotor to slow the bike.`
- `The brake pads are housed in the caliper.`
- `Some manufacturers specify automotive DOT brake fluid for their hydraulic brake systems.`

All three: status `verified`, grade `A`, evidence_type `service_manual`.

⚠ The third quote contains **one line break** after "use" (the PDF wraps there). In JSON it is a
single `\n`. Do not join the lines, do not add a space at the break.

**After 8a:** 12 edges in that file, merged **69 / 66**, **5 components, largest 45**,
**155 citations** (107 byte-exact + 48 whitespace-only), **38 of 43 chunks cited, 5 unused**.
Update Test Q's pins to exactly those numbers.

---

## Batch 8b — fork (the bridge to the cockpit)

Adds the missing `comp-fork` node and joins the cockpit cluster to the wheels.

**New node**

| id | type | name | evidence chunk | quote |
|---|---|---|---|---|
| `comp-fork` | component | Fork | `bike_repair_manual_chris_p0089_c00` | `turns the fork and the front wheel` |

**New edges**

| src | dst | type | status | chunk_id | quote |
|---|---|---|---|---|---|
| `comp-headset` | `comp-fork` | `interfaces_with` | verified | `bike_repair_manual_chris_p0088_c00` | `both hold the front fork securely in the head tube` |
| `comp-steerer` | `comp-fork` | `part_of` | verified | `bike_repair_manual_chris_p0089_c00` | `connected to the steerer tube by the stem` |
| `comp-fork` | `sys-wheels` | `interfaces_with` | verified | `bike_repair_manual_chris_p0089_c00` | `turns the fork and the front wheel` |
| `comp-fork-seals` | `comp-fork` | `part_of` | **needs_review** | `bike_repair_manual_chris_p0071_c05` | `Check stanchions for scoring, indicating possible seal failure.` |

The last one cites a `[VISUAL DATA]` analysis, not manual prose, so it must stay `needs_review`.
It still connects the island; it just is not promoted.

---

## Batch 8c — shock + crank

| src | dst | type | status | chunk_id | quote |
|---|---|---|---|---|---|
| `comp-rear-shock` | `sys-wheels` | `interfaces_with` | verified | `bike_repair_manual_chris_p0148_c00` | `connects the rear wheel to the shock absorber` |
| `comp-crank-arm` (new) | `comp-bb-threaded` | `mounted_on` | verified | `bike_repair_manual_chris_p0002_c02` | `extract crank arm from bottom bracket spindle` |
| `comp-chainring` (new) | `comp-crank-arm` | `mounted_on` | **needs_review** | `bike_repair_manual_chris_p0003_c00` | `countersunk bolt holes for chainring attachment` |
| `comp-crank-arm` | `prop-chainline` | `has_property` | verified | `big_blue_book_p0585_c00` | `Chainline is the relation of the front and rear sprockets to the center plane` |

New nodes: `comp-crank-arm` (component), `comp-chainring` (subcomponent).
`p0003_c00` is a visual analysis too → `needs_review` for the chainring edge.

---

## Acceptance rules for every batch

A batch is accepted only if **all** of these hold. Verify them yourself and do not trust the app's
own test output — that is exactly how four earlier fabrications passed.

1. The target file's node count is unchanged and the edge count is exactly as stated.
2. Every new `chunk_id` exists in `src/data/seed-evidence.json`.
3. Every new quote is a **literal substring** of that chunk's `text` (mind the `\n` rule).
4. Every relation is legal in `src/data/relation-ontology.json` at both ends.
5. No new dangling endpoints, no duplicate `src|type|dst`.
6. `seed_graph.json` and `seed-evidence.json` are byte-identical to their previous state.
7. The merged totals equal the projected numbers, recomputed from the files, not copied.
8. Test Q passes with updated pins; `tsc --noEmit` exit 0; `vite build` exit 0.

`tools/verify_wake22.py` does 1-7 mechanically against `kb.db` (needs the database file);
`tools/check_batch8a_quotes.py` checks the three 8a quotes against the bundle.

## Known soft spots (not blockers)

- The engine answers from documented edges only; it does not evaluate property-vs-property fitment
  (hub O.L.D. vs frame dropout). Deliberate: safe but limited.
- 48 of the seed's 59 citations differ from their chunk in whitespace only (OCR double spaces, e.g.
  `* DOT FLUID` vs `*   DOT FLUID`). Word sequences are identical. They were deliberately not
  "tidied": rewriting evidence text by hand is forbidden.
- `public/sql-wasm.wasm` is absent from this repo; only the optional local-DB attach needs it.

