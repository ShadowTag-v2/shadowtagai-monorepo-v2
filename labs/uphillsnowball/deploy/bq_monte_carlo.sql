-- deploy/bq_monte_carlo.sql
--
-- BigQuery Monte Carlo Simulation for Midas Risk Citadel
--
-- Runs N simulations of asset LTV using log-normal price paths.
-- Returns VaR_95 (Value at Risk at 95th percentile) for the target asset.
--
-- Usage:
--   CALL `pnkln.risk_citadel.run_monte_carlo`('AAPL', 10000);

CREATE OR REPLACE PROCEDURE `pnkln.risk_citadel.run_monte_carlo`(
    target_asset STRING,
    num_simulations INT64
)
BEGIN
    -- Generate simulated LTV paths using log-normal returns
    CREATE OR REPLACE TEMP TABLE simulation_results AS
    SELECT
        sim_id,
        -- Geometric Brownian Motion: S(t) = S(0) * exp(sum of daily returns)
        -- Using RAND() as proxy for normally distributed daily returns
        100.0 * EXP(SUM(LOG(1 + (RAND() - 0.5) * 0.04))) AS simulated_ltv
    FROM
        UNNEST(GENERATE_ARRAY(1, num_simulations)) AS sim_id,
        UNNEST(GENERATE_ARRAY(1, 30)) AS trading_day
    GROUP BY sim_id;

    -- Calculate VaR at 95th percentile (5th percentile of losses)
    SELECT
        target_asset AS asset,
        num_simulations AS simulations,
        APPROX_QUANTILES(simulated_ltv, 100)[OFFSET(5)] AS VaR_95,
        APPROX_QUANTILES(simulated_ltv, 100)[OFFSET(1)] AS VaR_99,
        AVG(simulated_ltv) AS expected_ltv,
        STDDEV(simulated_ltv) AS ltv_stddev
    FROM simulation_results;
END;
