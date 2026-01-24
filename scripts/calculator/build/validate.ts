/**
 * Validates all TSV files for:
 * - Required columns present
 * - No empty required fields
 * - Formula syntax is valid (mathjs can parse it)
 * - All formula inputs reference existing parameters or formulas
 * - No circular dependencies
 */

import { parse } from 'mathjs';
import { readTSV, listTSVFiles } from './utils.js';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

// Get the directory of this script
const __dirname = dirname(fileURLToPath(import.meta.url));

// Data directories (relative to repo root, which is 3 levels up from build/)
const DATA_ROOT = join(__dirname, '..', '..', '..', 'data');
const FORMULAS_DIR = join(DATA_ROOT, 'formulas');

// Parameter files are now spread across multiple directories
const PARAM_FILES = [
  join(DATA_ROOT, 'parameters', 'shared.tsv'),
  join(DATA_ROOT, 'organisms', 'organisms.tsv'),
  join(DATA_ROOT, 'imaging', 'imaging-modalities.tsv'),
  join(DATA_ROOT, 'recordings', 'neural-recording.tsv'),
  join(DATA_ROOT, 'costs', 'proofreading.tsv'),
];

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
  [key: string]: string;
}

async function validate(): Promise<void> {
  const errors: string[] = [];
  const warnings: string[] = [];

  console.log('Validating TSV files...\n');

  // Collect all parameter IDs
  const allParamIds = new Set<string>();

  for (const file of PARAM_FILES) {
    console.log(`  Checking ${file}...`);
    const rows = readTSV<ParameterRow>(file);

    for (const row of rows) {
      if (!row.id) {
        errors.push(`${file}: Row missing 'id' field`);
        continue;
      }

      if (allParamIds.has(row.id)) {
        errors.push(`${file}: Duplicate parameter ID '${row.id}'`);
      }
      allParamIds.add(row.id);

      if (!row.name) {
        warnings.push(`${file}: Parameter '${row.id}' missing 'name'`);
      }
    }
  }

  console.log(`  Found ${allParamIds.size} parameters\n`);

  // Collect and validate all formulas (exclude shared.tsv which is a parameter file)
  const allFormulaIds = new Set<string>();
  const formulaDeps = new Map<string, string[]>();
  const formulaFiles = listTSVFiles(FORMULAS_DIR).filter(f => !f.endsWith('shared.tsv'));

  for (const file of formulaFiles) {
    console.log(`  Checking ${file}...`);
    const rows = readTSV<FormulaRow>(file);

    for (const row of rows) {
      if (!row.id) {
        errors.push(`${file}: Row missing 'id' field`);
        continue;
      }

      if (allFormulaIds.has(row.id)) {
        errors.push(`${file}: Duplicate formula ID '${row.id}'`);
      }
      allFormulaIds.add(row.id);

      // Validate formula syntax
      if (!row.formula) {
        errors.push(`${file}: Formula '${row.id}' missing 'formula' field`);
        continue;
      }

      try {
        parse(row.formula);
      } catch (e) {
        errors.push(`${file}: Formula '${row.id}' has invalid syntax: ${(e as Error).message}`);
      }

      // Parse inputs
      const inputs = row.inputs ? row.inputs.split(',').map(s => s.trim()) : [];
      formulaDeps.set(row.id, inputs);
    }
  }

  console.log(`  Found ${allFormulaIds.size} formulas\n`);

  // Check that all formula inputs reference existing parameters or formulas
  console.log('  Checking formula dependencies...');
  for (const [formulaId, inputs] of formulaDeps) {
    for (const input of inputs) {
      if (!allParamIds.has(input) && !allFormulaIds.has(input)) {
        errors.push(`Formula '${formulaId}' references unknown input '${input}'`);
      }
    }
  }

  // Check for circular dependencies
  console.log('  Checking for circular dependencies...');
  const visited = new Set<string>();
  const recursionStack = new Set<string>();

  function hasCycle(id: string, path: string[] = []): string[] | null {
    if (recursionStack.has(id)) {
      return [...path, id];
    }
    if (visited.has(id)) {
      return null;
    }

    visited.add(id);
    recursionStack.add(id);

    const deps = formulaDeps.get(id) || [];
    for (const dep of deps) {
      if (allFormulaIds.has(dep)) {
        const cycle = hasCycle(dep, [...path, id]);
        if (cycle) return cycle;
      }
    }

    recursionStack.delete(id);
    return null;
  }

  for (const formulaId of allFormulaIds) {
    visited.clear();
    recursionStack.clear();
    const cycle = hasCycle(formulaId);
    if (cycle) {
      errors.push(`Circular dependency detected: ${cycle.join(' -> ')}`);
      break; // Only report first cycle
    }
  }

  // Report results
  console.log('\n' + '='.repeat(50));

  if (warnings.length > 0) {
    console.log(`\n⚠️  ${warnings.length} warnings:`);
    warnings.forEach(w => console.log(`   - ${w}`));
  }

  if (errors.length > 0) {
    console.log(`\n❌ ${errors.length} errors:`);
    errors.forEach(e => console.log(`   - ${e}`));
    console.log('\nValidation FAILED');
    process.exit(1);
  }

  console.log('\n✅ All validations passed!');
  console.log(`   ${allParamIds.size} parameters`);
  console.log(`   ${allFormulaIds.size} formulas`);
  console.log(`   0 errors`);
}

validate().catch(err => {
  console.error('Validation error:', err);
  process.exit(1);
});
