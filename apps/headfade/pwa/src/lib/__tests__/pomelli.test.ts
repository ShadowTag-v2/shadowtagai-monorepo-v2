import { describe, expect, it } from 'vitest';
import { PomellScorer } from '../pomelli';

describe('PomellScorer', () => {
  const scorer = new PomellScorer();

  it('should detect AI patterns in upload timestamp', () => {
    const metadata = {
      uploadTimestamp: new Date(2023, 1, 1, 12, 0, 0, 0).getTime(), // Round milliseconds
      fileSizeBytes: 123456,
      filename: 'video.mp4',
    };
    const score = scorer.analyze(metadata);
    expect(score).toBeGreaterThanOrEqual(25);
  });

  it('should detect AI patterns in file size (power of 2 / block size)', () => {
    const metadata = {
      uploadTimestamp: Date.now(),
      fileSizeBytes: 4096 * 10,
      filename: 'video.mp4',
    };
    const score = scorer.analyze(metadata);
    expect(score).toBeGreaterThanOrEqual(20);
  });

  it('should detect AI patterns in filename fingerprints', () => {
    const metadata = {
      uploadTimestamp: Date.now(),
      fileSizeBytes: 123456,
      filename: 'diffusion_gen_01.mp4',
    };
    const score = scorer.analyze(metadata);
    expect(score).toBeGreaterThanOrEqual(15);
  });

  it('should return 0 for non-suspicious metadata', () => {
    const metadata = {
      uploadTimestamp: 1677628801234, // Random-ish timestamp
      fileSizeBytes: 123457, // Not multiple of 4096
      filename: 'vacation.mov',
    };
    const score = scorer.analyze(metadata);
    expect(score).toBe(0);
  });

  it('should cap score at 100', () => {
    const metadata = {
      uploadTimestamp: new Date(2023, 1, 1, 12, 0, 0, 0).getTime(),
      fileSizeBytes: 1024 * 1024,
      filename: 'sora_generated_diffusion_h264.mp4',
    };
    const score = scorer.analyze(metadata);
    expect(score).toBe(100);
  });
});
