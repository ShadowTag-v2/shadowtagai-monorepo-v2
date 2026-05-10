import { verifySyntheticVideo } from '../src/tools/verify_synthetic_video.js';

// Mock the dependency
jest.mock('../src/utils/firebase-data-connect.js', () => ({
  executeGetVideoForensicsQuery: jest.fn().mockImplementation(({ id }) => {
    if (id === 'demo-123') {
      return Promise.resolve({
        video: {
          hdiScore: 95,
          modelsUsed: ['Veo 3.1', 'Gemini 3.1'],
          parentCreatorId: 'orig_123',
          remixTree: [],
        },
      });
    }
    return Promise.resolve({ video: null });
  }),
}));

describe('verifySyntheticVideo', () => {
  it('should return UNKNOWN for a non-existent video', async () => {
    const result = await verifySyntheticVideo('invalid-id', 'test_auth');
    expect(result.content[0].text).toContain('UNKNOWN: Video not found');
  });

  it('should return PROVENANCE analysis for a valid video', async () => {
    const result = await verifySyntheticVideo('demo-123', 'test_auth');
    expect(result.content[0].text).toContain('HEADFADE VERIFIED PROVENANCE');
    expect(result.content[0].text).toContain('95%');
    expect(result.content[0].text).toContain('Veo 3.1 + Gemini 3.1');
  });
});
