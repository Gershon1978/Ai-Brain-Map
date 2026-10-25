# Research findings: what the model returned, and what survived verification (2026-10-25)

`tools/weak_links.py` measured the graph's gaps. They were then written as questions in
`docs/RESEARCH_BRIEF.md`, with a fixed source list, a JSON schema, and rules that make output checkable.
AI Studio returned **47 rows** in the requested schema. This file records what happened to them.

## The five gaps, measured

| gap | what the graph had | why it matters to a mechanic |
|---|---|---|
| G1 numbers | **2 measurements for 44 components** | you cannot tighten a bolt to "somewhere about right" |
| G2 tools | **0 tool nodes** | every procedure assumes tools and names none |
| G3 diagnostic tests | **0 `diagnostic_test` nodes** | without a pass/fail test, a symptom cannot become a decision |
| G4 "unconfirmed" standards | 4 nodes literally named `*-unconfirmed` (chain pitch, XDR bearing dims, steerer dia, brake thru-axle) | a named unknown is a hole in the model, not a caveat |
| G5 symptom library | 4 symptoms, all from one grade-C OCR chart | a real shop sees dozens |

Also measured: `compatible_with` and `conditionally_compatible_with` are **never asserted** (verdicts are
derived, never stored), and 9 nodes rest on grade B evidence.

## What came back

- Format: correct JSON array, 47 rows, all required keys — **structurally excellent**.
- `tools/validate_research_datasheet.py`: **12 accepted, 35 pending, 0 rejected.**
  The 35 were flagged `hub_url`: they cite `https://www.sram.com/en/service`, a landing page, not a
  document, so nothing could ever be re-checked. The schema could not see that; the checker could.
- The JSON itself needed repairing: unescaped inch marks (`1"`, `1-1/8"`) broke parsing at line 670.
  Recorded, not hidden — a model that cannot escape quotes is a model whose output needs gating.

## Then the 12 "accepted" rows failed the only test that matters

`tools/verify_quotes_online.py` fetches each row's own `source_url` and looks for the row's own quote.

**FOUND 0 · NOT_FOUND 11 · UNFETCHABLE 1.**

Two examples, checked by hand against the live pages:

| the model's quote | what the page actually says |
|---|---|
| "For 11 and 12-speed chain, replace at or just before the 0.5% reading." | not on the page. It has a table: `Single-speed 1.0%` / `10-speed cassette/freewheel or less 0.75%` / `11-speed cassette or more 0.5%` |
| "Cone wrenches are necessary for hub adjustment because standard open end wrenches are too thick to fit on the cone flats." | not on the page. It says: "Cone wrenches, see DCW and SCW series wrenches — always use the smallest size that fits" |

The **numbers were right and the sentences were invented.** A value written into a fabricated quote
passes every mechanical check that only compares the value to its quote — which is exactly what my own
validator did before this gate existed.

## What was ingested, and only this

`phase14-chain-wear` — from pages I fetched and read myself, quotes copied from the fetched text:

- `comp-chain` (component): *"Chains are a consumable part of the bicycle drivetrain."*
  The graph had **no chain node at all**; the dangling endpoint of my first edge exposed it.
- `std-chain-wear-limit` (standard): the wear table, 1.0% / 0.75% / 0.5% by drivetrain class.
- `comp-chain → comp-cassette` (`interfaces_with`): *"...the chain to mesh poorly with cogs and
  chainrings..."*
- `comp-chain → std-chain-wear-limit` (`conforms_to`), with conditions recording the class dependence
  and the publisher's own caveat that each manufacturer specifies its own limit.

First web-sourced batch: every citation carries **`source_url` + `retrieved_at`**, now part of the
citation schema, because a web page changes while a printed page does not.

## The rule this establishes

A research model may **locate** a fact; it may never be the *record* of one. Ingest only what a script
has fetched and string-matched, and treat "the quote exists on the page" as the gate — not
"the number is in the quote". Anything else imports confident fiction into a brain whose only asset is
that every sentence can be traced to a page.

## Still open, deliberately

- The 35 `hub_url` rows: re-ask for **direct document URLs** (the PDF, not the index). Until then they
  are unproven, not disproven.
- `si.shimano.com` returns HTTP 403 to automated fetch; no Shimano value has been checked.
- Tools (G2) and diagnostic tests (G3) still need relations before nodes can exist: a `tool` node with
  no edge is an island, and Test Q fails on islands. That is the next ontology decision, not a data gap.
