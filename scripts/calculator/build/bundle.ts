/**
 * Bundles all TSV data into a single JSON file for the web app
 */

import { readTSV, writeFile, listTSVFiles, camelCase } from './utils.js';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

// Get the directory of this script
const __dirname = dirname(fileURLToPath(import.meta.url));

// Data directories (relative to repo root, which is 3 levels up from build/)
const DATA_ROOT = join(__dirname, '..', '..', '..', 'data');
const FORMULAS_DIR = join(DATA_ROOT, 'formulas');
const PARAMS_DIR = join(DATA_ROOT, 'parameters');
const ORGANISMS_DIR = join(DATA_ROOT, 'organisms');
const IMAGING_DIR = join(DATA_ROOT, 'imaging');
const RECORDINGS_DIR = join(DATA_ROOT, 'recordings');
const COSTS_DIR = join(DATA_ROOT, 'costs');
const OUTPUT_FILE = join(__dirname, '..', '..', '..', 'dist', 'calculator', 'data.json');

interface ParameterRow {
  id: string;
  [key: string]: string;
}

interface FormulaRow {
  id: string;
  formula: string;
  inputs: string;
  unit: string;
  section: string;
  row: string;
  description: string;
}

async function bundle(): Promise<void> {
  console.log('Bundling data into JSON...\n');

  // Load shared parameters
  const sharedRows = readTSV<ParameterRow>(join(PARAMS_DIR, 'shared.tsv'));
  const shared: Record<string, number | string> = {};
  for (const row of sharedRows) {
    const value = row.value;
    shared[row.id] = isNaN(Number(value)) ? value : Number(value);
  }

  // Load imaging modalities and pivot to modality -> params structure
  const modalityRows = readTSV<ParameterRow>(join(IMAGING_DIR, 'imaging-modalities.tsv'));
  // Filter out metadata columns to get just modality IDs (em, exm, etc.)
  const metadataColumns = ['id', 'name', 'definition', 'unit', 'source', 'ref_id', 'supporting_refs', 'ref_note', 'confidence', 'validated_by'];
  const modalityIds = Object.keys(modalityRows[0] || {}).filter(
    k => !metadataColumns.includes(k)
  );

  const modalities: Record<string, Record<string, number>> = {};
  for (const modalityId of modalityIds) {
    modalities[modalityId] = {};
    for (const row of modalityRows) {
      modalities[modalityId][row.id] = Number(row[modalityId]);
    }
  }

  // Load organisms
  const organismRows = readTSV<ParameterRow>(join(ORGANISMS_DIR, 'organisms.tsv'));
  const organisms: Record<string, {
    id: string;
    name: string;
    neurons: number;
    volumeMm3: number;
    synapses: number;
    source: string;
  }> = {};
  for (const row of organismRows) {
    organisms[row.id] = {
      id: row.id,
      name: row.name,
      neurons: Number(row.neurons),
      volumeMm3: Number(row.volume_mm3),
      synapses: Number(row.synapses),
      source: row.source,
    };
  }

  // Load proofreading parameters
  const proofreadingRows = readTSV<ParameterRow>(join(COSTS_DIR, 'proofreading.tsv'));
  const proofreading: Record<string, Record<string, number>> = {
    current: {},
    improved_1000x: {},
  };
  for (const row of proofreadingRows) {
    proofreading.current[row.id] = Number(row.current);
    proofreading.improved_1000x[row.id] = Number(row.improved_1000x);
  }

  // Load neural recording parameters
  const neuralRecordingRows = readTSV<ParameterRow>(join(RECORDINGS_DIR, 'neural-recording.tsv'));
  const neuralRecording: Record<string, number | string> = {};
  for (const row of neuralRecordingRows) {
    const value = row.mouse_example;
    neuralRecording[row.id] = value && !isNaN(Number(value)) ? Number(value) : value;
  }

  // Load all formulas (exclude shared.tsv which is a parameter file)
  const formulaFiles = listTSVFiles(FORMULAS_DIR).filter(f => !f.endsWith('shared.tsv'));
  const formulas: Array<{
    id: string;
    formula: string;
    inputs: string[];
    unit: string;
    section: string;
    row: number;
    description: string;
  }> = [];

  for (const file of formulaFiles) {
    const rows = readTSV<FormulaRow>(file);
    for (const row of rows) {
      formulas.push({
        id: row.id,
        formula: row.formula,
        inputs: row.inputs.split(',').map(s => s.trim()).filter(Boolean),
        unit: row.unit,
        section: row.section,
        row: Number(row.row) || 0,
        description: row.description,
      });
    }
  }

  // Build the output structure
  const output = {
    parameters: {
      shared,
      modalities,
      organisms,
      proofreading,
      neuralRecording,
    },
    formulas,
    metadata: {
      parameterCount: Object.keys(shared).length +
        modalityRows.length * modalityIds.length +
        organismRows.length +
        proofreadingRows.length * 2,
      formulaCount: formulas.length,
      modalityIds,
      organismIds: Object.keys(organisms),
      proofreadingScenarios: ['current', 'improved_1000x'],
    },
  };

  writeFile(OUTPUT_FILE, JSON.stringify(output, null, 2));

  console.log(`✅ Generated ${OUTPUT_FILE}`);
  console.log(`   Parameters: ${output.metadata.parameterCount}`);
  console.log(`   Formulas: ${output.metadata.formulaCount}`);
  console.log(`   Modalities: ${output.metadata.modalityIds.join(', ')}`);
  console.log(`   Organisms: ${output.metadata.organismIds.join(', ')}`);
}

bundle().catch(err => {
  console.error('Bundle error:', err);
  process.exit(1);
});
