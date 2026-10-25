# Frozen state — 2026-10-25

## The numbers (measured by `tools/verify_app_state.py`, not asserted)

| | |
|---|---|
| nodes | **73** — 64 verified, 1 candidate, 8 needs_review |
| edges | **73** — 59 verified, 14 needs_review |
| citations | **166** — 118 byte-exact, 48 whitespace-only (all in the frozen seed) |
| bundle | 43 chunks; **41 cited**, 2 deliberately uncited |
| components | **3** — largest 69 (95%), crankset island 3, `comp-fork-seals` 1 |
| batch ledger | 12 rows (seed + 11 expansion files) |

Checks, all observed on this state:

```
npm install                                  exit 0 (184 packages, no flags)
npm run lint   (tsc --noEmit)                exit 0
npm run build  (vite build)                  exit 0, built in ~2s
npx tsx tools/run_suite.mjs                  16/16 passed, exit 0
python tools/verify_app_state.py             PROBLEMS 0, PASS
```

Verifier warnings, **separately classified** because they mean different things:

- **48 whitespace-only citations** — OCR double-spaces in the frozen seed. Word sequence identical;
  evidence-integrity relevant, but not a wrong citation. Deliberately not "tidied".
- **11 undeclared sections** — metadata omissions (the chunk knows its section, the evidence object
  omits it). The app's Test P does not check absence, so the independent verifier counts them here.
- **1 known exception** — `comp-bb-threaded`'s section is truncated inside the frozen seed. Printed on
  every run; the verifier fails if the exception ever stops occurring, so the list can only shrink.

A green verifier means *the declared checks pass*. It does not mean every possible defect is ruled
out. 59 warnings are visible technical debt, not 59 confirmed graph errors.

## What is deliberately provisional

Three edges carry `needs_review` **and** a claim prefixed `Connectivity hypothesis:`. They express
coupling, not documented attachment, and the engine can only return `conditionally_compatible`
across them — never `verified_compatible`:

| edge | why provisional |
|---|---|
| `comp-fork → sys-wheels` (`affects`) | the text asserts co-motion ("turns the fork and the front wheel"), not attachment |
| `comp-rear-triangle → sys-wheels` (`affects`) | a linkage, not membership |
| `comp-chainring → comp-crank-arm` (`mounted_on`) | the source is a `[VISUAL DATA]` analysis |

The cockpit cluster reaches the main component **only** through the first of these. That is the honest
reason the graph has 3 components and not 1.

## Rejected evidence (kept, uncited, pinned)

- `big_blue_book_p0693_c00` — "manufacturers differ" is too generic to establish a fluid–caliper link.
- `bike_repair_manual_chris_p0071_c05` — a visual seal hint; it locates a symptom, it does not say the
  seals are part of the fork.

Both are listed in `EXPECTED_UNUSED` in Test Q, so neither can quietly become cited.

## Next task (not expansion)

1. **Reproducible sync** — AI Studio still holds pre-8a code and data (quota-blocked). When it returns,
   push the repo state and prove equality: dumped files byte-identical to `src/`, then re-run
   verifier + suite in the app.
2. **Regression check** — on a clean clone: `npm ci`, `npm run lint`, `npm run build`,
   `npx tsx tools/run_suite.mjs`, `python tools/verify_app_state.py`. All five must pass with no
   manual steps.
3. Only then consider new knowledge — which requires **new source evidence** or a **documented
   correction**, not a connectivity target.
