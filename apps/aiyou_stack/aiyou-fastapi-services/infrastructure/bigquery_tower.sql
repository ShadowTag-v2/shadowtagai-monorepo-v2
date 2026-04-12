-- PNKLN Tower Edge Telemetry Schema
-- Dataset: pnkln_intelligence

CREATE TABLE IF NOT EXISTS `pnkln_intelligence.tower_metrics` (
    event_timestamp TIMESTAMP NOT NULL OPTIONS(description="Time of reading"),
    node_id STRING NOT NULL OPTIONS(description="Unique Hardware ID"),
    location_code STRING,

    -- Network Performance
    connection_type STRING OPTIONS(description="FIBER, STARLINK, 5G"),
    latency_ms FLOAT64,
    jitter_ms FLOAT64,
    packet_loss_rate FLOAT64,

    -- Hardware Health (Passive Cooling Monitor)
    gpu_temp_c FLOAT64,
    coolant_pressure_psi FLOAT64, -- For 2-phase cooling monitoring
    power_draw_w FLOAT64,

    -- Economics
    backhaul_saved_gb FLOAT64 OPTIONS(description="Data processed locally vs sent to cloud"),
    revenue_generated_usd FLOAT64,

    -- Partitions for cost-effective querying
) PARTITION BY DATE(event_timestamp)
CLUSTER BY node_id, location_code;
