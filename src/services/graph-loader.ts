/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import seedGraphJson from '../data/seed_graph.json';
import expansionBrakesJson from '../data/expansion-brakes.json';
import expansionCockpitJson from '../data/expansion-cockpit.json';
import expansionDrivetrainJson from '../data/expansion-drivetrain.json';
import expansionRearshockJson from '../data/expansion-rearshock.json';
import expansionQuillstemJson from '../data/expansion-quillstem.json';
import expansionCassetteJson from '../data/expansion-cassette.json';
import expansionHubfitJson from '../data/expansion-hubfit.json';
import expansionConnectorsJson from '../data/expansion-connectors.json';
import expansionForkJson from '../data/expansion-fork.json';
import expansionCrankJson from '../data/expansion-crank.json';
import expansionReartriangleJson from '../data/expansion-reartriangle.json';
import expansionFrameJson from '../data/expansion-frame.json';
import { GraphPayload, GraphNode, GraphEdge } from '../types/graph.ts';

export interface ExpansionFile {
  schema_version: string;
  batch: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export function getSeedGraph(): GraphPayload {
  return seedGraphJson as unknown as GraphPayload;
}

export function getExpansionBrakes(): ExpansionFile {
  return expansionBrakesJson as unknown as ExpansionFile;
}

export function getExpansionCockpit(): ExpansionFile {
  return expansionCockpitJson as unknown as ExpansionFile;
}

export function getExpansionDrivetrain(): ExpansionFile {
  return expansionDrivetrainJson as unknown as ExpansionFile;
}

export function getExpansionRearshock(): ExpansionFile {
  return expansionRearshockJson as unknown as ExpansionFile;
}

export function getExpansionQuillstem(): ExpansionFile {
  return expansionQuillstemJson as unknown as ExpansionFile;
}

export function getExpansionCassette(): ExpansionFile {
  return expansionCassetteJson as unknown as ExpansionFile;
}

export function getExpansionHubfit(): ExpansionFile {
  return expansionHubfitJson as unknown as ExpansionFile;
}

export function getExpansionConnectors(): ExpansionFile {
  return expansionConnectorsJson as unknown as ExpansionFile;
}

/**
 * Registry of all expansion files.
 * Add new expansion datasets here to automatically integrate across the system.
 *
 * This list is hand-maintained AND machine-checked: `python tools/verify_registry.py` fails when a
 * `src/data/expansion-*.json` exists that is not registered here. That guard exists because the
 * independent verifier globs the data directory while this file imports statically, so a new batch
 * used to be visible to the verifier and invisible to the app — the suite would pass while the app
 * silently held an older graph.
 */
const expansionRegistry: ExpansionFile[] = [
  expansionBrakesJson as unknown as ExpansionFile,
  expansionCockpitJson as unknown as ExpansionFile,
  expansionDrivetrainJson as unknown as ExpansionFile,
  expansionRearshockJson as unknown as ExpansionFile,
  expansionQuillstemJson as unknown as ExpansionFile,
  expansionCassetteJson as unknown as ExpansionFile,
  expansionHubfitJson as unknown as ExpansionFile,
  expansionConnectorsJson as unknown as ExpansionFile,
  expansionForkJson as unknown as ExpansionFile,
  expansionCrankJson as unknown as ExpansionFile,
  expansionReartriangleJson as unknown as ExpansionFile,
  expansionFrameJson as unknown as ExpansionFile,
];

export function getExpansionRegistry(): ExpansionFile[] {
  return expansionRegistry;
}

/**
 * Derives the dynamic application subtitle from the expansion registry.
 */
export function getDerivedSubtitle(): string {
  const batchNameMap: Record<string, string> = {
    brake: 'Brakes',
    brakes: 'Brakes',
    cockpit: 'Cockpit',
    drivetrain: 'Drivetrain',
    rearshock: 'Rear Shock',
    quillstem: 'Quill Stem',
    cassette: 'Cassette',
    hubfit: 'Hub Fit',
    connectors: 'Connectors',
    fork: 'Fork',
    crank: 'Crank',
    reartriangle: 'Rear Triangle',
    frame: 'Frame',
  };
  // De-duplicated: phase5-brake-1 and phase8a-brakes are the same subject and used to be listed
  // twice; phase8a-style batches used to defeat the regex entirely and leak the raw batch id.
  const labels: string[] = [];
  for (const exp of getExpansionRegistry()) {
    const match = exp.batch.match(/phase\d+[a-z]?-([a-z]+)/i);
    const label = match
      ? (batchNameMap[match[1].toLowerCase()] ??
         match[1].charAt(0).toUpperCase() + match[1].slice(1))
      : exp.batch;
    if (!labels.includes(label)) labels.push(label);
  }
  const list =
    labels.length > 2
      ? `${labels.slice(0, -1).join(', ')} & ${labels[labels.length - 1]}`
      : labels.join(' & ');
  return `Hybrid Hierarchical & Constraint Reasoning System • ${list}`;
}

/**
 * Merges the frozen canonical seed graph with all registered Phase 5 expansions.
 * Preserves the pristine immutable state of seed_graph.json.
 */
export function getMergedGraph(): GraphPayload {
  const seed = getSeedGraph();
  const allExpansions = getExpansionRegistry();

  const mergedNodes: GraphNode[] = [...seed.nodes];
  const mergedEdges: GraphEdge[] = [...seed.edges];

  let totalNodeEvidence = seed.nodes.reduce((acc, n) => acc + (n.evidence?.length || 0), 0);
  let totalEdgeEvidence = seed.edges.reduce((acc, e) => acc + (e.evidence?.length || 0), 0);

  const batchDescriptions: string[] = [];

  for (const exp of allExpansions) {
    mergedNodes.push(...exp.nodes);
    mergedEdges.push(...exp.edges);
    totalNodeEvidence += exp.nodes.reduce((acc, n) => acc + (n.evidence?.length || 0), 0);
    totalEdgeEvidence += exp.edges.reduce((acc, e) => acc + (e.evidence?.length || 0), 0);
    batchDescriptions.push(`${exp.batch || 'expansion'} (${exp.nodes.length} nodes, ${exp.edges.length} edges)`);
  }

  return {
    schema_version: seed.schema_version,
    nodes: mergedNodes,
    edges: mergedEdges,
    provenance: {
      counts: {
        nodes: mergedNodes.length,
        edges: mergedEdges.length,
        node_evidence: totalNodeEvidence,
        edge_evidence: totalEdgeEvidence,
      },
      note: `Merged Graph: Seed (${seed.nodes.length} nodes, ${seed.edges.length} edges) + ${batchDescriptions.join(' + ')}`,
    },
  };
}
