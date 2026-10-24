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
| Nodes | **69** (61 verified, 1 candidate, 7 needs_review) |
| Edges | **63** (53 verified, 10 needs_review) |
| Citations | **152** (104 byte-exact, 48 differ from their chunk in whitespace only) |
| Evidence bundle | **43 chunks** (36 original + 7 added 2026-10-25) |
| Chunks cited | **36 of 43** — 7 unused (8a cites 2 of them, 8b/8c the rest) |
| Connectivity | 7 components, largest 35 (51%) |
| Test suite | **16 tests**, all passing headlessly (`npx tsx tools/run_suite.mjs`). Test Q pins the graph numbers *and* the exact list of uncited chunks; Test R pins the five ontology adjudications by reason |

Live app: Google AI Studio, app id `82983f51-5ac2-4ac3-ba0f-6d27161b376a`.

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
    expansion-*.json          8 growth batches (brakes, cockpit, drivetrain, rearshock,
                              quillstem, cassette, hubfit, connectors)
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
  tests/phase3-tests.ts       15 tests, including Test Q (coverage invariants)
docs/                         STATUS.md, bundle proposal, verification log
tools/                        the python verifiers used to grade the AI's work
```

## Run it

```bash
npm install
npm run dev      # vite
npm run build    # tsc --noEmit is run by the AI Studio build; vite build here
```

The in-app suite is opened from the UI (TestSuiteModal) and prints all 15 results. Test Q is the
integrity gate: it recomputes nodes, edges, status splits, citations, chunk coverage, connectivity
and the ceiling sentence, then compares them to deliberate pins. **If the data and the pins
disagree, that is a real finding, not a nuisance — never edit a pin to match a suspicious number
without recomputing it independently first.**

Note: `public/sql-wasm.wasm` is not in this repo (it is a 1 MB binary from the AI Studio project);
only the optional "attach a local kb.db" feature needs it.

---

## What to do next — see `HANDOFF.md`

The graph is at its **evidence ceiling**: all 36 original chunks are cited, so it could not grow.
On 2026-10-25 the owner approved growing the bundle to **43 chunks**, which unlocks the last 6
disconnected islands. `HANDOFF.md` contains the three ready batches (8a, 8b, 8c) with the exact
chunk ids, exact quotes and exact claims to place — plus the projected numbers after each one.
