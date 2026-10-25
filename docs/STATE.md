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
centerlock` is `evidence_type: mechanical_principle`; its quote describes six-bolt flanges and never
mentions incompatibility).

## The suspension cluster now hangs on a structural anchor (resolved 2026-10-25)

Before `phase9-frame`, the whole rear-suspension subsystem — `comp-rear-shock`, `comp-rear-triangle`
and the five `comp-shock-*` subcomponents — touched the rest of the graph **only** through
`edge-conn4-reartriangle-links-wheel`, the vaguest edge in the graph. Removing that one edge split the
graph from `[69, 3, 1]` into `[62, 7, 3, 1]`, which is how the weakness was found.

`phase9-frame` adds the node the corpus had been describing all along without ever naming: `comp-frame`.

| addition | evidence | status |
|---|---|---|
| `comp-frame` | p0148 "can move independently of the … rest of the frame" | verified |
| `comp-rear-shock → comp-frame` (`mounted_on`) | p0921 "The rear shock can develop wear at the bushing of the frame attachments." | verified |
| `comp-steerer → comp-frame` (`interfaces_with`) | p0861_c02 "This draws the steerer tube upwards relative to the frame…" | needs_review |

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
