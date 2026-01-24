/**
 * Calculator Engine Tests
 *
 * Tests the core calculation engine functionality.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { Calculator } from '../src/engine/calculator.js';
import data from '../src/generated/data.json';

describe('Calculator', () => {
  let calc: Calculator;

  beforeEach(() => {
    calc = new Calculator(data as any);
  });

  describe('initialization', () => {
    it('should create a calculator instance', () => {
      expect(calc).toBeInstanceOf(Calculator);
    });

    it('should list available organisms', () => {
      const organisms = calc.getOrganisms();
      expect(organisms.length).toBeGreaterThan(0);
      expect(organisms.map(o => o.id)).toContain('mouse');
      expect(organisms.map(o => o.id)).toContain('human');
    });

    it('should list available modalities', () => {
      const modalities = calc.getModalities();
      expect(modalities).toContain('em');
      expect(modalities).toContain('exm');
      expect(modalities).toContain('exm_molecular');
      expect(modalities).toContain('wellcome');
    });
  });

  describe('parameter loading', () => {
    it('should load shared parameters', () => {
      calc.loadShared();
      const context = calc.getContext();
      expect(context.project_duration).toBe(5);
      expect(context.microscope_budget).toBe(50000000);
    });

    it('should load organism parameters', () => {
      calc.loadOrganism('mouse');
      const context = calc.getContext();
      expect(context.biological_volume).toBe(500);
      expect(context.neuron_count).toBe(70000000);
    });

    it('should load modality parameters', () => {
      calc.loadModality('exm');
      const context = calc.getContext();
      expect(context.expansion_factor).toBe(16);
      expect(context.voxel_x).toBe(250);
    });

    it('should load proofreading parameters', () => {
      calc.loadProofreading('current');
      const context = calc.getContext();
      expect(context.hours_per_neuron).toBe(5);
    });

    it('should allow parameter overrides', () => {
      calc.loadShared({ microscope_budget: 100000000 });
      const context = calc.getContext();
      expect(context.microscope_budget).toBe(100000000);
    });
  });

  describe('individual calculations', () => {
    beforeEach(() => {
      calc.reset()
        .loadShared()
        .loadOrganism('mouse')
        .loadModality('exm')
        .loadProofreading('current');
    });

    it('should calculate voxels_per_mm3', () => {
      const result = calc.calculate('voxels_per_mm3');
      // 1e18 / (250 * 250 * 400) = 4e10
      expect(result).toBeCloseTo(4e10, -8);
    });

    it('should calculate effective_volume', () => {
      const result = calc.calculate('effective_volume');
      // 500 * 16^3 * (1 + 0) = 500 * 4096 = 2,048,000
      expect(result).toBeCloseTo(2048000, -2);
    });

    it('should calculate num_microscopes', () => {
      const result = calc.calculate('num_microscopes');
      // floor(50000000 / 500000) = 100
      expect(result).toBe(100);
    });

    it('should calculate imaging_years', () => {
      const result = calc.calculate('imaging_years');
      // Should be a positive number less than project duration
      expect(result).toBeGreaterThan(0);
      expect(result).toBeLessThan(10);
    });
  });

  describe('full calculation', () => {
    it('should calculate all formulas for mouse + ExM', () => {
      calc.reset()
        .loadShared()
        .loadOrganism('mouse')
        .loadModality('exm')
        .loadProofreading('current');

      const results = calc.calculateAll();

      // Check key outputs exist and are reasonable
      expect(results.voxels_per_mm3).toBeGreaterThan(0);
      expect(results.effective_volume).toBeGreaterThan(0);
      expect(results.imaging_years).toBeGreaterThan(0);
      expect(results.time_to_first_years).toBeGreaterThan(0);
    });

    it('should produce different results for different modalities', () => {
      calc.reset()
        .loadShared()
        .loadOrganism('mouse')
        .loadModality('em')
        .loadProofreading('current');
      const emResults = calc.calculateAll();

      calc.reset()
        .loadShared()
        .loadOrganism('mouse')
        .loadModality('exm')
        .loadProofreading('current');
      const exmResults = calc.calculateAll();

      // EM has smaller voxels, so more voxels per mm³
      expect(emResults.voxels_per_mm3).toBeGreaterThan(exmResults.voxels_per_mm3);

      // ExM has expansion, so larger effective volume
      expect(exmResults.effective_volume).toBeGreaterThan(emResults.effective_volume);
    });

    it('should scale costs with organism size', () => {
      calc.reset()
        .loadShared()
        .loadOrganism('c_elegans')
        .loadModality('exm')
        .loadProofreading('current');
      const wormResults = calc.calculateAll();

      calc.reset()
        .loadShared()
        .loadOrganism('mouse')
        .loadModality('exm')
        .loadProofreading('current');
      const mouseResults = calc.calculateAll();

      // Mouse should take longer than C. elegans
      expect(mouseResults.imaging_days).toBeGreaterThan(wormResults.imaging_days);
    });
  });

  describe('edge cases', () => {
    it('should handle zero values gracefully', () => {
      calc.reset()
        .loadShared()
        .loadOrganism('mouse')
        .loadModality('exm')
        .loadProofreading('current')
        .set('microscope_budget', 0);

      const results = calc.calculateAll();

      // With zero budget, num_microscopes should be 0
      expect(results.num_microscopes).toBe(0);
      // Imaging days should be 0 (handled by IF in formula)
      expect(results.imaging_days).toBe(0);
    });

    it('should throw for unknown organism', () => {
      expect(() => calc.loadOrganism('unknown')).toThrow('Unknown organism');
    });

    it('should throw for unknown modality', () => {
      expect(() => calc.loadModality('unknown')).toThrow('Unknown modality');
    });

    it('should throw for unknown formula', () => {
      expect(() => calc.calculate('nonexistent_formula')).toThrow('Unknown formula');
    });
  });
});
