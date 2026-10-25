# Frozen state — 2026-10-25

## The numbers (measured by `tools/verify_app_state.py`, not asserted)

| | |
|---|---|
| nodes | **74** — 65 verified, 1 candidate, 8 needs_review |
| edges | **75** — 59 verified, 16 needs_review |
| citations | **169** — 121 byte-exact, 48 whitespace-only (all in the frozen seed) |
| bundle | 43 chunks; **41 cited**, 2 deliberately uncited |
| components | **3** — largest 70 (95%), crankset island 3, `comp-fork-seals` 1 |
| batch ledger | 13 rows (seed + 12 expansion files) |

Checks, all observed on this state:

```
npm install                                  exit 0 (184 packages, no flags)
npm run lint   (tsc --noEmit)                exit 0
npm run build  (vite build)                  exit 0, built in ~2s
npx tsx tools/run_suite.mjs                  16/16 passed, exit 0
python tools/verify_app_state.py             PROBLEMS 0, PASS
```

Verifier warnings are **classified by where they can be fixed**, and that classification is enforced:

- **Frozen-seed artefacts — 59, counted as a class with an exact expected size** (48 whitespace-only
  citations + 11 undeclared sections, all inside `seed_graph.json`). Drift in either direction is a
  failure: more means new defects, fewer means the frozen seed was edited and this record is stale.
- **Outside the seed: zero tolerated.** Every expansion batch is byte-exact with a declared section,
  and a soft match or missing section anywhere in a batch is now a **PROBLEM, not a warning** — the
  verifier exits 1. Proven by sabotage: adding one extra space to a `phase9-frame` quote produces
  `VERDICT: FAIL` and names the edge.
- **1 known exception** — `comp-bb-threaded`'s section is truncated inside the frozen seed. Printed on
  every run; the verifier fails if the exception ever stops occurring, so the list can only shrink.

A green verifier means *the declared checks pass*. It does not mean every possible defect is ruled
out; it means the noise is now separated from the signal.

## The mechanical canon (four distinctions, each learned by catching a real defect)

1. **Co-motion is not attachment.** "Turns the fork and the front wheel" does not prove the wheel is
   mounted to the fork.
2. **A removal instruction is not an installed state.** "Extract the crank arm from the bottom bracket
   spindle" does not document how the arm is fixed.
3. **A grade-B visual estimate cannot back a `verified` claim**, and never a number.
4. **Presupposition is not assertion.** Naming a part as a modifier, a wear site or a diagnostic
   condition establishes that it exists in discourse, not that it is fixed to anything. *Worked
   example:* "wear at the bushing of the frame attachments" presupposes a mounting without stating
   one, which is why `comp-rear-shock → comp-frame` is `needs_review` and not `verified`.

Rules 1–3 were enforced by hand and then encoded in statuses. Rule 4 is now the one to apply first in
any new batch: it is the cheapest way an author smuggles world knowledge into an evidence graph.

## What is deliberately provisional

Fifteen edges carry `needs_review`. Because the engine only returns `verified_compatible` across
`verified` edges, status alone is the gate — a "hypothesis" prefix is a human-readable warning, not a
mechanism. Two of the fifteen are explicitly labelled, because they express coupling rather than
documented attachment:

| edge | why provisional |
|---|---|
| `comp-fork → sys-wheels` (`affects`) | the text asserts co-motion ("turns the fork and the front wheel"), not attachment |
| `comp-rear-triangle → sys-wheels` (`affects`) | a linkage, not membership — and it is load-bearing, see below |

The other thirteen fall into three classes: **grade-B visual estimates** (`edge-steerer-conforms-to-dia`,
`edge-derailleur-conforms-to-pitch`, `edge-xdr-conforms-to-bearing-dim`,
`comp-rear-hub_conforms_to_std-brake-thru-axle`, `edge-conn4-chainring-on-crank`), **brand-scoped
statements dressed as universal properties** (`edge-conn4-caliper-uses-dot-fluid` cites Hayes
specifically), and **principle-derived claims with no textual assertion** (`edge-rotor6bolt-incomp-
centerlock` is `evidence_type: mechanical_principle`, status `needs_review`). Its first quote only
describes six-bolt flanges; its second is a truncated figure caption that stops mid-phrase at
"…accept rotors made with". The exclusion is *reasoned* from "a center-lock hub is designed with
splined fittings to accept rotors made with a matching internal pattern" plus "six bolts on a flange" —
which is why the record says `mechanical_principle` and not `service_manual`. Both quotes live in the
frozen seed, so neither the truncation nor the whitespace can be repaired without unfreezing it.

## The suspension cluster now hangs on a structural anchor (resolved 2026-10-25)

Before `phase9-frame`, the whole rear-suspension subsystem — `comp-rear-shock`, `comp-rear-triangle`
and the five `comp-shock-*` subcomponents — touched the rest of the graph **only** through
`edge-conn4-reartriangle-links-wheel`, the vaguest edge in the graph. Removing that one edge split the
graph from `[69, 3, 1]` into `[62, 7, 3, 1]`, which is how the weakness was found.

`phase9-frame` adds the node the corpus had been describing all along without ever naming: `comp-frame`.

| addition | evidence | status |
|---|---|---|
| `comp-frame` | p0148 "can move independently of the … rest of the frame" | verified |
| `comp-rear-shock → comp-frame` (`mounted_on`) | p0921 "…the bushing of the frame attachments" **and** "…shock mounting bolt tightness" | **needs_review** |
| `comp-steerer → comp-frame` (`interfaces_with`) | p0861_c02 "This draws the steerer tube upwards relative to the frame…" | needs_review |

The shock edge was briefly `verified` and was demoted after an independent judgment check
(`docs/REVIEW_GEMINI.md`): both sentences **presuppose** a mounting — they talk about wear at the
frame attachments and about checking a shock mounting bolt — but neither states that the shock is
mounted to the frame. That is the same standard that demoted "extract crank arm from bottom bracket
spindle", so consistency requires `needs_review`. Both quotes are cited, byte-exact, and the cluster
stays attached (connectivity does not depend on status).

All three quotes were **sliced out of the chunk text by a script**, so byte-exactness is a property of
construction rather than of careful typing. The steerer edge stays provisional on purpose: the manual
asserts relative motion, not a pressed-in fit.

The vague `edge-conn4-reartriangle-links-wheel` was **kept**, not deleted: it is still the only edge
that speaks about the wheel end, and the graph is stronger with a documented hypothesis than with a
deleted fact. The suspension cluster is now doubly attached.

### The gap that nearly shipped: app and verifier disagreed about which files exist

`tools/verify_app_state.py` globs `expansion-*.json`; `src/services/graph-loader.ts` imported a
hand-maintained list. Adding `expansion-frame.json` therefore changed what the **verifier** measured
while the **app** kept serving the old graph — the suite went 16/16 green against `73/73/166` while the
verifier reported `74/75/169`. Two green checks, two different graphs.

Fixed with `tools/verify_registry.py`, which fails when any `expansion-*.json` is not imported and
registered, and now runs first in every cycle. `import.meta.glob` was rejected deliberately: it is
Vite-only and would break the headless `tsx` runner.

Operational lesson from the same session: an export folder inside the repo (`_for_gemini/`) was
picked up by `tsc`, breaking `npm run lint` for everyone. It now lives outside the repo and `tsconfig`
excludes it explicitly.

## Rejected evidence (kept, uncited, pinned)

- `big_blue_book_p0693_c00` — "manufacturers differ" is too generic to establish a fluid–caliper link.
- `bike_repair_manual_chris_p0071_c05` — a visual seal hint; it locates a symptom, it does not say the
  seals are part of the fork.

Both are listed in `EXPECTED_UNUSED` in Test Q, so neither can quietly become cited.

## The app was blank while every check was green (fixed 2026-10-25)

Four gates were green — registry guard, `tsc`, 16/16 suite, verifier `PROBLEMS 0` — and the shipped
app rendered **nothing**. Opening `localhost:8080` in a real browser produced:

```
ReferenceError: __DEFINES__ is not defined          (Vite's modulepreload polyfill)
ReferenceError: __HMR_CONFIG_NAME__ is not defined  (Vite's dev client, bundled into production)
```

Both throw on the first statement of the bundle, so React never mounted. Neither was a build failure:
`vite build` exited 0 every time. **No check in the project ever loaded the page**, so the failure was
invisible — the build, the tests and the verifier all operate on source and data, not on a running app.

Root causes, both AI-Studio-era assumptions that a standalone build does not satisfy:

1. the modulepreload polyfill dereferences a build-time `__DEFINES__` global that AI Studio injected;
2. the dev/HMR client ends up in the bundle with its dev-server placeholders unreplaced (reproduced on
   Vite 8/rolldown **and** Vite 7, so it is not a version bug).

Fixes in `vite.config.ts`: the polyfill is disabled (it only polyfills `modulepreload` for browsers
that lack it), `__DEFINES__` is defined as `{}` as a belt, and a small `dropViteDevClient` plugin
redirects any import of `vite/client` / `vite/dist/client` to an empty module.

**New gate: `tools/smoke_app.py`.** It loads the served `dist/` over CDP and asserts zero console
errors, zero uncaught page errors, a mounted `#root`, and that the UI's own counters equal the counts
computed from `src/data`. It prints SKIP (exit 0) when no browser is reachable rather than pretending
to pass. Current result:

```
smoke: url=http://localhost:8080  mounted=1  nodes=74  edges=75  chunks=43
PASS - built app runs, React mounted, UI counters match src/data
```

Two stale strings died with it: the provenance label was hardcoded `(36 chunks)` while the bundle had
grown to 43 — now computed from `seed-evidence.json` — and the app subtitle leaked raw batch ids
(`phase8a-brakes`) and listed Brakes twice; it is now de-duplicated and fully named. The badge reads
`KNOWLEDGE EXPLORER`, not `PHASE 5 EXPLORER`.

### The lesson

A green pipeline proves what it checks and nothing else. Build/test/verify all ran *before* the
browser, so "the app builds" was mistaken for "the app works" for an entire session. Any project whose
deliverable is a web page needs one check that opens the page.

## Islands, measured rather than argued

| island | size | why it is still isolated |
|---|---|---|
| crankset (`comp-bb-threaded`, `comp-chainring`, `comp-crank-arm`) | 3 | no installed-relationship sentence exists: `tools/scan_crankset.py` finds 0 assertions, 1 procedural, 5 removal steps |
| `comp-fork-seals` | 1 | **2** sentences mention seals with the fork, both merely *mention*: "Inspect fork seals for leaks or damage" and "Check stanchions for scoring, indicating possible seal failure". Nothing states the seals are part of the fork, so the earlier rejection of `p0035_c01` is upheld. |

Both are evidence-starved, not mis-modelled. Closing either needs a source page that states the
relationship, not a cleverer inference.

## Evidence quality — what the gates could not see (audited 2026-10-25)

`tools/audit_quote_quality.py` exists because "the quote is a substring of the chunk" is a low bar. It
flags quotes that are **section headings / tables of contents**, **truncated mid-word**, **four words
or fewer**, or **reused across many entities**. Current result: 60 findings — 5 high, 55 medium.

- **55 medium are by design.** A node and the edge about that node legitimately cite the same
  sentence; reuse across a component and its own relation is not a defect.
- **5 high are real**, and three of them are the same artefact: the headset chapter's contents list
  (`CHAPTER 16 — HEADSETS / Headset Types / Headset Service / …`) used as evidence.
  - `edge-threadless-headset-part-of-cockpit` was `verified` on that TOC. Downgraded to
    `needs_review`: a contents list documents the manual's *grouping*, not structural membership in
    the cockpit subsystem. Edges now 58 verified / 17 needs_review.
  - `node comp-headset` and `edge-headset-interfaces-steerer` rest on the same TOC, but both live in
    the frozen seed, so they are recorded rather than edited. `edge-headset-interfaces-steerer` does
    carry a second, substantive quote ("The bolt in the top cap puts pressure on the stem.").
  - the two `DOT FLUID, CAUSTIC MATERIAL` hits are real safety statements, not TOCs — the detector is
    deliberately blunt and these are false positives.

The rule this leaves behind: **a heading is a label, not a fact.** Future batches must cite the
sentence that asserts the relationship, and the auditor is now available to catch it when they don't.

## The reasoning engine had a one-sided gate (found 2026-10-25 by the query harness)

`tools/query_harness.mjs` drives the 5-state engine the way a mechanic would — a plain query mapped to
a `(subject, target)` pair with the verdict the evidence must produce. It found an asymmetry:

| path | before | now |
|---|---|---|
| `verified` + `fits_into` | `verified_compatible` | unchanged |
| `needs_review` + `fits_into` | `conditionally_compatible` (the "Fix C" gate) | unchanged |
| `verified` + `incompatible_with` | `incompatible` | unchanged |
| **`needs_review` + `incompatible_with`** | **`incompatible`** — a hard verdict from an unreviewed edge | **`conditionally_compatible`** |

So the engine refused to *assert* fitment from an unreviewed edge, but happily asserted *exclusion*
from one. Fixed in `constraint-engine.ts` (`rule-unreviewed-exclusion`) and pinned by **Test S**, which
also asserts that a `mounted_on` edge never fabricates fitment (mounting ≠ compatibility).

Harness result: **6/6 verdicts as expected**, covering `incompatible` ×2,
`conditionally_compatible`, `unknown_missing_evidence` ×2 and `verified_compatible`.

One expectation of mine was wrong and corrected: I assumed a verified `mounted_on` edge made
"does a quill stem fit a threaded steerer" answer `verified_compatible`. It returns
`unknown_missing_evidence`, which is right — a mounting tells you how two parts are joined, not
whether a particular diameter mates.

## Conformance was inverted (found by extending the harness to 12 cases)

The harness now covers 12 paths and passes 12/12. Extending it exposed a second engine defect, and this
one was a logic inversion rather than a missing gate:

| relation | caveats (`conditions[]`) | before | now |
|---|---|---|---|
| `conforms_to` | non-empty | `conditionally_compatible` | unchanged |
| `conforms_to` | **empty** | **`unknown_missing_evidence`** | **`verified_compatible`** |

So adding caveats made a conformance *answerable* while a clean verified conformance fell through to
"unknown". A `verified conforms_to` asserts the conformance itself, so it now answers; an unreviewed
one degrades to conditional, like every other relation. Pinned as S5/S6 in Test S.

Gaps that remain genuinely unfillable, verified rather than assumed:

- **`conflicted` is unreachable in this graph.** 0 edges carry a non-empty `conflicts[]`, and 0 node
  pairs carry opposing `compatible_with`/`incompatible_with` edges. The verdict is implemented and
  tested by construction, not by data.
- `std-quill-diameter-fit` has **no edge to `comp-steerer`** (the real relation is
  `comp-stem-quill → std-quill-diameter-fit`), so a quill-diameter query cannot exercise that pair.

## `conflicted` is construct-only, and that is now a verified fact

The verdict is implemented, reachable by rule, and pinned by construction — but it has never fired on
real data, and two independent methods agree it cannot with this corpus:

- **Structural:** 0 of 75 edges carry a non-empty `conflicts[]`; 0 node pairs carry opposing
  `compatible_with` / `incompatible_with` edges.
- **Textual:** a scan of all 43 chunks finds **no mechanical contradiction** — 5 torque statements,
  no subject with differing values; 4 fluid mentions, all consistent (the "DOT vs mineral" hits are one
  Hayes sentence split across a line break); 33 dimension statements, all consistent with their own
  standards.

A reviewer asked to find a contradiction answered `NO CONTRADICTION IN CORPUS`, and the scan confirms
it. **No synthetic conflict will be added.** Fabricating a contradiction to exercise a code path would
undermine the only thing this graph claims — that every assertion is grounded in a cited sentence.
`conflicted` stays proven by construction until two sources genuinely disagree.

## Next task

1. **Local-first is settled** — the app runs with no AI Studio: `serve_local.cmd` → `localhost:8080`,
   built from `dist/`. `docs/REGRESSION.md` proves a clean clone reproduces the state.
2. **The crankset island is the last structural hole, and it is evidence-starved — measured, not
   assumed.** `python tools/scan_crankset.py` classifies every crankset sentence in the bundle:
   **0** assert an installed relationship, **1** only asks the mechanic to confirm shell width and
   threading (`p0002_c02`), **5** are removal or service steps. The removal-instruction rule that
   demoted `comp-crank-arm → comp-bb-threaded` is applied literally there. Closing the island needs a
   bottom-bracket interface source, not more inference.
3. The rear-suspension cluster is anchored now, but its anchor is one grade-A sentence about bushing
   wear. A frame/suspension schematic page would replace "wear at the frame attachments" with an
   explicit mounting statement.
4. New knowledge otherwise requires **new source evidence** or a **documented correction** — never a
   connectivity target.
