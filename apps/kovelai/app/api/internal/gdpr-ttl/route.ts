/**
 * Cloud Tasks GDPR TTL Enforcement
 *
 * Sprint Item #9: Automated 30-day data retention enforcement.
 *
 * Architecture:
 * - Cloud Scheduler triggers this function daily at 02:00 UTC
 * - Queries Firestore for expired search intents, sessions, dossiers
 * - Permanently deletes records older than 30 days
 * - Logs deletion count for compliance audit trail
 *
 * GDPR Article 17 — Right to Erasure
 * Client search data MUST be purged within 30 days.
 *
 * @see lib/queue/cloud-tasks.ts — Queue infrastructure
 */

import { z } from 'zod';

// ─── Configuration ──────────────────────────────────────────────────

const GDPR_TTL_DAYS = 30;
const COLLECTIONS_TO_ENFORCE = [
  'search_intents',
  'sessions',
  'dossiers',
  'anxiety_signals',
  'kovel_attestations',
  'audit_logs',
] as const;

const DeleteReportSchema = z.object({
  collection: z.string(),
  deletedCount: z.number().int(),
  cutoffDate: z.string().datetime(),
  executedAt: z.string().datetime(),
});

type DeleteReport = z.infer<typeof DeleteReportSchema>;

// ─── Main Enforcement Function ──────────────────────────────────────

/**
 * Executes GDPR TTL enforcement across all temporal collections.
 *
 * This is the Cloud Tasks handler — triggered by Cloud Scheduler.
 * NOT a Cloud Function — runs as a Cloud Run internal endpoint.
 */
export async function enforceGDPRRetention(): Promise<DeleteReport[]> {
  const cutoffDate = new Date(Date.now() - GDPR_TTL_DAYS * 24 * 60 * 60 * 1000);
  const reports: DeleteReport[] = [];
  const executedAt = new Date().toISOString();

  console.log(`[GDPR TTL] Starting enforcement. Cutoff: ${cutoffDate.toISOString()}`);

  for (const collection of COLLECTIONS_TO_ENFORCE) {
    try {
      const deletedCount = await purgeExpiredDocuments(
        collection,
        cutoffDate,
      );

      const report: DeleteReport = {
        collection,
        deletedCount,
        cutoffDate: cutoffDate.toISOString(),
        executedAt,
      };

      reports.push(report);
      console.log(`[GDPR TTL] ${collection}: deleted ${deletedCount} expired records`);
    } catch (error) {
      console.error(`[GDPR TTL] Failed to purge ${collection}:`, error);
      reports.push({
        collection,
        deletedCount: -1,
        cutoffDate: cutoffDate.toISOString(),
        executedAt,
      });
    }
  }

  // Log the enforcement report to the compliance audit trail
  await logComplianceReport(reports);

  return reports;
}

// ─── Firestore Purge Logic ──────────────────────────────────────────

async function purgeExpiredDocuments(
  collection: string,
  cutoffDate: Date,
): Promise<number> {
  const projectId = process.env.GCP_PROJECT_ID ?? 'shadowtag-omega-v4';
  const databaseId = '(default)';
  const baseUrl = `https://firestore.googleapis.com/v1/projects/${projectId}/databases/${databaseId}/documents`;

  // Query for expired documents
  const queryResponse = await fetch(
    `https://firestore.googleapis.com/v1/projects/${projectId}/databases/${databaseId}/documents:runQuery`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${await getAccessToken()}`,
      },
      body: JSON.stringify({
        structuredQuery: {
          from: [{ collectionId: collection }],
          where: {
            fieldFilter: {
              field: { fieldPath: 'createdAt' },
              op: 'LESS_THAN',
              value: {
                timestampValue: cutoffDate.toISOString(),
              },
            },
          },
          limit: 500,
        },
      }),
    },
  );

  if (!queryResponse.ok) {
    throw new Error(`Firestore query failed: ${queryResponse.status}`);
  }

  const results = await queryResponse.json();
  let deletedCount = 0;

  // Batch delete
  for (const result of results) {
    if (result.document?.name) {
      const deleteResponse = await fetch(`${baseUrl}/${result.document.name}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${await getAccessToken()}`,
        },
      });

      if (deleteResponse.ok) {
        deletedCount++;
      }
    }
  }

  return deletedCount;
}

// ─── Compliance Audit Trail ─────────────────────────────────────────

async function logComplianceReport(reports: DeleteReport[]): Promise<void> {
  const projectId = process.env.GCP_PROJECT_ID ?? 'shadowtag-omega-v4';
  const databaseId = '(default)';

  const totalDeleted = reports.reduce((sum, r) => sum + Math.max(0, r.deletedCount), 0);
  const failedCollections = reports.filter((r) => r.deletedCount === -1);

  const complianceEntry = {
    type: 'GDPR_TTL_ENFORCEMENT',
    executedAt: new Date().toISOString(),
    totalDeleted,
    collectionReports: reports,
    status: failedCollections.length === 0 ? 'SUCCESS' : 'PARTIAL_FAILURE',
    failedCollections: failedCollections.map((r) => r.collection),
    nextScheduledRun: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
  };

  try {
    await fetch(
      `https://firestore.googleapis.com/v1/projects/${projectId}/databases/${databaseId}/documents/gdpr_compliance_log`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await getAccessToken()}`,
        },
        body: JSON.stringify({
          fields: {
            data: { stringValue: JSON.stringify(complianceEntry) },
          },
        }),
      },
    );
  } catch (error) {
    console.error('[GDPR TTL] Failed to log compliance report:', error);
  }
}

// ─── Cloud Scheduler Configuration ──────────────────────────────────

/**
 * Cloud Scheduler job definition (for reference — applied via gcloud CLI):
 *
 * gcloud scheduler jobs create http gdpr-ttl-enforcement \
 *   --schedule="0 2 * * *" \
 *   --time-zone="UTC" \
 *   --uri="https://counselconduit-api.run.app/internal/gdpr-ttl" \
 *   --http-method=POST \
 *   --oidc-service-account-email="counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com" \
 *   --location=us-central1
 */

// ─── Auth Helper ────────────────────────────────────────────────────

async function getAccessToken(): Promise<string> {
  try {
    const res = await fetch(
      'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token',
      { headers: { 'Metadata-Flavor': 'Google' } },
    );
    const data = await res.json();
    return data.access_token;
  } catch {
    return process.env.GOOGLE_ACCESS_TOKEN ?? '';
  }
}

// ─── Next.js API Route Handler ──────────────────────────────────────

import { NextResponse, type NextRequest } from 'next/server';

export async function POST(req: NextRequest): Promise<NextResponse> {
  // Verify internal-only access
  const authHeader = req.headers.get('authorization');
  if (!authHeader?.startsWith('Bearer ') && process.env.NODE_ENV === 'production') {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const reports = await enforceGDPRRetention();
    return NextResponse.json({
      status: 'completed',
      reports,
      totalDeleted: reports.reduce((sum, r) => sum + Math.max(0, r.deletedCount), 0),
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'GDPR enforcement failed', details: error instanceof Error ? error.message : 'Unknown' },
      { status: 500 },
    );
  }
}
