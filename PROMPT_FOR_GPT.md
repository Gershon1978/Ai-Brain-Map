# Prompt to give ChatGPT / GPT-5

Copy everything below into the chat, with the repo link.

---

You are taking over a small, strict engineering project. Read the repository first, then work.

**Repo:** https://github.com/Gershon1978/Ai-Brain-Map

Read in this order:
1. `README.md` — what the project is, its hard rules, the file map, the current numbers.
2. `HANDOFF.md` — the three ready batches (8a, 8b, 8c) with exact chunk ids, exact quotes and
   exact claims, plus the projected totals after each one.
3. `docs/BUNDLE_PROPOSAL_v1.md` — why those chunks were chosen (the six disconnected islands).
4. `docs/STATUS.md` — optional but important: the history, including four fabrications that were
   caught and the rules they produced. Do not treat the rules as bureaucracy.

Then do three things:

**1. Implement the batches.** Add batch 8a, then 8b, then 8c, exactly as specified in `HANDOFF.md`.
Do not invent a chunk id, do not retype a quote from the tables — open
`src/data/seed-evidence.json`, find the chunk, and copy the quote character for character (one of
them contains a line break; it must stay). Do not touch `seed_graph.json` or `seed-evidence.json`.
After each batch, update the pinned numbers in `src/tests/phase3-tests.ts` (Test Q) to the values
recomputed from the files.

**2. Audit the result.** For every new edge, show me the evidence object, the chunk id, and prove
the quote is a literal substring of that chunk's `text`. Then report: node count, edge count,
citation count, distinct chunks cited, component count and largest component size — all recomputed
from the files, not from any test output.

**3. Critique the design.** Where is this model weakest? Concretely:
- the 5-state verdict engine answers only from documented edges; what would it take to evaluate
  property-vs-property fitment (e.g. hub O.L.D. vs dropout spacing) without inventing evidence?
- 48 of the 59 seed citations differ from their source chunk in whitespace only. Leave them alone,
  but say whether a normalised comparison is acceptable in an evidence-first system, and how you
  would record that decision.
- what is the next unit of knowledge worth buying, given that each new chunk costs an owner
  approval?

Constraints that are not negotiable: no paraphrased evidence, no invented ids, no new numbers that
are not recomputed, and never edit a quote to make a test pass.
