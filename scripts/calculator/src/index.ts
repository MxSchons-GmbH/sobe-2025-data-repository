/**
 * Brain Emulation Calculator
 *
 * A calculator for estimating brain emulation project costs and timelines.
 *
 * @example
 * ```typescript
 * import { createCalculator } from 'brain-emulation-calculator';
 *
 * const calc = await createCalculator();
 *
 * const results = calc
 *   .reset()
 *   .loadShared()
 *   .loadOrganism('mouse')
 *   .loadModality('exm')
 *   .loadProofreading('current')
 *   .calculateAll();
 *
 * console.log(`Time to first connectome: ${results.time_to_first_years} years`);
 * console.log(`Cost per neuron: $${results.avg_cost_per_neuron}`);
 * ```
 */

export { Calculator, createCalculator, createCalculatorSync } from './engine/index.js';
export type { FormulaDefinition, OrganismData, CalculatorData } from './engine/index.js';
