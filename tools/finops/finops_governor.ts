import { BigQuery } from '@google-cloud/bigquery';

async function evaluateEmpiricalEconomics() {
    console.log("⚡ [Bun] Initializing Opus 4.6 FinOps Governor...");
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
        console.error("FATAL: Cannot verify empirical ledger.", e);
        process.exit(1);
    }
}
await evaluateEmpiricalEconomics();
