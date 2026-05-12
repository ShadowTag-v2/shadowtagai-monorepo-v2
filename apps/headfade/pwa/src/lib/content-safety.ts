/**
 * HeadFade Content Safety & Moderation Pipeline
 *
 * Multi-layered content moderation system using industry-standard APIs
 * for detecting and filtering illegal and harmful content.
 *
 * Categories covered:
 * 1. CSAM detection & NCMEC reporting (18 U.S.C. § 2258A)
 * 2. Non-consensual intimate imagery / deepfake detection
 * 3. Pornographic content filtering
 * 4. Violent extremism content flagging (actual incitement to violence)
 * 5. Spam and bot detection
 *
 * Integration points:
 * - Google Cloud Vision SafeSearch API
 * - PhotoDNA / Microsoft CSAM hash matching
 * - NCMEC CyberTipline reporting
 * - Internal moderation queue
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type SafetyVerdict = 'APPROVED' | 'FLAGGED_FOR_REVIEW' | 'BLOCKED' | 'REPORTED_NCMEC';

export type SafetyCategory =
  | 'CSAM'
  | 'NCII_DEEPFAKE'
  | 'PORNOGRAPHY'
  | 'VIOLENT_EXTREMISM'
  | 'SPAM_BOT'
  | 'SAFE';

export interface SafeSearchAnnotation {
  adult: LikelihoodLevel;
  spoof: LikelihoodLevel;
  medical: LikelihoodLevel;
  violence: LikelihoodLevel;
  racy: LikelihoodLevel;
}

export type LikelihoodLevel =
  | 'UNKNOWN'
  | 'VERY_UNLIKELY'
  | 'UNLIKELY'
  | 'POSSIBLE'
  | 'LIKELY'
  | 'VERY_LIKELY';

export interface ModerationResult {
  contentId: string;
  verdict: SafetyVerdict;
  category: SafetyCategory;
  confidence: number;
  details: string;
  timestamp: string;
  reviewRequired: boolean;
  ncmecReportId?: string;
}

export interface ContentSubmission {
  contentId: string;
  mediaUrl: string;
  mediaType: 'image' | 'video' | 'text';
  uploaderUserId: string;
  uploaderIp: string;
  textContent?: string;
  metadata?: Record<string, string>;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const LIKELIHOOD_SCORES: Record<LikelihoodLevel, number> = {
  UNKNOWN: 0,
  VERY_UNLIKELY: 0.05,
  UNLIKELY: 0.2,
  POSSIBLE: 0.5,
  LIKELY: 0.8,
  VERY_LIKELY: 0.95,
};

/** Threshold above which content is auto-blocked */
const AUTO_BLOCK_THRESHOLD = 0.8;
/** Threshold above which content goes to human review */
const REVIEW_THRESHOLD = 0.5;

// ---------------------------------------------------------------------------
// 1. Google Cloud Vision SafeSearch Integration
// ---------------------------------------------------------------------------

/**
 * Calls the Google Cloud Vision SafeSearch API to classify an image.
 *
 * Requires: `GOOGLE_CLOUD_PROJECT_ID` env var and ADC credentials.
 * API: https://cloud.google.com/vision/docs/detecting-safe-search
 */
export async function analyzeImageSafeSearch(imageUri: string): Promise<SafeSearchAnnotation> {
  const projectId = process.env.GOOGLE_CLOUD_PROJECT_ID;
  if (!projectId) {
    throw new Error('GOOGLE_CLOUD_PROJECT_ID is required for Vision API calls');
  }

  const endpoint = `https://vision.googleapis.com/v1/images:annotate`;

  const requestBody = {
    requests: [
      {
        image: { source: { imageUri } },
        features: [{ type: 'SAFE_SEARCH_DETECTION', maxResults: 1 }],
      },
    ],
  };

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${await getAccessToken()}`,
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Vision API error ${response.status}: ${errorText}`);
  }

  const data = await response.json();
  const annotation = data.responses?.[0]?.safeSearchAnnotation;

  if (!annotation) {
    return {
      adult: 'UNKNOWN',
      spoof: 'UNKNOWN',
      medical: 'UNKNOWN',
      violence: 'UNKNOWN',
      racy: 'UNKNOWN',
    };
  }

  return annotation as SafeSearchAnnotation;
}

// ---------------------------------------------------------------------------
// 2. CSAM Detection & NCMEC Reporting
// ---------------------------------------------------------------------------

/**
 * Checks content against known CSAM hash databases.
 *
 * In production, this integrates with:
 * - Microsoft PhotoDNA Cloud Service
 * - NCMEC hash list
 * - Google Content Safety API CSAM classifier
 *
 * Any positive match MUST be:
 * 1. Immediately blocked
 * 2. Preserved (not deleted) for law enforcement
 * 3. Reported to NCMEC CyberTipline within 24 hours
 * 4. User account suspended pending investigation
 *
 * Per 18 U.S.C. § 2258A, electronic service providers are REQUIRED
 * to report apparent CSAM to NCMEC.
 */
export async function checkCSAM(submission: ContentSubmission): Promise<ModerationResult> {
  // Step 1: Compute perceptual hash and check against PhotoDNA database
  const hashMatch = await checkPhotoHashDatabase(submission.mediaUrl);

  if (hashMatch.isMatch) {
    // MANDATORY: Report to NCMEC CyberTipline
    const ncmecReportId = await reportToNCMEC({
      contentId: submission.contentId,
      mediaUrl: submission.mediaUrl,
      uploaderUserId: submission.uploaderUserId,
      uploaderIp: submission.uploaderIp,
      detectionMethod: 'PhotoDNA hash match',
      confidence: hashMatch.confidence,
    });

    return {
      contentId: submission.contentId,
      verdict: 'REPORTED_NCMEC',
      category: 'CSAM',
      confidence: hashMatch.confidence,
      details: `PhotoDNA hash match detected. NCMEC report filed.`,
      timestamp: new Date().toISOString(),
      reviewRequired: false, // Auto-action required by law
      ncmecReportId,
    };
  }

  // Step 2: Run through ML classifier as secondary check
  const classifierResult = await runCSAMClassifier(submission.mediaUrl);

  if (classifierResult.score >= AUTO_BLOCK_THRESHOLD) {
    const ncmecReportId = await reportToNCMEC({
      contentId: submission.contentId,
      mediaUrl: submission.mediaUrl,
      uploaderUserId: submission.uploaderUserId,
      uploaderIp: submission.uploaderIp,
      detectionMethod: 'ML classifier',
      confidence: classifierResult.score,
    });

    return {
      contentId: submission.contentId,
      verdict: 'REPORTED_NCMEC',
      category: 'CSAM',
      confidence: classifierResult.score,
      details: `ML classifier flagged content. NCMEC report filed.`,
      timestamp: new Date().toISOString(),
      reviewRequired: false,
      ncmecReportId,
    };
  }

  if (classifierResult.score >= REVIEW_THRESHOLD) {
    return {
      contentId: submission.contentId,
      verdict: 'FLAGGED_FOR_REVIEW',
      category: 'CSAM',
      confidence: classifierResult.score,
      details: `ML classifier flagged for human review.`,
      timestamp: new Date().toISOString(),
      reviewRequired: true,
    };
  }

  return {
    contentId: submission.contentId,
    verdict: 'APPROVED',
    category: 'SAFE',
    confidence: 1 - classifierResult.score,
    details: 'Passed CSAM screening.',
    timestamp: new Date().toISOString(),
    reviewRequired: false,
  };
}

// ---------------------------------------------------------------------------
// 3. Non-Consensual Intimate Imagery / Deepfake Detection
// ---------------------------------------------------------------------------

/**
 * Detects non-consensual intimate imagery and sexual deepfakes.
 *
 * Uses a combination of:
 * - Face manipulation detection (GAN artifact analysis)
 * - Known victim hash databases (e.g., StopNCII.org)
 * - Explicit content + face detection co-occurrence
 */
export async function checkNCII(submission: ContentSubmission): Promise<ModerationResult> {
  // Check against StopNCII.org hash database
  const stopNCIIResult = await checkStopNCIIHashes(submission.mediaUrl);

  if (stopNCIIResult.isMatch) {
    return {
      contentId: submission.contentId,
      verdict: 'BLOCKED',
      category: 'NCII_DEEPFAKE',
      confidence: stopNCIIResult.confidence,
      details: 'Matched StopNCII.org hash database. Content blocked.',
      timestamp: new Date().toISOString(),
      reviewRequired: false,
    };
  }

  // Run deepfake detection model
  const deepfakeScore = await analyzeDeepfakeIndicators(submission.mediaUrl);

  // Check if explicit content contains identifiable faces (NCII signal)
  const safeSearch = await analyzeImageSafeSearch(submission.mediaUrl);
  const isExplicit = LIKELIHOOD_SCORES[safeSearch.adult] >= AUTO_BLOCK_THRESHOLD;

  if (isExplicit && deepfakeScore >= REVIEW_THRESHOLD) {
    return {
      contentId: submission.contentId,
      verdict: 'BLOCKED',
      category: 'NCII_DEEPFAKE',
      confidence: deepfakeScore,
      details: 'Explicit content with deepfake indicators detected. Auto-blocked.',
      timestamp: new Date().toISOString(),
      reviewRequired: true,
    };
  }

  return {
    contentId: submission.contentId,
    verdict: 'APPROVED',
    category: 'SAFE',
    confidence: 1 - deepfakeScore,
    details: 'Passed NCII/deepfake screening.',
    timestamp: new Date().toISOString(),
    reviewRequired: false,
  };
}

// ---------------------------------------------------------------------------
// 4. Pornographic Content Filtering
// ---------------------------------------------------------------------------

/**
 * Filters pornographic content using Google Cloud Vision SafeSearch.
 * Blocks content classified as LIKELY or VERY_LIKELY adult.
 */
export async function checkPornography(submission: ContentSubmission): Promise<ModerationResult> {
  const safeSearch = await analyzeImageSafeSearch(submission.mediaUrl);

  const adultScore = LIKELIHOOD_SCORES[safeSearch.adult];
  const racyScore = LIKELIHOOD_SCORES[safeSearch.racy];

  if (adultScore >= AUTO_BLOCK_THRESHOLD) {
    return {
      contentId: submission.contentId,
      verdict: 'BLOCKED',
      category: 'PORNOGRAPHY',
      confidence: adultScore,
      details: `SafeSearch adult=${safeSearch.adult}. Auto-blocked.`,
      timestamp: new Date().toISOString(),
      reviewRequired: false,
    };
  }

  if (adultScore >= REVIEW_THRESHOLD || racyScore >= AUTO_BLOCK_THRESHOLD) {
    return {
      contentId: submission.contentId,
      verdict: 'FLAGGED_FOR_REVIEW',
      category: 'PORNOGRAPHY',
      confidence: Math.max(adultScore, racyScore),
      details: `SafeSearch adult=${safeSearch.adult}, racy=${safeSearch.racy}. Flagged for review.`,
      timestamp: new Date().toISOString(),
      reviewRequired: true,
    };
  }

  return {
    contentId: submission.contentId,
    verdict: 'APPROVED',
    category: 'SAFE',
    confidence: 1 - adultScore,
    details: 'Passed pornography screening.',
    timestamp: new Date().toISOString(),
    reviewRequired: false,
  };
}

// ---------------------------------------------------------------------------
// 5. Violent Extremism Content Flagging
// ---------------------------------------------------------------------------

/**
 * Flags content that constitutes actual incitement to violence.
 *
 * This checks for:
 * - Direct calls to commit acts of violence against specific targets
 * - Glorification of terrorist attacks
 * - Recruitment material for designated terrorist organizations
 * - Instructions for creating weapons / explosive devices
 *
 * This does NOT flag political opinions, protests, or dissent.
 */
export async function checkViolentExtremism(
  submission: ContentSubmission,
): Promise<ModerationResult> {
  const results: { score: number; signal: string }[] = [];

  // Check visual content for graphic violence
  if (submission.mediaType === 'image' || submission.mediaType === 'video') {
    const safeSearch = await analyzeImageSafeSearch(submission.mediaUrl);
    const violenceScore = LIKELIHOOD_SCORES[safeSearch.violence];

    if (violenceScore >= AUTO_BLOCK_THRESHOLD) {
      results.push({
        score: violenceScore,
        signal: `Graphic violence: ${safeSearch.violence}`,
      });
    }
  }

  // Check text content for incitement patterns
  if (submission.textContent) {
    const textResult = await analyzeTextForIncitement(submission.textContent);
    if (textResult.score >= REVIEW_THRESHOLD) {
      results.push({
        score: textResult.score,
        signal: textResult.signal,
      });
    }
  }

  if (results.length === 0) {
    return {
      contentId: submission.contentId,
      verdict: 'APPROVED',
      category: 'SAFE',
      confidence: 0.95,
      details: 'Passed violent extremism screening.',
      timestamp: new Date().toISOString(),
      reviewRequired: false,
    };
  }

  const maxScore = Math.max(...results.map((r) => r.score));
  const signals = results.map((r) => r.signal).join('; ');

  return {
    contentId: submission.contentId,
    verdict: maxScore >= AUTO_BLOCK_THRESHOLD ? 'BLOCKED' : 'FLAGGED_FOR_REVIEW',
    category: 'VIOLENT_EXTREMISM',
    confidence: maxScore,
    details: signals,
    timestamp: new Date().toISOString(),
    reviewRequired: true,
  };
}

// ---------------------------------------------------------------------------
// 6. Spam & Bot Detection
// ---------------------------------------------------------------------------

/**
 * Detects spam content and bot-generated submissions.
 *
 * Signals include:
 * - Rapid-fire posting from same IP/account
 * - Known spam URL patterns
 * - Duplicate content fingerprints
 * - Account age < threshold with high activity
 */
export async function checkSpamBot(submission: ContentSubmission): Promise<ModerationResult> {
  const signals: { score: number; reason: string }[] = [];

  // Rate-limit check
  const rateResult = await checkRateLimit(submission.uploaderUserId, submission.uploaderIp);
  if (rateResult.exceeded) {
    signals.push({ score: 0.9, reason: 'Rate limit exceeded' });
  }

  // Duplicate content fingerprint
  const duplicateResult = await checkContentFingerprint(submission.contentId);
  if (duplicateResult.isDuplicate) {
    signals.push({
      score: 0.85,
      reason: `Duplicate of content ${duplicateResult.originalId}`,
    });
  }

  // Text spam patterns
  if (submission.textContent) {
    const spamScore = analyzeTextSpamSignals(submission.textContent);
    if (spamScore >= REVIEW_THRESHOLD) {
      signals.push({ score: spamScore, reason: 'Text spam patterns detected' });
    }
  }

  if (signals.length === 0) {
    return {
      contentId: submission.contentId,
      verdict: 'APPROVED',
      category: 'SAFE',
      confidence: 0.95,
      details: 'Passed spam/bot screening.',
      timestamp: new Date().toISOString(),
      reviewRequired: false,
    };
  }

  const maxScore = Math.max(...signals.map((s) => s.score));
  const reasons = signals.map((s) => s.reason).join('; ');

  return {
    contentId: submission.contentId,
    verdict: maxScore >= AUTO_BLOCK_THRESHOLD ? 'BLOCKED' : 'FLAGGED_FOR_REVIEW',
    category: 'SPAM_BOT',
    confidence: maxScore,
    details: reasons,
    timestamp: new Date().toISOString(),
    reviewRequired: maxScore < AUTO_BLOCK_THRESHOLD,
  };
}

// ---------------------------------------------------------------------------
// Main Pipeline Orchestrator
// ---------------------------------------------------------------------------

/**
 * Runs the full content safety pipeline.
 *
 * Order matters — CSAM is checked first because it has mandatory
 * legal reporting obligations under 18 U.S.C. § 2258A.
 */
export async function runContentSafetyPipeline(
  submission: ContentSubmission,
): Promise<ModerationResult> {
  // Stage 1: CSAM (mandatory legal reporting — always first)
  const csamResult = await checkCSAM(submission);
  if (csamResult.verdict !== 'APPROVED') {
    await logModerationAction(csamResult);
    return csamResult;
  }

  // Stage 2: NCII / Deepfakes
  const nciiResult = await checkNCII(submission);
  if (nciiResult.verdict !== 'APPROVED') {
    await logModerationAction(nciiResult);
    return nciiResult;
  }

  // Stage 3: Pornography
  const pornResult = await checkPornography(submission);
  if (pornResult.verdict !== 'APPROVED') {
    await logModerationAction(pornResult);
    return pornResult;
  }

  // Stage 4: Violent extremism
  const violenceResult = await checkViolentExtremism(submission);
  if (violenceResult.verdict !== 'APPROVED') {
    await logModerationAction(violenceResult);
    return violenceResult;
  }

  // Stage 5: Spam / Bot
  const spamResult = await checkSpamBot(submission);
  if (spamResult.verdict !== 'APPROVED') {
    await logModerationAction(spamResult);
    return spamResult;
  }

  // All clear
  const approvedResult: ModerationResult = {
    contentId: submission.contentId,
    verdict: 'APPROVED',
    category: 'SAFE',
    confidence: 0.99,
    details: 'Passed all safety checks.',
    timestamp: new Date().toISOString(),
    reviewRequired: false,
  };

  await logModerationAction(approvedResult);
  return approvedResult;
}

// ---------------------------------------------------------------------------
// Internal Helper Stubs (replace with real integrations in production)
// ---------------------------------------------------------------------------

async function getAccessToken(): Promise<string> {
  // In production: use google-auth-library to get ADC token
  // const { GoogleAuth } = require('google-auth-library');
  // const auth = new GoogleAuth({ scopes: ['https://www.googleapis.com/auth/cloud-vision'] });
  // const client = await auth.getClient();
  // const { token } = await client.getAccessToken();
  // return token;
  throw new Error('getAccessToken() requires google-auth-library with ADC configured');
}

async function checkPhotoHashDatabase(
  _mediaUrl: string,
): Promise<{ isMatch: boolean; confidence: number }> {
  // Integration point: Microsoft PhotoDNA Cloud Service
  // https://www.microsoft.com/en-us/photodna
  return { isMatch: false, confidence: 0 };
}

interface NCMECReport {
  contentId: string;
  mediaUrl: string;
  uploaderUserId: string;
  uploaderIp: string;
  detectionMethod: string;
  confidence: number;
}

async function reportToNCMEC(report: NCMECReport): Promise<string> {
  return `NCMEC-${Date.now()}-${report.contentId}`;
}

async function runCSAMClassifier(_mediaUrl: string): Promise<{ score: number }> {
  // Integration point: Google Content Safety API or equivalent ML classifier
  return { score: 0 };
}

async function checkStopNCIIHashes(
  _mediaUrl: string,
): Promise<{ isMatch: boolean; confidence: number }> {
  // Integration point: StopNCII.org hash sharing API
  // https://stopncii.org/
  return { isMatch: false, confidence: 0 };
}

async function analyzeDeepfakeIndicators(_mediaUrl: string): Promise<number> {
  // Integration point: Deepfake detection model
  // Analyze GAN artifacts, facial inconsistencies, temporal anomalies
  return 0;
}

async function analyzeTextForIncitement(_text: string): Promise<{ score: number; signal: string }> {
  // Integration point: NLP classifier for incitement to violence
  // Checks for direct calls to violence, not political opinions
  return { score: 0, signal: '' };
}

async function checkRateLimit(_userId: string, _ip: string): Promise<{ exceeded: boolean }> {
  // Integration point: Rate limiter (e.g., Redis sliding window)
  return { exceeded: false };
}

async function checkContentFingerprint(
  _contentId: string,
): Promise<{ isDuplicate: boolean; originalId?: string }> {
  // Integration point: Content fingerprint database
  return { isDuplicate: false };
}

function analyzeTextSpamSignals(text: string): number {
  let score = 0;
  const lowerText = text.toLowerCase();

  // Excessive caps
  const capsRatio = (text.match(/[A-Z]/g)?.length ?? 0) / Math.max(text.length, 1);
  if (capsRatio > 0.6) score += 0.3;

  // Excessive exclamation/question marks
  const punctuationCount = text.match(/[!?]{2,}/g)?.length ?? 0;
  if (punctuationCount > 3) score += 0.2;

  // Known spam phrases
  const spamPhrases = [
    'click here',
    'free money',
    'act now',
    'limited time',
    'congratulations you won',
    'earn from home',
  ];
  for (const phrase of spamPhrases) {
    if (lowerText.includes(phrase)) {
      score += 0.25;
    }
  }

  // Excessive URLs
  const urlCount = text.match(/https?:\/\//g)?.length ?? 0;
  if (urlCount > 3) score += 0.3;

  return Math.min(score, 1);
}

async function logModerationAction(result: ModerationResult): Promise<void> {
  // Integration point: Firestore moderation_logs collection
  // Store: contentId, verdict, category, confidence, timestamp, reviewerId (if human)
  console.log(
    `[MODERATION] ${result.verdict} | ${result.category} | ` +
      `confidence=${result.confidence.toFixed(2)} | ${result.details}`,
  );
}
