/**
 * The evidence corpus is a UNION of bundles.
 *
 * Bundle 1 (`seed-evidence.json`) is the frozen kb.db excerpt: 43 chunks, never edited.
 * Bundle 2 (`evidence-bundle-2.json`) holds pages ingested from the source PDFs' own text layer, and
 * exists because the excerpt was missing the sentences that document how parts attach (e.g. the
 * bottom bracket threading into the frame's shell).
 *
 * Bundle 3 (`evidence-bundle-3.json`) is the same idea for the Sidwells pages that connect the fork
 * seals to the fork (pp.35, 141). Grade A: the publisher's text layer, not an OCR transcription.
 *
 * One accessor so the app, the test suite and the independent verifier cannot disagree about which
 * chunks exist - the same failure mode `tools/verify_registry.py` exists to prevent for graph files.
 */
import bundle1 from '../data/seed-evidence.json';
import bundle2 from '../data/evidence-bundle-2.json';
import bundle3 from '../data/evidence-bundle-3.json';

export interface EvidenceChunk {
  chunk_id: string;
  book: string;
  page?: number | string;
  section?: string;
  text: string;
}

function asChunks(bundle: { chunks?: Record<string, unknown> }): Record<string, EvidenceChunk> {
  return (bundle.chunks || {}) as Record<string, EvidenceChunk>;
}

export const EVIDENCE_BUNDLE_FILES = ['seed-evidence.json', 'evidence-bundle-2.json', 'evidence-bundle-3.json'] as const;

export function getEvidenceChunks(): Record<string, EvidenceChunk> {
  return { ...asChunks(bundle1 as { chunks?: Record<string, unknown> }),
           ...asChunks(bundle2 as { chunks?: Record<string, unknown> }),
           ...asChunks(bundle3 as { chunks?: Record<string, unknown> }) };
}

export function getChunkText(): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [id, rec] of Object.entries(getEvidenceChunks())) out[id] = rec.text;
  return out;
}
