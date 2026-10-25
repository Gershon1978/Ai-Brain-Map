# Ai-Brain-Map — Hi5 Mechanical Knowledge Graph

An evidence-grounded knowledge graph of **bicycle mechanics**, plus a React app that shows it,
answers compatibility questions from it, and reports its own evidence coverage.

Every statement in the graph is tied to a **verbatim excerpt** of a service manual that is stored
in `src/data/seed-evidence.json`. If a claim has no excerpt, it is not in the graph. That is the
whole point of the project, and it is the rule that matters most.

---

## Where it stands

| | |
|---|---|
| Nodes | **73** (64 verified, 1 candidate, 8 needs_review) |
| Edges | **73** (58 verified, 15 needs_review) |
| Citations | **166** (118 byte-exact, 48 differ from their chunk in whitespace only) |
| Evidence bundle | **43 chunks** (36 original + 7 added 2026-10-25) |
| Chunks cited | **41 of 43** — the 2 left uncited are *rejected* evidence, listed in Test Q |
| Connectivity | **3 components**, largest 69 (95%); the crankset is a separate 3-node island |
| Test suite | **16 tests**, all passing headlessly (`npx tsx tools/run_suite.mjs`) |

Run it locally — no AI Studio, no account, no network: `serve_local.cmd` serves the built `dist/` on
<http://localhost:8080>. For development, `npm run dev` (Vite).

### What the graph is *for*

Ask it "does a cassette fit this freehub", "which brake fluid for this caliper", "is this hub
width compatible with this frame" — and it answers with a 5-state verdict
(`verified_compatible` / `conditionally_compatible` / `incompatible` / `unknown_missing_evidence` /
`conflicted`) **plus the manual excerpt** that justifies it. It never answers from vibes.

---

## Hard rules (they exist because each was broken once)

1. **Never write, paraphrase, tidy or "improve" evidence text.** Quotes come from
   `src/data/seed-evidence.json` character for character. If a quote has a line break in the
   source, the JSON quote keeps that `\n`.
2. **`src/data/seed_graph.json` is frozen**: 27 nodes, 12 edges, 59 citations. All growth happens
   in `src/data/expansion-*.json`.
3. **Never mark a property or edge `verified` without a chunk citation.** A grade-B visual
   description may not justify a number (and generally not a `verified` edge either — use
   `needs_review`).
4. **Never invent a `chunk_id`.** Every id must exist in the bundle; every quote must be a literal
   substring of that chunk's `text`.
5. **The coverage panel and Test Q are computed, not hard-coded.** If you change the graph, the
   numbers in `src/tests/phase3-tests.ts` must be updated to the recomputed truth — never the
   other way round.

Read `docs/STATUS.md` (long, chronological) for how four separate fabrications were caught before
this discipline was tightened. It is the most useful file for understanding *why* the rules look
paranoid.

---

## Layout

```
src/
  App.tsx                     app shell, tabs, canvas + panes
  components/
    GraphCanvas.tsx           the graph view (degree collapse, depth limit, legend)
    DetailPane.tsx            node/edge detail with evidence + quotes
    NavPane.tsx               tree / filters
    CoveragePanel.tsx         coverage & integrity panel (computed at runtime)
    ImportModal.tsx           import a graph payload
    TestSuiteModal.tsx        runs the suite in the browser
  data/
    seed_graph.json           FROZEN 27 nodes / 12 edges / 59 citations
    seed-evidence.json        43 verbatim chunks (the corpus the app may cite)
    expansion-*.json          11 growth batches: phase5 (brakes, cockpit, drivetrain,
                              rearshock, quillstem, cassette, hubfit) + phase8 (connectors,
                              fork, crank, reartriangle)
    graph.schema.json         JSON schema for nodes/edges
    relation-ontology.json    14 legal relations + which endpoint types each accepts
  services/
    graph-loader.ts           loads seed + expansions, merges them
    graph-validator.ts        schema + quote + ontology gate
    constraint-engine.ts      5-state compatibility engine
    coverage-service.ts       computes the coverage report (no literals)
    hybrid-layout.ts          layout
    graph-export.ts           JSONL / GraphML export with evidence
    sqlite-service.ts         optional sql.js attach of a local kb.db
  tests/phase3-tests.ts       16 tests, including Test Q (coverage invariants)
docs/                         STATUS.md, bundle proposal, verification log
tools/                        the python verifiers used to grade the AI's work
```

## Run it

```bash
npm ci           # lockfile is tracked
npm run dev      # vite, http://localhost:3000
npm run lint     # tsc --noEmit
npm run build    # vite build -> dist/
npx tsx tools/run_suite.mjs        # 16 tests headlessly, no browser
python tools/verify_app_state.py   # independent verifier, PROBLEMS must be 0
```

`docs/REGRESSION.md` shows all five of those passing in a fresh clone (commit `90401e3`).
`serve_local.cmd` serves the built `dist/` on port 8080 with no node and no network.

The in-app suite is opened from the UI (TestSuiteModal) and prints all 16 results. Test Q is the
integrity gate: it recomputes nodes, edges, status splits, citations, chunk coverage, connectivity
and the ceiling sentence, then compares them to deliberate pins. **If the data and the pins
disagree, that is a real finding, not a nuisance — never edit a pin to match a suspicious number
without recomputing it independently first.**

Note: `public/sql-wasm.wasm` is not in this repo (it is a 1 MB binary from the AI Studio project);
only the optional "attach a local kb.db" feature needs it.

---

## What to do next — the bundle is frozen

The evidence work is **complete for this bundle**: 41 of the 43 chunks are cited, and the two that are
not (`p0693_c00`, `p0071_c05`) were audited and **rejected** — one is a generic "manufacturers
differ" sentence, the other a visual seal hint. Both are pinned in Test Q so they cannot quietly
become cited.

43/43 coverage would be a coverage milestone, not proof of completeness: it would not mean every
useful claim in the manuals has been extracted, nor that every relationship is established. New
knowledge enters only with **new source evidence** or a **documented correction**.

`docs/STATE.md` records the frozen state and what the next task should be (a reproducible
synchronisation + regression check, not further expansion).
