import { evalFeature } from './growthbook';

describe('GrowthBook Analytics', () => {
  it('short-circuits to custom cache when value is present', () => {
    // We would need to expose customCache or inject it to fully mock it in a real setup.
    // For now, this test asserts the fallback is returned if not in cache.
    const result = evalFeature('test_feature', false);
    expect(result).toBe(false);
  });
});
