# Regression report — clean clone

Reproducible from an empty directory. Nothing was installed by hand, no environment variables set,
no `--legacy-peer-deps`, and `npm ci` (not `npm install`) performs the install.

| | |
|---|---|
| commit under test | `90401e345fba95f87d79afc5ad9b59df17da8fce` (short `90401e3`) |
| node | v26.3.1 |
| npm | 11.16.0 |
| lockfile | `package-lock.json` tracked in the repo (141,553 bytes) |
| clone | `git clone https://github.com/Gershon1978/Ai-Brain-Map.git` |
| date | 2026-10-25 |

## Commands and observed results

| # | command | result |
|---|---|---|
| 1 | `npm ci --no-audit --no-fund` | `added 184 packages in 2m`, **exit 0** |
| 2 | `npm run lint` → `tsc --noEmit` | **exit 0**, no output = no diagnostics |
| 3 | `npm run build` → `vite build` | `✓ 1702 modules transformed`, `✓ built in 3.46s`, **exit 0** |
| 4 | `npx tsx tools/run_suite.mjs` | **16/16 passed**, `OVERALL: true`, **exit 0** |
| 5 | `python tools/verify_app_state.py` | **PROBLEMS 0**, `VERDICT: PASS`, **exit 0** |

`lint` is a real script (`"lint": "tsc --noEmit"` in `package.json`), not a placeholder — it exits
non-zero on any type error, and step 2 shows the script banner above its exit code.

## What the verifier measured in the clone

```
nodes=73  edges=73  citations=166
quotes: byte-exact=118  whitespace-only=48  missing=0
chunks: cited 41 of 43, unused 2 [p0693_c00, p0071_c05]
node status: verified 64, candidate 1, needs_review 8
edge status: verified 58, needs_review 15
components=3 sizes=[69, 3, 1] largest=69 (95%)
```

Identical to the working tree — the clone reproduces the frozen state exactly, including the two
rejected chunks and the twelve-row batch ledger.

## Non-fatal warnings, expected on this project

- `index.html` references AI Studio's injected `/_aistudio-iframe.js` without `type="module"` — the
  bundle builds around it; harmless.
- One chunk >500 kB (bundle-size advice from Vite), and a `@tailwindcss/vite` timing note.
- Verifier: 48 whitespace-only citations, 11 undeclared sections, 1 known frozen-seed exception
  (all classified in `docs/STATE.md`; none of them are failures).

## What this report does **not** claim

- It does not claim the deployed AI Studio app contains this state. That is stage 1 of the sync and
  is still pending (AI Studio is daily-quota-blocked; its copy predates batch 8a).
- It does not claim the knowledge base is complete. 41 of 43 chunks cited is coverage, not
  completeness — two chunks are **rejected** evidence, pinned in Test Q.

## Re-running it

```bash
git clone https://github.com/Gershon1978/Ai-Brain-Map.git && cd Ai-Brain-Map
git checkout 90401e3
npm ci --no-audit --no-fund
npm run lint
npm run build
npx tsx tools/run_suite.mjs
python tools/verify_app_state.py
```

Every step above must exit 0 and the verifier must print `PROBLEMS 0`.
