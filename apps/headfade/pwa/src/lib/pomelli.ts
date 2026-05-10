export interface VideoMetadata {
  uploadTimestamp: number;
  fileSizeBytes: number;
  filename: string;
}

/**
 * PomellScorer analyzes video metadata to detect AI-generation patterns.
 * Part of the Pomelli AI-detection suite for HeadFade.
 */
export class PomellScorer {
  /**
   * Analyzes video metadata and returns a confidence score 0-100 for AI-generation likelihood.
   */
  analyze(metadata: VideoMetadata): number {
    let score = 0;

    // 1. uploadTimestamp patterns
    // Heuristic: AI generations are often processed in batches, resulting in round timestamps
    // or specific millisecond patterns from automated uploaders.
    const date = new Date(metadata.uploadTimestamp);
    if (date.getMilliseconds() === 0) {
      score += 25;
    }
    if (date.getSeconds() === 0 && date.getMinutes() % 5 === 0) {
      score += 15;
    }

    // 2. fileSizeBytes distributions
    // Heuristic: AI-generated media often exhibits very specific compression ratios
    // resulting in file sizes that are multiples of common block sizes or power-of-2.
    if (metadata.fileSizeBytes % 4096 === 0) {
      score += 20;
    }
    // High entropy or unusually small/large sizes for the duration (not available here)
    // could be another indicator.

    // 3. Codec fingerprints from filename
    // Heuristic: Filenames containing specific codec markers or "generated" tags.
    const filenameLower = metadata.filename.toLowerCase();
    const aiFingerprints = [
      'h264',
      'hevc',
      'av1',
      'vp9',
      'crf',
      'ffmpeg',
      'generated',
      'diffusion',
      'sora',
      'luma',
    ];

    for (const fingerprint of aiFingerprints) {
      if (filenameLower.includes(fingerprint)) {
        score += 15;
        break; // Count at most once for simplicity
      }
    }

    // 4. Distribution patterns
    // If the size is exactly a round number of megabytes (common in some synthetic datasets)
    if (metadata.fileSizeBytes % (1024 * 1024) === 0) {
      score += 30;
    }

    // Return confidence score capped at 100
    return Math.min(score, 100);
  }
}
