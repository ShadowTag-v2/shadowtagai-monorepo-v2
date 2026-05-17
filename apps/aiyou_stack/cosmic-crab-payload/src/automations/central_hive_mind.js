// apps/ShadowTag-v2_stack/cosmic-crab-payload/src/automations/central_hive_mind.js
const { Firestore, field, countAll } = require("@google-cloud/firestore");

// Initialize the Database referencing the new Cor.Enterprise layout
const db = new Firestore({
  projectId: "shadowtag-omega-v4",
  databaseId: "cor-enterprise-native",
});

async function computeTrendVelocityIndex() {
  console.log("🌊 [HIVE MIND] Executing Native Firestore Pipeline for Global Alpha...");

  // The O(1) Heavy Lift: Aggregate the raw OSINT exhaust ingested by the Jetski fleet
  const snapshot = await db
    .pipeline()
    .collection("global_osint_exhaust")

    // 1. Unnest the arrays.
    // This allows array properties to split into unique rows for counting in real-time.
    .unnest(field("extracted_tags").as("trendName"))

    // 2. Group and count the velocity of each trend directly in the database
    // Because this uses the 2026 update, it bypasses the 1-second index limitation.
    .aggregate({
      accumulators: [countAll().as("velocityScore")],
      groups: ["trendName"],
    })

    // 3. Sort by highest velocity (No pre-built index required!)
    .sort(field("velocityScore").descending())
    .limit(1)
    .execute();

  if (snapshot.docs.length > 0) {
    const topTrend = snapshot.docs[0].data();
    console.log(
      `🔥 HIGH VELOCITY TREND ACQUIRED: ${topTrend.trendName} (Score: ${topTrend.velocityScore})`,
    );
    return topTrend;
  } else {
    console.log("⚠️ [HIVE MIND] Exhaust pipeline dry. Awaiting Jetski payloads.");
    return null;
  }
}

if (require.main === module) {
  // Cloud Run execution binding
  computeTrendVelocityIndex().catch(console.error);
}

module.exports = { computeTrendVelocityIndex };
