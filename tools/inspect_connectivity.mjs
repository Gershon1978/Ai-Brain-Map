/** Print the connectivity block the app computes, so Test Q can pin membership, not just counts. */
import { computeCoverageReport } from '../src/services/coverage-service.ts';

const r = computeCoverageReport();
console.log(JSON.stringify(r.connectivity, null, 2));
