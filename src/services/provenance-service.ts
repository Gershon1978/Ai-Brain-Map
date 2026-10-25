/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import seedEvidence from '../data/seed-evidence.json';
import { EvidenceGrade } from '../types/graph.ts';

export type ProvenanceSource = 'bundled' | 'attached_db';

// Computed from the bundle, never typed: the label used to say "36 chunks" long after the corpus
// grew to 43, which is exactly the kind of frozen copy this project forbids in a provenance claim.
const BUNDLED_CHUNK_COUNT = Object.keys((seedEvidence as { chunks?: Record<string, unknown> }).chunks || {}).length;

export function getProvenanceLabel(source: ProvenanceSource, totalDbChunks?: number): string {
  if (source === 'attached_db') {
    return `verified against attached kb.db (${(totalDbChunks ?? 3921).toLocaleString()} chunks)`;
  }
  return `verified against bundled corpus excerpt (${BUNDLED_CHUNK_COUNT} chunks)`;
}

export function getGradeRationale(grade: EvidenceGrade): string {
  switch (grade) {
    case 'A':
      return 'A = Prose manual text (quotable at spec level)';
    case 'B+':
      return 'B+ = Model table image extraction (asserts existence, not certified dimension)';
    case 'B':
      return 'B = model visual description, page locator only';
    case 'D':
      return 'D = Curated error code row with source_page = 0';
    default:
      return `${grade} = Unclassified evidence source`;
  }
}
