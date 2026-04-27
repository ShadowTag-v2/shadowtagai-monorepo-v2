import { normalizeString } from '../string.utils';

describe('normalizeString', () => {
  it('converts to lowercase and removes spaces and punctuation', () => {
    expect(normalizeString('Hello World! 123')).toBe('helloworld123');
  });

  it('preserves Unicode letters and digits, removes symbols', () => {
    expect(normalizeString('ŁÓDŹ 50%')).toBe('łódź50');
  });

  it('removes emojis and symbols while keeping letters and digits', () => {
    expect(normalizeString('foo😀bar—baz_123')).toBe('foobarbaz123');
  });

  it('preserves accented characters', () => {
    expect(normalizeString('café, naïve & résumé')).toBe('cafénaïverésumé');
  });

  it('strips currency symbols and punctuation inside numbers', () => {
    expect(normalizeString('Price: $99.99')).toBe('price9999');
  });

  it('handles empty string', () => {
    expect(normalizeString('')).toBe('');
  });

  it('returns empty string when input contains only symbols', () => {
    expect(normalizeString("$%^&*()—_+=[]{}|;:'\"<>,.?/`~"))
      .toBe('');
  });

  it('preserves CJK characters', () => {
    expect(normalizeString('漢字テスト123!')).toBe('漢字テスト123');
  });

  it('preserves RTL scripts (Hebrew/Arabic)', () => {
    expect(normalizeString('שלום123!')).toBe('שלום123');
    expect(normalizeString('مرحبا 456?')).toBe('مرحبا456');
  });

  it('removes quotes and special punctuation', () => {
    expect(normalizeString('Test$123\'abc"'))
      .toBe('test123abc');
  });
});
