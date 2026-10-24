# Adjudication of the five ontology violations (2026-10-25)

Rule applied: **change the edge when the edge is wrong; change the ontology only when the relation
is valid in general and the ontology is too restrictive.** Each case was decided from the record and
its verbatim evidence, not from the error message.

Before: `docs/app_state_verification_before_adjudication.txt` — PROBLEMS 5, FAIL.
After: `docs/app_state_verification.txt` — PROBLEMS 0, PASS.
Counts are **identical** before and after (69/66/155, 5 components): only two records and two rules
changed, so nothing else moved.

| # | edge | verdict | change | why |
|---|---|---|---|---|
| 1 | `std-brake-centerlock --has_property--> std-brake-centerlock-torque` | **record was wrong** | node `std-brake-centerlock-torque`: `standard` → `measurement` | A 40 N·m torque value is a measurement, not a standard. `has_property` *already* permits `measurement` targets, so the rule was not too narrow — the node was mis-typed. Widening `has_property` to accept `standard` would have been the wrong repair. |
| 2 | `proc-brake-bleed --affects--> comp-caliper-hydraulic` | **rule was too narrow** | `affects.allowed_source_types` += `procedure` | A bleed procedure demonstrably acts on a caliper. `affects` already lists `procedure` as an allowed **target**, so excluding it as a source was an unexplained asymmetry in the ontology's own definition. |
| 3 | `comp-rear-hub --interfaces_with--> std-brake-thru-axle` | **record was wrong** | edge retyped to `conforms_to` (id renamed to match), claim sharpened | A hub does not "interface with" a standard, it *conforms* to one. The same map already expresses exactly this with `conforms_to` three times (`edge-hub-conforms-width`, `…boost-148mm`, `…fat-tire-170mm`), so the old shape was internally inconsistent as well as illegal. |
| 4 | `comp-freehub-ratchet --part_of--> comp-freehub-body` | **rule was too narrow** | `part_of.allowed_target_types` += `subcomponent` | Nested assemblies are legitimate ("hubs designed with a freehub contain a ratcheting mechanism"). More decisively: `part_of`'s declared inverse `contains` already allowed a `subcomponent` target, so the pair contradicted each other. |
| 5 | `comp-freehub-cartridge-bearing --part_of--> comp-freehub-body` | same as 4 | same rule change | "cartridge bearings inside the freehub" — containment; same inverse asymmetry. |

## Regression tests: `Test R` (src/tests/phase3-tests.ts, test 16)

Each adjudication is pinned **by its own reason**, so a revert fails with the specific cause:

- **R1** — the torque node is `measurement`; `has_property` accepts `measurement`; and
  `has_property` must **not** accept `standard` (proving the fix was a retype, not a widening).
- **R2** — `affects` accepts a `procedure` source; the edge exists as `affects`; `proc-brake-bleed`
  is still a `procedure`.
- **R3** — the hub→thru-axle edge is `conforms_to`; `conforms_to` accepts `standard`; and
  `interfaces_with` must **not** accept `standard`.
- **R4** — `part_of` accepts a `subcomponent` target **and** `contains` still does (inverse symmetry).
- **R5** — both containment edges exist, and **no `part_of` cycle** exists in the merged graph.

Current result: 16/16 tests pass, `tsc --noEmit` exit 0, `vite build` exit 0.
