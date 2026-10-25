# Frozen state — 2026-10-25

## The numbers (measured by `tools/verify_app_state.py`, not asserted)

| | |
|---|---|
| nodes | **89** — 80 verified, 1 candidate, 8 needs_review |
| edges | **92** — 76 verified, 16 needs_review |
| citations | **204** — 156 byte-exact, 48 whitespace-only (all in the frozen seed) |
| bundle | 63 chunks (43 seed + 7 text-layer pages + 11 OCR'd picture pages + 2 verified web); **51 cited** |
| components | **1** — all 89 nodes connected; no islands |
| batch ledger | 18 rows (seed + 17 expansion files) |

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

**There are none left. `connectivity = 1 component, 78 nodes`** (was `[74,1]`, then `[76,2]`, now `[78]`).

| island | was | how it was closed |
|---|---|---|
| crankset (`comp-bb-threaded`, `comp-chainring`, `comp-crank-arm`) | 3 | `phase10-bb-frame`: BBB p373's own sentence about the shell |
| `comp-fork-seals` | 1 | `phase12-fork-seal`: **Sidwells pp.35 and 141**, from the text layer |

### How the fork-seal island was actually closed (and why the earlier verdict was wrong)

The recorded blocker was *"Sidwells p2 is image-only and there is no OCR engine"*. Both halves were
wrong, and the error was in the premise rather than the tooling:

1. **p2 never needed OCR.** `tools/ocr_page.py inventory` says Sidwells has a text layer on **158 of
   160** pages; the image-only ones are **p2 and p6**, and rendering them shows both are full-page
   *photographs* (p2: a hand with a chain tool on a chainring; p6: a cassette with a screwdriver). OCR
   returns 0 lines because there is no text to recover. A photo cannot testify.
2. **The evidence was in the text layer the whole time.** `tools/find_pages.py` locates the suspension
   chapter at **pp.140–147**, and p141's exploded-fork diagram carries the sentence that was missing:
   *"Seal / Keeps dirt out of fork's interior"*, plus p35's service list: *"Fork and shock seals for
   cracks and slackness"* and *"Seals on forks and shocks, as part of bi-annual service by qualified
   technician"*, and *"Play, absence of oil lines, and cracked seals are all evidence of worn seals,
   which should be replaced by a qualified technician."*

That last sentence is a diagnostic rule stated outright by the publisher, so phase12 adds three nodes
(`prop-fork-seal-function`, `sym-fork-seal-wear`, `fm-worn-fork-seals`) and four edges at **grade A**,
including `sym-fork-seal-wear → comp-fork-seals` (`indicates`). The island's previous support was a
**grade-B vision description**; it now rests on the publisher's own words.

### OCR: what was bought, and what it measured

`rapidocr_onnxruntime` (CPU, ONNX, no PyTorch, no admin) is installed in the workspace venv, so a real
OCR engine exists after all — the earlier "no OCR engine" claim only ever checked for *system* binaries
(`tesseract`, `pdftotext`). `tools/ocr_page.py` renders with PyMuPDF and OCRs, and it **measures itself**
against pages whose text layer is known, instead of being trusted:

| page | reference | OCR output | edit distance | CER | word recall | verdict |
|---|---|---|---|---|---|---|
| BBB p349 | 1013 chars | 1013 chars | **0** | **0.00%** | 100% | byte-perfect |
| BBB p337 | 925 chars | 931 chars | 19 | **2.05%** | 92.5% | usable, one graphic misread |

The p337 errors are a stylised figure caption being read as `OUHUIHS` — exactly the failure mode grade C
exists to contain. **No claim in the graph currently rests on OCR output**, because the pages that
needed evidence turned out to have a text layer.

### Two gates were quietly wrong, and adding a bundle exposed both

Neither bug was in the app; both were in checks that had hardcoded the *old* corpus.

- `tools/verify_app_state.py` loaded `evidence-bundle-2.json` **by name**, so it counted 48 chunks and
  175 citations while the app had 50 and 182. It now globs `evidence-bundle-*.json`, for the same reason
  the expansion files have always been globbed: a new file must never be invisible to a gate.
- `tools/smoke_app.py` did the same for its chunk count. This one mattered more, because the first smoke
  run after the new batch failed with *"UI shows 75/77/48, data has 50 chunks"* — the gate was right and
  the **served `dist/` was stale**. A data change without a rebuild is now a caught failure rather than
  a false green.

And the verifier caught a modelling error the suite did not: `sym-fork-seal-wear → comp-fork-seals`
violated the ontology because `indicates` allowed `component` targets but not `subcomponent`. That was
widened deliberately (recorded as **R6** in Test R, same reasoning as R2/R4: every relation that names
`component` also names `subcomponent`), rather than bending the edge to point at the whole fork.


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

## Working from the manuals, not the kb.db (2026-10-25)

The corpus began as a 43-chunk excerpt of a `kb.db` built from two service manuals. Both PDFs are on
disk and were verified as the real origin:

| book | file | pages | text layer |
|---|---|---|---|
| Big Blue Book, 4th ed. (Park Tool / C. Calvin Jones) | `723775317-Big-Blue-Book-…pdf` | **992** | yes |
| Bicycle Repair Manual (Chris Sidwells) | `22743195-Bicycle-Repair-Manual-…pdf` | **160** | yes, except p2 and p6, which are photographs |

Page mapping was checked rather than assumed: a quote from `big_blue_book_p0921_c00` is on page 921,
`p0679_c00` on 679, and `bike_repair_manual_chris_p0148_c00` on 148.

The earlier claim that *"Sidwells page 2 is a scan, so that book cannot be cited from its text layer"*
was wrong twice over (see *How the fork-seal island was actually closed*): p2 is a photograph with no
text, and 158 of the book's 160 pages do have a text layer. `tools/ocr_page.py inventory` is the check
that settles this in one command, and `tools/find_pages.py` is what finds the page that carries a claim.

**Ingested: 4 pages, each one cited** (`src/data/evidence-bundle-2.json`). The rule is to ingest only
what is about to be used — adding all 1152 pages would drop coverage to a meaningless fraction and
bury the corpus. Bundle 1 stays frozen; `src/services/evidence-corpus.ts` merges the two so the app,
the suite and the verifier cannot disagree about which chunks exist.

### The crankset island is closed, with declarative sentences at last

| edge | status | evidence (byte-exact, page) |
|---|---|---|
| `comp-bb-threaded → comp-frame` (`fits_into`) | verified | p374 "Threaded bottom bracket shells have an internal thread to accept the external thread of the bottom bracket bearing cups or adaptors (figure 7.31)." + p373 "The bottom bracket shell is part of the frame that houses the bottom bracket bearings and spindle." |
| `comp-crank-arm → comp-bb-threaded` (`mounted_on`) | **needs_review → verified** | p337 "Crank bolts secure the left and right cranks to the spindle." |
| `comp-chainring → comp-crank-arm` (`mounted_on`) | **needs_review → verified** | p421 "Chainrings are toothed sprockets attached to the cranks." |

Components went from `[70, 3, 1]` to **`[73, 1]`**, and the last island (`comp-fork-seals`) was closed
later by `phase12-fork-seal` from the Sidwells text layer, giving **`[78]` — one connected graph**.

Two rules did real work here. The chainring edge had been `needs_review` because its only evidence was
a `[VISUAL DATA]` analysis; promoting it while that quote was still attached tripped the verifier's
"verified but quote inside visual data" rule, so the visual citation was removed and the prose one kept.
And the crank-puller sentence that once demoted the crank edge was replaced — not reinterpreted — by a
sentence that states the fastening outright.

### OCR the 900-page book? Measured before spending an hour (2026-10-25)

`tools/figure_pages.py` maps Big Blue Book first: **992 pages, 20 with no text layer, 682 illustrated,
621 pages carrying 625 FIGURE captions — 36 of them diagnostic** ("Look and feel for pits along ball
path of cone", "Grab wheel and pull side-to-side laterally to check for play", "Pull up and down at
middle of chain to test chain wear").

Then `tools/ocr_figure_gain.py` asks the only question that matters before bulk OCR: *does OCR of a
figure page add words the text layer does not already have?*

| sample pages | layer words | OCR words | words only the image had |
|---|---|---|---|
| 77, 100, 108, 230, 300, 373 | 155 | 157 | **2** (`imano`, `ultegra` — a logo, misread) |

**1.3%, all artefact.** BBB's figure labels are vector text and are already in the layer, so OCR-ing
992 pages would add noise, not knowledge. That experiment cost four minutes and saved about an hour.

The place OCR pays is the **20 pages with no text at all**. `tools/ocr_batch_pages.py` on exactly those
pages: 11 produce ≥40 chars, and **six of them are SYMPTOM / CAUSE / SOLUTION troubleshooting tables**
(p188 tyres, p254 hub bearings, p301 spokes, p486 chain, p803 rim brakes, p842 stems), plus three
specification tables (p219 hub/axle widths, p986 tool interfaces, p990 crown-race standards). Those
charts are invisible to every text extractor — a mechanic's differential-diagnosis logic, locked in an
image.

### Reading order is not reading: the table had to be reconstructed

The first build produced quotes like
`"Wheel moves laterally back\nadjustment\n2. Loose skewer or thru axle\nand forth at rim"` — RapidOCR
returns boxes in the order it finds them, which on a three-column table interleaves the columns. The
guard refused to write it (the quote *was* a substring, and still nonsense), so `tools/ocr_table.py`
clusters boxes by x-centre into columns and emits a column-wise linearisation, where a cell becomes one
contiguous string: `"Wheel moves laterally back and forth at rim"`. Only then could a citation be made.

### phase13-fault-charts: the first diagnostic trees in the graph

From p254, whose transcription was checked against the rendered page before any claim was written:

| symptom | cause (failure mode) | solution (procedure) |
|---|---|---|
| wheel moves laterally at the rim | loose hub bearing adjustment | tighten bearing adjustment |
| wheel slows quickly when spun | hub adjustment too tight | loosen adjustment |
| wheel turns roughly or rumbles | worn hub bearings | replace bearings |

9 nodes, 9 edges, **all grade C**. Each symptom points at both its failure mode and at `comp-rear-hub`,
because the connectivity pin failed on two disconnected 3-node sub-trees until it did — the gate
demanding better modelling, not the author.

New relation: **`resolves`** (procedure → failure_mode), the SOLUTION column of a troubleshooting table.
Without it a graph can say *what is wrong* and never *what fixes it*, which is the difference between a
parts catalogue and a mechanic. Pinned as **R7** in Test R.

Grade C is doing real work here: the same pages include numeric tables (hub widths, crown-race
diameters), and Test K means none of those digits may support a verified numeric claim. They are
ingested as retrievable text and nothing more.

### One seed citation is contaminated — found while closing the island

`comp-fork-seals` carries two seed citations. The second is:

- `chunk_id: bike_repair_manual_chris_p0112_c03`, `page: 112`, `section: "V-BRAKE ANATOMY"`,
  `evidence_grade: "A"`, quote: `"**Fork Seal Condition:** Inspect fork seals for leaks or damage."`

That chunk is **not Sidwells page 112**. Its text begins *"nch or 27.5-inch wheel. Tire shows knobby
tread pattern"* and continues `"**B.3 Front Brake:** Hydraulic disc brake…"` — it is a machine-generated
bike-inspection report (the markdown bold is the tell), filed under a real book and a real page number
that it never came from. So a **grade-A citation was resting on fabricated provenance**.

Consequences, stated plainly:

- It is in the **frozen seed**, so it is recorded, not edited. The node's other seed citation
  (`p0035_c01`, a mid-word slice: *"ribute in fork Freehub body and freewheel for play…"*) is genuine
  but says nothing about seals either.
- This is why phase12 matters: `comp-fork-seals` now connects to the graph on the publisher's own
  words, and the two seed citations are no longer load-bearing.
- The verifier has a rule for `verified` quotes that sit inside `[VISUAL DATA]`, but this chunk carries
  no marker, so the rule cannot see it. **Detecting machine-written chunks that are dressed as book
  pages is not yet automated** — that is the next gate worth writing (a grade-A citation whose chunk
  contains markdown bold, or whose first 120 chars do not appear in the named PDF page, is suspect).


### The five vendor sources GPT suggested — inspected, with verdicts (2026-10-25)

Each was fetched rather than assumed; only what was actually reachable is reported as reachable.

| source | status | what it is | verdict for this brain |
|---|---|---|---|
| `si.shimano.com` | **HTTP 403** to automated fetch | not retrieved, so not assessed | needs a real browser session or a manual download; do not claim content we have not read |
| `sram.com/en/service` | reachable, HTML index | manuals are **PDFs** behind the index (spare-parts catalogues 72–85 MB, bleed manuals, **Service Interval Chart 50 KB**, **Basic Troubleshooting 5.8 MB**, suspension setup guide), plus a compatibility-advisor tool | **highest numeric value**: service intervals and the DOT-vs-mineral bleed split are exactly the numbers this graph lacks. Copyright SRAM LLC; quote-only posture applies |
| `parktool.com/.../repair-help` | reachable, **189 HTML articles**, server-rendered, dated | diagnostic *reasoning*, keyed by "where's the problem" | **highest diagnostic value per byte**: `if X then Y` logic plus the traps a mature mechanic knows |
| `trekbikes.com/…/owners_manuals` | **HTTP 404** | — | dead URL as given; needs a corrected path before any judgement |
| `giant-bicycles.com/global/manuals` | reachable, large HTML library | owner's and component manuals as PDFs, many languages | low diagnostic density (assembly/fit/warranty), some torque tables. Not first |

The Park Tool headset article is the model of what belongs in an *experienced mechanic's* graph, and it
shows what this ontology still lacks:

> "If the headset seems to lock in place or center itself when the wheel is straight, it is likely the
> lower races have dents from the ball bearings. The headset should be replaced."
>
> "Over time, a loose headset may allow play in the cup or adapter of the headset, wallowing out the head
> tube. A bearing adjustment will not fix this."
>
> "If play always seems present no matter the adjustment, the steering column may be too long for the
> stem and top cap."

That is symptom → competing cause → **trap** → resolution, i.e. differential diagnosis. Encoding it
needs two things this round deliberately did not half-build: a citation field for web provenance
(**`retrieved_at`** — a web page changes, a printed page does not) and a relation from a
`diagnostic_test` to the thing it tests.

Sources were read, not copied: no vendor text is in the corpus, and nothing from the three reachable
sites has been ingested. The BBB charts were local, grade C, and were used instead.

### Evidence grades (what each one may and may not support)

| grade | meaning | may back a `verified` numeric claim? |
|---|---|---|
| **A** | the publisher's own prose, in the text layer | yes |
| **B+** | table extracted from an image: asserts existence only | no |
| **B** | model's visual description of a page | no |
| **C** | **machine transcription of a scanned page** (OCR / vision model) | **no** |
| **D** | curated row with no chunk link | no |

Grade **C** exists for text that a *machine* produced from a page image, and it is never allowed to
carry a number. Test K enforces that B **and C** cannot justify a numeric claim, and
`provenance-service.ts` states it in the UI. A grade-C claim can be useful for wording and structure; it
can never carry a torque, a diameter or a tolerance.

The grade is not hypothetical any more: `tools/ocr_page.py` gives the machine the ability to produce
exactly such text, and measures its own error rate first (0.00% on BBB p349, 2.05% on p337). If a page
ever arrives that is a genuine scan *and* carries a needed claim, the path is: OCR it, ingest at grade C,
cite the surrounding wording, and never the digits.

### Torque from prose, not from a photo (phase11)

`edge-crank-conforms-bolt-torque` (`comp-crank-arm → std-crank-bolt-torque`, `conforms_to`, verified)
cites p349: *"The bolt/nut may need 25 to 38 Nm (300 to 450 inch-pounds) depending upon brand."* The
`std-crank-bolt-torque` node is a `measurement`, and the edge carries a `conditions[]` entry saying the
figure is brand-dependent — so the engine answers "conditionally compatible" rather than pretending to
a single number. This replaces a family of visual estimates for crankset fasteners with the manual's
own prose.

## Next task

1. **Local-first is settled** — the app runs with no AI Studio: `serve_local.cmd` → `localhost:8080`,
   built from `dist/`. `docs/REGRESSION.md` proves a clean clone reproduces the state.
2. **Connectivity is done: 1 component, 78 nodes, 0 islands.** Both islands were closed by finding the
   sentence that states the relationship (`phase10-bb-frame` from BBB p373, `phase12-fork-seal` from
   Sidwells pp.35/141) — not by loosening a rule or inferring membership. There is no structural hole
   left to argue about.
3. The rear-suspension cluster is anchored now, but its anchor is one grade-A sentence about bushing
   wear. A frame/suspension schematic page would replace "wear at the frame attachments" with an
   explicit mounting statement.
4. New knowledge otherwise requires **new source evidence** or a **documented correction** — never a
   connectivity target. `tools/find_pages.py` should be the first move on any gap: search the text
   layer before concluding a fact is missing, because twice now the sentence was already there.
