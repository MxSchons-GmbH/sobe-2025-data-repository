/**
 * Generates markdown documentation from TSV files
 */

import { readTSV, writeFile, listTSVFiles, formatNumber } from './utils.js';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

// Get the directory of this script
const __dirname = dirname(fileURLToPath(import.meta.url));

// Data directories (relative to repo root, which is 3 levels up from build/)
const DATA_ROOT = join(__dirname, '..', '..', '..', 'data');
const FORMULAS_DIR = join(DATA_ROOT, 'formulas');
const ORGANISMS_DIR = join(DATA_ROOT, 'organisms');
const IMAGING_DIR = join(DATA_ROOT, 'imaging');
const COSTS_DIR = join(DATA_ROOT, 'costs');
const PARAMS_DIR = join(DATA_ROOT, 'parameters');
const DOCS_DIR = join(__dirname, '..', 'docs');

interface ParameterRow {
  id: string;
  name: string;
  definition: string;
  unit: string;
  source: string;
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

async function generateDocs(): Promise<void> {
  console.log('Generating documentation...\n');

  // Generate parameters documentation
  let paramsMd = `# Parameter Reference

This document describes all input parameters used in the brain emulation calculator.
These values can be edited in the TSV files under the \`data/\` directory.

---

`;

  // Shared parameters
  const shared = readTSV<ParameterRow>(join(PARAMS_DIR, 'shared.tsv'));
  paramsMd += `## Shared Parameters

Project-level parameters that apply across all calculations.

| Parameter | Value | Unit | Description |
|-----------|-------|------|-------------|
`;
  for (const p of shared) {
    const value = isNaN(Number(p.value)) ? p.value : formatNumber(Number(p.value));
    paramsMd += `| ${p.name} | ${value} | ${p.unit} | ${p.definition} |\n`;
  }
  paramsMd += '\n';

  // Imaging modalities
  const modalities = readTSV<ParameterRow>(join(IMAGING_DIR, 'imaging-modalities.tsv'));
  const modalityIds = Object.keys(modalities[0] || {}).filter(
    k => !['id', 'name', 'definition', 'unit', 'source'].includes(k)
  );

  paramsMd += `## Imaging Modalities

Parameters specific to each imaging technology.

| Parameter | Unit | ${modalityIds.map(m => m.toUpperCase()).join(' | ')} |
|-----------|------|${modalityIds.map(() => '---').join('|')}|
`;
  for (const p of modalities) {
    const values = modalityIds.map(m => {
      const v = p[m];
      return isNaN(Number(v)) ? v : formatNumber(Number(v));
    });
    paramsMd += `| ${p.name} | ${p.unit} | ${values.join(' | ')} |\n`;
  }
  paramsMd += '\n';

  // Organisms
  const organisms = readTSV<ParameterRow>(join(ORGANISMS_DIR, 'organisms.tsv'));
  paramsMd += `## Organisms

Reference data for different model organisms.

| Organism | Neurons | Volume (mm³) | Synapses | Source |
|----------|---------|--------------|----------|--------|
`;
  for (const o of organisms) {
    paramsMd += `| ${o.name} | ${formatNumber(Number(o.neurons))} | ${formatNumber(Number(o.volume_mm3))} | ${formatNumber(Number(o.synapses))} | ${o.source} |\n`;
  }
  paramsMd += '\n';

  // Proofreading
  const proofreading = readTSV<ParameterRow>(join(COSTS_DIR, 'proofreading.tsv'));
  paramsMd += `## Proofreading Parameters

Human proofreading assumptions for different technology scenarios.

| Parameter | Unit | Current | 1000× Improved |
|-----------|------|---------|----------------|
`;
  for (const p of proofreading) {
    paramsMd += `| ${p.name} | ${p.unit} | ${formatNumber(Number(p.current))} | ${formatNumber(Number(p.improved_1000x))} |\n`;
  }
  paramsMd += '\n';

  writeFile(join(DOCS_DIR, 'parameters.md'), paramsMd);
  console.log('  ✅ Generated docs/parameters.md');

  // Generate formulas documentation
  let formulasMd = `# Formula Reference

This document describes all calculation formulas used in the brain emulation calculator.
Formulas are defined in TSV files under \`data/formulas/\` and evaluated using [mathjs](https://mathjs.org/).

---

`;

  // Exclude shared.tsv which is a parameter file, not formulas
  const formulaFiles = listTSVFiles(FORMULAS_DIR).filter(f => !f.endsWith('shared.tsv'));

  for (const file of formulaFiles) {
    const filename = file.split('/').pop()?.replace('.tsv', '') || '';
    const formulas = readTSV<FormulaRow>(file);

    formulasMd += `## ${filename.charAt(0).toUpperCase() + filename.slice(1).replace(/-/g, ' ')} Formulas

`;

    // Group by section
    const sections = new Map<string, FormulaRow[]>();
    for (const f of formulas) {
      const section = f.section || 'general';
      if (!sections.has(section)) {
        sections.set(section, []);
      }
      sections.get(section)!.push(f);
    }

    for (const [section, sectionFormulas] of sections) {
      formulasMd += `### ${section.charAt(0).toUpperCase() + section.slice(1)}\n\n`;
      formulasMd += `| ID | Formula | Unit | Description |\n`;
      formulasMd += `|----|---------|------|-------------|\n`;

      for (const f of sectionFormulas) {
        // Escape pipe characters in formula
        const formula = f.formula.replace(/\|/g, '\\|');
        formulasMd += `| \`${f.id}\` | \`${formula}\` | ${f.unit} | ${f.description} |\n`;
      }
      formulasMd += '\n';
    }
  }

  // Add dependency information
  formulasMd += `## Formula Dependencies

Each formula depends on input parameters and/or other formulas. The calculator
automatically resolves these dependencies in the correct order.

`;

  for (const file of formulaFiles) {
    const formulas = readTSV<FormulaRow>(file);
    for (const f of formulas) {
      const inputs = f.inputs.split(',').map(s => s.trim()).filter(Boolean);
      if (inputs.length > 0) {
        formulasMd += `- **${f.id}** depends on: ${inputs.map(i => `\`${i}\``).join(', ')}\n`;
      }
    }
  }

  writeFile(join(DOCS_DIR, 'formulas.md'), formulasMd);
  console.log('  ✅ Generated docs/formulas.md');

  console.log('\n✅ Documentation generation complete');
}

generateDocs().catch(err => {
  console.error('Documentation generation error:', err);
  process.exit(1);
});
