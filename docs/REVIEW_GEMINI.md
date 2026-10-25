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

## The lesson

An external reviewer that reads the corpus but invents identifiers produces work that is *more*
dangerous than an obvious hallucination, because the quotes check out and the conclusions look
auditable. **Never accept a review whose identifiers you have not machine-verified against the data
first** — and never let a reviewer's promotion override a grade rule you wrote after being burned.
