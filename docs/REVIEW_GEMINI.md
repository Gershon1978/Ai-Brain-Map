# External review — Gemini, 2026-10-25 (chat `/app/37b8b3003108b51e`)

An outside model was asked four questions about the frozen state, with the whole repo shared as a
Google Drive folder. Its answer was audited mechanically, not read politely. The audit is the
interesting part.

## Pass 1 — unusable, and why

Gemini returned confident per-edge verdicts on **15 edge ids that do not exist**:

```
edge-cassette-on-freehub          edge-rotor-on-hub-6bolt       edge-rotor-centerlock-fit
edge-quill-stem-in-steerer        edge-hub-motor-in-wheel       edge-chain-drives-cassette
edge-freewheel-allows-rotation    edge-remover-tool-engages-lockring
edge-shift-wire-retention         edge-top-cap-compresses-spacers
edge-brake-pad-thickness-inspection   edge-star-nut-setter-drive
edge-frame-bushing-play           edge-shock-air-chamber-extension
edge-bms-cutoff-controller
```

Machine check against all 73 edge ids in `src/data`: **0 of 15 exist**.

It had read the corpus, though — of 13 quoted phrases, **10 were genuinely present** (5 byte-exact,
5 whitespace/case-only) and 3 were invented. Chunk ids it cited (`p0585`, `p0679`, `p0820`,
`p0003`, `p0066`) all resolve to real chunks.

So the failure mode is precise, and it is the same one this project has caught four times before:
**real evidence, invented structure.** It reconstructed plausible ids from the *shape* of the naming
convention and then reasoned about statuses as if they were facts. Every verdict was void.

Reproduce: `tools/verify_review_claims.py`.

## Pass 2 — after injecting the real ids

The 15 real `needs_review` edges were pasted in, with the previous pass explicitly voided. The second
answer used only supplied ids (13 of 15 referenced; none invented). Verdicts:

| # | edge | Gemini | project rule | outcome |
|---|---|---|---|---|
| 1 | comp-brake-hose_interfaces_with_comp-caliper-hydraulic | KEEP | caution ≠ interface | agreed |
| 2 | comp-rear-hub_conforms_to_std-brake-thru-axle | DROP | grade-B presumption | agreed |
| 3 | edge-conn4-caliper-uses-dot-fluid | **PROMOTE** | grade A, but **Hayes-specific** | **rejected: scope** |
| 4 | edge-conn4-chainring-on-crank | DROP | grade B | dropped-from-verified, kept as review |
| 5 | edge-conn4-crank-on-bb-spindle | DROP | removal ≠ installed | too harsh — keep, do not delete |
| 6 | edge-conn4-fork-turns-front-wheel | DROP | co-motion ≠ attachment | too harsh — keep, do not delete |
| 7 | edge-conn4-reartriangle-links-wheel | **PROMOTE** | grade A, quote names the **shock absorber** | **accepted as a finding, not as a promote** |
| 8 | edge-derailleur-conforms-to-pitch | DROP | visual estimate | agreed |
| 9 | edge-headset-interfaces-steerer | DROP | quote is a table of contents | agreed |
| 10 | edge-rotor6bolt-incomp-centerlock | DROP | `mechanical_principle`, not manual text | defensible, keep as review |
| 11 | edge-steerer-conforms-to-dia | DROP | visual estimate | agreed |
| 12 | edge-stem-conforms-to-torque | **PROMOTE** | **grade B** | **rejected: rule 3** |
| 13 | edge-unknown-freehub-length | KEEP | first-class unknown marker | agreed |
| 14 | edge-xdr-conforms-to-bearing-dim | DROP | visual estimate | agreed |
| 15 | std-brake-centerlock…torque | **PROMOTE** | **grade B**, and the quote says "verify with service manual" | **rejected: rule 3** |

**All four promotions fail.** Two are grade-B sources, which rule 3 forbids from backing `verified`.
One generalises a Hayes-specific sentence to the generic `comp-caliper-hydraulic` node, which would
turn one brand's spec into a universal property. The fourth is the real catch, below.

### The one finding worth keeping (edge 7)

`edge-conn4-reartriangle-links-wheel` targets `sys-wheels` with the relation `affects`, and its claim
is hedged as a "Connectivity hypothesis". But the cited sentence is unhedged and specific about the
*other* endpoint:

> The rear triangle of the frame, which connects the rear wheel to the shock absorber

That supports a rear-triangle ↔ **rear-shock** connection — a structural relation — not a vague
"affects wheels" coupling. The status is arguably fine; the **type and target are wrong**, which is a
different defect from the one the grade rules cover, and one no test in the suite can see (the
ontology checks only that the endpoints are *legal* types, never that they are the *right* ones).

Proposed correction, **not applied** — it needs approval because it changes serialized state:

- retarget to `comp-rear-shock`, choose the ontology relation that means "structurally connects"
  (check `relation-ontology.json`; `affects` is the wrong one), and drop the "hypothesis" hedge from
  the claim since the sentence is declarative.
- expected effect: node/edge counts unchanged, `needs_review` 15 → 14, and one edge stops being a
  hypothesis. Test Q pins would move and must be recomputed, not edited.

## Its other answers

- **Q1, the island:** "defensible; the evidence to join it is not in this bundle." Agrees with the
  frozen state, and correctly refuses to use section titles or co-mention as attachment.
- **Q3, what the tests cannot see:** the same blind spot identified above — the suite validates
  endpoint *types* and quote *presence*, never whether a citation actually supports the relation
  drawn from it. That is precisely the failure mode this review exercised twice.
- **Q4, next unit:** a structured bottom bracket interface standard, to bridge the crankset island
  into the drivetrain. Reasonable, and consistent with the island being evidence-starved rather than
  mis-built.

## Correction to my own proposal (same session)

I proposed retargeting `edge-conn4-reartriangle-links-wheel` to `comp-rear-shock`. That was wrong, and
the data said so in two ways:

1. **The precise edge already existed.** `edge-conn4-reartriangle-holds-shock`
   (`comp-rear-triangle → comp-rear-shock`, `interfaces_with`, verified) carries the same chunk and the
   same sentence. Retargeting would have produced a duplicate — the verifier's `src|type|dst` check
   would have failed the build.
2. **The vague edge is load-bearing.** Deleting it split the graph from `[69, 3, 1]` into
   `[62, 7, 3, 1]`: the 7-node island is the whole rear-suspension cluster, which touches the rest of
   the graph through nothing else.

So the edge was restored, the change reverted, and the measurement kept in `docs/STATE.md`. The lesson
is not "Gemini was wrong" — it is that **a reviewer's finding has to be checked against the graph's
existing edges and its connectivity, not just against the quote.** The quote check passed; the
structural check is what killed it.

### What the review did earn

- A verified statement that the graph's vaguest edge is also its most load-bearing one, now documented.
- A `tsc` hazard found and fixed: an export folder inside the repo was being compiled.
- Two stale claims in our own docs corrected (`59 verified/14 needs_review` → `58/15`; "three edges
  carry the hypothesis prefix" → two).

### Third pass — a search, not an opinion, and it paid

After the experiment failed I gave Gemini a **search** task with a machine-checkable output format:
find any sentence attaching the rear suspension to the frame; quote it character for character; if
nothing exists, print `NO FRAME ATTACHMENT EVIDENCE IN CORPUS`.

It returned exactly one candidate:

```
big_blue_book_p0921_c00 | The rear shock can develop wear at the bushing of the frame attachments. | A
```

Machine check: **byte-exact substring** of that chunk, page 921, section `SHOCKS (REAR SHOCKS)`. That
sentence is now the anchor of `phase9-frame` — `comp-frame` exists as a node because of it, and
`comp-rear-shock → comp-frame` is a verified `mounted_on` edge resting on it.

This is the shape of review that works: **one narrow question, a strict answer format, and an
identifier/quote check before belief.** The same pass also established the negative — no chunk
attaches the crankset — which is now the documented next target.

### Fourth pass — a correct negative

The same search, aimed at the last hole (the 3-node crankset island), returned
`ONLY REMOVAL INSTRUCTIONS`. That is the right answer and it was independently confirmed:
`tools/scan_crankset.py` finds **0** sentences asserting an installed relationship, **1** that only
tells the mechanic to confirm shell width and threading, and **5** removal/service steps. A reviewer
that can say "there is nothing here" is worth more than one that always finds something.

### Fifth pass — the review caught me being inconsistent

I asked it to judge two of my own decisions in one session: demoting `comp-headset-threadless →
sys-cockpit` (evidence = a chapter TOC) while promoting `comp-rear-shock → comp-frame` (evidence =
"wear at the bushing of the frame attachments").

Answer, verbatim:

```
A: CORRECT - A table of contents reflects editorial taxonomy, not an explicit mechanical assertion.
B: OVERREACH - Status should be needs_review; a noun phrase inside a diagnostic wear test refers to
   "the frame attachments" without asserting an explicit, installed mounted_on standard.
VERDICT: INCONSISTENT - Case B must change to needs_review ...
```

It was right, and for the exact reason I had used one message earlier against the crank-puller
sentence: **a wear diagnostic presupposes an installed state, it does not assert one.** Accepting it
cost a `verified` edge and gained consistency; the edge also picked up a second, stronger quote
("shock mounting bolt tightness") so no evidence was lost.

House rule that came out of it: *presupposition is not assertion.* A sentence may only carry a
`verified` structural relation if it says the relation, not if it implies the part exists.

### Sixth pass — its acceptance queries found an engine defect (and one of its own expectations was wrong)

Given the harness task, it produced six mechanic-style queries plus the id each would lean on. Four of
six ids were real; `edge-cassette-xdr-fits-freehub` and `edge-cassette-xd-fits-freehub` do not exist
(the real ones are `edge-xdr-incomp-cassette` and `edge-cassette-fits-freehub`), so the queries were
re-mapped onto real pairs — the *queries* were right even where the ids were not.

Its expected verdict for 6-bolt → Center Lock was `incompatible`. The engine said `incompatible` too —
and both were wrong: that exclusion edge is `needs_review`, so a confident exclusion is exactly what
the project forbids. Running the harness surfaced a real one-sided gate in `constraint-engine.ts`
(fitment was gated on review status, exclusion was not). Fixed, pinned by Test S.

That is the most useful thing a reviewer has done in this project: **its test cases, not its answers.
** The answers carried two invented ids; the test cases exposed a defect that four green gates and
17 passing tests had missed.

### Seventh pass — the coverage audit found a logic inversion

Asked which paths the 6-case harness did *not* cover, it returned 8 gaps with `UNFILLABLE` used
honestly twice. Verified against the graph: 5 usable, 2 correctly unfillable, 1 wrong
(`std-quill-diameter-fit` has no edge to `comp-steerer`). Its claim that `conflicted` is unreachable
was true and checkable — 0 edges carry `conflicts[]`, 0 pairs carry opposing edges.

Implementing the usable gaps (12 cases) immediately failed: a **verified `conforms_to` with no
caveats** returned `unknown_missing_evidence` while the same relation *with* caveats returned
`conditionally_compatible`. That inversion is now fixed and pinned (S5/S6).

Two passes in a row, its *test cases* found engine defects its *answers* would never have found.

## The lesson

An external reviewer that reads the corpus but invents identifiers produces work that is *more*
dangerous than an obvious hallucination, because the quotes check out and the conclusions look
auditable. **Never accept a review whose identifiers you have not machine-verified against the data
first** — and never let a reviewer's promotion override a grade rule you wrote after being burned.
