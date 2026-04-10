-- PNKLN Intelligence Pipeline - Business Impact Dashboard Queries
-- Tracks ROI, revenue acceleration, and cost avoidance
-- ATP 5-19 RA-1 Compliance Monitoring

-- ============================================================================
-- QUERY 1: Daily Intelligence Summary
-- ============================================================================
CREATE OR REPLACE VIEW pnkln_intelligence.daily_summary AS
SELECT
  DATE(published_date) as date,
  COUNT(*) as total_items,
  COUNTIF(tier = 'tier_1') as tier_1_critical,
  COUNTIF(tier = 'tier_2') as tier_2_medium,
  COUNTIF(tier = 'tier_3') as tier_3_low,
  AVG(jr_score) as avg_jr_score,
  source,
FROM `PROJECT_ID.pnkln_intelligence.intelligence_items`
GROUP BY date, source
ORDER BY date DESC;

-- ============================================================================
-- QUERY 2: Tier 1 Critical Items Requiring CEO Attention
-- ============================================================================
CREATE OR REPLACE VIEW pnkln_intelligence.tier1_ceo_briefing AS
SELECT
  id,
  title,
  source,
  published_date,
  jr_score,
  tier_reasoning,
  cor_synthesis,
  action_items,
  url
FROM `PROJECT_ID.pnkln_intelligence.intelligence_items`
WHERE tier = 'tier_1'
  AND DATE(published_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAYS)
ORDER BY jr_score DESC, published_date DESC;

-- ============================================================================
-- QUERY 3: Regulatory Compliance Head-Start Analysis
-- ============================================================================
-- Calculates average lead time on regulatory intelligence
CREATE OR REPLACE VIEW pnkln_intelligence.regulatory_lead_time AS
SELECT
  title,
  source,
  published_date,
  ingested_at,
  TIMESTAMP_DIFF(ingested_at, published_date, DAY) as detection_delay_days,
  CASE
    WHEN TIMESTAMP_DIFF(ingested_at, published_date, DAY) <= 1 THEN 'Same Day'
    WHEN TIMESTAMP_DIFF(ingested_at, published_date, DAY) <= 7 THEN 'Within Week'
    WHEN TIMESTAMP_DIFF(ingested_at, published_date, DAY) <= 30 THEN 'Within Month'
    ELSE 'Delayed'
  END as detection_speed,
  jr_score,
  tier
FROM `PROJECT_ID.pnkln_intelligence.intelligence_items`
WHERE source IN ('federal_register', 'state_legislation', 'regulatory_agency')
  AND tier IN ('tier_1', 'tier_2')
ORDER BY published_date DESC;

-- ============================================================================
-- QUERY 4: Competitive Intelligence Tracking
-- ============================================================================
CREATE OR REPLACE VIEW pnkln_intelligence.competitive_intelligence AS
SELECT
  DATE_TRUNC(published_date, MONTH) as month,
  JSON_EXTRACT_SCALAR(metadata, '$.competitor') as competitor,
  COUNT(*) as mentions,
  AVG(jr_score) as avg_relevance,
  COUNTIF(tier = 'tier_1') as critical_items,
  STRING_AGG(title, ' | ' LIMIT 3) as top_items
FROM `PROJECT_ID.pnkln_intelligence.intelligence_items`
WHERE source = 'competitor_blog'
GROUP BY month, competitor
ORDER BY month DESC, mentions DESC;

-- ============================================================================
-- QUERY 5: Source Performance Analysis
-- ============================================================================
CREATE OR REPLACE VIEW pnkln_intelligence.source_performance AS
SELECT
  source,
  COUNT(*) as total_items,
  AVG(jr_score) as avg_score,
  COUNTIF(tier = 'tier_1') as tier1_count,
  COUNTIF(tier = 'tier_2') as tier2_count,
  COUNTIF(tier = 'tier_3') as tier3_count,
  ROUND(100.0 * COUNTIF(tier = 'tier_1') / COUNT(*), 2) as tier1_percentage,
  MIN(published_date) as first_item,
  MAX(published_date) as latest_item
FROM `PROJECT_ID.pnkln_intelligence.intelligence_items`
GROUP BY source
ORDER BY tier1_count DESC, avg_score DESC;

-- ============================================================================
-- QUERY 6: Business Impact Tracking - Revenue Acceleration
-- ============================================================================
-- Tracks intelligence items likely to impact revenue gates
CREATE OR REPLACE VIEW pnkln_intelligence.revenue_impact AS
WITH revenue_relevant AS (
  SELECT
    DATE_TRUNC(published_date, MONTH) as month,
    tier,
    source,
    title,
    jr_score,
    CASE
      WHEN jr_score >= 0.8 AND tier = 'tier_1' THEN 'High Revenue Impact'
      WHEN jr_score >= 0.7 AND tier = 'tier_1' THEN 'Medium Revenue Impact'
      WHEN tier = 'tier_2' THEN 'Indirect Revenue Impact'
      ELSE 'Low Impact'
    END as impact_category,
    -- Estimated value based on tier and score
    CASE
      WHEN jr_score >= 0.8 AND tier = 'tier_1' THEN 112000  -- 15% win rate boost on $750K pipeline
      WHEN jr_score >= 0.7 AND tier = 'tier_1' THEN 75000
      WHEN tier = 'tier_2' THEN 25000
      ELSE 0
    END as estimated_value_usd
  FROM `PROJECT_ID.pnkln_intelligence.intelligence_items`
  WHERE published_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTHS)
)
SELECT
  month,
  impact_category,
  COUNT(*) as item_count,
  SUM(estimated_value_usd) as total_estimated_value,
  AVG(jr_score) as avg_score,
  STRING_AGG(CONCAT(source, ': ', SUBSTR(title, 1, 50)), ' | ' LIMIT 5) as sample_items
FROM revenue_relevant
GROUP BY month, impact_category
ORDER BY month DESC, total_estimated_value DESC;

-- ============================================================================
-- QUERY 7: Cost Avoidance Tracking
-- ============================================================================
-- Tracks compliance items that prevent violations
CREATE OR REPLACE VIEW pnkln_intelligence.cost_avoidance AS
SELECT
  DATE_TRUNC(published_date, QUARTER) as quarter,
  COUNT(*) as compliance_items,
  COUNTIF(tier = 'tier_1') as critical_compliance,
  -- Estimated cost avoidance (based on penalty prevention)
  COUNTIF(tier = 'tier_1') * 125000 as estimated_penalty_avoidance,
  -- Time saved (vs manual monitoring)
  COUNT(*) * 8 as hours_saved,  -- 8 hours per item if done manually
  STRING_AGG(
    CASE WHEN tier = 'tier_1' THEN title ELSE NULL END,
    ' | '
    LIMIT 10
  ) as critical_compliance_items
FROM `PROJECT_ID.pnkln_intelligence.intelligence_items`
WHERE source IN ('federal_register', 'state_legislation', 'regulatory_agency')
  AND published_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTHS)
GROUP BY quarter
ORDER BY quarter DESC;

-- ============================================================================
-- QUERY 8: Pipeline ROI Dashboard
-- ============================================================================
-- Comprehensive ROI calculation
CREATE OR REPLACE VIEW pnkln_intelligence.roi_dashboard AS
WITH costs AS (
  SELECT
    DATE_TRUNC(CURRENT_DATE(), MONTH) as month,
    370 as monthly_cost_usd,
    370 * DATE_DIFF(CURRENT_DATE(), DATE('2025-01-01'), MONTH) as cumulative_cost
),
revenue_impact AS (
  SELECT
    SUM(
      CASE
        WHEN jr_score >= 0.8 AND tier = 'tier_1' THEN 112000
        WHEN jr_score >= 0.7 AND tier = 'tier_1' THEN 75000
        WHEN tier = 'tier_2' THEN 25000
        ELSE 0
      END
    ) as estimated_revenue_value
  FROM `PROJECT_ID.pnkln_intelligence.intelligence_items`
),
cost_avoidance AS (
  SELECT
    COUNTIF(tier = 'tier_1') * 125000 as estimated_cost_avoidance
  FROM `PROJECT_ID.pnkln_intelligence.intelligence_items`
  WHERE source IN ('federal_register', 'state_legislation', 'regulatory_agency')
)
SELECT
  costs.month,
  costs.monthly_cost_usd,
  costs.cumulative_cost,
  revenue_impact.estimated_revenue_value,
  cost_avoidance.estimated_cost_avoidance,
  revenue_impact.estimated_revenue_value + cost_avoidance.estimated_cost_avoidance as total_value,
  ROUND(
    (revenue_impact.estimated_revenue_value + cost_avoidance.estimated_cost_avoidance) / NULLIF(costs.cumulative_cost, 0),
    2
  ) as roi_multiple
FROM costs, revenue_impact, cost_avoidance;

-- ============================================================================
-- QUERY 9: ATP 5-19 Compliance Monitoring
-- ============================================================================
-- Ensures ethical scraping compliance
CREATE OR REPLACE VIEW pnkln_intelligence.atp_compliance AS
SELECT
  DATE(ingested_at) as date,
  source,
  COUNT(*) as items_ingested,
  COUNT(DISTINCT url) as unique_sources,
  -- Check for suspicious patterns (too many items = possible violation)
  CASE
    WHEN COUNT(*) > 1000 THEN 'REVIEW: High volume'
    WHEN COUNT(*) > 500 THEN 'CAUTION: Medium volume'
    ELSE 'OK'
  END as volume_check,
  -- Verify date distribution (batch = good, realtime = suspicious)
  TIMESTAMP_DIFF(MAX(ingested_at), MIN(ingested_at), HOUR) as ingestion_duration_hours,
  CASE
    WHEN TIMESTAMP_DIFF(MAX(ingested_at), MIN(ingested_at), HOUR) < 1 THEN 'OK: Batch ingestion'
    WHEN TIMESTAMP_DIFF(MAX(ingested_at), MIN(ingested_at), HOUR) < 4 THEN 'OK: Normal'
    ELSE 'REVIEW: Extended duration'
  END as duration_check
FROM `PROJECT_ID.pnkln_intelligence.intelligence_items`
WHERE DATE(ingested_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAYS)
GROUP BY date, source
ORDER BY date DESC;

-- ============================================================================
-- QUERY 10: Executive Summary for CEO Briefing
-- ============================================================================
CREATE OR REPLACE VIEW pnkln_intelligence.executive_summary AS
WITH last_30_days AS (
  SELECT
    COUNT(*) as total_items,
    COUNTIF(tier = 'tier_1') as tier1_items,
    COUNTIF(tier = 'tier_2') as tier2_items,
    AVG(jr_score) as avg_score
  FROM `PROJECT_ID.pnkln_intelligence.intelligence_items`
  WHERE DATE(published_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAYS)
),
top_tier1 AS (
  SELECT
    ARRAY_AGG(
      STRUCT(title, source, jr_score, url)
      ORDER BY jr_score DESC
      LIMIT 5
    ) as top_items
  FROM `PROJECT_ID.pnkln_intelligence.intelligence_items`
  WHERE tier = 'tier_1'
    AND DATE(published_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAYS)
)
SELECT
  CURRENT_DATE() as report_date,
  last_30_days.total_items,
  last_30_days.tier1_items,
  last_30_days.tier2_items,
  ROUND(last_30_days.avg_score, 3) as avg_score,
  top_tier1.top_items
FROM last_30_days, top_tier1;
