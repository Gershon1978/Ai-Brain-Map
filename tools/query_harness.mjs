/**
 * Query harness: exercises the 5-state compatibility engine end-to-end.
 *
 * The suite tests the engine's rules in isolation; this drives it the way a mechanic would, with a
 * plain-language query mapped to a (subject, target) pair, and asserts the verdict. Run with:
 *   npx tsx tools/query_harness.mjs           (diagnostic table)
 *   npx tsx tools/query_harness.mjs --check   (exit 1 on any deviation from EXPECTED)
 */
import { ConstraintEngine } from '../src/services/constraint-engine.ts';
import { getMergedGraph } from '../src/services/graph-loader.ts';

const graph = getMergedGraph();
const nodes = new Map(graph.nodes.map((n) => [n.id, n]));
const engine = new ConstraintEngine({ nodes, edges: graph.edges, isDatabaseAttached: false });

// expected = the verdict the evidence at the time of writing must produce.
// C is deliberately NOT "incompatible": that exclusion edge is needs_review, and the gate must
// refuse to answer verified_compatible/incompatible from an unreviewed edge.
const CASES = [
  { q: 'Can I use DOT 4 fluid in a mineral-oil hydraulic brake?', a: 'prop-fluid-dot', b: 'prop-fluid-mineral', expected: 'incompatible', why: 'verified incompatible_with edge' },
  { q: 'Can I put an XDR cassette body on a standard cassette?', a: 'comp-freehub-xdr', b: 'comp-cassette', expected: 'incompatible', why: 'verified incompatible_with edge' },
  { q: 'Can I fit a 6-bolt rotor to a Center Lock hub without an adapter?', a: 'comp-rotor-6bolt', b: 'comp-hub-centerlock', expected: 'conditionally_compatible', why: 'the exclusion edge is needs_review, so the engine must not assert it' },
  { q: 'Does an 11-speed road cassette fit this freehub body?', a: 'unk-freehub-body-length', b: 'comp-cassette', expected: 'unknown_missing_evidence', why: 'no dimension in the corpus' },
  { q: 'Does a cassette fit a freehub body?', a: 'comp-cassette', b: 'comp-freehub-body', expected: 'verified_compatible', why: 'verified fits_into edge' },
  { q: 'Does a quill stem fit a threaded steerer?', a: 'comp-stem-quill', b: 'comp-steerer', expected: 'unknown_missing_evidence', why: 'a mounted_on edge documents a mounting, NOT fitment - the engine is right to refuse' },
  // --- coverage cases: paths the first six did not touch ---
  { q: 'Does a hub conform to a width standard that carries caveats?', a: 'comp-rear-hub', b: 'std-hub-width', expected: 'conditionally_compatible', why: 'verified conforms_to with non-empty conditions[]' },
  { q: 'Does a hub conform to the Boost 148 standard?', a: 'comp-rear-hub', b: 'std-rear-boost-148mm', expected: 'verified_compatible', why: 'verified conforms_to, no caveats: conformance is the claim, so it should carry' },
  { q: 'Which fluid does this caliper use?', a: 'comp-caliper-hydraulic', b: 'prop-fluid-dot', expected: 'unknown_missing_evidence', why: 'has_property answers a property, not fitment - and this one is needs_review anyway' },
  { q: 'Can this unknown-length freehub take a rear hub?', a: 'unk-freehub-body-length', b: 'comp-rear-hub', expected: 'unknown_missing_evidence', why: 'unknown_requirement NODE path, no edge between the pair' },
  { q: 'Does a brake pad fit a fork?', a: 'comp-brake-pad', b: 'comp-fork', expected: 'unknown_missing_evidence', why: 'no edge at all between the pair' },
  { q: 'Does a freehub body accept a cassette (reversed direction)?', a: 'comp-freehub-body', b: 'comp-cassette', expected: 'verified_compatible', why: 'verified fits_into, queried in the opposite direction - the engine must be symmetric' },
];

const check = process.argv.includes('--check');
let bad = 0;
console.log('state'.padEnd(28), 'expected'.padEnd(28), 'query');
for (const c of CASES) {
  let verdict = 'ERROR';
  try {
    verdict = engine.evaluateCompatibility(c.a, c.b).verdict;
  } catch (e) {
    verdict = 'ERROR: ' + String(e).slice(0, 60);
  }
  const ok = verdict === c.expected;
  if (!ok) bad++;
  console.log(
    (ok ? 'PASS ' : 'FAIL ') + verdict.padEnd(22),
    c.expected.padEnd(28),
    c.q,
  );
  if (!ok) console.log('      ' + c.a + ' -> ' + c.b + '  [' + c.why + ']');
}
console.log(`\n${CASES.length - bad}/${CASES.length} verdicts as expected`);
process.exit(check && bad ? 1 : 0);
