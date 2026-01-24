import { readFileSync, writeFileSync, readdirSync } from 'fs';
import { join } from 'path';

/**
 * Parse a TSV file into an array of objects
 */
export function readTSV<T extends Record<string, string>>(filepath: string): T[] {
  const content = readFileSync(filepath, 'utf-8');
  // Handle both Unix (\n) and Windows (\r\n) line endings
  const lines = content.trim().replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n');

  if (lines.length < 2) {
    return [];
  }

  // Trim whitespace from headers and values
  const headers = lines[0].split('\t').map(h => h.trim());
  const rows: T[] = [];

  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split('\t').map(v => v.trim());
    const row: Record<string, string> = {};

    for (let j = 0; j < headers.length; j++) {
      row[headers[j]] = values[j] || '';
    }

    rows.push(row as T);
  }

  return rows;
}

/**
 * Write an array of objects to a TSV file
 */
export function writeTSV(filepath: string, data: Record<string, unknown>[], columns: string[]): void {
  const header = columns.join('\t');
  const rows = data.map(row => columns.map(col => String(row[col] ?? '')).join('\t'));
  writeFileSync(filepath, [header, ...rows].join('\n'));
}

/**
 * Write content to a file
 */
export function writeFile(filepath: string, content: string): void {
  writeFileSync(filepath, content);
}

/**
 * Convert a string to camelCase
 */
export function camelCase(str: string): string {
  return str
    .toLowerCase()
    .replace(/[^a-zA-Z0-9]+(.)/g, (_, chr) => chr.toUpperCase())
    .replace(/^./, chr => chr.toLowerCase());
}

/**
 * Convert a string to a valid TypeScript identifier
 */
export function toIdentifier(str: string): string {
  return str
    .replace(/[^a-zA-Z0-9_]/g, '_')
    .replace(/^(\d)/, '_$1')
    .replace(/_+/g, '_')
    .replace(/^_|_$/g, '');
}

/**
 * List all TSV files in a directory
 */
export function listTSVFiles(dir: string): string[] {
  return readdirSync(dir)
    .filter(f => f.endsWith('.tsv'))
    .map(f => join(dir, f));
}

/**
 * Format a number for display
 */
export function formatNumber(n: number): string {
  if (Math.abs(n) >= 1e12) return `${(n / 1e12).toFixed(1)}T`;
  if (Math.abs(n) >= 1e9) return `${(n / 1e9).toFixed(1)}B`;
  if (Math.abs(n) >= 1e6) return `${(n / 1e6).toFixed(1)}M`;
  if (Math.abs(n) >= 1e3) return `${(n / 1e3).toFixed(1)}K`;
  if (Number.isInteger(n)) return n.toString();
  return n.toFixed(2);
}
