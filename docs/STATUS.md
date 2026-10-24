# Hi5 Mechanical Knowledge Graph — supervisor status

Updated: 2026-10-24 22:55 (local) — read the dated sections at the bottom; this table is the summary

## Where the build stands

| Phase | State |
|---|---|
| Plan (v4) | **Approved** — after 3 rejections for fabricated evidence |
| Phase 3 — schema, seed graph, validator, constraint engine, tests | **Verified & approved** |
| Phase 4 — explorer UI, canvas, detail/evidence panes, export | **Built; build green; static audit clean; runtime check pending** |
| Phase 5 — evidence-first expansion batches | **Batch 7 accepted on evidence; one correction open; batch 8 refused.** Batches 1–7 all **closed on evidence**. Brakes 10/10 (7/3), cockpit 7/7 (5/2), drivetrain 7/7 (5/2), rearshock 5/5, quillstem 4/4, cassette 5/5, hubfit 5/5 (three graph-quality defects issued 21:45). Map at **70 nodes / 55 edges** = **62 verified + 1 candidate + 7 needs_review nodes; 45 verified + 10 needs_review edges**, recomputed by me from the files (`_verify_batch7.txt`, `problems=0 literal=10/10`), not from the app's tests |
| Phase 5+ | **Batch 8 is not authorised.** 14 of the 36 bundled chunks are unused and none is mechanical evidence: 6 synthetic visual analyses ("this analysis is based solely on visual information", "(estimated)", "let me know if you want more details"), 4 contents lists or OCR'd tables, 4 electrical/e-bike. Batch 7 used `big_blue_book_p0219_c01`, the last real mechanical table. Growth beyond the bundle would mean changing the frozen `seed-evidence.json` (36 chunks) — a protocol change that stays with the human |
| Phase 6 — connector pass | **Connectors-1 rejected on the bundle rule at 22:45** (5 of its 6 chunks were not in the bundled 36, so the suite read 13/14). Corrected set of **3 edges** sent 22:50:38: rotor→rear hub (`p0679_c00`), quill→steerer (`p0820_c00`), hub135→rear hub (`p0219_c01`); freewheel→hub, pad→rotor, derailleur→cassette **dropped for lack of bundled evidence**. Expect 69 nodes / 57 edges, 13 groups, largest 24, 14/14. See the 22:45 section |

## What is verified, mechanically

Run by me against `C:\Users\Gershon\Desktop\WORKSPACE\hi5-andrey-server\live\app\data\kb.db`, not by the app's own tests:

- 27 nodes / 12 edges — ids and topology identical to the approved spec
- 20/20 edge citations and 39/39 node citations are literal substrings of their chunk
- 36/36 chunk texts in `seed-evidence.json` byte-identical to `chunks.text`
- no numeric claim resting only on grade-B evidence
- no property marked `verified` without an evidence chunk
- app's own suite: 11/11 PASSED, production build green ("✓ built in 624ms")

## The four fabrications that were caught

1. **v1 plan** — every `chunk_id` invented (`bbb_ch04_spline_0028` …): 0 of 12 existed in the DB.
2. **v2** — ids real, but 6 of 12 pointed at the right page, wrong chunk.
3. **v3** — ids correct, but 4 excerpts were invented, including one graded "A" that contradicted BBB p.200, and its own Test B certified it.
4. **Phase 3** — `seed-evidence.json` was a *rewritten copy* of the corpus, so "59 substring asserts" validated quotes against text written to match them. Replaced with the real 36 chunks; circularity gone.

## What I changed in the app myself

- `src/data/seed-evidence.json` — replaced with 36 verbatim chunk texts from kb.db
- `src/data/seed_graph.json` — restored 39 node-level citations the AI had dropped; downgraded 16 uncited `verified` properties to `needs_review`
- both confirmed byte-identical to my authoritative copies afterwards (`_fixed/`)

## Autonomous supervision (runs without me)

`restart_autopilot.cmd` → `autopilot.py` (pythonw, detached, 5-minute cycle):

1. connects to Chrome/CDP, finds the AI Studio tab
2. classifies state: RUNNING / CURTAIN / IDLE / NO_PAGE
3. CURTAIN → clicks Proceed (plans already vetted)
4. IDLE → snapshots all editor models → runs `audit_app.py` → logs
5. problems → sends a templated correction (cooldown 8 min, cap 6/hour, no repeats)
6. clean → pops one instruction from `_autopilot_queue.txt`
7. refuses to grade a cycle if the data files are not readable (no stale passes)

Log: `_autopilot.log`. Snapshots: `_auto_snap/<timestamp>/`. State: `_autopilot_state.json`.
Stop it: `powershell -c "Get-CimInstance Win32_Process -Filter \"Name='pythonw.exe'\" | ? { $_.CommandLine -like '*autopilot*' } | % { Stop-Process -Id $_.ProcessId -Force }"`

## Queue (what it may still ask for)

1. ~~finish Phase 4 within guardrails~~ (sent, 16:34)
2. build fix (sent automatically, 16:39 — build now green)
3. Phase-4 self-review: verdicts must come from the engine, provenance labels must distinguish bundled vs attached, export round-trip, degree>40 collapse enforced in code

## Known gaps / open questions for you

- App is still titled "Untitled" (asked the builder to set "Hi5 Mechanical Knowledge Graph")
- `sqlite-service.ts` opens the uploaded DB in memory via sql.js; I have not yet verified the file is never written back
- Property-vs-property fitment (hub O.L.D. vs dropout spacing) is not evaluated by the engine — it answers only from documented edges, which is safe but limited
- The seed graph is 27 nodes. Everything else in kb.db (3,921 chunks) is reachable only as evidence text, not as graph structure — that is Phase 5+ work

## Files worth opening

- `_audit_app.txt` — latest mechanical audit
- `_scan_phase4.txt` — Phase 4 static checks
- `_autopilot.log` — autonomous cycle history
- `seed_graph.json`, `_fixed/seed-evidence.json` — ground truth
- `_studio_read.png` — screenshot of the current AI Studio state

---

## 2026-10-24 ~19:20 — the loop is now autonomous (owner approved Phase 5)

Owner instruction: *"finish this map with google ai… all the process are yours. I approve all
your decisions."* Phase 5 is therefore open, in bounded evidence-first batches.

### Built

- **`relay.py` / `relay.cmd`** — the `/task` handshake. When AI Studio finishes a reply it
  fires `vscode://saoudrizwan.claude-dev/task?prompt=[[SUPERVISOR WAKE]]…`, which starts a
  fresh supervisor task. Guards: pause file, per-reply dedupe, approval curtain,
  `_NEEDS_APPROVAL.txt`, **no second supervisor while one is `running`** (read from
  `sessions.db`), 12 min cooldown, 5/h, 30/day. Documented in `RELAY.md`.
  Verified: two probes (`_relay.log`) — baseline, then `no new reply`.
- **Cron specs** written to both scopes:
  `<workspace>/.cline/cron/` and `~/.cline/data/cron/` `hi5-supervisor-heartbeat.cron.md`
  (every 20 min). Format taken from the bundle's validator, not guessed.
  **Checked 19:21 — the native cron is inert on this install:** `~/.cline/data/db/cron.db`
  does not exist and `sessions.db.schedules` has 0 rows, so nothing consumes those specs.
  The live cron is the **Windows Scheduled Task `Hi5SupervisorRelay`** (every 5 min,
  `relay.cmd`), which was created successfully and needs no Cline feature.
- **`autopilot.py`** now appends the `[[TASK]]` relay footer to every message it sends, so the
  marker protocol holds even for its templated corrections.
- `WAKE_PROMPT.md` rewritten (v1 kept as `WAKE_PROMPT_v1.md`): Phase 5 allowed, "verify then
  send one instruction", clock/loop documented.

### Verified in the 2026-10-23 17:02 reply (the self-review)

- still 27 nodes / 12 edges, 20/20 edge + 39/39 node citations literal, 36/36 chunk texts
  byte-identical — `audit_app.py` problems=0, `scan_phase4.py` problems=0
- suite is **13** tests, every one with a real predicate (0 hard-coded passes); Test M
  (export round-trip) and Test N (limits/collapse) exist and are non-vacuous
- `hybrid-layout.ts` really computes degrees and applies `degreeCollapseThreshold` (default
  40), `depthLimit`, `resultLimit` — not just UI controls
- GraphML export carries node+edge evidence objects and the importer re-reads
  `d_node_evidence` / `d_edge_evidence`, so citations survive the round-trip
- two of my own checks were wrong before I corrected them: I grepped for `maxDegree` (the real
  name is `degreeCollapseThreshold`) and flagged `d_node_chunk_ids` as not re-read (it is
  redundant — the evidence objects carry `chunk_id`). Both corrected in `_verify_phase4b.txt`.

### Sent (one instruction)

Phase 5 batch 1 — brake subsystem, in a **new** `src/data/expansion-brakes.json`, citing only
7 chunk_ids that already exist in the bundled `seed-evidence.json` (zero new evidence, zero
transcription risk), plus Test P (seed immutability) and the stale "(11 Acceptance Tests)"
header. Instruction is `_msg4.txt`.

### The stall this fixed

The autopilot ran every 5 minutes for **26 hours** with an empty queue and sent nothing: its
last instruction was delivered 2026-10-23 16:54. Nothing was broken — it had simply run out of
work. The relay now closes that loop by waking a supervisor whenever the AI replies.

---

## 2026-10-24 ~19:40 — Phase 5 batch 1 landed (37 nodes / 22 edges)

Instruction `_msg4_batch1.txt`; AI ran ~12 min; 9 files touched.

### What it built

- `src/data/expansion-brakes.json` — **10 nodes / 10 edges**, tagged `batch: phase5-brake-1`
- `src/services/graph-loader.ts` (44 lines) merges seed + expansion; `App.tsx` now imports the
  loader and no longer reads `seed_graph` directly
- `Test P: Seed Immutability & Expansion Merge` → suite is **14 tests**, no hard-coded passes
- `TestSuiteModal` header is now dynamic (`{testRun?.results.length} Acceptance Tests`)

### Mechanically verified (`_verify_expansion.txt`, `_post_batch1.txt`, `_schema_check.txt`)

| Check | Result |
|---|---|
| seed byte/ids/topology unchanged | **UNCHANGED** (27 nodes / 12 edges) |
| expansion node ids unique / no seed collision | none |
| citations whose quote is a literal substring of a real kb.db chunk | **20/20** |
| chunk_ids outside the 7 permitted | **0** |
| nodes / edges with ≥1 citation | 10/10, 10/10 |
| uncited `verified` properties | 0 |
| node types + relation types legal in schema/ontology | all legal |
| audit / phase-4 scan | problems=0 / problems=0 |

### Three defects I caught and sent back (not accepted)

1. **Invented `section` fields** on 5 of 7 chunks (book and page were correct). The gate now
   compares `book` / `page` / `section` against `chunks` in kb.db and **fails on a mismatch**.
2. **`comp-brake-hose` marked `verified`** on the quote *"be careful when using any brake
   lines."* — a handling caution, not evidence that the hose is a pressure conduit.
3. **`std-brake-thru-axle` marked `verified`** on a quote that says the diameter *"cannot be
   definitively determined from image"*. The source contradicts the status.

That is the whole point of the lane: the AI's own 14/14 suite passed while all three were
present, because its tests check quote-membership, not whether the quote supports the claim.
`_expansion_edges.txt` (claim + quote side by side) is the human-readable check for this.

### Loop state at hand-off

- Scheduled task `Hi5SupervisorRelay` created, every 5 min, runs `relay.cmd`
- `_relay_pause.txt` holds the relay back while this task is working; it is removed at the end
- `relay.py` has 14/14 unit tests (`test_relay_decide.py`) for its guards

### End-to-end proof captured before hand-off (19:36–19:38)

```
19:36:32 probe ... marker=2 -> skip (marker grew - confirming on next probe)
19:36:47 probe ... marker=2 -> FIRE (confirmed marker growth (2))        [dry run, left pending]
19:38:03 probe ... marker=2 -> skip (supervisor session 1792764699174_pvl4o still running (6s))
```

The first two lines prove the reply is detected; the third proves the "one supervisor at a
time" guard actually reads this task from `sessions.db` and refuses to fire. Because the block
stores a `pending` entry, the **next scheduled run after this task ends will fire the wake** —
no manual step needed.

One correction made at that point: the guard originally aged sessions on `started_at`, so a
task resumed a day later looked stale (3 h TTL) and the guard failed open. It now ages on
`updated_at`, which moves as a task works, with a 45 min TTL. `_sess_ts.py` is the probe that
proved which column is live.

### Corrections accepted (second pass, 19:35)

The AI fixed all three, and the gate now reads:

```
metadata (book/page/section) mismatches: 0     (was 10)
literal quotes OK : 20        unknown chunk_ids : 0        quotes not found : 0
seed: 27 nodes / 12 edges, ids and topology identical to approved
VERDICT: PASS
```

- `comp-brake-hose` → `needs_review`, renamed "Brake Line", description cut back to the quote
- `std-brake-thru-axle` → `needs_review`, renamed "Thru-Axle Diameter (unconfirmed)"
- edges `comp-brake-hose → comp-caliper-hydraulic` and
  `comp-rear-hub → std-brake-thru-axle` → `needs_review`

**Map now: 37 nodes / 22 edges** (27+10 / 12+10), of which 8 expansion nodes and 8 expansion
edges are `verified` and 2 + 2 are honestly `needs_review`.

---

## 2026-10-24 19:45 — batch 1 re-verified; Test K found blind; one instruction sent

**Why I was woken.** The relay's retry path fired again for the *same* reply (marker=2,
len=76455, the 19:34 corrections answer). I checked before acting: `_send3_log.txt` showed no
`clicked Send` after **19:31:08**, `_relay_state.pending` was null, `_NEEDS_APPROVAL.txt` absent,
autopilot queue exhausted (`queue_done [0,1]`), page shows `Ran for 2m 22s` — not running. So
nothing had been sent since the corrections and one instruction was owed.

**Verified myself, against `kb.db`, not against the app's tests** (`_out_audit.txt`,
`_out_scan.txt`, `_verify_expansion.txt`, `_verify_batch1_final.txt`):

| Check | Result |
|---|---|
| seed vs `_fixed/seed_graph.json` | 27/12, node ids + edge topology **identical** |
| seed citations | 20/20 edge + 39/39 node literal; evidence file 36/36 identical to `chunks.text` (not circular) |
| expansion citations | 20/20 literal substrings, 0 unknown `chunk_id`, 7 distinct chunks |
| `section` field vs `chunks.section_title` | **0 mismatches**; correctly **omitted** on `p0253_c01` and `p0680_c02` (both empty in db) |
| statuses | nodes 8 verified / 2 needs_review, edges 8 / 2 — the AI's counts are true |
| `comp-brake-hose` | `needs_review`, name "Brake Line", `aliases: []`, no pressure-conduit claim |
| `std-brake-thru-axle` | `needs_review`, renamed "Thru-Axle Diameter (unconfirmed)", `aliases: []`, edge downgraded |
| audit / phase-4 scan | problems=0 / problems=0 |

**Defect the AI did not report and its own 14/14 could not see.** `phase3-tests.ts` lines 55/60
set `const payload = seedGraph`, so **Test K scans the 12 seed edges and never the expansion**. I
replayed Test K's exact regex: over the seed it finds 0 violations; over seed + expansion it finds
**2**, one of them on an edge marked `verified` —
`std-brake-centerlock_has_property_std-brake-centerlock-torque`, claim "…specifies 40 N·m…",
`evidence_grade: "B"`. That is precisely the rule Test K is named for, passing because it is
vacuous with respect to new data. Same class of failure as the four earlier fabrications: the
suite is green on the wrong graph.

Two more, both truth defects in code rather than cites:
- `graph-loader.ts:41` — the provenance **note is a hard-coded sentence** ("Seed (27 nodes, 12
  edges) + … (10 nodes, 10 edges)") while the counts beside it are computed. It becomes false at
  batch 2.
- `comp-brake-hose` description says "…during servicing and clamp usage". `clamp` **is** in
  `big_blue_book_p0728_c04` (it may stay); `servicing` is in **neither** cited chunk.

**One of my own earlier readings was wrong, and I corrected it.** `post_batch1.py` printed
`TestSuiteModal header count: NOT FOUND` / `modal mentions 11: True`. The header is in fact
dynamic — `{testRun?.results.length ?? 0} Acceptance Tests` — and the "11" it matched is the CSS
class `text-[11px]`. No defect there; the script's regex was the problem, not the app.

**Sent** (one instruction, `_msg5_batch1_fixes.txt` copied to `_msg4.txt`, `run_send3.cmd 420`):
(1) run Test K over `getMergedGraph()` and print the number of edges scanned, extend it to
node-level numeric claims on grade B; (2) `std-brake-centerlock-torque` node **and** its edge →
`needs_review`, no re-grading to A — expansion then 7/3 nodes, 7/3 edges; (3) derive the
`graph-loader` provenance note from the arrays; (4) drop "servicing" from the hose description.
No new nodes.

**The trap I left in my own instruction, written down so the next wake checks it.** I told the AI
to run Test K over the merged graph, but Test K's current predicate is *status-agnostic*: it flags
any edge whose claim holds a number and cites grade B. Two merged edges match today — the torque
edge (`verified`) and `comp-rear-hub_interfaces_with_std-brake-thru-axle` (`needs_review`,
"presumed 12mm or 15mm"). The correct fix makes it a rule about **verified** claims only; the lazy
fix deletes the honest thru-axle node to turn the suite green. **Next wake, check:** the
`std-brake-thru-axle` node still exists and is still `needs_review`, and Test K's predicate now
keys on status. Recovery copies taken before sending:
`_fixed/expansion-brakes.batch1-corrected.json` and `_fixed/phase3-tests.batch1-corrected.ts`
(21139 / 18792 bytes, identical to what was live at 19:46).

**How the send actually behaved, since this matters for the loop.** The first attempt
(`cmd /c run_send3.cmd 420`, 19:45:40) died the moment the next foreground command closed the
console — it logged `before_len` and nothing else, so no text reached the composer. The relaunch
as a detached `pythonw studio_send3.py` (19:47:18) survived: `filled=3087` at 19:47:27,
`clicked Send` at 19:47:28, page 76238 → 79327. **Use the pythonw form, not `run_send3.cmd`, from
a task whose shell is this broken.**

**Environment note for the next wake.** This task's PowerShell is in a broken PSReadLine state
(`System.ArgumentOutOfRangeException … top -1` while rendering any long line). Every command here
was therefore redirected to a file and read back; `run_commands` reports rc=1 from that PowerShell
exception even when the command itself succeeded. Also: `studio_state.py` is dead (needs
`playwright` on `py -3`); the working CDP entry points are `tail_reply.py` and the `run_*.cmd`
wrappers, which use the `.venv` python.

**Still open:** batch 2 = cockpit (stems/headsets) from the 8 bundled chunk ids already listed
below; the unused verbatim 16-chunk pack `_expansion_source.json`; the `evidence_grade` convention
(every expansion cite so far is B, which now forces `needs_review` wherever a number is involved —
worth settling before batch 2).

### Open items carried forward (do not let these rot)

1. `graph-loader.ts` writes a **hard-coded** provenance note ("Seed 27 … Batch 1 10 …"). The
   moment batch 2 lands that string is false. It must be derived from the arrays.
2. `evidence_grade` in the expansion is `"B"` for every citation, including the Center Lock
   40 N·m torque. Test K forbids a numeric claim resting on grade B — check whether that
   value should be `needs_review` or whether the source supports a higher grade.
3. Batch 2 candidate: **cockpit** (stems/headsets) from the bundled chunks
   `big_blue_book_p0820_c00`, `p0825_c00`, `p0861_c00`, `p0861_c02`, `p0888_c00`, `p0888_c02`,
   `p0051_c00`, `p0052_c00` — all already in `seed-evidence.json`, so no new evidence is needed.
4. The 16-chunk pack `_expansion_source.json` (built from kb.db, unused in batch 1) is ready
   for the first batch that has to go *beyond* the bundled 36; its texts are verbatim.

---

## 2026-10-24 20:15 — batch 1 closed on evidence; batch 2 (cockpit) sent

**Why I was woken.** The reply to the 19:47 corrections finished at ~19:50 (`_send3_log.txt`:
`clicked Send` 19:47:28, `STABLE at 198s`), marker 2→3. The relay had already handled it.

### The thing that nearly fooled me, first

`_app_files` was **stale at 19:41:22** — every file byte-identical to the pre-correction copies
in `_fixed/`. My first `getall` ran in a combined command and was killed when the next command
closed the console (`_out_getall2.txt` 0 bytes), so `audit_app.py` and `scan_phase4.py` graded
the **pre-fix** dump and printed a clean `problems=0` that meant nothing at all. Caught it by
hashing the dump against `_fixed/` before believing anything. Re-dumped detached
(`getall_now.cmd` → `pythonw`) at 20:05:43; all three edited files changed size
(expansion 21139→21133, loader 1669→1752, tests 18792→21929).

**Rule for the next wake: check `_app_files` mtime against the reply time before running the
gate.** A dump older than the reply is not evidence of anything.

### Verified on the fresh dump (`_verify_batch1_fix.txt`, `_verify_expansion.txt`, `_audit_app.txt`)

| Claim in the reply | What I measured |
|---|---|
| Test K scans the merged graph, 22 edges + 37 nodes | **true** — `getMergedGraph()` at line 219, six `*.length` counters, both loops, counts interpolated into the message (line 271) |
| Test K keys on status, so it can fail | **true** — `if (edge.status === 'verified')` line 234, `if (node.status === 'verified')` line 244; the node scan covers name, description and every property value+unit |
| torque node + edge → `needs_review`, value kept, no re-grade | **true** — both `needs_review`, `40` + `N·m` still in the property, grades still `['B']`, no `A` anywhere |
| provenance note derived | **true** — line 41 is a template over `seed.nodes.length` / `expansion.batch` / `expansion.nodes.length`; my hard-coded-count regex finds **nothing** |
| "servicing" cut | **true** — description now ends "…during clamp usage." |
| 7 verified / 3 needs_review, nodes and edges | **exactly** that, both levels; the 3 are `comp-brake-hose`, `std-brake-thru-axle`, `std-brake-centerlock-torque` |
| seed untouched | 27 / 12, ids + topology identical, 20/20 edge + 39/39 node citations literal, evidence file 36/36 identical to `chunks.text` |
| expansion citations | 20/20 literal, 0 unknown chunk_ids, 7 distinct chunks, **0** metadata mismatches, 0 uncited `verified` |

**The proof that the fix is a status key and not a deletion.** I replayed the rule myself over
seed+expansion: status-agnostic → 2 edge + 2 node violations; **verified-only → 0**. The two the
old predicate flagged are exactly the honest `needs_review` items, and all three downgraded nodes
still exist. That is the trap the last wake left in its own instruction, and it was not taken.

`App.tsx` imports `getMergedGraph` and never `getSeedGraph`, so the UI shows 37/22. The suite is
14 named tests with **0** hard-coded `passed: true`.

### What I did not accept on trust

- `studio_getall.py`'s page probe returns `failed_build: true` — a **false positive**: its regex
  searches the whole page text and matches the historical "Failed to build" line 1339 in the
  conversation. The autopilot's position-aware detector has logged `build_failed=False` on every
  cycle since 19:53. **I did not run the build** — the project exists only as Monaco models, so
  "build green" rests on the app's own log plus that detector, not on a build I observed.
- "14/14" is likewise the app's own suite. I checked its structure (14 results, real predicates,
  no constant passes) but I cannot execute it. Every substantive claim above was checked against
  `kb.db` or by replaying the predicate in Python, not by believing the green line.
### Two tooling defects of my own, both fixed

1. **My gate could grade a dead copy.** `studio_getall.py` never purged `_app_files`, so nine
   stale duplicate models (`App.tsx`, `data__*`, `services__*`, `tests__*`, `types__*`) sat
   beside the live `src__` files; `audit_app.py` read `tests__phase3-tests.ts` by bare name and
   `scan_phase4.py` took the first suffix match. This round they happened to be byte-identical to
   their twins, so nothing false passed — but that was luck, not design. Now `studio_getall.py`
   purges before dumping, `audit_app.py` resolves `src__` first, `scan_phase4.py`'s `find()`
   prefers `src__`. Re-ran the gate after the change: still `problems=0 / problems=0`, and the
   notes now name the `src__` paths, which is the proof the resolver works.
2. `run_getall.cmd` calls plain `python.exe`, so a closing console kills the dump mid-flight.
   `getall_now.cmd` launches `pythonw` with `start ""` (detached) instead. **Use it.**

### Evidence-grade convention settled (my call, owner-delegated)

The grade describes **how directly the chunk states the claim**, not how good the book is:
**A** when the cited sentence states the fact in words; **B** when the chunk only supports it
indirectly (a figure, a caption, a warning, "verify with the service manual"). A number resting on
B must be `needs_review`. Measured baseline: the seed is A 39 / A 19 / B 1 (`p0888_c00` only);
batch 1 was B for all 20 citations, which is exactly why 3 of its 10 nodes honestly carry numbers
as `needs_review`. Never upgrade a grade to make a test pass.

### Sent (one instruction, `_msg6_batch2_cockpit.txt` → `_msg4.txt`)

`start "" pythonw studio_send3.py 900 …` — `filled=3749`, `clicked Send` 20:10:51, page
82819 → 89126, instruction verified present in the page text, `Running for 52s` at 20:11.

**Phase 5 batch 2 — cockpit.** Part 1, before the new file exists: make the merge handle N
expansions — one registry array in `graph-loader.ts`, and **delete Test P's `allowedChunks`
allow-list of the 7 brake ids** (replacing it with "chunk_id exists in the bundled evidence and the
quote is a literal substring"), because that allow-list is the same vacuous-test defect one level
up. Part 2: add `src/data/expansion-cockpit.json`, batch `phase5-cockpit-2`, 6–8 nodes and 6–8
edges, citing only these 8 ids — each machine-checked present in `kb.db` **and** in the bundled
evidence, with book / page / section:

```
big_blue_book_p0820_c00  p820  "QUILL STEMS"
big_blue_book_p0825_c00  p825  no section
big_blue_book_p0861_c00  p861  "THREADLESS HEADSET ADJUSTMENT"
big_blue_book_p0861_c02  p861  "THREADLESS HEADSET ADJUSTMENT"
big_blue_book_p0888_c00  p888  no section
big_blue_book_p0888_c02  p888  no section
big_blue_book_p0051_c00  p51   "CHAPTER 16 — HEADSETS"   (161 chars — heading)
big_blue_book_p0052_c00  p52   no section                (137 chars — heading)
```

The two heading chunks may support existence/scope only, never a number or a procedure step.

### What the next wake must check (written down before it is forgotten)

1. **`_app_files` mtime must be later than the reply.** If not, re-dump detached; do not grade.
2. **Test P: did it get generic, or did the allow-list just grow to 15 ids?** A list that grew is
   the lazy fix and goes back. The honest check derives its scope from the registry.
3. The 8 cockpit chunk ids must still be the only new ones, `expansion-brakes.json` byte-stable,
   seed still 27/12/59, and no new node may have smuggled a number in on grade B.
4. Batch 3 candidate after cockpit: drivetrain (cranks / BB / cassette) — likely bundled chunks
   already in `seed-evidence.json`, but check the ids against `kb.db` first, never assume.

### The `[[TASK]]` marker is not a reply signal — it is a send signal

Measured while closing this wake (relay log, 20:10–20:15):

```
20:10:29  probe ... marker=3 len=82819 -> skip (no new reply)      <- after the 19:50 reply
20:10:51  [sent the batch-2 instruction, which ends with [[TASK]]]
20:15:16  probe ... marker=4 len=86642 -> skip (supervisor session ... still running (3s))
```

The count went 3→4 when the **instruction** was posted, not when anything was answered. The 19:50
reply added no marker of its own (`_reply_tail.txt` ends at "Finished"; the only `[[TASK]]` on the
page is the one inside my 19:47 message). So **the AI is not printing the footer**, and marker
growth can never distinguish "I just posted an instruction" from "the reply landed". The relay has
been surviving on the `Running for Ns` true→false edge plus the "one supervisor at a time" guard —
which is exactly the shape of a guard that fails open if the session row ever ages out mid-reply.

Do not treat marker growth as proof a reply finished. Check `_send3_log.txt` for `clicked Send`
and `STABLE`, and the page for `Running for` / `Ran for`. Worth hardening in `relay.py` next time:
ignore marker deltas within N seconds of our own send, and require running→false.

---

## 2026-10-24 20:35 — batch 2 verified against the corpus; batch 3 (drivetrain) sent

### Why I was woken — a FALSE fire, and the reason

The relay fired at **20:16:34** on `marker=4`. The reply had **not** finished: the page said
`Running for 8m 37s` (generation started 20:11:51, finished 20:20:09, `Ran for 8m 18s`).
I waited instead of interrupting (§1C), and it landed on its own.

Root cause, read from the code: `relay.py` line 74 decides running with
`/Running for \d+s/ || /\bWorking\b/`. `Running for 8m 37s` does **not** match `\d+s` (the unit is
minutes), and `Working` was not in the text at the moment of that probe. So a live generation
reported `running=False` — fail-open, exactly the shape §2 warns about.

**Not patched on purpose.** The relay is one long-lived loop (`relay loop start interval=60s`,
pid 15752 since 19:58), so editing the file changes nothing until it restarts, and restarting the
live loop from a console this broken is a worse risk than one wasted wake. Next wake: change the
literal to `/Running for \d+[ms]/` (still matches `Running for 52s` and `Running for 8m 37s`;
a finished turn reads `Ran for`, which does not match), restart deliberately, confirm a fresh
`relay loop start` line, then probe once.

### Verified on the 20:20:29 dump + the file I had to open by hand

| Claim in the reply | What I measured |
|---|---|
| 4 files edited, incl. new `src/data/expansion-cockpit.json` | **true, but invisible to the model dump.** `monaco.editor.getModels()` returned **29** models and no cockpit file — a file never opened in the tab is not a model. I opened it via the Code panel (`wake9e.py`) and read all **13,852** chars |
| cockpit 7 nodes / 7 edges, 5 verified / 2 needs_review at both levels | **exactly that** (`_verify_cockpit-2.txt`) |
| 14 citations literal, right chunk | **14/14 literal substrings of `chunks.text` in kb.db**, 0 unknown ids, **0 outside the 8 I allowed**, 0 book/page/section mismatches |
| grades | A 10 / B 4; the two `needs_review` are the two numbers on grade B (28.6 mm steerer, 5-7 Nm stem clamp). No verified numeric claim on B — Test K's rule holds |
| Test P generic, not a grown allow-list | **true** — `allowedChunks` 0 occurrences, `getExpansionRegistry` 3, `expansionsActual` 8; the message interpolates files/nodes/edges/citations |
| merged 44 nodes / 29 edges, 39 verified / 5 needs_review | **true** — and the live preview frame renders `44 Nodes / 29 Edges`, `Visible: 44/44` |
| seed untouched | `seed_graph.json` and `seed-evidence.json` **byte-identical** to `_fixed/` (sha256 63ac5126…, d45b173e…) |
| brakes untouched | re-verified independently: **20/20 literal**, 0 metadata mismatches, 7 verified / 3 needs_review, A 10 / B 10 — the same numbers I recorded closing batch 1 |
| p0051 heading used for a procedure step? | no — used once, on `edge-threadless-headset-part-of-cockpit`, a scope claim |

Nothing to send back on the content. Two defects of shape, both sent as corrections:

1. **`App.tsx:134` still hard-codes** `"Hybrid Hierarchical & Constraint Reasoning System • Brakes & Cockpit"` — the provenance-note defect one level up. It goes false the moment batch 3 lands.
2. **Test P's `knownStatusesHonest`** is a five-id list with optional chaining (`!steererDiaNode || …`), so a *missing* node passes. Replace it with a rule plus a printed count: any registered expansion entity whose text or property values contain a digit and whose citations are all grade B/D must be `needs_review`.

### Two tooling defects of mine, both fixed

1. **My gate could not see a new file.** `audit_app.py` graded 29 files and called it clean while
   `graph-loader.ts` imported a 30th that was not in the dump. It now parses every
   `from '../data/…'` in `graph-loader.ts` and raises a **problem** when `_app_files` has no copy
   (`== IMPORTS vs DUMP`). Re-ran: `problems=0 / problems=0`, all three imports `yes`. Opening the
   panel took the model count 29 → 30 and the file dumped itself, so opening a file is how a new
   one becomes visible (`wake9e.py`).
2. **`studio_send3.py` could have typed into the code editor.** With the Code panel open the page
   has two visible textareas and Monaco's is 1×1; `.first` was luck. It now picks the widest
   non-Monaco textarea, logs candidates, and **aborts** unless the composer holds ≥98 % of the
   message. This send: `filled=4432 value_len=4432`, `clicked Send` 20:34:53, 91637 → 95638.

### Sent (one instruction, `_msg7_batch3_drivetrain.txt` → `_msg4.txt`)

**Batch 3 — drivetrain: freehub / cassette / chainline**, `src/data/expansion-drivetrain.json`,
batch `phase5-drivetrain-3`, 6–8 nodes / 6–8 edges, citing **only** these 8 ids — every one already
inside the bundled `seed-evidence.json` (checked in the bundle **and** in kb.db), with char counts
so a mismatch is visible:

```
big_blue_book_p0238_c00  p238  "FREEHUB REMOVAL & INSTALLATION"  682
big_blue_book_p0250_c00  p250  "FREEHUB BEARINGS"                 824
big_blue_book_p0585_c00  p585  "CHAINLINE"                       1494
big_blue_book_p0637_c00  p637  "REAR DERAILLEUR"                 1591
big_blue_book_p0200_c00  p200  no section                        1580
big_blue_book_p0244_c01  p244  no section                        1532
bike_repair_manual_chris_p0066_c00  p66  "MAINTAINING YOUR TRANSMISSION • CHAIN, CASSETTE, AND CHAINSET"  1430
big_blue_book_p0024_c00  p24   no section                         292  (contents list)
```

`p0024_c00` is a contents list → scope only. `p0637_c00` and `p0244_c01` carry `[VISUAL DATA]`
sections → a claim resting on those is B, manual prose is A, no averaging. CHAINLINE says "50mm" in
words, so that number may be A/verified. **No evidence-file change is needed for batch 3** — that
is why I chose bundled chunks. Crankset/BB chunks (`p0336_c00`, `p0341_c00`, `p0192_c00`,
`p0194_c00`) exist in kb.db but are not bundled; supplying them means pasting text, and pasted text
cannot be used to verify itself — that batch needs a different protocol.

### What the next wake must check

1. `_app_files` mtime **after** the reply; then **open any new file** (`wake9e.py`) before grading.
   `audit_app.py` now fails when an import is missing from the dump — do not read that as a build
   failure until the file has been opened.
2. `App.tsx` subtitle **derived** from the registry (no "Brakes & Cockpit" literal); the preview
   header follows it.
3. `knownStatusesHonest` replaced by the rule, with a printed count that must be > 0.
4. Drivetrain file: 6–8 nodes/edges, only those 8 ids, ids unique vs seed + brakes + cockpit,
   `p0024_c00` never used for a number or a step, seed still 27/12/59 byte-identical, brakes and
   cockpit unchanged, merged map **50–52 nodes / 35–37 edges** (44 + 6–8, 29 + 6–8).
5. The relay still has the wrong `Running for` regex until it restarts — a wake that arrives while
   the page says `Running for Nm Ns` is a false fire: wait, do not send.

---

## 2026-10-24 20:52 — batch 3 (drivetrain) verified against the corpus; two status-accounting defects; batch 4 (rear shock) sent

### Why I was woken

The reply to the batch-3 instruction finished: `_send3_log.txt` `clicked Send` **20:34:53**, page
91637 → 95693 → 94843 (`Ran for 3m 30s`). The relay fired at **20:40:50** on
`marker=5 … -> FIRE (retry blocked reply (marker>=5))`. Autopilot was alive throughout
(`20:39:24 snapshot files=9 audit problems=0`), page idle, no curtain, no `_NEEDS_APPROVAL.txt`.

**Freshness of the dump, checked first (the 20:15 lesson).** `getall` ran 20:42:37 on a reply that
ended 20:39 — and the dump grew 30 → **31 files**, `src__data__expansion-drivetrain.json` among them.
So `audit_app.py` (`problems=0`) and `scan_phase4.py` (`problems=0`, notes=2 — both benign: DetailPane
and types "mention verdict states … confirm it only renders engine output") graded the new state.

### What I verified myself, against `kb.db` and the bundled corpus — `_verify_batch3.txt`, `_verify_code3.txt`

| Claim in the reply | What I measured |
|---|---|
| drivetrain 7 nodes / 7 edges, 5 verified / 2 `needs_review` at both levels | **exactly that**, tag `phase5-drivetrain-3` on every node and edge, no duplicate ids, **no** collision with seed / brakes / cockpit |
| 14 citations, all real | **14/14 literal substrings of `chunks.text` AND of the bundled `seed-evidence.json`**; 0 unknown ids; **0 outside the 8 I allowed**; 0 book/page/section mismatches; 0 dangling endpoints |
| grades | **A 10 / B 4**; no verified entity with a digit whose citations are all B/D; no verified property without a citation |
| `p0024_c00` (contents list) scope only | **never used for a digit** — 0 hits |
| `[VISUAL DATA]` handling | `p0637_c00`'s visual block starts at char 269; the one quote inside it (12.7 mm pitch) is graded **B** and is `needs_review`; the grade-A quotes sit in the prose before it. `p0244_c01` has no marker |
| seed untouched | `seed_graph.json` `63ac51261765d930…`, `seed-evidence.json` `d45b173e48d85f8b…`, both **byte-identical** to `_fixed/` |
| subtitle derived | **true** — `App.tsx:134` is `{getDerivedSubtitle()}`, no literal subsystem list; `graph-loader.ts:52-65` builds it from the registry batches (`Brakes, Cockpit & Drivetrain`); registry imports 3 files |
| Test P generic now | **true** — `knownStatusesHonest` **0** occurrences, `allowedChunks` **0**, the rule loops over every registered expansion entity, `entitiesExaminedForRule` is interpolated into the message, `numericGradeBDEntitiesCount` sits in `details` |
| Test K scans the merged graph, 36 edges / 51 nodes | **true** — 12 seed + 24 expansion edges, 27 + 24 nodes; the 48 expansion citations match 20 + 14 + 14 |

`14/14 tests, tsc --noEmit and build clean` is the one claim I could not observe: there is no build
here, and I do not grade the app by its own suite. I checked the code paths and the data instead.

### The defect: the reply's status table is wrong about the seed, and the totals inherit it

The reply printed `Seed: 27 nodes (27 verified, 0 needs_review)`, `Seed: 12 edges (12 verified, 0
needs_review)`, then `51 total (44 verified)` and `36 total (29 verified)`.

The frozen seed actually contains:

```
unk-freehub-body-length            status="candidate"     0 citations   (an unknown_requirement)
edge-rotor6bolt-incomp-centerlock  status="needs_review"
edge-headset-interfaces-steerer    status="needs_review"
edge-unknown-freehub-length        status="needs_review"
```

so the honest composition is **43 verified + 1 candidate + 7 `needs_review` = 51 nodes** and
**26 verified + 10 `needs_review` = 36 edges**. The app's own Test P message does *not* claim seed
statuses — it reports expansion counts (17/7) and totals — so this is prose the model wrote without
computing it. Same class as the four fabrications: a number asserted, not derived. This also corrects
my own earlier arithmetic: the 20:35 section's "39 verified / 5 needs_review" counted the seed as
all-verified. Fixed in the table at the top.

Two schema facts worth keeping: the seed's four `sys-*` subsystem nodes are `verified` with **0
citations** (approved in Phase 3, frozen — out of scope, but it is why a naive
`verified == has evidence` check must exclude them), and `candidate` is a legal status in
`graph.schema.json` next to `rejected`, `conflicted`, `superseded`.

### The residual in Test P: the rule can still pass vacuously

`numericGradeBDEntitiesCount` is incremented but **never asserted and never printed** — only
`entitiesExaminedForRule` reaches the message. Zero entities constrained by the grade-B/D rule would
still print "48 entities examined" and pass. Today N > 0 (brakes torque 40 N·m, cockpit 28.6 mm and
5-7 N·m, drivetrain 12.7 mm and 15 × 28 mm — all on B), so the suite is green for the right reason by
luck of the data, not by rule.

### One of my own gates was wrong, and it is worth writing down

`_verify_batch3.txt` flagged `expansion-brakes.json changed since batch 1 was closed`. That is my
baseline, not the app: `_fixed/expansion-brakes.batch1-corrected.json` is the AI's 19:46 file, taken
*before* my own corrections. The app copy is the corrected one — the hose description ends "…during
clamp usage." and the Center Lock 40 N·m node **and** edge are `needs_review` — so my batch-1 fix is
still in place. Re-verified independently: 20/20 literal, 0 metadata mismatches, A 10 / B 10, 7/3 at
both levels. Next time: compare against the state I closed with, not against the AI copy I overrode.

### Sent (one instruction, `_msg11_batch4_rearshock.txt` → `_msg4.txt`, pythonw form)

`copied 20:50:23`, `filled=4364 value_len=4364`, **`clicked Send` 20:50:46**, page 94843 → 99283 and
still climbing. Two corrections plus:

**Batch 4 — rear suspension shock**, `src/data/expansion-rearshock.json`, tag
`phase5-rearshock-4`, **5 nodes / 5 edges**, subsystem `sys-wheels` (as the seed classifies
`comp-rear-shock`), citing **only** `big_blue_book_p0921_c00` (p921, section "SHOCKS (REAR SHOCKS)",
1532 chars, manual prose, no `[VISUAL DATA]`). Rules: prose may be grade A, but the chunk states **no
torque, no pressure, no travel, no seal dimension** — invent none, import none from other chunks; ≥3
of the 5 edges must attach to `comp-rear-shock` or `sys-wheels` so the batch grows the seed graph
instead of floating; edge types must satisfy `relation-ontology.json`'s `allowed_source_types` /
`allowed_target_types` at both ends (note `conforms_to` and `part_of` do not accept a `standard` as
source — that is why this batch hangs off a *component*, not off `std-hub-width`).

### What the next wake must check

1. `_app_files` mtime after the reply, and the file count (31 → 32 with the new expansion file); a
   new file only enters the model dump once it has been opened in the tab.
2. Test P prints a per-file composition keyed by the statuses it actually saw, fails when an
   expansion entity carries any status other than verified / needs_review, and prints N > 0 for the
   grade-B/D rule. The reply must quote computed numbers only — 43/1/7 and 26/10, not 44/29.
3. Rear-shock batch: 5/5, only `p0921_c00`, 0 metadata mismatches, no invented numbers (regex the
   batch for digits and require each digit to appear inside the cited quote), ≥3 edges touching
   `comp-rear-shock` / `sys-wheels`, ontology types legal at both ends, seed still 27/12/59
   byte-identical, brakes / cockpit / drivetrain unchanged.
4. My gates: `verify_batch3.py` (copy per batch, edit `ALLOWED` and the file names) and
   `verify_code3.py`. Both write a report; read the report file, not the console.

### Environment, so the next wake does not lose time

`run_commands` never observes completion in this task (always `rc=1`, output only as raw terminal
text) and long commands crash PSReadLine (`top -1`). What works: write a `.cmd` or `.py` with the
editor, run it with a short `cmd /c` that redirects to a file, then read the file (`tail6.py` for
tails). Sending needs the detached `pythonw` form (`_wake11_send.cmd`), never `run_send3.cmd`, and
`findstr` on `_send3_log.txt` for `filled=` / `clicked Send` is the proof of delivery.

## 2026-10-24 21:06 — batch 4 (rear shock) accepted on evidence; wording pass + batch 5 (quill stem) sent

### Why I was woken

A real fire. `_relay.log` 20:54:51 `FIRE (running->idle)`; the batch-4 message
(`_msg11_batch4_rearshock.txt` → `_msg4.txt`) had gone out at `20:50:46`, the reply ran 3m56s,
marker count 5 → 6, page 94843 → 101543. Autopilot healthy throughout.

### What I verified myself — `_verify_batch4.txt` (`problems=0 literal=10/10`)

Against `kb.db` and the bundled corpus, never against the app's own test output:
5 nodes / 5 edges, tag `phase5-rearshock-4`, `subsystem: sys-wheels` on all five nodes,
**10/10 quotes literal substrings** of `chunks.text` **and** of the bundled `seed-evidence.json`,
0 unknown chunk ids, 0 citations outside `{big_blue_book_p0921_c00}`, 0 book/page/section
mismatches, grades all A, no grade-A quote from a `[VISUAL DATA]` region, no dangling endpoint,
no duplicate ids, no collision with seed or batches 1–3, every node and edge cited.
Ontology legal at both ends — `part_of` ×4 and `mounted_on` ×1, all `subcomponent → comp-rear-shock`,
and `comp-rear-shock` is a `component`, so both relations are permitted by their
`allowed_target_types`. Anchoring 5/5 (I asked for ≥3). `seed_graph.json` and `seed-evidence.json`
byte-identical to `_fixed/`.

Chunk read verbatim (`_chunk_0921.txt`): 1532 chars, manual prose, no torque / pressure / travel /
seal dimensions. `_chunk_words.txt` confirms the only digits in the batch all sit inside a cited
quote.

**Test P is genuinely fixed, not restated.** The composition is now built from the statuses the
files actually carry — `seedNodeStatuses[n.status]` prints a `candidate` key nobody named — it pushes
an error for any expansion status outside verified/needs_review, and `numericGradeBDEntitiesCount` is
printed *and* asserted (`> 0` in `testPPassed`). The reply's numbers reproduce exactly, computed by me:
seed `[verified 26, candidate 1]` / `[verified 9, needs_review 3]`; 7/3 and 7/3; 5/2 and 5/2;
5/2 and 5/2; 5/5 and 5/5; merged **56 = 48 verified + 1 candidate + 7 needs_review**, edges
**41 = 31 verified + 10 needs_review**. N=12, recomputed independently by me (`_n_check.txt`) as
4 brake-1 + 4 cockpit-2 + 4 drivetrain-3 + 0 rearshock, all grade B, all already `needs_review`.
Registry clean (`graph-loader.ts`): imported, in `expansionRegistry`, subtitle derived, no literals.

### The one thing I did not accept: unsupported words on `verified` entities

Not a number, not an id — wording that goes past the source. `_chunk_words.txt` lists, objectively,
the batch's content words that `big_blue_book_p0921_c00` does not contain:

| entity | word(s) | chunk actually says |
|---|---|---|
| `comp-shock-frame-bushing` | "eyelets", "rotational", alias "Shock Eyelet Bushing" | only "wear at the bushing of the frame attachments" |
| `edge-shock-stanchion-seal-part-of-rear-shock` | "prevents fluid or pressure leakage" | "may develop leakage at the seals" — "prevents" turns a possibility into a guarantee |
| `comp-shock-stanchion-seal` | "fluid or pressure leakage" | "leakage at the seals" |
| `comp-shock-coil-spring` | "coil" | "a large external spring surrounding the damper" |

Two resolutions allowed, no third: reword into the chunk's own words, or set the entity
`needs_review` with "Needs review: <specific> is not stated in big_blue_book_p0921_c00" in the
description. No citation, quote, id or page may move. This is the fifth defect class found, and the
first one that is purely lexical.

### My own false alarm, closed properly this time

`verify_batch3.py`'s `PROBLEMS: 1` — "expansion-brakes.json changed since batch 1 was closed" — was
**my baseline, not the app**. `_fixed/expansion-brakes.batch1-corrected.json` is the AI's 19:46 file
taken *before* my own corrections. I proved it with a real diff this wake (`_brakes_diff.txt`): the
only three differences are exactly my three corrections — hose description ends "…during clamp
usage.", and `std-brake-centerlock-torque` **and** its `has_property` edge are `needs_review`. Both
`verify_batch3.py` and `verify_batch4.py` were comparing against the pre-correction copy, so the
earlier note in this file was right and the gate was wrong. Fixed: the accepted state is now
`_fixed/expansion-brakes.batch1-ACCEPTED.json` (sha256 `a384a15f…`), `verify_batch4.py` compares
against it and carries the explanation inline. Re-run: **`problems=0`**.

Note for whoever reads this next: the Center Lock 40 N·m downgrade is *required* by the grade-B/D
rule (digit + grade-B-only citation). My batch-1 "correction" that set it `verified` was the wrong
call; the app was right to move it. Do not "restore" it.

### Sent (one instruction, `_msg12_batch5_quillstem.txt` → `_msg4.txt`, pythonw form)

`copied 21:06:04`, `msg4 bytes=6350`, `filled=6314 value_len=6314` **21:06:26**, **`clicked Send`
21:06:27**, page 101543 → 107753 and climbing. Previous log archived to `_send3_log.batch4.txt`.

**Batch 5 — quill stem**, `src/data/expansion-quillstem.json`, tag `phase5-quillstem-5`,
**4 nodes / 4 edges**, subsystem `sys-cockpit` (as the seed classifies `comp-stem-quill`), citing
**only** `big_blue_book_p0820_c00` (p820, section "QUILL STEMS", 1488 chars — verified in `kb.db`).
That chunk is prose → figure legend `FIGURE 15.12` (callouts A–F) → `[VISUAL DATA]` image description
at char 930. So: grade A on prose only, B at most on the legend, never A after the `[VISUAL DATA]`
marker, and the only digit in the chunk is the figure number `15.12`. The prose's own content was
quoted to the app so it cannot import torque/diameter/degree values, and it is told the chunk breaks
off mid-sentence at "There are several different steering column" and must not complete it. ≥3 of 4
edges must touch `comp-stem-quill` / `sys-cockpit`; `comp-stem-quill` currently has **no edge at all**
in the seed, so this batch is what structures it.

### What the next wake must check

1. `_app_files` must be re-dumped; file count 32 → 33 with `expansion-quillstem.json`, and a new file
   only enters the model dump once it has been opened in the tab.
2. Batch 5 gates: copy `verify_batch4.py` → `verify_batch5.py`, set `BATCH="phase5-quillstem-5"`,
   `ALLOWED={"big_blue_book_p0820_c00"}`, add the file to `FILES`, `ANCHORS={"comp-stem-quill",
   "sys-cockpit"}`, bounds 4/4. Check the legend rule by each quote's offset against the
   `[VISUAL DATA]` marker at 930 and the `FIGURE 15.12` offset: a quote from the legend region must
   not be graded A.
3. The four wording items: the reply must name a resolution per item and the file must match it.
   Re-run the `chunk_words.py` logic on the edited rearshock file — it must return "(none)" for the
   flagged words, or those entities must be `needs_review`.
4. Re-verify the merged composition after the edit; a wording fix must not silently move statuses.
   `rearshock-4` should stay 5 nodes / 5 edges, or drop to a stated 4/1 + 1 needs_review.
5. `seed_graph.json` / `seed-evidence.json` still byte-identical; brakes (now `…batch1-ACCEPTED.json`),
   cockpit, drivetrain hashes unchanged (`a384a15f`, `13f28204`, `62442afc`).
6. Still unverified by me, and recorded as such: the app's own `14/14 tests passing` and
   `tsc --noEmit` clean. That code lives only in AI Studio; I cannot run it. I verify the data and the
   test *logic*, never their green tick.

### Environment, updated

`run_commands` still never observes completion (`rc=1`, raw terminal text only), and **chained
`Start-Sleep` / `Get-Content` one-liners do not survive** — the sleep is killed when the next command
starts. What works: `Start-Process -Wait -NoNewWindow -RedirectStandardOutput/-Error`, then read the
file; and `cmd /c somefile.cmd` for multi-step sequences (`_wake12.cmd`). Browser scripts write their
own outputs — never redirect a script's stdout onto the file it writes. I truncated `_audit_app.txt`
and `_scan_phase4.txt` to garbage that way this wake; both recovered on a clean re-run.












## 2026-10-24 21:18 — batch 5 (quill stem) accepted on evidence; three wording items; batch 6 (cassette/freewheel) sent

### Why I was woken

A real fire. `_relay.log` 21:09:39 `FIRE (running->idle)`; the batch-5 message
(`_msg12_batch5_quillstem.txt` → `_msg4.txt`) went out 21:06:27, the reply ran 2m38s, marker 6 → 7,
page 101543 → 111378. Autopilot healthy every cycle (last 21:14:45, `audit problems=0`).

### What I verified myself — `_verify_batch5.txt` (`problems=0 literal=8/8`)

Built `verify_batch5.py` from `verify_batch4.py` (`BATCH=phase5-quillstem-5`,
`ALLOWED={big_blue_book_p0820_c00}`, `ANCHORS={comp-stem-quill,sys-cockpit}`, bounds 4/4,
subsystem `sys-cockpit`). Against `kb.db` and the bundle, never the app's tests:

- 4 nodes / 4 edges, tag correct, `subsystem: sys-cockpit` on all four, **8/8 quotes literal** in
  `chunks.text` **and** in the bundled `seed-evidence.json`, 0 unknown ids, 0 outside the allow-list,
  0 book/page/section mismatches, no duplicate ids, no collision with seed or batches 1–4, no dangling
  endpoint, every entity cited, grades all A
- **legend rule**: the `FIGURE 15.12` legend occupies chars 557–701, the quoted prose starts at 702,
  `[VISUAL DATA]` at 930. Nothing graded A touches either region. My first version of the rule
  ("anything after the FIGURE marker") flagged those two quotes; that was **my** false positive — the
  legend is three lines and prose resumes after it. Fixed in `verify_batch5.py`, then problems=0.
- digits: the chunk's only digit run is `15.12`; the batch contains no digit at all
- ontology legal at both ends (`part_of` ×3 subcomponent→component, `conforms_to` component→standard),
  anchoring 4/4, Test-K rule clean, no uncited `verified` property
- `seed_graph.json` / `seed-evidence.json` byte-identical to `_fixed/`; brakes `a384a15f`,
  cockpit `13f28204`, drivetrain `62442afc` unchanged; rearshock now `ace4858b`, quillstem `add08f18`
- **rearshock after the edit still passes its own gate**: `verify_batch4.py` → `problems=0`,
  `literal=10/10`, 5 nodes / 5 edges, all five verified. `_chunk_words.txt`: eyelet, rotational,
  coil, fluid, pressure all gone from the batch and all absent from the chunk. "resulting in play
  when lifted up and down" is supported — the chunk says "Play is felt when the bike is lifted up
  and down."
- composition recomputed by me, and it matches the reply exactly: seed `[26 verified, 1 candidate]` /
  `[9 verified, 3 needs_review]`; 7/3; 5/2; 5/2; 5/5; 4/4 (nodes and edges alike); merged **60 nodes =
  52 verified + 1 candidate + 7 needs_review**, **45 edges = 35 verified + 10 needs_review**. N=12.
- registry clean: `graph-loader.ts` imports the quillstem file, sits in `expansionRegistry`, the
  subtitle is derived from the batch name, no literal counts
- `_audit_app.txt` `problems=0` (seed still 27/12, 20/20 + 39/39 citations, 36/36 chunks identical),
  `_scan_phase4.txt` `problems=0`

Still **not** verified by me and recorded as such: the reply's "14/14 tests passing", `tsc --noEmit`
and "Built". That code lives only in AI Studio.

### What I did not accept — three wording items (same class as the four rearshock ones)

`_chunk_words5.txt`, computed against `big_blue_book_p0820_c00`:

| entity | word(s) | chunk actually says |
|---|---|---|
| `edge-quill-stem-conforms-to-diameter-fit` | "must" correctly match | "It is important that the stem's quill diameter is a correct match for…" |
| `std-quill-diameter-fit` | "Standard", "Specification requiring", "Clearance", "Matching" | a fit requirement, no named standard |
| `comp-quill-binder-bolt` | alias "Quill Expander Bolt" | "A bolt draws up a wedge or cone" — nothing expands |

`must` was **my** word in the instruction, not the AI's — which is exactly why the check has to run
against the chunk and not against my message. Checked and *not* flagged: alias "Quill Section" is
supported by the legend line "(D) quill section of stem"; the three properties are already
`needs_review`, so they carry no verified claim.

### Sent (one instruction, `_msg13_batch6_cassette.txt` → `_msg4.txt`, pythonw form)

`copied 21:17:36`, `msg4 bytes=7650`, `filled=7603 value_len=7603` 21:18:03, **`clicked Send`
21:18:06**, page 111366 → 118777. Previous log archived to `_send3_log.batch5.txt`.

Batch 6 — **cassette and freewheel**, `src/data/expansion-cassette.json`, tag `phase5-cassette-6`,
**5 nodes / 5 edges**, subsystem `sys-drivetrain`, citing **only** `bike_repair_manual_chris_p0066_c00`
(p66, section "MAINTAINING YOUR TRANSMISSION • CHAIN, CASSETTE, AND CHAINSET", 1430 chars, real manual
prose, no `[VISUAL DATA]` marker, ends in a figure-label block that is B at most). Chosen because
`comp-cassette` is a seed component with **no `part_of` edge and no sub-component of its own**, and
`sys-drivetrain` is a bare subsystem (0 edges) — the chunk is genuinely unexpanded (`cited_by=seed`).
Rules: 4 of 5 edges must touch `comp-cassette` / `comp-freehub-body` / `comp-rear-hub` /
`sys-drivetrain` / `prop-chainline`, at least one `part_of`/`contains` hanging off `comp-cassette`;
node types limited to component / subcomponent / property / compatibility_rule (**no `tool`** — the
ontology gives it no legal edge); the tool-dependence statement must be a `compatibility_rule`
attached with `constrains`; digits only inside quotes; no imports from p219 hub tables or the
chainline page. Also added reply item **(f)**: list every word in a verified entity that is not in the
chunk — "none" only if actually compared. That self-check is what would have caught items 1–3.

### What the next wake must check

1. `_app_files` re-dumped; file count 33 → 34 with `expansion-cassette.json` (a new file only enters
   the model dump once the tab has opened it).
2. Batch 6 gates: copy `verify_batch5.py` → `verify_batch6.py`, set `BATCH="phase5-cassette-6"`,
   `ALLOWED={"bike_repair_manual_chris_p0066_c00"}`, add the file to `FILES`,
   `ANCHORS={"comp-cassette","comp-freehub-body","comp-rear-hub","sys-drivetrain","prop-chainline"}`,
   `SUBSYS="sys-drivetrain"`, bounds 5/5. The legend rule needs the figure-label block, not a
   `FIGURE` marker: compute the offset where the prose stops ("Freewheel" / "1 2 3" tail) and require
   that a quote overlapping that block is not graded A.
3. The three wording items: a resolution per item, and the file must match what was claimed.
   Re-run the `chunk_words5.py` logic — "must" gone from the claim or the edge `needs_review`;
   "Standard"/"Specification"/"requiring"/"Clearance"/"Matching" gone from the std node or it is
   `needs_review`; the "Quill Expander Bolt" alias gone or that node `needs_review`.
4. Re-verify the merged composition after the edits; a wording fix must not move statuses silently.
   Expected if all six resolutions are rewording: quillstem stays 4/4, rearshock stays 5/5,
   merged still 60/45 = 52+1+7 / 35+10.
5. `seed_graph.json` / `seed-evidence.json` still byte-identical; brakes `a384a15f`, cockpit
   `13f28204`, drivetrain `62442afc` unchanged.
6. Still unverified by me: the app's own test count, `tsc`, and the build tick.
7. Do not "restore" the Center Lock 40 N·m downgrade, and do not treat
   `_fixed/expansion-brakes.batch1-corrected.json` as the accepted baseline (it is the AI's
   pre-correction copy; the accepted state is `…batch1-ACCEPTED.json`).

### Environment, unchanged from last wake

`run_commands` never observes completion (`rc=1`, raw terminal text). `cmd /c <script.cmd>` works;
`timeout /t 40 /nobreak` inside `cmd /c` is the way to wait (a bare `ping > nul` inside PowerShell
errors with "FileStream … not a file"). Sending needs the detached pythonw form
(`_wake13_send.cmd`), and `_send3_log.txt` showing `filled=` + `clicked Send` is the proof of
delivery. Browser scripts write their own output files — never redirect a script's stdout onto the
file it writes.

### New harness files this wake (mine, not the app's)

`verify_batch5.py`, `chunk_words5.py`, `chk_rearshock_after.py`, `list_chunks.py`, `seed_bare.py`,
`dump_cands.py`, `dump_cands2.py`, `_wake13_send.cmd`; reports `_verify_batch5.txt`,
`_chunk_words5.txt`, `_rearshock_after.txt`, `_chunk_inventory.txt`, `_seed_bare.txt`,
`_chunk_cands.txt`, `_chunk_cands2.txt`, `_cassette_edges.txt`.

### One honest caveat on the send

At 21:21 (three minutes after `clicked Send`) the relay and autopilot both still read
`running=False` at len≈119.1k, i.e. **the message is in the thread (marker 7 → 8, full 7603 chars
filled) but I did not observe the model start generating.** That may be start-up latency; it is
recorded rather than asserted. If the next wake finds no reply, the loop did not stall on delivery —
the instruction is posted. Also: `run_read.cmd 0` returned a stale page on my last attempt
(`_reply_tail.txt` still showed the batch-5 reply, `LEN=111534`), so the page dump is not proof of
state; `_relay.log` and `_autopilot.log` are.


## 2026-10-24 21:33 — batch 6 (cassette) accepted on evidence; three wording items + batch 7 (hub width) sent

### Why I was woken — and the first thing that was wrong

`_relay.log` 21:22:17 `FIRE (retry blocked reply (marker>=8))`. **That fire was not a reply.** The marker
went 7 → 8 at 21:19:08 because *my own* 7603-char instruction landed in the thread: every message I send
ends with `[[TASK]]`, so the relay's marker count rises by exactly one per send. At 21:23:04 the page still
read `Gemini 3.8 Flash / Running for 4m 59s`; my poller saw idle from 21:24:56. The real reply arrived
`Ran for 6m 43s`, page 119.2k → 122.8k.

**Rule for the next wake:** a FIRE within ~3 minutes of `clicked Send`, with no `Running for` line and only
the length of the message added, is my own message. `_autopilot.log`'s `state running=…` line is the
reliable signal; the relay marker is not. This has now happened twice and will happen after every send.

### What I verified myself — `_verify_batch6.txt` (`problems=0 literal=10/10`)

Against `kb.db` and the bundled corpus, never against the app's own test output: 5 nodes / 5 edges, tag
`phase5-cassette-6`, `subsystem: sys-drivetrain` on all five nodes, **10/10 quotes literal substrings** of
`chunks.text` **and** of the bundled `seed-evidence.json`, 0 unknown chunk ids, 0 citations outside
`{bike_repair_manual_chris_p0066_c00}`, 0 book/page/section mismatches, all ten graded A, no dangling
endpoint, no duplicate ids, no collision with seed or batches 1–5, every node and edge cited.

Label rule, computed not asserted: chunk length 1430, figure-label block starts at **1292** ("Parts of a
freewheel and a cassette … 1 2 3"), no `[VISUAL DATA]` marker, **no grade-A quote reaches into 1292+**. The
chunk's only digit runs are `1 2 3`, and `_verify_batch6.txt` §6b finds **no digit in the batch that is not
inside a cited quote**.

Ontology legal at both ends: `part_of` ×4 (three subcomponent → component, one component → subsystem) and
`constrains` ×1 (compatibility_rule → component). Anchoring **4/5** to
`comp-cassette` / `sys-drivetrain` (asked for ≥3, and at least one `part_of` hanging off `comp-cassette` —
two do). `seed_graph.json` and `seed-evidence.json` byte-identical to `_fixed/`; brakes `a384a15f`,
cockpit `13f28204`, drivetrain `62442afc` unchanged (asserted by hash in the gate, not eyeballed).
`_audit_app.txt` `problems=0`, `_scan_phase4.txt` `problems=0`, `_app_files` 33 → 34 with
`expansion-cassette.json`. Registry clean: imported, in `expansionRegistry`, subtitle derived.

Composition recomputed by me and identical to the reply: seed `[verified 26, candidate 1]` /
`[verified 9, needs_review 3]`; 7/3 and 7/3; 5/2 and 5/2; 5/2 and 5/2; 5/5 and 5/5; 4/4 and 4/4; 5/5 and
5/5; merged **65 nodes = 57 verified + 1 candidate + 7 needs_review**, **50 edges = 40 verified + 10
needs_review**. N=12.

Still **not** verified by me and recorded as such: the reply's "14/14 tests passing", `tsc --noEmit` and
"Built". That code lives only in AI Studio.

### The three quill resolutions: accepted — and checked in the file, not in the reply

`_check_wake14.txt`: `must` is gone from the claim (it is now the chunk's own sentence), `Standard` /
`Specification` / `requiring` / `Matching` / `Clearance` are gone from `std-quill-diameter-fit`, and the
alias `Quill Expander Bolt` is gone. The sentence it added — "The quill should be slightly smaller than the
inside of the column." — **is in the chunk at char 836**, so it is not an invention. Keeping that node typed
`standard` is right: `conforms_to` requires a standard target.

On its item (f) "none": accurate for name / description / claim / alias. I did also compare property
*names* — "Wheel Rotation", "Block Replacement", "Stem Retention", "Thread Lubrication", "Insertion
Location" strike words the chunks do not contain — but every one of those properties is already
`needs_review`, so no verified claim rests on them. Not flagged, and said so, so the AI is not pushed to
churn.

### What I did not accept — three wording items in batch 6 (fifth defect class, second variant)

`_chunk_words6.txt` does not catch these: every word exists in the chunk. What is wrong is the *strength*
and the *sentence*.

| entity | problem | chunk actually says |
|---|---|---|
| `comp-cassette-sprockets` + edge | "can wear and **will eventually need replacing**" | "The sprockets on both can also wear." The *internal mechanisms* are what wear out and need replacing |
| `comp-freewheel-block` | description drops the parenthesis: "Their internal mechanisms the block in a freewheel will eventually wear out…" | "Their internal mechanisms – the freehub body of a cassette and the block in a freewheel – will eventually wear out…" |
| `comp-cassette-lockring` + edge claim | description is a procedure, edge claim is a fragment | "…the lockring at the centre of the cassette" |

Item 1 is the rearshock defect in reverse: there a possibility was hardened into a guarantee ("prevents"),
here `can` became `will eventually`. Two resolutions allowed, no third: reword into the chunk's words, or
`needs_review` with the specific reason. No id, quote or page may move.

### Batch 7 chosen on content — and this is the last easy one

`cands7.py` / `_cands7.txt`: **15 of the 36 bundled chunks are still unused by any expansion**, and they are
nearly exhausted as *mechanical* evidence. Reading them (`_cands7_text.txt`) settles it:

- 6 are synthetic visual analyses, not manual prose: "This analysis is based solely on visual information",
  "(estimated)", "would be critical to check the FSA manual", "Let me know if you want more details".
  Growing verified A-grade knowledge out of those would be exactly the fabrication this project keeps
  catching.
- 4 are contents lists (`p0024_c00` 292 chars, `p0052_c00` 137 chars) or OCR'd tables.
- 5 are electrical / e-bike (BMS, controller voltage, Xiaomi error codes).

Chosen: **`big_blue_book_p0219_c01`** (p219, 1401 chars) — hub width / axle / dropout table. Real data, and
the natural anchors already exist: `comp-rear-hub` (4 edges) and `std-hub-width` (a seed standard whose only
edge is `comp-rear-hub --conforms_to--> std-hub-width`).

The hazard is written into the instruction rather than left for the AI to notice: the chunk **starts
mid-table**, its 100–135mm block has **no Front/Rear header**, the `**Rear:**` block (140–190mm) is
unambiguous, and the thru-axle `**Rear:**` header has **no rows under it**. So: no front/rear claim about the
first block, and no thru-axle rear row may appear. It also forbids the inference this table invites — no
"a 148mm hub fits a 142mm frame", no computed dish/spacing/offset.

### Sent (one instruction, `_msg14_batch7_hubfit.txt` → `_msg4.txt`)

`copied 21:33:10`, `msg4 bytes=7968`, **`filled=7913 value_len=7913` 21:33:40**, **`clicked Send` 21:33:42**
(`_send3_log.txt`). Three wording items plus batch 7: `src/data/expansion-hubfit.json`, tag
`phase5-hubfit-7`, **5 nodes / 5 edges**, subsystem `sys-wheels` on all five, citing **only**
`big_blue_book_p0219_c01`, node types limited to `compatibility_rule` / `standard` / `property` (no new
component may be invented), ≥3 of the 5 edges on `comp-rear-hub` / `sys-wheels`, every number in an
entity's own text required to sit inside its own quote, and the legal relation pairs spelled out from
`relation-ontology.json` (notably: `conforms_to` may not take a `standard` as source, but `has_property`
from `std-hub-width` is legal).

**Delivery confirmed independently** — `_relay.log` 21:34:05 `probe running=True marker=9 len=130764`: the
marker went 8 → 9 and the page grew by the message, and the app is generating. `_send3_log.txt` stopped at
`clicked Send` in my reads while the relay already showed the change, so **treat a file read of
`_send3_log.txt` as possibly cached and confirm delivery from `_relay.log`'s marker/len line instead.**

**Harness lesson (cost me two attempts):** `_wake14_send.cmd`'s detached `pythonw` + `start /b` form died
after logging `candidates=` and never filled the composer — the same form that worked at 21:17. What worked
was the **foreground** `python.exe studio_send3.py` inside `_wake14_send2.cmd`: the fill takes ~25 s for an
8k message and completes ~30 s after start. Do not conclude "stalled" before ~40 s, and do not close the
terminal while it runs — poll `_send3_log.txt` with a file read, never with another shell command.

### What the next wake must check

1. `_app_files` count **34 → 35** with `src__data__expansion-hubfit.json`.
2. Budget gate for batch 7: copy `verify_batch6.py` → `verify_batch7.py`; set `BATCH="phase5-hubfit-7"`,
   `ALLOWED={"big_blue_book_p0219_c01"}`, add `"hubfit-7"` to `FILES` and `"cassette-6"` to the previous-ids
   loop, `ANCHORS={"comp-rear-hub","sys-wheels","std-hub-width"}`, `SUBSYS="sys-wheels"`, `NN, NE = 5, 5`.
   The legend rule must be **replaced**, not reused: this chunk has no `[VISUAL DATA]` and no label block, so
   the crux is instead (a) every digit in a batch entity inside its own quote, and (b) no "front"/"rear"
   wording on any entity resting on the unlabelled 100–135mm block.
3. The three wording items resolved **in the file**; `_chunk_words6.py` will not catch them — read the texts.
4. Hashes to diff: cassette `328bfcf81aca68…` (will change if items 1–3 land — record the new one), cassette
   becomes the new expectation; others must stay brakes `a384a15f`, cockpit `13f28204`, drivetrain `62442afc`,
   rearshock `ace4858b`, quillstem `69526d23`, seed `63ac5126`, seed-evidence `d45b173e`.
5. Composition after a wording-only fix: still 65 nodes / 50 edges, cassette 5/5 verified; batch 7 should take
   it to **70 nodes / 55 edges**.
6. A FIRE within ~3 minutes of `clicked Send` is my own message (see the top of this section). The reply here
   should take ~6–7 minutes, as batch 6 did.

### Harness added this wake

`verify_batch6.py`, `chunk_words6.py`, `check_wake14.py`, `cands7.py`, `dump_cands7.py`, `_poll_idle.py`;
`.cmd` wrappers `_wake14_read / _verify / _chk / _dump / _send / _send2 / _diag / _poll`; reports
`_verify_batch6.txt`, `_chunk_words6.txt`, `_check_wake14.txt`, `_cands7.txt`, `_cands7_text.txt`, `_poll.txt`,
`_diag14.txt`.

## 2026-10-24 21:46 — batch 7 (hub width) accepted on evidence; three graph-quality defects found; correction sent, batch 8 refused

### Why I was woken

`_relay.log` 21:36:07 `FIRE (running->idle)`, marker 8 → 9, len 130.8k. **That fire was early, and I did
not act on it.** A page read at 21:37:05 showed `Running for 3m 26s` + `Working`; the fire came 2m22s after
delivery while the model was still generating (the "Running for" element flickers out of the DOM). I waited
(§1C), re-read at 21:38 (`Running for 4m 38s`), and the reply actually landed ~21:40. Third variant of the
same lesson: **a FIRE is a hint, the page is the fact** — and now also *`state running=True` in the autopilot
log is not reliable either*, because the autopilot read `running=False` at 21:35:41 while the model was mid-run.

### What I verified myself — my own gate, `_verify_batch7.txt` (`problems=0 literal=10/10`)

Written fresh for this batch (`verify_batch7.py`), because batch 6's figure-label rule does not apply to a
table. Batch 7: 5 nodes / 5 edges, tag `phase5-hubfit-7`, `sys-wheels` on all five, **10/10 quotes literal**
in `chunks.text` *and* in the bundled `seed-evidence.json`, all grade A, 0 unknown ids, 0 outside
`{big_blue_book_p0219_c01}`, 0 metadata mismatches, every entity cited, no dangling endpoint, no id collision
with seed or batches 1–6, ontology legal at both ends, **5/5 edges anchored** (`comp-rear-hub` ×2,
`sys-wheels` ×2, `std-hub-width` ×1).

The block rule replaced the legend rule and was computed, not asserted: chunk length 1401, unlabelled block
`0..452`, rear block `452..917`, thru-axle front `946..1388`, thru-axle `*   **Rear:**` header at **1388 with
nothing under it** (`tail = '*   **Rear:**'`). Result: 10/10 quotes are **exact whole table rows**; the four
entities resting only on the unlabelled block (`rule-hub-135mm`, `rule-hub-130mm` and their two edges)
carry **no front/rear word anywhere**; **no citation sits at or after 1388**. Every digit in every entity is
inside that entity's own quote, and — new check 8b — **every word** of every verified entity occurs in the
chunk (this is the machine form of the reply's "(f) none", and this time it was true).

Composition recomputed by me and identical to the reply: seed `[verified 26, candidate 1]` /
`[verified 9, needs_review 3]`; 7/3 and 7/3; 5/2 and 5/2; 5/2 and 5/2; 5/5 and 5/5; 4/4 and 4/4; 5/5 and 5/5;
5/5 and 5/5; merged **70 nodes = 62 verified + 1 candidate + 7 needs_review**, **55 edges = 45 verified + 10
needs_review**. N=12.

Hashes: `cockpit 13f28204`, `drivetrain 62442afc`, `rearshock ace4858b`, `quillstem 69526d23` unchanged; seed
`63ac5126`, seed-evidence `d45b173e` byte-identical to `_fixed/`; brakes identical to
`_fixed/expansion-brakes.batch1-ACCEPTED.json`. **cassette moved 328bfcf8 → 0a15c418** (the three wording
items) and is the new baseline. `_app_files` 34 → **35** with `src__data__expansion-hubfit.json`;
`audit_app.txt` `problems=0` (27/12, 20/20, 39/39, 36/36), `scan_phase4.txt` `problems=0`; `graph-loader.ts`
has the import, the getter, the registry entry and the `hubfit` subtitle key.

### The three batch-6 wording items — resolved, checked in the file (`_check_wake15.txt`, problems=0)

`comp-cassette-sprockets` node **and** edge claim are now "The sprockets on both can also wear." (the chunk's
own sentence; `will eventually` / `need replacing` gone). `comp-freewheel-block` has the parenthesis back
character for character. `comp-cassette-lockring` description is no longer the imperative
("The lockring at the centre of the cassette.") and the edge claim now reads "Lockring part of the cassette at
the centre." — clumsy English, but it is the chunk's words and it states the relation, so I accepted it rather
than churn the file. All ten quotes still literal.

### The three defects I did find — none of them an evidence defect

My gate cannot see these and the app's 14 tests did not either (`substance7.py` → `_substance7.txt`):

1. **Three node names are copied table rows, identical to their own description** — `rule-hub-135mm` (85
   chars), `rule-hub-130mm` (67), `std-rear-fat-tire-170mm` (60). Every other node in the merged map has a
   name (longest elsewhere 50 chars, sentence-style). A row as a label is unreadable on canvas/nav/export.
2. **`prop-hub-width-148mm` + `edge-std-hub-width-has-prop-148mm`** — its property key `measurement` occurs
   **nowhere else in the graph** (the other four nodes use `hub_width`), it duplicates the inline
   `hub_width = 148mm` on `std-rear-boost-148mm`, and it hangs one of thirteen table rows on the seed
   `std-hub-width`, whose own property says **"Guide, not exhaustive list"** (`needs_review` — my own earlier
   downgrade). Selective extraction, not a false quote.
3. Not a defect but recorded: `constrains` from a single table row (`rule-hub-135mm`) to the whole of
   `sys-wheels` is broad. I wrote that edge type into the instruction's legal list, so I am not asking for a
   change — it is my allowance, noted.

### Batch 8 refused, deliberately

The bundled corpus is out of mechanical evidence: of the 14 chunks no expansion cites, 6 are synthetic visual
analyses, 4 are contents lists / OCR'd tables, 4 are electrical / e-bike. Growing grade-A knowledge from those
is the exact fabrication this project keeps catching. I told the AI to stop after the correction and told it
the call was mine so it does not re-use an exhausted chunk to keep the loop fed.

### Sent (one instruction, `_msg15_batch7_fix.txt` → `_msg4.txt`)

`copied 21:44:44`, `msg4 bytes=4240` (18 lines, CRLF), **`filled=4222 value_len=4222` 21:45:02**,
**`clicked Send` 21:45:04`, `_send3_log.txt`**. Message integrity proved, not assumed (`_msg15_integrity.txt`):
file chars = **4222** = `filled`, 0 non-ASCII, `utf8_bytes - chars = 0`, `[[TASK]]` present exactly once and as
the last non-empty line — so `bytes=4240` was just the 18 CRLFs, not a truncation.

**Delivery confirmed independently from `_relay.log`, not from the send log:** 21:46:19
`probe running=True curtain=False marker=10 len=140741` — marker 9 → 10 (my own `[[TASK]]`) and the page grew
136.2k → 140.7k; `_autopilot.log` 21:46:17 `state running=True`. `_wake15_send.log` never got its `done rc=`
line while I polled it — do not treat a missing `done` as a failed send; `_send3_log.txt`'s
`filled=`/`clicked Send` pair plus the relay's marker/len is the proof.

The instruction: the three wording items are accepted (said so, item by item); batch 7 is accepted on
evidence; then the three defects above with **two resolutions each and no third** (item 1: proper name from
chunk words only, or `needs_review` with the reason; item 2: R1 delete `prop-hub-width-148mm` +
`edge-std-hub-width-has-prop-148mm` → 4/4 and merged 69/54, or R2 keep them with key `hub_width` and justify
the selective reading); plus **"DO NOT START BATCH 8"** with the exhaustion reason, the guardrail list
(seed byte-identical, batches 1–6 frozen, cassette at its new baseline, no literal counts, register nothing
new), and the reply format (a)–(e).

### Harness change I made myself

`_autopilot_queue.txt` still held **two stale Phase-4 instructions** (yesterday's "Continue the approved
Phase 4 work… **Do not start Phase 5**" and the Phase-4 self-review). The autopilot pops one instruction per
clean cycle, so a stale order could have been delivered into an approved Phase-5 batch-7 thread. Moved to
`_autopilot_queue.phase4-stale.txt` (`_queue_cleared.txt` 21:44:21, "1 file(s) moved"). **The queue is now
empty on purpose — a new instruction must be written to it, or the autopilot will only send corrections.**

### What the next wake must check

1. `_app_files` mtime; the reply's composition must be **69/54 with 61+1+7 / 44+10 if it took R1**, or 70/55
   with 62+1+7 / 45+10 if it took R2 and the key is `hub_width`. Recompute from the files (`verify_batch7.py`
   recomputes; after an R1 deletion expect `missing`/count problems there — that is the gate doing its job).
2. Item 1: the three names must be **shorter than their row**, **different from the description**, and every
   word must be in `big_blue_book_p0219_c01` — check 8b does exactly that. No new front/rear word on
   `rule-hub-135mm` / `rule-hub-130mm`.
3. Item 2: if `prop-hub-width-148mm` survives, `measurement` must be gone from the file and from the whole
   graph (grep every `src__data__*.json`).
4. Hashes: seed `63ac5126`, seed-evidence `d45b173e`, brakes = `_fixed/...ACCEPTED`; cockpit `13f28204`,
   drivetrain `62442afc`, rearshock `ace4858b`, quillstem `69526d23`; cassette baseline is now **0a15c418**.
5. Still not verifiable from here, and never reported as verified: "14/14 tests", `tsc`, "Built".
6. The fire that wakes you will be ~4 min after 21:45:04 and **may again be a false idle**, as this one was.
7. Do not let a "batch 8" proposal through on a synthetic-visual-analysis chunk. That is the next temptation.

### Harness added this wake

`verify_batch7.py` (new block rule + word-ledger), `check_wake15.py`, `substance7.py`, `dump_chunk7.py`,
`msg15_integrity.py`; `.cmd` wrappers `_wake15_read / _chunk / _verify / _audit2 / _subst / _loop /
_clearqueue / _send / _check / _wait`; reports `_verify_batch7.txt`, `_check_wake15.txt`, `_substance7.txt`,
`_chunk7.txt`, `_msg15_integrity.txt`, `_loop_health.txt`, `_appfiles_list.txt`.

**Harness lessons (mine, all cost time):** (a) never redirect a script's stdout onto the file it writes —
`audit_app.py > _audit_app.txt` gave `PermissionError` and both audits silently produced tracebacks instead of
results; redirect to `_audit_stdout.txt`. (b) `start /b` survives the `run_commands` tool call returning, but
dies as soon as I start **another** command — so a `timeout /t 80` waiter must be the only thing running.
(c) `_poll_idle.py` needs `saw_running=True` before it will ever dump, so it is useless when started after the
flicker; drive the re-read directly instead.



## 2026-10-24 22:12 — batch-7 label fix verified from the files; only one file moved; Phase 5 extraction is closed at 69/54

### Why I was woken

Relay `21:48:25 FIRE (retry blocked reply (marker>=10))`, `len=146515`. That reply was the
answer to my `_msg15_batch7_fix.txt`. It is complete: `Ran for 51s`, `Edited 1 file`
(`src/data/expansion-hubfit.json`), `Built`, `Checkpoint created` (`_reply_tail.txt`, read
twice — 21:49 and again 21:57 after the fix).

### Delivery of my instruction, proven

`_send3_log.txt`: `21:54:45 filled=2518 value_len=2518`, `21:54:49 clicked Send`, then
`len=148856 → 149167`. **2518 is exactly the char count `msg16_integrity.py` measured** on
`_msg16_batch7_label.txt` (2549 bytes, 31 CRLFs, 0 non-ASCII, `[[TASK]]` once and last), so
what the composer received is what I wrote. No `done rc=` line: my own next shell command
killed `studio_send3.py` after the click — the same artefact as 21:46, not a failed send.
The relay could not confirm the marker this time (`21:55:13` CDP `Connection closed`,
`21:56:16` `probe TIMEOUT`) because the sender held the CDP session; the send log plus the
page growing by 2.4 kB at the click is the evidence, and I say so rather than claim a
marker I did not see.

### The fix landed, character for character

`_app_files/src/data/expansion-hubfit.json`:

```
rule-hub-135mm  name(61) = "135mm Hub Width: MTB internal gear hubs, road disc brake hubs"
                desc(85) = "10mm Axle, 6-12 Speeds, 135mm Hub Width: MTB internal gear hubs, road disc brake hubs"
```

The dropped clause is back, nothing else on the node moved, and the label is still shorter
than its row and still different from its description.

**My own error, recorded:** I told the AI the replacement "is 66 characters". It is **61**
(the 85-char row minus the 24-char axle/speeds prefix). The string I dictated was right;
my arithmetic was not, and it was the only thing in that instruction that was wrong.

### Verified from the files, not from the reply (`verify_wake17.py` → `problems=0`)

1. **Composition, re-derived:** 69 nodes — 61 verified, 1 candidate, 7 needs_review; 54
   edges — 44 verified, 10 needs_review. Per file: seed 27/12, brake 10/10, cockpit 7/7,
   drivetrain 7/7, rearshock 5/5, quill 4/4, cassette 5/5, hubfit **4/4**.
2. **Only one file changed.** Every other file reproduces its previous CRLF-normalised
   hash exactly — seed `63ac5126`, brakes `a384a15f`, cockpit `13f28204`, drivetrain
   `62442afc`, rearshock `ace4858b`, quillstem `69526d23`, cassette `0a15c418`. hubfit
   `3cd50ecb → 2e86bcd4`. Seed and seed-evidence still identical to `_fixed`
   (`63ac5126` / `d45b173e`). Batches 1–6 are provably untouched, not merely unmentioned.
3. **All four labels** are shorter than their row, differ from their own description, use
   only words inside `big_blue_book_p0219_c01`, and — the check that caught this defect —
   drop **no** documented application clause: `std-rear-boost-148mm` 1/1, `170mm` 1/1,
   `135mm` now **2/2**, `130mm` 2/2.
4. **8/8 citations** still literal substrings of `kb.db`'s chunk (1401 chars).
5. **R1 still in force:** no `prop-hub-width-148mm`, no `edge-std-hub-width-has-prop-148mm`,
   and no property *key* named `measurement` anywhere. (The bare word occurs twice inside
   frozen seed prose — a FIGURE caption and an alias — which is not a key and may never
   change. My earlier wording "occurs nowhere else in the graph" was imprecise; corrected
   here, and `verify_wake16.py`'s substring test was replaced with a key-space test.)
6. `audit_app.py` `problems=0`, `scan_phase4.py` `problems=0` against the restored snapshot.
7. **Not verified, and not reported as verified:** "14/14 tests", `> tsc --noEmit`,
   "Build succeeded - the applet is compiled". The checkpoint and the edit are visible; the
   test and typecheck output is the app's own word.



### The defect class is now closed — and I can name it

Three instances, one pattern: **the entity says less than the evidence, in a way that reads
as if it said everything.** (a) a `property` hung on `std-hub-width` with a key used nowhere
else; (b) `rule-hub-135mm` labelled with half its row; (c) earlier, three labels that were
the whole row. Fixed by the no-dropped-clause rule in `verify_wake17.py`, which I did not
have when I wrote the instruction — that is why the AI could comply with the letter of my
instruction and still narrow the claim.

### The snapshot was destroyed and rebuilt (harness bug, now fixed)

At 21:58 `run_getall.cmd` reported `models=1`: the checkpoint had reset the Code panel and
Monaco held only `metadata.json`. `studio_getall.py` **purged `_app_files` before checking it
had anything to write**, so 35 verified files became 1. Recovered, and the bug is fixed:

- `studio_getall.py` now treats `/src/data/seed_graph.json` being open as the only proof of
  a whole dump; a partial dump writes what it has and **deletes nothing**. Tested live:
  `PARTIAL dump (8 models, seed graph not open) - nothing deleted`, 35 files survived.
- **`studio_origin_dump.py` (new)** rebuilds the snapshot from the app's own origin: opens a
  throwaway tab on the Vite dev URL inside the existing Chrome context (so the auth *cookie*
  applies) and fetches each path, `?raw` for non-JSON. 35/35 restored. A plain HTTP GET with
  only `?__aistudio_auth_token=` returns a **"Cookie check"** page — the token is not the
  credential, the cookie is, which is why the frame/context route is the one that works.
- Files arrive **LF** while the editor model is **CRLF**, so every hash comparison in
  `verify_wake17.py` is on CRLF-normalised bytes; that is what makes "unchanged" provable
  across the two transports.
- Also new: `studio_frames.py`, `studio_frame_file.py`, `studio_frame_dump.py` (all read the
  preview iframe; they fail cleanly with `NO_APP_FRAME` when the preview is torn down).

### Where the map stands — Phase 5 extraction closed, deliberately

69 nodes / 54 edges, 61 verified nodes and 44 verified edges, seeded by a 27/12/59 graph
that is still byte-identical. The 7 needs_review nodes and 10 needs_review edges are the
honest known gaps: `unk-freehub-body-length` (candidate), `std-brake-centerlock-torque`,
`comp-brake-hose`, `std-brake-thru-axle`, `std-steerer-dia-unconfirmed`,
`rule-stem-clamp-torque`, `std-chain-pitch-unconfirmed`, `std-xdr-bearing-dim-unconfirmed`,
plus their edges and the seed's three. They stay unverified because `kb.db` does not settle
them — that is the correct state, not a backlog.

**No batch 8.** As of 21:46 (not re-derived this wake) 14 bundled chunks are cited by no
expansion, and none is mechanical manual prose: 6 are synthetic visual analyses that say so
in their own text, 4 are contents lists or OCR'd tables, 4 are electrical/e-bike. Growing
verified A-grade knowledge out of those would be the fabrication this project keeps catching.

### What the next wake must do

**Nothing to send.** The reply that woke me is fully processed. If the relay fires again for
it, do not re-send: confirm the hashes above and stop with `DONE`.

- `_msg4.txt` now holds **`_msg16_batch7_label.txt` (delivered 21:54)** — re-running
  `run_send3.cmd` without rewriting it re-sends a spent order. Copy kept in `_msg4_prev.txt`
  and `_send3_log.wake16.txt`.
- `run_getall.cmd` is safe again, but **on a Code panel that has no data files it returns a
  partial dump**. When in doubt use `studio_origin_dump.py`, then re-run the audits.
- Hashes to carry forward: seed `63ac5126`, seed-evidence `d45b173e`, brakes `a384a15f`,
  cockpit `13f28204`, drivetrain `62442afc`, rearshock `ace4858b`, quillstem `69526d23`,
  cassette `0a15c418`, **hubfit `2e86bcd4` (new baseline)** — all CRLF-normalised.
- The one thing still unverified anywhere in this project: the app's own test and build

## 2026-10-24 22:37 — connector pass opened (`phase6-connectors-1`); gate written before the instruction; batch 1 sent

### What the measurement said (this is why the pass exists)

Asked how the map compares to the corpus, I measured instead of asserting (`_verify_connectors.txt` §A–B):

| | |
|---|---|
| kb.db | **3,921 chunks / 4.65 M chars / 8 books** (Big Blue Book 2,712 + Chris 595 = the 3,307 mechanical chunks) |
| map | 69 nodes / 54 edges / **179 citations** |
| corpus touched | **36 distinct chunks = 0.92%** |
| connectivity | **16 components**, largest **16 (23%)**, 4 isolated nodes |
| density | avg degree **1.57**, density **0.023** |
| edges | `part_of` **21** (39%), `conforms_to` 10, `constrains` 5, `interfaces_with` 4, `incompatible_with` **3**, `fits_into` **1** |
| nodes | subcomponent 24, component 15, standard 13, subsystem 4, rule 4, property 3, **procedure 2** |
| catalog | 6,337 products / 75 categories vs **15 component types**, no instance layer |

### Three findings that changed the plan

1. **Four of the sixteen islands are the subsystem nodes themselves.** Every node carries `subsystem: sys-…`, but that is metadata, not an edge, so members float free of their own subsystem. Part of the fragmentation is a modelling artifact.
2. **`graph.schema.json` allows 39 edge types; `relation-ontology.json` defines 15.** The ceiling was never the app — it is the ontology. `causes`, `may_cause`, `replaced_by`, `transmits_torque_to`, `diagnosed_by`, `tightened_to`, `requires_adapter` are all already legal in the schema. That is the unlock for the procedure/symptom work later.
3. **A blanket subsystem pass would poison the map.** 65 of 69 nodes carry the field; drawing them all adds 65 derived edges against 68 evidenced ones — about half the map would be inference dressed as knowledge. I narrowed the owner's approval to **minimal anchoring**: only edges that actually merge a fragment (**4 derived edges**, not 65).

### Approved scope (owner decision, 22:30)

Mechanical connectors + minimal subsystem anchoring + **one** evidenced anchor node `comp-fork`. Projected **16 → 1 component, largest 69/69**, 54 → 72 edges, 4 derived (6%).

### Gate written BEFORE the instruction: `verify_connectors.py`

It declares the six approved edges itself, and checks: the eight frozen files by CRLF-normalised hash (seed byte-identical to `_fixed`); the connectors file exists with tag `phase6-connectors-1` and **zero nodes**; the edge set is exactly the approved one (no extras, no omissions); every quote is a **literal substring** of the declared `kb.db` chunk *and* contains the phrase I chose; ontology legality on both ends; no duplicate or reverse-duplicate edge; no dangling endpoint; `graph-loader.ts` has the import, the `getExpansionConnectors` getter and the registry entry; and a **measured** connectivity delta.

First run, before anything was sent: `problems=1` — only "connectors file not present", with the baseline reproduced exactly (`components=16 largest=16 (23%) avg_deg=1.57`, sizes `[16,7,7,6,5,5,5,4,3,3,2,2,1,1,1,1]`). The gate is known-good against the current state.

  output. Nobody has watched `14/14` run.


### Evidence: chosen by me, not delegated

The six joins are mechanically obvious, which is exactly when a model invents a quote. So I searched `kb.db` and fixed the chunk **and** the quote text in the instruction; the AI may only copy them:

| edge | relation | chunk | quote |
|---|---|---|---|
| `comp-freewheel → comp-rear-hub` | `mounted_on` | `big_blue_book_p0193_c00` p193 | "FIGURE 3.3: Rear threaded hub with thread-on freewheel" |
| `comp-rotor-6bolt → comp-rear-hub` | `mounted_on` | `big_blue_book_p0183_c02` p183 | "The rotor is secured to the hub with at least six, likely Torx-head (T25) bolts." |
| `comp-brake-pad → comp-rotor-6bolt` | `interfaces_with` | `big_blue_book_p0668_c01` p668 | "Ensure proper brake pad alignment with the rotor to prevent rubbing." |
| `comp-stem-quill → comp-steerer` | `mounted_on` | `bike_repair_manual_chris_p0092_c00` p92 | "or quill, that fits inside the steerer." |
| `comp-rear-derailleur → comp-cassette-sprockets` | `interfaces_with` | `bike_repair_manual_chris_p0007_c03` p7 | "Rotate B-screw clockwise or counter-clockwise to adjust derailleur body angle relative to the cassette." |
| `rule-hub-135mm → comp-rear-hub` | `constrains` | `big_blue_book_p0219_c01` p219 | "10mm Axle, 6-12 Speeds, 135mm Hub Width: MTB internal gear hubs, road disc brake hubs" |

Feasibility is not in doubt: `freewheel+hub` 73 chunks, `rotor+hub` 124, `stem+steerer` 109, `derailleur+cassette` 232, `headset+steerer` 79, `fork+steerer` 75, `pad+rotor` 115.

### Sent

`_msg17_connectors1.txt` → `_msg4.txt` (4,033 B). `_msg17_integrity.txt`: **3,967 chars**, 0 non-ASCII, `[[TASK]]` once and last, 6 edge ids, 6 chunk refs. `_send3_log.txt`: **`filled=3967 value_len=3967` 22:36:07**, **`clicked Send` 22:36:08**, page `34,101 → 37,809`. `filled` equals the measured char count exactly, so what the composer received is what I wrote.

### Harness note that will mislead the next wake

The page text is now much smaller than during the hubfit work (149 k → 34 k) and the relay reports **marker=3** where it reported 10 an hour ago: AI Studio virtualises old messages out of the DOM, so **marker count is not comparable across wakes** and `len` only means "this view". Do not read marker=3 as "the conversation was lost" — my label-fix text is still in the page (`_studio_read.txt` lines 479–545) and it is the same `APP_ID` thread.

### What the next wake must do

1. `cmd /c run_getall.cmd` then **`py -3 verify_connectors.py`**. Expect `problems=0` and `DELTA components 16 -> 10, largest 16 -> 39`.
2. Reject the batch if: any edge is unapproved or missing, any quote is not literal, any node appears in a batch that must add none, or `graph-loader.ts` lacks the getter.
3. If it passed, batch 2 is the next four edges (headset/steerer, dot-fluid, brake-fluid rule, xiaomi/motor) — already in the plan; do not send it in the same wake as the acceptance.
4. `_msg4.txt` now holds the connectors instruction (delivered 22:36). Copy kept: `_msg4_wake16.txt`.
> **SUPERSEDED at 22:45 — see the next section.** Points 1 and 3 above are void: the correct
> expectation is `problems=0` with `components 13, largest 24` (not `16 -> 10 / 39`), and the six-edge
> set they describe was rejected because five of its chunks are not in the bundled 36. Point 2 still
> stands. Point 4's copy is `_msg4_wake17.txt`; `_msg4.txt` now holds the wake-18 correction.



## 2026-10-24 22:45 — connectors-1 REJECTED on the bundle rule; corrected set (3 edges) sent

### Why I was woken — a false relay fire

`_relay.log` 22:37:52 `FIRE (running->idle)` at `len=37850`, up only 15 chars from the previous
probe. That was **not** a finished reply: `_studio_read.txt` still ended with my own instruction
plus `Running for 3m 6s` / `Working` / `Editing files` and green ticks on
`src/data/expansion-connectors.json` and `src/services/graph-loader.ts`. The relay read the
"Running for Ns" counter ticking as an idle page. I waited (case C), re-read at **22:40:17**:
45,459 chars, `Running for` count 0 — then worked. *Relay defect: `running` can drop for one probe
mid-generation; one `running=False` is not proof a reply is complete. Confirm with two probes.*

### What the AI actually delivered (verified, not assumed)

`expansion-connectors.json`: `schema_version 1.0.0`, `batch phase6-connectors-1`, **0 nodes, 6 edges**.
All six claims are **character-identical** to the ones I dictated (string equality, not similarity).
Every evidence object carries `chunk_id, book, page, quote, evidence_grade "A", linked_to_chunk true,
confidence 1.0` — no missing fields. Ontology legal at both ends for all six (`mounted_on`,
`interfaces_with`, `constrains`). No dangling endpoints, no duplicate edges, no node added, no status
changed. `graph-loader.ts` has the import, `getExpansionConnectors` and the `connectors: 'Connectors'`
registry entry. Gate A: seed + batches 1–7 **unchanged byte for byte**; `seed_graph.json` and
`seed-evidence.json` identical to `_fixed/`. Good work, all of it.

### The defect — and it is mine, not the test's

The app's own suite came back **`Overall passed: false (13/14)`**:

> Test P failed … Edge edge-conn-freewheel-on-rearhub cites chunk `big_blue_book_p0193_c00` which
> does not exist in seedEvidence.chunks (and the same for rotor, pad, quill, derailleur)

I checked it three ways instead of believing either side:

| check | result |
|---|---|
| `seed-evidence.json` chunk keys | exactly **36**, `chunk_count 36` |
| chunks the seed cites | **36 distinct, all inside the bundle** |
| chunks each expansion cites, outside the bundle | batches 1–7: **0 each**. connectors-1: **5 of 6** |

The five are `p0193_c00`, `p0183_c02`, `p0668_c01`, `chris_p0092_c00`, `chris_p0007_c03`. They are
real chunks with real text in `kb.db` and every quote is a literal substring there — **nothing was
fabricated** — but they are not in the bundled corpus, so the app cannot render them and Test P is
correct. Eight batches of precedent say expansions cite the 36; in wake 17 I searched `kb.db`
(232 candidate chunks) and never checked the bundle. My error. The three freewheel/pad/derailleur
joins are not wrong mechanics, they were simply not *bundle-evidenced*.



### What is left that the bundle can vouch for

Searched all 36 chunks for wording that states each join. Only two survive, and I dictated both
quotes (each verified literal in the bundle **and** in `kb.db`, `bundle text == kb.db text`,
ASCII only, page numbers agreeing):

| edge | chunk | quote |
|---|---|---|
| `edge-conn-rotor-on-rearhub` (kept, re-pointed) | `big_blue_book_p0679_c00` p679 | `The common system uses six bolts on a flange built into the hub shell.` |
| `edge-conn-quill-in-steerer` (kept, re-pointed) | `big_blue_book_p0820_c00` p820 | `the vertical post that inserts inside of a` + **line break** + `threaded steering column.` |
| `edge-conn-hub135-constrains-rearhub` (unchanged) | `big_blue_book_p0219_c01` p219 | row already used by hubfit |

Dropped, because no bundled chunk states the join and I will not re-cite from outside the bundle:
`edge-conn-freewheel-on-rearhub` (p0066_c00 states the freewheel's *function*, not its mounting),
`edge-conn-pad-against-rotor` (p0112_c03 inspects pad thickness and rotor trueness separately),
`edge-conn-derailleur-over-cassette` (p0585_c00 is chainline, p0637_c00 is installation only).

### My gate now catches this class of defect

`verify_connectors.py` rewritten: **E2** checks every cited chunk is a key of `seed-evidence.json`
**and** that the quote is literal in the *bundled* text **and** that the bundled text is
byte-identical to `kb.db` (anti-circularity); **G2** asserts the pre-computed connectivity
`(components, largest) == (13, 24)`. Known-bad run against the uncorrected file:
**`problems=13`** — the 3 unapproved edges, the 2 wrong chunk ids, the 5 non-bundled citations and
the `(10, 39)` mismatch. The gate is live, not decorative.

### Sent (one instruction, `_msg18_connectors_fix.txt` → `_msg4.txt`, detached `pythonw`)

3,596 chars, ASCII only, one `[[TASK]]`, file ends on it. `msg18_integrity.py` proved the two
dictated quotes are byte-exact (real line break present, space-joined variant absent) and that the
four forbidden chunk ids appear 0 times, so they cannot be copied back.
`copied 22:50:21`, **`filled=3596 value_len=3596`**, **`clicked Send 22:50:38`**, page 45,278 → 48,898.
Numbers stated in the message, to be checked next wake: 8 files / 42 nodes / 45 edges; merged
69 nodes (61/1/7), **57 edges (47 verified, 10 needs_review)**; connectivity 13 groups, largest 24;
**14/14**.

*Process note:* my first send attempt at 22:49 used console `python.exe` and my next `run_commands`
killed it mid-fill (log stopped at `candidates=`). Use `start "" /b pythonw.exe` — `_wake18_send.cmd`
now does, which is why `_wake11_send.cmd` was written that way.

### Loop health — one real fault

Relay: probing every minute, healthy. Autopilot: **alive but not grading** — `SKIP AUDIT:
authoritative data file not readable` on every cycle since **22:02** (ten in a row). Cause found and
narrowed: `autopilot.py snapshot()` reads Monaco models that happen to be **open**; after the ~22:02
tab reload only **2 of 38** were open (`services__constraint-engine.ts`, `types__graph.ts` — the two
flat-name files still sitting in `_app_files`), so `seed_graph.json` always reads "missing" and the
cycle aborts before `run_audit()`. `studio_getall.py` gets all 38 because it opens them. Fix next
wake (point the snapshot at the getall path), **not** now — the app is mid-generation. Until then
the supervisor's own audit is the only grading, and it runs every wake.

### Open decision, recorded not taken

The three dropped joins are real and their chunks sit in `kb.db`; drawing them means growing
`seed-evidence.json` from 36 to 41 chunks. That changes a frozen artifact and what the app bundles
offline, so it stays with the owner. Not done, not smuggled in.

### What the next wake must check

1. Two relay probes after the send, not one — a single `running=False` lies mid-generation.
2. `_verify_connectors.txt` after `run_getall.cmd`: `problems=0`, `E2` all `in_bundle=True
   literal_in_bundle=True bundle==kb.db=True`, `G` = `nodes=69 edges=57 components=13 largest=24`.
3. The file: exactly 3 edges, the two re-pointed quotes byte-identical to the strings above
   (including the line break after "of a"), the three dropped ids absent, `nodes: []`.
4. The reply's own test output must read **14/14**. If it still shows 13/14, the AI changed the
   test or re-cited an outside chunk — reject and read the failure line.
5. Then, and only then, the next batch of connectors drawn **bundle-first**: list the 36 chunk ids
   first, choose the joins from them, and never look at `kb.db` for evidence again.

### Verified on arrival (22:56, after the send — no second instruction)

The corrected reply landed while I was writing this section (`len 48,898 -> 56,800`, "Finished",
`Overall passed: true (14/14)`). I did not take its word for it:

- **My gate** (`_verify_connectors.txt`): `problems=0`. 3 edges, all three chunks
  `in_bundle=True literal_in_bundle=True bundle==kb.db=True`, every quote byte-identical to the text
  I dictated, ontology legal at both ends, no dangling, no duplicates.
- **Connectivity**: `nodes=69 edges=57 components=13 largest=24` — matches the `(13, 24)` I
  computed and asserted *before* sending. Nothing was reverse-fitted to the result.
- **Frozen material**: seed + batches 1–7 unchanged byte for byte; `seed_graph.json` and
  `seed-evidence.json` identical to `_fixed/`; `audit_app.py` still `27 nodes / 12 edges`,
  `20/20` edge citations, `39/39` node citations, `36/36` bundled chunks byte-identical to `kb.db`.
- **The app's own suite** now reads `Test P: Seed Immutability & Expansion Merge PASS`, 8 files,
  42 nodes, 45 edges, 87 citations, `phase6-connectors-1 (nodes [], edges [verified: 3])`, merged
  61/1/7 nodes and 47/10 edges, `tsc --noEmit` clean, "Build succeeded".

Acceptance of connectors-1 therefore rests on my own measurement agreeing with the app's, not on
the app's alone. **Phase 6 as originally scoped (6 joins) is closed at 3: the map is 69 nodes /
57 edges, 13 groups, largest 24.** I sent nothing further — one instruction per wake. The next
wake sends nothing either until it has re-run the gate and decided what, if anything, to add.

## 2026-10-24 23:04 — wake accepted connectors-1 a second time, then opened batch 2 (bundle-first)

### Why I was woken — a duplicate fire for a reply already closed

`_relay.log` 22:56:37 `FIRE (retry blocked reply (marker>=5))`, then `FIRED /task`. That was the
previous supervisor session (`1792870676850_h6n21`) still holding the probe, so the relay retried
a marker it had already consumed. The reply it fired on is the one wake 18 verified at 22:56. **I
still re-ran everything rather than inherit a verdict.**

### Re-verified from scratch (nothing taken on trust)

| check | result |
|---|---|
| `run_read.cmd 0` + `tail_reply.py` | `LEN=56800`, ends `Finished` — no new content since 22:56 |
| `run_getall.cmd` | **38** files |
| `audit_app.py` | `problems=0`; 27 nodes / 12 edges; **20/20** edge + **39/39** node citations; 36/36 bundled chunks byte-identical to `kb.db` |
| `scan_phase4.py` | `problems=0`, 3 notes (same three as before) |
| `verify_connectors.py` | `problems=0`; `E2` all three `in_bundle=True literal_in_bundle=True bundle==kb.db=True`; `G` = `nodes=69 edges=57 components=13 largest=24`, matching the `(13, 24)` asserted before that send |

Then a **fourth, independent** check (`check_wake19.py`) written from scratch, importing nothing from
the gate: it reads `_app_files\src__data__expansion-connectors.json`, opens `kb.db` read-only, and
re-derives each citation. All three: `db=True lit_db=True bundle=True lit_bundle=True same=True`.
The five rejected wake-17 ids appear **0** times in the file.

*Process note against myself:* the first run of that checker printed `FAIL` on all three. The bug was
mine — it selected the integer `id` column instead of `chunk_id`. Corrected, it passed. Had I only
run my own script and stopped, I would have "found" a defect that does not exist; had I only run the
gate, I would have had one opinion. Two independent implementations disagreeing is what caught it.

**Nothing was wrong with the reply. connectors-1 stands at 3 edges: 69 nodes / 57 edges, 13 groups, largest 24.**

### Decision: batch 2, and the method is inverted on purpose

Wake 17 failed because it searched `kb.db` (232 candidates) and only afterwards discovered the app
can render just the **36 bundled chunks**. Batch 2 is therefore **bundle-first**: I dumped all 36
bundled chunks (`dump_bundle36.py` -> `_w19_bundle36.txt`), read the full text of every candidate,
and then chose joins from what those chunks actually say. No `kb.db`-only evidence can enter.

Islands before batch 2 (`_w19_islands.txt`, measured, not assumed):

`24, 12, 7, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1` — the 12 is the whole cockpit/headset cluster, the 7 is
brakes, the 6 is the rear shock, the 5 is derailleur/chainline.

### The 4 approved edges — each one merges a fragment, each evidenced inside the bundle

| edge | relation | chunk | quote (literal in bundle **and** `kb.db`, `bundle==kb.db`) | merges |
|---|---|---|---|---|
| `comp-headset-threadless -> comp-headset` | `part_of` | `big_blue_book_p0861_c00` p861 | `Threadless headsets, including EC, ZS, and IS types, operate on the same` | 4 into 12 |
| `comp-ebike-motor -> comp-rear-hub` | `fits_into` | `Ai_generated_ebike_motor_p0003_c00` p3 | `Hub Motor An electric motor built into the hub of a wheel, directly driving the` | 2 into 24 |
| `ec-xiaomi-table -> comp-ebike-motor` | `indicates` | `xiaomi_ebike_escooter_p0001_c02` p1 | `5. The following error codes suggest issues with the controller or motor:` | 1 into that |
| `rule-brake-fluid-contamination -> comp-caliper-hydraulic` | `constrains` | `big_blue_book_p0728_c04` p728 | `DOT FLUID, CAUSTIC MATERIAL. USE PROPER GLOVES.` | 1 into 7 |

Ontology checked by hand against `relation-ontology.json` before writing the gate: `part_of`
(component->component), `fits_into` (component->component), `indicates` (error_code->component) and
`constrains` (safety_constraint->component) are all legal at both ends. `indicates` and `constrains`
had **never been used in this map** — that is the unlock the wake-17 analysis predicted.

### Gate written BEFORE the instruction: `verify_connectors2.py`

It declares the 7-edge end state (the 3 accepted + these 4) and checks: the eight frozen files by
CRLF-normalised hash, `seed_graph.json`/`seed-evidence.json` identical to `_fixed`; top-level batch
tag `phase6-connectors-2` **and** each edge's own `batch` label; zero nodes; no extra/missing edge;
dangling, duplicate and symmetric-both-ways; every quote equal to the approved text **and** literal
in `kb.db` **and** ASCII **and** literal in the *bundled* text **and** `bundle==kb.db`; ontology
legality both ends; loader registry; measured connectivity against a declared `(9, 27)`; plus a
simulation section that computes the expected end state from the declarations alone.

Known-bad run against the current file: **`problems=6`** — batch tag still `connectors-1`, the 4
edges missing, connectivity `(13, 24)`. `I. SIMULATION` printed `edges=61 components=9 largest=27`
and agreed with the declared `(9, 27)`. The gate is live, not decorative.

Pre-send quote proof (`precheck_batch8.py` -> `_w19_precheck.txt`): all four `BAD: 0`, with page,
section title and 40 characters of context printed around each hit.

### Sent (one instruction, detached)

`_msg19_connectors2.txt` -> `_msg4.txt`. `msg19_integrity.py` (`_w19_msgcheck.txt`): **3,630 chars**,
0 non-ASCII, one `[[TASK]]` and it is the last line, all four chunk ids exactly once each, all four
quotes re-extracted *from the message text* and confirmed literal in the bundle, no `claim=` wraps a
line. `_wake19_send.cmd` (detached `pythonw`): `msg4 bytes=3630`; `filled=3570 value_len=3570`;
**`clicked Send 23:04:56`**; page `56,645 -> 59,967`. `filled` is 60 short of `chars` because the
composer normalises 60 `CRLF` pairs to `LF` — the same offset as every earlier send, not truncation.
Relay probe `23:05:16`: `running=True marker=6 len=60021` — the order took.

### What the next wake must check (in this order)

1. **Two** probes with `running=False`, not one (wake 18 was woken by a single idle reading).
2. `_verify_connectors2.txt` after `run_getall.cmd`: `problems=0`; `E2` seven lines all
   `in_bundle=True literal_in_bundle=True bundle==kb.db=True`; `F` four `ok` for the new relations;
   `G` = `nodes=69 edges=61 components=9 largest=27`.
3. The file: exactly **7** edges, top-level `batch` = `phase6-connectors-2`, the 3 old edges still
   carrying `batch: phase6-connectors-1` with byte-identical quotes, still `nodes: []`.
4. `audit_app.py` still `27 nodes / 12 edges`, 20/20, 39/39, 36/36 — the seed must not drift.
5. The reply's own output must read **14/14**. A `Test P` failure naming any of the four new chunk
   ids means a quote was retyped: reject, read the failing line, and do not "fix" the test.
6. Islands left after this batch, for batch 3 (`_w19_islands.txt`): **12** cockpit/headset (the big
   one), **7** brakes, **6** rear shock, **5** derailleur/chainline, **4** threadless-headset and
   `sys-cockpit`, **3** freewheel/`sys-drivetrain`, **2** DOT/mineral fluid, plus singletons
   `comp-bb-threaded`, `comp-fork-seals`. Chainline is the cheapest next merge:
   `big_blue_book_p0585_c00` reads "Chainline is the relation of the front and rear sprockets to the
   center plane" (ASCII-safe substring, does not cross a line break).

### State carried forward

- `_msg4.txt` now holds **`_msg19_connectors2.txt` (delivered 23:04:56)** — re-running
  `run_send3.cmd` without rewriting it re-sends a spent order. Copies kept: `_msg4_wake18_pre.txt`,
  `_send3_log.wake19_pre.txt`, plus `_send3_log.wake19_*`.
- Frozen hashes unchanged and still authoritative: seed `63ac5126`, brakes `a384a15f`, cockpit
  `13f28204`, drivetrain `62442afc`, rearshock `ace4858b`, quillstem `69526d23`, cassette `0a15c418`,
  hubfit `2e86bcd4` (CRLF-normalised).
- New tools this wake, all read-only: `check_wake19.py`, `dump_bundle36.py`, `plan_batch8.py`,
  `dump_batch2_texts.py`, `precheck_batch8.py`, `msg19_integrity.py`, `verify_connectors2.py`.
- `_NEEDS_APPROVAL.txt` does not exist; nothing is waiting on a human.
## 2026-10-24 23:15 — batch 2 accepted on three independent checks; batch 3 (2 edges) sent

### Why I was woken

Relay `23:09:01 FIRE (retry blocked reply (marker>=6))` after the reply finished at 23:06:59:
`len 60,095 -> 71,224`, and **three** consecutive probes (23:06:59, 23:08:00, 23:09:01) agreed on
`running=False` — the two-probe rule from the wake-18 lesson satisfied.

### Harness defect caught before it could matter

The first read cycle reported nothing and `_reply_tail.txt` was still the **stale** 22:57 file
(`LEN=56800`, the 3-edge reply). `_studio_read.txt` was fresh (23:09:47, 72,974 B) while the relay
measured page `len=71224`, so the *read* had worked and only `tail_reply.py` had not run — it was
chained after `run_read.cmd` in one line and got skipped. Re-ran it alone: `LEN=71379`, page
`Finished`. **Rule for next time: run `tail_reply.py` as its own command and check its mtime, not
the exit code of a pipeline.**

### Batch 2 verified three ways and accepted

| check | result |
|---|---|
| `verify_connectors2.py` | `problems=0`. C: `batch=phase6-connectors-2 nodes=0 edges=7`, expected 7 found 7. E: 7 `ok`. E2: 7 lines, every one `in_bundle=True literal_in_bundle=True bundle==kb.db=True`. F: 7 `ok`, including the four first-time relations (`part_of`, `fits_into`, `indicates`, `constrains`). G: `nodes=69 edges=61 components=9 largest=27` — **matches the `(9, 27)` I declared before sending** |
| `audit_app.py` / `scan_phase4.py` | `problems=0` both; seed still 27/12, 20/20, 39/39, 36/36 |
| `check_wake19.py` (independent implementation) | `BAD EVIDENCE: 0` across all 7 edges |
| `check_wake20_claims.py` (new) | 7/7 `OK`; each edge carries the right per-edge `batch`; the 4 new claims are **byte-exact** to the text I dictated; `edges not in the approved 7: none`; `approved edges missing: none`; `BAD: 0` |

What the app itself printed, and every figure had been stated in my message **before** the work:
8 expansion files / 42 nodes / 49 edges; merged 69 nodes / 61 edges (51 verified, 10 needs_review);
9 components, largest 27; `Test P ... phase6-connectors-2 (nodes [], edges [verified: 7])`;
91 citations; `Overall passed: true (14/14)`; `tsc` clean; `Build succeeded`.
Agreement on all seven numbers is corroboration, not proof — the proof is my own gate reading the file.

*Second self-inflicted error of the session:* `check_wake20_claims.py` failed with `FileNotFoundError`
because the path I wrote as `src__data__expansion-connectors.json` was stored with a **collapsed
double underscore** (`src__data\expansion-...`). Rebuilt the name from parts
(`"src" + "__" + "data" + "__" + ...`) and it read fine. Both of this session's failures have been my
own tooling; neither was an app defect, and neither was reported as one.

### Batch 3 scoped down on purpose — two joins, and two rejections on the record

Remaining islands after batch 2: `sys-cockpit 16, sys-brakes 8, comp-rear-shock 6, prop-chainline 5,
sys-drivetrain 3, prop-fluid-dot 2, comp-bb-threaded 1, comp-fork-seals 1`.

**Approved (bundle-evidenced):**

| edge | relation | chunk | quote | merges |
|---|---|---|---|---|
| `comp-cassette -> prop-chainline` | `has_property` | `big_blue_book_p0585_c00` p585 | `Chainline is the relation of the front and rear sprockets to the center plane` | 5-island into main |
| `comp-freewheel -> comp-cassette` | `interfaces_with` | `bike_repair_manual_chris_p0066_c00` p66 | `The cassette and freewheel allow the rear` + line break + `wheel to rotate while the pedals remain` | 3-island into main |

**Rejected, and written into the gate's docstring so they cannot creep in later:**

- `comp-brake-pad -> comp-rotor-6bolt` — `bike_repair_manual_chris_p0112_c03` lists "Verify brake pad
  thickness" and "Check rotor for trueness" as **separate** bullets; it never says the pad contacts the
  rotor. This is the same join wake 18 dropped, re-checked in full text and still unsupported.
- `comp-rear-shock -> sys-wheels` — `big_blue_book_p0921_c00` defines the rear shock as the rear
  suspension damping mechanism; nothing in the bundle places it in the wheels subsystem. Drawing it
  would be the "inference dressed as knowledge" the wake-17 analysis warned about.

`prop-fluid-dot`, `comp-bb-threaded` and `comp-fork-seals` have no bundle-evidenced join left. The
bundle well is now nearly dry — that is the finding, not a reason to loosen the standard.

### Gate written BEFORE the instruction: `verify_connectors3.py`

Same checks as batch 2, generalised to three batches: 9 edges expected (3 + 4 + 2), top-level tag
`phase6-connectors-3`, and **each edge's own `batch` label** verified against the batch it came from;
frozen hashes; zero nodes; dangling/duplicate/symmetric-both-ways; quote equal to the approved text,
literal in `kb.db`, ASCII, literal in the bundled text, `bundle==kb.db`; ontology both ends; loader;
declared connectivity `(7, 35)`; plus the simulation section.

Known-bad run before sending: **`problems=4`** — tag still `connectors-2`, the 2 edges missing,
connectivity `(9, 27)`. `I. SIMULATION`: `edges=63 components=7 largest=35`, agreeing with the
declared `(7, 35)`. The 7 accepted edges still passed E/E2/F, so the gate did not regress.

Pre-send quote proof (`precheck_b3.py` -> `_w20_pre3.txt`): `BAD: 0`; the `p0066_c00` quote carries
**exactly 1** newline and the `p0585_c00` quote 0, both ASCII, both byte-identical bundle-to-`kb.db`.

### Sent (one instruction, detached)

`_msg20_connectors3.txt` -> `_msg4.txt`. `msg20_integrity.py`: **3,262 chars**, 0 non-ASCII, one
`[[TASK]]` and it is the last line, 2 chunk/quote pairs both literal in the bundle, the multi-line
quote's newline count asserted at 1, no `claim=` wraps. `_wake20_send.cmd` (detached `pythonw`):
`msg4 bytes=3317`; **`filled=3262 value_len=3262`** — exact match, no CR offset this time because the
message file has LF endings; **`clicked Send 23:15:51`**; page `71,224 -> 74,278` and climbing.

### What the next wake must check (in this order)

1. `tail_reply.py` **as its own command**, then confirm `_reply_tail.txt` mtime is newer than
   `_studio_read.txt`. Do not trust a chained pipeline.
2. Two probes with `running=False` before acting.
3. `verify_connectors3.py` after `run_getall.cmd`: `problems=0`; C `batch=phase6-connectors-3 nodes=0
   edges=9`; E2 nine lines all `True`; G = `nodes=69 edges=63 components=7 largest=35`.
4. The two new quotes: `big_blue_book_p0585_c00` (no newline) and
   `bike_repair_manual_chris_p0066_c00` (**one** newline after "the rear"). A `Test P` failure naming
   either means the quote was retyped — reject, do not edit the test.
5. `audit_app.py` still `27 nodes / 12 edges`, 20/20, 39/39, 36/36.
6. Expect the app to print: 42 nodes / **51** expansion edges; merged 69 nodes / **63** edges
   (53 verified, 10 needs_review); **7** components, largest **35**; `Test P ... phase6-connectors-3
   (nodes [], edges [verified: 2])`; 93 citations; **14/14**; `tsc` clean; `Build succeeded`.
7. After acceptance the islands are `sys-cockpit 16, sys-brakes 8, comp-rear-shock 6, prop-fluid-dot 2,
   comp-bb-threaded 1, comp-fork-seals 1` = 6 components. **The 36-chunk bundle has no evidenced join
   for any of them.** The next step is therefore a decision for the owner, not another batch: either
   grow `seed-evidence.json` beyond 36 chunks (changes a frozen artifact and what the app bundles
   offline) or stop treating connectivity as the goal and move the map's axis to procedures/symptoms,
   where `graph.schema.json` already allows `causes`, `may_cause`, `diagnosed_by`, `transmitted...`
   relations that the ontology does not yet define.

### State carried forward

- `_msg4.txt` holds **`_msg20_connectors3.txt` (delivered 23:15:51)** — a spent order. Copy of the
  previous one: `_msg4_wake19_pre.txt`.
- Autopilot is **still dead as a grader** (`SKIP AUDIT: authoritative data file not readable`, every
  cycle since 22:02 — `_autopilot.log`). Root cause identified in wake 18: `autopilot.py snapshot()`
  reads only Monaco models that happen to be open, so `seed_graph.json` reads "missing". **This is now
  overdue** and is the first local fix on the next wake that is not mid-send; the supervisor's own
  audit has been the only grading for ~75 minutes.
- New tools this wake, read-only: `check_wake20_claims.py`, `dump_b3_texts.py`, `dump_b3_brakes.py`,
  `precheck_b3.py`, `msg20_integrity.py`, `verify_connectors3.py`.
- Frozen hashes unchanged: seed `63ac5126`, brakes `a384a15f`, cockpit `13f28204`, drivetrain
  `62442afc`, rearshock `ace4858b`, quillstem `69526d23`, cassette `0a15c418`, hubfit `2e86bcd4`.







## 2026-10-24 23:34 — wake 22 (relay retry): connectors-3 **accepted on evidence**; the bundle is exhausted

I was woken at 23:25:02 as `retry blocked reply (marker>=7)` — wake 21 was cut off mid-verification and
never sent. The reply it was checking landed 23:17:42 (`len=87407`, marker 7) and answers
`_msg20_connectors3.txt`.

### Verified myself (`verify_wake22.py` -> `_verify_wake22.txt`, PROBLEMS: 0)

Every number in the reply was recomputed from `_app_files\` (origin dump 23:23:43, after the reply) and
from `kb.db` — not from the app's own test output:

| Check | Result |
|---|---|
| frozen files, hash vs the values recorded before wake 20 | 8/8 UNCHANGED (`seed 63ac51261765d930` … `hubfit 2e86bcd491646ba3`) |
| `seed_graph.json`, `seed-evidence.json` vs `_fixed/` | byte-identical |
| seed | 27 nodes / 12 edges / 59 citations (39 node + 20 edge) — intact |
| bundle vs kb.db | 36/36 texts identical, 0 ghost chunk_ids |
| `expansion-connectors.json` | 0 nodes, 9 edges, top-level `phase6-connectors-3`; per-edge batch labels 3/4/2 exactly right; both dictated ids and both dictated claims character-exact; E6 line break preserved |
| the 9 connectors citations | 9/9 in the bundled 36, 9/9 **byte-literal** in the bundle, 9/9 byte-literal in kb.db, 9/9 book/page match the bundle record |
| merged map | **69 nodes / 63 edges**; nodes 61 verified + 1 candidate + 7 needs_review; edges 53 verified + 10 needs_review; expansion contribution 42 nodes / 51 edges |
| dangling endpoints / duplicate edges / duplicate node ids | none / none / none |
| connectivity | **7 components, largest 35 (51%)**, sizes [35,16,8,6,2,1,1] — exactly the pre-computed expectation |
| ontology, the 2 new relations | legal at both ends |
| verified edges whose numbers rest only on grade B | 0 (the 6 such claims are all correctly held at `needs_review`) |
| properties marked `verified` with no citation | 0 |
| every citation in all 9 files | 152 total; 0 not in the bundle; 0 not in kb.db (`audit_app.py` also re-run: problems=0) |

`tsc` and `Build succeeded`: **not re-runnable from here** (the app lives in AI Studio). Reported, not
verified.

### What I caught (a wording correction, not a fabrication)

The long-standing STATUS line "20/20 + 39/39 citations are literal substrings" is true only after
whitespace collapse. Byte for byte it is **11 of 59**: 48 seed quotes differ from their chunk in
whitespace only — e.g. quote `* DOT FLUID, CAUSTIC MATERIAL.` vs chunk `*   DOT FLUID, …` (three
spaces). After `\s+ -> ' '` it is 59/59 and the word sequence is identical, so nothing was invented.
The 9 connectors quotes, dictated with exact newlines, are 9/9 byte-exact. I did **not** touch the seed
quotes: the seed is frozen and I do not rewrite evidence text by hand.

### The map is at its evidence ceiling

All **36 of 36** bundled chunks are now cited by some node or edge — 0 unused. `probe_w22c.py` /
`probe_w22d.py` show no bundled chunk carries a sentence that joins two of the six remaining islands
(`sys-cockpit` 16, `sys-brakes` 8, `comp-rear-shock` 6, `prop-fluid-dot`+`prop-fluid-mineral` 2,
`comp-bb-threaded` 1, `comp-fork-seals` 1); the keyword overlaps are false positives ("stem" inside
"system"). So no connectors-4 is defensible, and growing `seed-evidence.json` past 36 chunks is a
protocol change that stays with the owner. That decision is now the only thing standing between this
map and further size.

### Sent (one instruction)

`_msg22_closeout.txt` -> `_msg4.txt`: a **closeout pass** — no evidence work, no node/edge/chunk edits.
(1) a "Coverage & Integrity" panel whose every number is *computed at runtime* (69/63; 61/1/7 nodes;
53/10 edges; per-batch ledger; 152 citations with 104 byte-exact and 48 whitespace-only; 36 of 36 chunks
cited, 0 unused; 7 components, largest 35, plus the six islands; one sentence stating the ceiling),
(2) **Test Q** that recomputes those numbers and fails on any drift, (3) an explicit ban on editing any
quote, (4) raw suite + tsc + build output.

Next wake checks: 15/15 passing, Test Q non-vacuous, panel numbers from code not literals,
69/63/152/104/48/36/0/7/35 unchanged, seed + bundle byte-identical, build.

### Housekeeping

- `_msg4_prev.txt` now holds wake 20's order (the earlier copy survives as `_msg15_batch7_fix.txt`).
- App title is already `Hi5 Mechanical Knowledge Graph` in `metadata.json` **and** `index.html` — the
  "Untitled" item in the summary table above is stale; drop it.
- Autopilot still cannot grade (`SKIP AUDIT: authoritative data file not readable` every cycle); the
  origin-dump fallback at 23:23:43 recovered it (`_app_files` 38 files). My audit, not its, is the grade.
- New read-only tools this wake: `verify_wake22.py`, `probe_w22.py`, `probe_w22b.py`, `probe_w22c.py`,
  `probe_w22d.py`, `check_msg22.py`.


## 2026-10-25 01:40 — closeout accepted; environment repaired; where this goes next

### What happened between 23:37 and 01:35

1. My closeout instruction was delivered 23:37:01 (`_send3_log.txt`: `filled=2828`,
   `clicked Send`). The turn **failed** with `Error: Quota limits exceeded` (Ran for 0s) — no work.
2. Chrome had been closed by ~00:40, so the relay degraded: `connect_over_cdp` timeouts, then
   `NO_PAGE` (00:40-00:47). Then the scheduled task **`Hi5SupervisorRelay` was found
   `Status: Disabled`** — that is why the log stops at 00:47. Re-enabled (see below).
3. Chrome relaunched on `WORKSPACE\.chrome_debug` with `--remote-debugging-port=9222`
   (`launch_chrome.py`); CDP open, app tab loaded and still logged in. The gemini MCP bridge sees
   `connected:false` for the same reason — it needs that port too.
4. The retry (run through a **scheduled task**, because this Cline terminal kills any child when it
   closes — `start /b`, `Start-Process` and even `pythonw` all died with it) succeeded at 01:26.
   Gemini answered in **5m 9s**:
   `Edited 5 files` — `src/services/coverage-service.ts`, `src/components/CoveragePanel.tsx`,
   `src/App.tsx`, `src/components/NavPane.tsx`, `src/tests/phase3-tests.ts`; `tsc` exit 0;
   `vite build` exit 0 (`✓ built in 752ms`); suite `15/15` with `#15 [PASS] Test Q`.

### Verified myself, not from the reply (`verify_closeout.py` -> `_w23_verify_closeout.txt`, PROBLEMS: 0)

| Check | Result |
|---|---|
| `coverage-service.ts` (5,305 chars) uses `getSeedGraph`, `getMergedGraph`, `getExpansionRegistry` and the chunk texts | yes |
| hard-coded `69` / `63` / `152` inside the service | **0 occurrences** (the numbers are computed) |
| connectivity really computed (adjacency map, `components`, `visited`, BFS `queue`) | yes |
| byte-exact citation test does a substring compare against chunk text | yes |
| `Test Q` in `phase3-tests.ts` (30,195 chars) | present, calls `computeCoverageReport()`, **16** `qErrors.push` assertions, pins 69/63/152/104/48/36/35/7 |
| panel wired: `App.tsx` imports **and** renders `<CoveragePanel>`, `NavPane` has the entry | yes |
| data untouched: `verify_wake22.py` re-run on the 01:34 dump | **PROBLEMS=0** — 9 connectors edges still byte-literal, 69/63, 152 citations (104 byte-exact / 48 whitespace-only), 36 of 36 chunks, 0 unused, 7 components, largest 35 |
| frozen hashes (seed `63ac5126…`, brakes `a384a15f…`, … hubfit `2e86bcd4…`) | unchanged |

`tsc` / `build`: the app's own output (exit code 0 twice). Not re-runnable from this machine — say so,
never claim it as mine.

**The closeout batch is accepted.** The map now reports its own coverage and its own ceiling, and the
suite fails if any of those numbers drift.

### Environment facts that cost time (worth remembering)

- This terminal kills every child process the moment the tool call returns. Browser work must run as a
  **scheduled task** (`schtasks /Create` + `/Run`, wrapper `.cmd` -> venv python). `_msg4` sends must be
  finished inside one call or repeated until `_send3_log.txt` shows `clicked Send`.
- `py -3` (system Python) has no `playwright`; use `WORKSPACE\.venv\Scripts\python.exe`.
- The origin dump wraps each `.ts/.tsx` as `export default "<escaped source>"`, so a naive line/token
  scan reads garbage. Decode with `json.loads` first (`probe_closeout.py`, `verify_closeout.py`).
- The `[[TASK]]` marker is inflated by my own messages (they end with the same marker), so "marker grew"
  alone is not proof of a reply; the length/`Running for` signals matter.

### Where the project actually stands

- **Graph**: 69 nodes / 63 edges, 61 verified + 1 candidate + 7 needs_review nodes, 53 + 10 edges,
  152 citations, **36 of 36 bundled chunks cited, 0 unused**, 7 components (largest 35 = 51%),
  6 islands: `sys-cockpit` 16, `sys-brakes` 8, `comp-rear-shock` 6, `prop-fluid-dot`+`prop-fluid-mineral` 2,
  `comp-bb-threaded` 1, `comp-fork-seals` 1.
- **The only thing that can still make this map bigger is new source evidence.** Adding chunks to
  `src/data/seed-evidence.json` is a protocol change and stays with the owner. Two sane next steps:
  1. **Grow the bundle** (owner decision): pick the next N pages from `kb.db` (3,921 chunks) — e.g. the
     cockpit/brakes/shock chapters that would join the 6 islands — and re-open Phase 5 with a new bundle.
  2. **Stay at 36 chunks and build outward instead of bigger**: a compatibility/query surface over the
     existing verified edges (the engine already returns 5 states; only the seed's 12 edges are wired to
     it in the UI), and a procedure/symptom axis once the ontology defines `causes`/`diagnosed_by`.
- Autopilot still cannot grade (`SKIP AUDIT …`) — it has never been the grade; my scripts are.

### Housekeeping done

- `Hi5SupervisorRelay` re-enabled; temp tasks `Hi5RetrySend`, `Hi5DumpPage`, `Hi5RefreshVerify` removed
  after use (they exist only to escape this terminal's kill-on-close).
- New read-only tools: `launch_chrome.py`, `retry_send.py` (+`.cmd`), `dump_page.cmd`,
  `refresh_and_verify.cmd`, `probe_chrome.py/2/3`, `probe_url.py`, `probe_closeout.py`,
  `verify_closeout.py`, `grep_closeout.py`, `tail_read.py`.
