import { describe, it, expect } from 'vitest';
import { loadCassette, validateCassette, discoverCassettes, runBughunterScan, formatResults } from '../../../src/commands/bughunter.js';
import type { CassetteFile } from '../../../src/commands/bughunter.js';
import { join } from 'path';

const FIXTURES_DIR = join(__dirname, '..', '..', 'fixtures', 'vcr');

describe('Bughunter: loadCassette', () => {
  it('loads a valid cassette', () => {
    const c = loadCassette(join(FIXTURES_DIR, 'firestore-read.json'));
    expect(c.name).toBe('firestore-read');
    expect(c.interactions.length).toBeGreaterThan(0);
  });

  it('throws on invalid JSON', () => {
    expect(() => loadCassette('/nonexistent/path.json')).toThrow();
  });
});

describe('Bughunter: validateCassette', () => {
  it('returns no errors for valid cassette', () => {
    const c: CassetteFile = {
      name: 'test',
      interactions: [{
        request: { method: 'GET', url: 'https://api.example.com/test' },
        response: { status_code: 200, body: '{"ok":true}' },
      }],
    };
    expect(validateCassette(c)).toEqual([]);
  });

  it('flags empty cassettes', () => {
    const c: CassetteFile = { name: 'empty', interactions: [] };
    const errors = validateCassette(c);
    expect(errors.length).toBe(1);
    expect(errors[0]).toContain('Empty cassette');
  });

  it('flags missing request method', () => {
    const c: CassetteFile = {
      name: 'bad',
      interactions: [{
        request: { method: '', url: 'https://api.example.com' },
        response: { status_code: 200, body: '{}' },
      }],
    };
    const errors = validateCassette(c);
    expect(errors.some(e => e.includes('Missing request method'))).toBe(true);
  });

  it('flags server errors', () => {
    const c: CassetteFile = {
      name: 'err',
      interactions: [{
        request: { method: 'GET', url: 'https://api.example.com' },
        response: { status_code: 503, body: 'Service Unavailable' },
      }],
    };
    expect(validateCassette(c).some(e => e.includes('server error'))).toBe(true);
  });

  it('flags unscrubbed Bearer tokens', () => {
    const c: CassetteFile = {
      name: 'leak',
      interactions: [{
        request: { method: 'GET', url: 'https://api.example.com', headers: { Authorization: 'Bearer eyJhbGciOiJSUzI1NiJ9' } },
        response: { status_code: 200, body: '{}' },
      }],
    };
    expect(validateCassette(c).some(e => e.includes('Unscrubbed Bearer'))).toBe(true);
  });
});

describe('Bughunter: discoverCassettes', () => {
  it('discovers JSON cassettes in fixture dir', () => {
    const paths = discoverCassettes(FIXTURES_DIR);
    expect(paths.length).toBeGreaterThan(0);
    expect(paths.every(p => p.endsWith('.json'))).toBe(true);
  });

  it('returns empty for nonexistent dir', () => {
    expect(discoverCassettes('/nonexistent')).toEqual([]);
  });
});

describe('Bughunter: runBughunterScan', () => {
  it('returns results for fixture dir', () => {
    const results = runBughunterScan(FIXTURES_DIR);
    expect(results.length).toBeGreaterThan(0);
    for (const r of results) {
      expect(r.cassette).toBeTruthy();
      expect(typeof r.totalInteractions).toBe('number');
    }
  });
});

describe('Bughunter: formatResults', () => {
  it('formats empty results', () => {
    expect(formatResults([])).toContain('No cassettes found');
  });

  it('formats results with box drawing', () => {
    const results = [{ cassette: 'test', totalInteractions: 2, passed: 2, failed: 0, errors: [] }];
    const output = formatResults(results);
    expect(output).toContain('BUGHUNTER');
    expect(output).toContain('✓');
  });
});
