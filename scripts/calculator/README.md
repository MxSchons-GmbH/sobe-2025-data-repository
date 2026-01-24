# Brain Emulation Calculator

A calculator for estimating costs and timelines of whole brain emulation projects, covering connectomics (brain mapping), neural recording, and storage requirements.

## Overview

This repository provides a **data-driven calculation engine** where:

- **Parameters** are defined in human-readable TSV files
- **Formulas** are defined in TSV files using mathjs syntax
- **TypeScript** provides the calculation engine
- **Documentation** is auto-generated from the data files

## Quick Start

```bash
# Install dependencies
npm install

# Build data (validate, generate types, docs, bundle)
npm run build:data

# Run tests
npm test
```

## Repository Structure

```
├── data/
│   ├── parameters/           # Input parameter TSV files
│   │   ├── shared.tsv        # Project-level assumptions
│   │   ├── organisms.tsv     # Brain sizes, neuron counts
│   │   ├── imaging-modalities.tsv  # EM, ExM specs
│   │   ├── proofreading.tsv  # Human review parameters
│   │   └── neural-recording.tsv
│   │
│   └── formulas/             # Calculation formula TSV files
│       ├── connectomics.tsv  # Imaging, timeline formulas
│       ├── storage.tsv       # Storage cost formulas
│       └── costs.tsv         # Budget formulas
│
├── src/
│   ├── engine/               # Calculation engine
│   │   └── calculator.ts     # Main Calculator class
│   ├── generated/            # Auto-generated files (git-ignored)
│   │   ├── types.ts
│   │   └── data.json
│   └── index.ts
│
├── scripts/                  # Build scripts
│   ├── validate.ts           # TSV validation
│   ├── generate-types.ts     # TypeScript generation
│   ├── generate-docs.ts      # Documentation generation
│   └── bundle.ts             # JSON bundler
│
├── tests/                    # Test suites
├── docs/                     # Generated documentation
└── original/                 # Original spreadsheet files
```

## Data Format

### Parameter Files (TSV)

Parameters are defined with full metadata:

```tsv
id	name	definition	unit	value
biological_volume	Volume (biological)	Physical brain volume to be mapped	mm³	500
neuron_count	Number of neurons	Neurons in the given volume	count	70000000
```

### Formula Files (TSV)

Formulas use mathjs syntax with explicit dependencies:

```tsv
id	formula	inputs	unit	section	row	description
voxels_per_mm3	1e18 / (voxel_x * voxel_y * voxel_z)	voxel_x,voxel_y,voxel_z	voxels/mm³	imaging	100	Voxels per cubic mm
effective_volume	biological_volume * expansion_factor^3	biological_volume,expansion_factor	mm³	imaging	99	Volume after expansion
```

Supported functions: `if(cond, true, false)`, `max()`, `min()`, `floor()`, `round()`, `sum()`, and all standard math operations.

## Usage

### Programmatic API

```typescript
import { Calculator } from './src/engine';
import data from './src/generated/data.json';

const calc = new Calculator(data);

const results = calc
  .reset()
  .loadShared()
  .loadOrganism('mouse')
  .loadModality('exm')
  .loadProofreading('current')
  .calculateAll();

console.log(`Time to first connectome: ${results.time_to_first_years.toFixed(1)} years`);
console.log(`Cost per neuron: $${results.avg_cost_per_neuron.toFixed(2)}`);
```

### Available Organisms

| ID | Name | Neurons | Volume |
|----|------|---------|--------|
| c_elegans | C. elegans | 302 | 0.001 mm³ |
| drosophila | Drosophila | 135,000 | 0.5 mm³ |
| mouse | Mouse | 70,000,000 | 500 mm³ |
| human | Human | 86,000,000,000 | 1,200,000 mm³ |

### Available Imaging Modalities

| ID | Name | Resolution | Expansion |
|----|------|------------|-----------|
| em | Electron Microscopy | 15nm | 1× |
| exm | Expansion Microscopy | 250nm | 16× |
| exm_molecular | ExM + Molecular | 250nm | 16× (800 channels) |
| wellcome | Wellcome EM | 10nm | 1× |

## Contributing

### Editing Parameters

1. Open the relevant TSV file in `data/parameters/`
2. Edit values (can use Excel, Google Sheets, or any text editor)
3. Run `npm run validate` to check for errors
4. Run `npm run build:data` to regenerate types and docs
5. Run `npm test` to verify calculations
6. Commit changes

### Adding a New Formula

1. Add a row to the appropriate file in `data/formulas/`
2. Specify: `id`, `formula`, `inputs` (comma-separated), `unit`, `section`, `row`, `description`
3. Run validation and tests

### Adding a New Imaging Modality

1. Add a new column to `data/parameters/imaging-modalities.tsv`
2. Add metadata row to the file
3. Rebuild and test

## Scripts

| Command | Description |
|---------|-------------|
| `npm run validate` | Validate all TSV files |
| `npm run generate:types` | Generate TypeScript interfaces |
| `npm run generate:docs` | Generate markdown documentation |
| `npm run bundle` | Bundle data into JSON |
| `npm run build:data` | Run all of the above |
| `npm test` | Run test suite |

## License

MIT
