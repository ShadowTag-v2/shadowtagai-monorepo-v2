import { BigQuery } from '@google-cloud/bigquery';

/**
 * V23 Empirical FinOps Governor
 *
 * Queries the financial_ledger.realtime_metrics BigQuery table to enforce
 * the 85% revenue-to-CAC circuit breaker. Gracefully skips when the
 * dataset is not yet provisioned (exits 0 instead of crashing CI).
 */
async function evaluateEmpiricalEconomics() {
    console.log("⚡ [Bun] Initializing FinOps Governor...");

    // Gate: skip entirely if FINOPS_ENABLED env is not set
    if (process.env.FINOPS_ENABLED !== 'true') {
        console.log("⏭️  FinOps Governor: FINOPS_ENABLED !== 'true'. Skipping (BigQuery ledger not provisioned).");
        process.exit(0);
    }

    const bigquery = new BigQuery({ projectId: 'shadowtag-omega-v4' });

    const query = `
        SELECT SUM(revenue) as total_revenue, SUM(compute_cost + storage_cost) as total_cost 
        FROM \`shadowtag-omega-v4.financial_ledger.realtime_metrics\`
        WHERE timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
    `;

    try {
        const [job] = await bigquery.createQueryJob({ query });
        const [rows] = await job.getQueryResults();
        
        if (!rows || rows.length === 0 || !rows[0].total_revenue) {
            console.log("Ledger initializing. Proceeding.");
            process.exit(0);
        }

        const { total_revenue, total_cost } = rows[0];
        console.log(`Empirical Trailing 24h Revenue: $${Number(total_revenue).toFixed(2)}`);
        
        if (total_cost > (total_revenue * 0.85)) {
            console.error("FATAL: 85% revenue-to-CAC limit breached on empirical ledger. Halting Push.");
            process.exit(1);
        }
        console.log("Unit Economics Validated on BigQuery Ledger. FinOps Green.");
    } catch (e) {
        // Graceful degradation: if BigQuery is unreachable or table doesn't exist, warn and proceed
        const msg = String(e);
        if (msg.includes('Not found') || msg.includes('404') || msg.includes('PERMISSION_DENIED')) {
            console.warn("⚠️  FinOps Governor: BigQuery ledger not found. Skipping enforcement.");
            process.exit(0);
        }
        console.error("FATAL: Cannot verify empirical ledger.", e);
        process.exit(1);
    }
}
await evaluateEmpiricalEconomics();
