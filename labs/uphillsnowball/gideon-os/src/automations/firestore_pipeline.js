/**
 * src/automations/firestore_pipeline.js
 * Firestore Enterprise Pipelines — The 86% Compute Slaughter
 * O(1) Aggregation for the Central Hive Mind.
 * Replaces Redis + BigQuery with native Firestore .pipeline() functions.
 *
 * Deployed on Cloud Run Jobs.
 */

const { Firestore, field, countAll } = require('@google-cloud/firestore');
const db = new Firestore({ databaseId: 'cor-enterprise-native' });

/**
 * Compute the Trend Velocity Index using native Firestore pipeline aggregation.
 * Replaces the previous BigQuery SQL + Redis cache topology.
 * @returns {Promise<{trendName: string, velocityScore: number}>}
 */
async function computeTrendVelocityIndex() {
  console.log('🌊 [HIVE MIND] Executing Native Firestore Pipeline for Global Alpha...');

  // The O(1) Heavy Lift: Aggregate OSINT exhaust ingested by the Jetski fleet
  const snapshot = await db.pipeline()
    .collection('global_osint_exhaust')
    .unnest(field('extracted_tags').as('trendName'))
    .aggregate({
      accumulators: [countAll().as('velocityScore')],
      groups: ['trendName'],
    })
    .sort(field('velocityScore').descending())
    .limit(1)
    .execute();

  if (snapshot.docs.length === 0) {
    console.warn('⚠️ No OSINT data found in pipeline.');
    return { trendName: 'NONE', velocityScore: 0 };
  }

  const topTrend = snapshot.docs[0].data();
  console.log(`🔥 HIGH VELOCITY TREND ACQUIRED: ${topTrend.trendName} (Score: ${topTrend.velocityScore})`);
  return topTrend;
}

/**
 * Fetch compliance telemetry for the CISO Dashboard.
 * Uses native Firestore pipeline aggregation instead of BigQuery SQL.
 * @returns {Promise<Array<{layerId: string, failureCount: number}>>}
 */
async function fetchComplianceTelemetry() {
  console.log('📊 [CISO] Fetching compliance telemetry via Firestore Pipeline...');

  const telemetry = await db.pipeline()
    .collection('whiteboard_issues')
    .where(field('status').equal('KICKBACK_LOOP'))
    .unnest(field('violated_layers').as('layerId'))
    .aggregate({
      accumulators: [countAll().as('failureCount')],
      groups: ['layerId'],
    })
    .sort(field('failureCount').descending())
    .execute();

  return telemetry.docs.map((doc) => doc.data());
}

module.exports = { computeTrendVelocityIndex, fetchComplianceTelemetry };
