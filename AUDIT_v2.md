---

# Evidence audit v2 — 2026-10-25 (supersedes the three tables above)

Reviewer objection accepted: three of the nine planned edges asserted more than their sentences
say. Every edge was re-audited against the bundle text. Verdicts, with the exact sentence that
decides each one:

| # | batch | edge | verdict | deciding text |
|---|---|---|---|---|
| 1 | 8a | `comp-brake-pad -> comp-rotor-6bolt` | **KEEP** | "Brake pads are housed in the caliper and are forced against the rotor" — direct contact |
| 2 | 8a | `comp-caliper-hydraulic -> comp-brake-pad` | **KEEP** | "Brake pads are housed in the caliper" — direct containment |
| 3 | 8a | fluid ↔ caliper | **RE-QUOTE + RE-TYPE** | `big_blue_book_p0710_c00`: "Hayes® offers brakes in both mineral oil and hydraulic brakes using DOT\n3 or DOT 4 brake fluid." The old quote (`p0693_c00`) only says manufacturers differ. Direction flips to `comp-caliper-hydraulic -> prop-fluid-dot` (`has_property`), because `interfaces_with` does not accept a `property` as its source, and the claim ("a hydraulic caliper may use DOT fluid") is a property of the caliper, not an interface of the fluid. `needs_review`, because the class is mixed — other calipers use mineral oil |
| 4 | 8b | `comp-steerer -> comp-fork` (`part_of`) | **KEEP, RE-QUOTE** | `p0088_c00`: "the part of the fork known as the steerer tube". My earlier quote described the *stem*, exactly as the reviewer said; the relation itself is stated outright in this sentence |
| 5 | 8b | `comp-headset -> comp-fork` | **KEEP** | "both hold the front fork securely in the head tube" |
| 6 | 8b | `comp-fork -> sys-wheels` | **RE-TYPE + `needs_review`** | only co-motion is asserted: "turns\nthe fork and the front wheel". `interfaces_with` cannot target a `subsystem`, so the relation is `affects` — and at `needs_review`, because co-motion is not attachment |
| 7 | 8b | `comp-fork-seals -> comp-fork` (`part_of`) | **DROP** | "Check stanchions for scoring, indicating possible seal failure." locates a symptom, it does not say the seals are part of the fork. No other bundled chunk says it. The edge is not replaced |
| 8 | 8c | `comp-rear-shock -> sys-wheels` | **REDESIGN** | the sentence credits a third part: "The rear triangle of the frame,\nwhich connects the rear wheel to the shock\nabsorber". Add node `comp-rear-triangle` (component) citing that sentence, then `comp-rear-triangle -> comp-rear-shock` (`interfaces_with`, `verified`) and `comp-rear-triangle -> sys-wheels` (`affects`, `needs_review` — a linkage is not membership) |
| 9 | 8c | `comp-crank-arm -> comp-bb-threaded` | **KEEP** | "Tighten crank puller to extract crank arm from bottom bracket spindle." |
| 10 | 8c | `comp-chainring -> comp-crank-arm` | **KEEP as `needs_review`** | "countersunk bolt holes for chainring attachment" — structural statement, but from a `[VISUAL DATA]` analysis, so it does not buy `verified` |
| 11 | 8c | `comp-crank-arm -> prop-chainline` (`has_property`) | **DROP** | "Chainline is the relation of the front and rear sprockets to the center plane" says nothing about the crank arm. Chainline is a property of the sprocket arrangement, and `prop-chainline` is already attached to the map via `comp-cassette` |

## What that actually yields (recomputed, not targeted)

| | now | after the audited batches |
|---|---|---|
| nodes | 69 | **73** (+`comp-fork`, +`comp-crank-arm`, +`comp-chainring`, +`comp-rear-triangle`) |
| edges | 63 | **73** (10 added; 2 dropped, 1 redesigned into 2) |
| citations | 152 | **166** |
| chunks cited | 36 of 43 | **41 of 43**, unused 2 (`p0693_c00`, `p0071_c05`) |
| components | 7 | **3** — largest **69 (95%)**, then `{comp-bb-threaded, comp-crank-arm, comp-chainring}` (3) and `comp-fork-seals` alone (1) |

These numbers come from `tools/verify_batch_plan.py`, which consumes the **exact proposed records** —
literal quotes, real statuses — and recomputes everything, then compares to the claims above. Its
output is committed at `docs/batch_plan_verification.txt`: **PROBLEMS 0, VERDICT PASS.**

Status split after the batches: nodes **64 verified / 1 candidate / 8 needs_review**;
edges **59 verified / 14 needs_review**.

## What the ontology forced (found by the checker, not by me)

Three of my proposed records were **illegal relations**, and my earlier verifier had been reading
`source_types`/`target_types` while the ontology actually declares
`allowed_source_types`/`allowed_target_types` — so its "legal at both ends" verdict had been vacuous
for every edge it ever passed.

- `interfaces_with` accepts `component | subcomponent | interface` on **both** ends. A `property`
  (DOT fluid) cannot be its source, and a `subsystem` (`sys-wheels`) cannot be its target.
- A `subsystem` is therefore reachable only by `part_of` or `affects`. `part_of` would claim
  membership ("the fork is part of the wheels subsystem") which the text does not say, so both
  subsystem links are `affects` at `needs_review`.

This is the useful part of the exercise: the ontology, not the target count, decided the shape.


## Exact quote strings (extracted from the bundle, line breaks included)

Five of the sentences are wrapped in the source PDF, so a one-line copy would only match after
whitespace collapse. These are the byte-exact strings to put in the JSON `quote` field; `\n` below
means one real newline inside the JSON string:

| edge | chunk | quote (byte-exact) |
|---|---|---|
| 8a pad→rotor | `big_blue_book_p0663_c00` | `Brake pads are housed in the caliper and are forced against the rotor` |
| 8a caliper→pad | `big_blue_book_p0663_c00` | `Brake pads are housed in the caliper` |
| 8a dot→caliper | `big_blue_book_p0710_c00` | `Hayes® offers brakes in both mineral oil and hydraulic brakes using DOT\n3 or DOT 4 brake fluid.` |
| 8b headset→fork | `bike_repair_manual_chris_p0088_c00` | `both hold the front fork securely \nin the head tube` |
| 8b steerer→fork | `bike_repair_manual_chris_p0088_c00` | `the part of\nthe fork known as the steerer tube` |
| 8b fork→wheels (`needs_review`) | `bike_repair_manual_chris_p0089_c00` | `turns\nthe fork and the front wheel` |
| 8c rear triangle (node + 2 edges) | `bike_repair_manual_chris_p0148_c00` | `The rear triangle of the frame,\nwhich connects the rear wheel to the shock\nabsorber` |
| 8c crank→bb | `bike_repair_manual_chris_p0002_c02` | `Tighten crank puller to extract crank arm from bottom bracket spindle.` |
| 8c chainring→crank (`needs_review`) | `bike_repair_manual_chris_p0003_c00` | `countersunk bolt holes for chainring attachment` |

Note the space before the newline in the `p0088_c00` headset quote — the PDF has a trailing space.
Copy the strings as given, do not "clean" them.


**Not one component.** The earlier promise of a single connected graph was a target, and the bundle
does not support it: there is no bundled sentence linking the crank cluster, or `comp-fork-seals`,
to anything else. The plan no longer pretends otherwise. If a single component matters, it needs
new evidence (a crank/BB chunk that reaches the drivetrain, and a fork-seal chunk) — an owner
decision, not a modelling trick.

## Process rule adopted from the review

A batch may not certify itself. The Test Q pins are written from `tools/verify_wake22.py`, which
recomputes nodes, edges, citations, coverage and connectivity **from `seed_graph.json` plus the
expansion files**, independently of whatever the batch reports. If the batch's own numbers and the
verifier disagree, the verifier wins and the batch is rejected — never the reverse. `needs_review`
is reserved for evidence that is suggestive but insufficient; it is not a shelf for a relationship
that needs redesigning.
