/**
 * Brain Emulation Calculator Engine
 *
 * Evaluates formulas from TSV definitions using mathjs.
 * Automatically resolves dependencies between formulas.
 */

import { create, all, type EvalFunction } from 'mathjs';

// Create a custom mathjs instance with additional functions
const math = create(all);

// Add an 'if' function for conditional expressions
// Usage: if(condition, valueIfTrue, valueIfFalse)
math.import({
  'if': function(condition: boolean | number, trueVal: number, falseVal: number): number {
    return condition ? trueVal : falseVal;
  }
}, { override: true });

interface FormulaDefinition {
  id: string;
  formula: string;
  inputs: string[];
  unit: string;
  section: string;
  row: number;
  description: string;
}

interface CalculatorData {
  parameters: {
    shared: Record<string, number | string>;
    modalities: Record<string, Record<string, number>>;
    organisms: Record<string, {
      id: string;
      name: string;
      neurons: number;
      volumeMm3: number;
      synapses: number;
      source: string;
    }>;
    proofreading: Record<string, Record<string, number>>;
  };
  formulas: FormulaDefinition[];
}

export class Calculator {
  private data: CalculatorData;
  private context: Record<string, number> = {};
  private compiledFormulas: Map<string, EvalFunction> = new Map();
  private formulaMap: Map<string, FormulaDefinition> = new Map();
  private sortedFormulas: FormulaDefinition[] = [];

  constructor(data: CalculatorData) {
    this.data = data;

    // Build formula lookup map
    for (const formula of data.formulas) {
      this.formulaMap.set(formula.id, formula);
    }

    // Pre-compile all formulas using custom math instance
    for (const formula of data.formulas) {
      try {
        this.compiledFormulas.set(formula.id, math.compile(formula.formula));
      } catch (e) {
        console.error(`Failed to compile formula '${formula.id}': ${(e as Error).message}`);
      }
    }

    // Topologically sort formulas for evaluation order
    this.sortedFormulas = this.topologicalSort(data.formulas);
  }

  /**
   * Topologically sort formulas based on dependencies
   */
  private topologicalSort(formulas: FormulaDefinition[]): FormulaDefinition[] {
    const formulaIds = new Set(formulas.map(f => f.id));
    const visited = new Set<string>();
    const result: FormulaDefinition[] = [];

    const visit = (formula: FormulaDefinition) => {
      if (visited.has(formula.id)) return;
      visited.add(formula.id);

      // Visit dependencies first (only if they're formulas, not parameters)
      for (const input of formula.inputs) {
        if (formulaIds.has(input)) {
          const dep = this.formulaMap.get(input);
          if (dep) visit(dep);
        }
      }

      result.push(formula);
    };

    for (const formula of formulas) {
      visit(formula);
    }

    return result;
  }

  /**
   * Reset calculation context
   */
  reset(): this {
    this.context = {};
    return this;
  }

  /**
   * Load shared parameters into context
   */
  loadShared(overrides?: Record<string, number>): this {
    for (const [key, value] of Object.entries(this.data.parameters.shared)) {
      if (typeof value === 'number') {
        this.context[key] = overrides?.[key] ?? value;
      }
    }
    return this;
  }

  /**
   * Load organism parameters into context
   */
  loadOrganism(organismId: string): this {
    const organism = this.data.parameters.organisms[organismId];
    if (!organism) {
      throw new Error(`Unknown organism: ${organismId}`);
    }

    this.context.biological_volume = organism.volumeMm3;
    this.context.neuron_count = organism.neurons;
    this.context.synapse_count = organism.synapses;

    return this;
  }

  /**
   * Load imaging modality parameters into context
   */
  loadModality(modalityId: string): this {
    const modality = this.data.parameters.modalities[modalityId];
    if (!modality) {
      throw new Error(`Unknown modality: ${modalityId}`);
    }

    for (const [key, value] of Object.entries(modality)) {
      this.context[key] = value;
    }

    return this;
  }

  /**
   * Load proofreading parameters into context
   */
  loadProofreading(scenario: 'current' | 'improved_1000x'): this {
    const params = this.data.parameters.proofreading[scenario];
    if (!params) {
      throw new Error(`Unknown proofreading scenario: ${scenario}`);
    }

    for (const [key, value] of Object.entries(params)) {
      this.context[key] = value;
    }

    return this;
  }

  /**
   * Set a single parameter value
   */
  set(key: string, value: number): this {
    this.context[key] = value;
    return this;
  }

  /**
   * Set multiple parameter values
   */
  setMany(params: Record<string, number>): this {
    for (const [key, value] of Object.entries(params)) {
      this.context[key] = value;
    }
    return this;
  }

  /**
   * Get current context (all parameter values)
   */
  getContext(): Record<string, number> {
    return { ...this.context };
  }

  /**
   * Calculate a single formula by ID
   */
  calculate(formulaId: string): number {
    const compiled = this.compiledFormulas.get(formulaId);
    if (!compiled) {
      throw new Error(`Unknown formula: ${formulaId}`);
    }

    const formula = this.formulaMap.get(formulaId)!;

    // Calculate dependencies first
    for (const input of formula.inputs) {
      if (!(input in this.context) && this.formulaMap.has(input)) {
        this.context[input] = this.calculate(input);
      }
    }

    // Check all inputs are available
    for (const input of formula.inputs) {
      if (!(input in this.context)) {
        throw new Error(`Formula '${formulaId}' missing input '${input}'`);
      }
    }

    const result = compiled.evaluate(this.context) as number;
    this.context[formulaId] = result;

    return result;
  }

  /**
   * Calculate all formulas and return results
   */
  calculateAll(): Record<string, number> {
    const results: Record<string, number> = {};

    for (const formula of this.sortedFormulas) {
      try {
        results[formula.id] = this.calculate(formula.id);
      } catch (e) {
        console.error(`Error calculating '${formula.id}': ${(e as Error).message}`);
        results[formula.id] = NaN;
      }
    }

    return results;
  }

  /**
   * Get list of available organisms
   */
  getOrganisms(): Array<{ id: string; name: string; neurons: number }> {
    return Object.values(this.data.parameters.organisms).map(o => ({
      id: o.id,
      name: o.name,
      neurons: o.neurons,
    }));
  }

  /**
   * Get list of available modalities
   */
  getModalities(): string[] {
    return Object.keys(this.data.parameters.modalities);
  }

  /**
   * Get formula metadata
   */
  getFormulaInfo(formulaId: string): FormulaDefinition | undefined {
    return this.formulaMap.get(formulaId);
  }

  /**
   * Get all formula metadata
   */
  getAllFormulas(): FormulaDefinition[] {
    return [...this.data.formulas];
  }
}

/**
 * Create a calculator instance from bundled data
 */
export async function createCalculator(): Promise<Calculator> {
  // In a real app, this would load from the generated JSON
  // For now, we'll import it directly
  const data = await import('../generated/data.json', { assert: { type: 'json' } });
  return new Calculator(data.default as CalculatorData);
}

/**
 * Create a calculator instance from provided data
 */
export function createCalculatorSync(data: CalculatorData): Calculator {
  return new Calculator(data);
}
