/**
 * Generates TypeScript interfaces from TSV structure
 */

import { readTSV, writeFile, camelCase, listTSVFiles } from './utils.js';
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
const OUTPUT_FILE = join(__dirname, '..', 'src', 'generated', 'types.ts');

interface ParameterRow {
  id: string;
  name: string;
  definition: string;
  unit: string;
  [key: string]: string;
}

interface FormulaRow {
  id: string;
  formula: string;
  inputs: string;
  unit: string;
  description: string;
}

async function generateTypes(): Promise<void> {
  console.log('Generating TypeScript types...\n');

  let output = `/**
 * AUTO-GENERATED FILE - DO NOT EDIT
 * Generated from TSV files by scripts/generate-types.ts
 * Run 'npm run generate:types' to regenerate
 */

`;

  // Load shared parameters
  const shared = readTSV<ParameterRow>(join(PARAMS_DIR, 'shared.tsv'));
  output += `/**
 * Shared project-level parameters
 */
export interface SharedParameters {\n`;
  for (const p of shared) {
    const value = p.value;
    const isNumeric = !isNaN(Number(value));
    output += `  /** ${p.definition || p.name} (${p.unit}) */\n`;
    output += `  ${camelCase(p.id)}: ${isNumeric ? 'number' : 'string'};\n`;
  }
  output += `}\n\n`;

  // Load imaging modalities
  const modalities = readTSV<ParameterRow>(join(IMAGING_DIR, 'imaging-modalities.tsv'));
  const modalityIds = Object.keys(modalities[0] || {}).filter(
    k => !['id', 'name', 'definition', 'unit', 'source'].includes(k)
  );

  output += `/**
 * Imaging modality parameter values
 */
export interface ImagingModalityParams {\n`;
  for (const p of modalities) {
    output += `  /** ${p.definition || p.name} (${p.unit}) */\n`;
    output += `  ${camelCase(p.id)}: number;\n`;
  }
  output += `}\n\n`;

  output += `/**
 * Available imaging modality IDs
 */
export type ModalityId = ${modalityIds.map(m => `'${m}'`).join(' | ')};\n\n`;

  output += `/**
 * All imaging modalities indexed by ID
 */
export type ImagingModalities = Record<ModalityId, ImagingModalityParams>;\n\n`;

  // Load organisms
  const organisms = readTSV<ParameterRow>(join(ORGANISMS_DIR, 'organisms.tsv'));
  output += `/**
 * Organism specifications
 */
export interface Organism {\n`;
  output += `  id: string;\n`;
  output += `  name: string;\n`;
  output += `  neurons: number;\n`;
  output += `  volumeMm3: number;\n`;
  output += `  synapses: number;\n`;
  output += `  source: string;\n`;
  output += `}\n\n`;

  const organismIds = organisms.map(o => o.id);
  output += `/**
 * Available organism IDs
 */
export type OrganismId = ${organismIds.map(o => `'${o}'`).join(' | ')};\n\n`;

  // Load proofreading parameters
  const proofreading = readTSV<ParameterRow>(join(COSTS_DIR, 'proofreading.tsv'));
  output += `/**
 * Proofreading parameters
 */
export interface ProofreadingParams {\n`;
  for (const p of proofreading) {
    output += `  /** ${p.definition || p.name} (${p.unit}) */\n`;
    output += `  ${camelCase(p.id)}: number;\n`;
  }
  output += `}\n\n`;

  output += `/**
 * Proofreading scenario
 */
export type ProofreadingScenario = 'current' | 'improved_1000x';\n\n`;

  // Load all formulas and create result interface
  const formulaFiles = listTSVFiles(FORMULAS_DIR);
  const allFormulas: FormulaRow[] = [];

  for (const file of formulaFiles) {
    const formulas = readTSV<FormulaRow>(file);
    allFormulas.push(...formulas);
  }

  output += `/**
 * All calculated formula results
 */
export interface CalculationResults {\n`;
  for (const f of allFormulas) {
    output += `  /** ${f.description} (${f.unit}) */\n`;
    output += `  ${camelCase(f.id)}: number;\n`;
  }
  output += `}\n\n`;

  // Formula metadata type
  output += `/**
 * Formula definition metadata
 */
export interface FormulaDefinition {
  id: string;
  formula: string;
  inputs: string[];
  unit: string;
  section: string;
  row: number;
  description: string;
}\n\n`;

  // Calculator input type
  output += `/**
 * Input parameters for the calculator
 */
export interface CalculatorInput {
  organism: OrganismId;
  modality: ModalityId;
  proofreadingScenario: ProofreadingScenario;
  overrides?: Partial<SharedParameters & ImagingModalityParams & ProofreadingParams>;
}\n\n`;

  // Calculator output type
  output += `/**
 * Full calculator output
 */
export interface CalculatorOutput {
  inputs: Record<string, number>;
  results: CalculationResults;
  metadata: {
    organism: Organism;
    modality: ModalityId;
    proofreadingScenario: ProofreadingScenario;
  };
}\n`;

  writeFile(OUTPUT_FILE, output);
  console.log(`✅ Generated ${OUTPUT_FILE}`);
  console.log(`   ${shared.length} shared parameters`);
  console.log(`   ${modalities.length} modality parameters × ${modalityIds.length} modalities`);
  console.log(`   ${organisms.length} organisms`);
  console.log(`   ${allFormulas.length} formulas`);
}

generateTypes().catch(err => {
  console.error('Type generation error:', err);
  process.exit(1);
});
