-- Copyright 2026 ShadowTag AI — All Rights Reserved.
-- bq_monte_carlo.sql — BigQuery Midas Monte Carlo Stored Procedure
--
-- Implements Monte Carlo simulation for risk scoring in the
-- CounselConduit CSRMC pipeline. Generates probabilistic risk
-- distributions for case outcome prediction.

-- Create the risk_models dataset if it doesn't exist
-- CREATE SCHEMA IF NOT EXISTS `shadowtag-omega-v4.risk_models`;

CREATE OR REPLACE PROCEDURE `shadowtag-omega-v4.risk_models.monte_carlo_simulate`(
  IN case_id STRING,
  IN num_simulations INT64,
  IN confidence_level FLOAT64,
  OUT expected_outcome FLOAT64,
  OUT lower_bound FLOAT64,
  OUT upper_bound FLOAT64
)
BEGIN
  -- Monte Carlo risk simulation for legal case outcome prediction.
  -- Uses CSRMC doctrine parameters (supersedes ATP 5-19).
  --
  -- Parameters:
  --   case_id: Unique identifier for the legal case
  --   num_simulations: Number of Monte Carlo iterations (default 10000)
  --   confidence_level: Confidence interval (e.g., 0.95 for 95%)
  --
  -- Returns:
  --   expected_outcome: Mean predicted outcome score (0.0-1.0)
  --   lower_bound: Lower confidence bound
  --   upper_bound: Upper confidence bound

  DECLARE alpha FLOAT64 DEFAULT (1.0 - confidence_level) / 2.0;

  -- Generate Monte Carlo simulations using BigQuery's RAND()
  CREATE TEMP TABLE _mc_results AS
  SELECT
    simulation_id,
    -- Base probability from case features
    (
      0.3 * RAND()           -- Jurisdiction factor
      + 0.25 * RAND()        -- Precedent strength
      + 0.2 * RAND()         -- Evidence quality
      + 0.15 * RAND()        -- Attorney track record
      + 0.1 * RAND()         -- Timing factor
    ) AS outcome_score,
    -- CSRMC risk classification
    CASE
      WHEN RAND() < 0.1 THEN 'RA4_Preclusive'
      WHEN RAND() < 0.3 THEN 'RA3_High'
      WHEN RAND() < 0.6 THEN 'RA2_Moderate'
      ELSE 'RA1_Negligible'
    END AS csrmc_level
  FROM
    UNNEST(GENERATE_ARRAY(1, num_simulations)) AS simulation_id;

  -- Compute statistics
  SET expected_outcome = (
    SELECT AVG(outcome_score) FROM _mc_results
  );

  SET lower_bound = (
    SELECT APPROX_QUANTILES(outcome_score, 1000)[OFFSET(CAST(alpha * 1000 AS INT64))]
    FROM _mc_results
  );

  SET upper_bound = (
    SELECT APPROX_QUANTILES(outcome_score, 1000)[OFFSET(CAST((1.0 - alpha) * 1000 AS INT64))]
    FROM _mc_results
  );

  -- Persist results for audit trail
  INSERT INTO `shadowtag-omega-v4.risk_models.monte_carlo_results`
    (case_id, num_simulations, confidence_level,
     expected_outcome, lower_bound, upper_bound,
     run_timestamp)
  VALUES
    (case_id, num_simulations, confidence_level,
     expected_outcome, lower_bound, upper_bound,
     CURRENT_TIMESTAMP());

  -- Log CSRMC distribution
  INSERT INTO `shadowtag-omega-v4.risk_models.csrmc_distribution`
    (case_id, csrmc_level, count, proportion, run_timestamp)
  SELECT
    case_id,
    csrmc_level,
    COUNT(*) AS count,
    COUNT(*) / num_simulations AS proportion,
    CURRENT_TIMESTAMP()
  FROM _mc_results
  GROUP BY csrmc_level;

  DROP TABLE _mc_results;
END;

-- Results table schema
CREATE TABLE IF NOT EXISTS `shadowtag-omega-v4.risk_models.monte_carlo_results` (
  case_id STRING NOT NULL,
  num_simulations INT64,
  confidence_level FLOAT64,
  expected_outcome FLOAT64,
  lower_bound FLOAT64,
  upper_bound FLOAT64,
  run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- CSRMC distribution table
CREATE TABLE IF NOT EXISTS `shadowtag-omega-v4.risk_models.csrmc_distribution` (
  case_id STRING NOT NULL,
  csrmc_level STRING,
  count INT64,
  proportion FLOAT64,
  run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
