/**
 * Run the graph test suite headlessly (no browser), so a test result is observed rather than assumed.
 * Usage: npx tsx tools/run_suite.mjs
 */
import { runPhase3Tests } from '../src/tests/phase3-tests.ts';

const r = runPhase3Tests();
let pass = 0;
for (const t of r.results) {
  const mark = t.passed ? 'PASS' : 'FAIL';
  if (t.passed) pass++;
  console.log(`${mark}  ${t.name}`);
  if (!t.passed) console.log(`      ${String(t.message).slice(0, 400)}`);
}
console.log(`\nOVERALL: ${r.passed}  (${pass}/${r.results.length} passed)`);
process.exit(r.passed ? 0 : 1);
