SELECT
    tag,
    COUNT(*) as event_count
FROM `shadowtag-omega-v2.velocity_dataset.events_raw`
WHERE
    -- 1. PARTITION FILTER (Mandatory due to 'require_partition_filter = true')
    dt >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)

    -- 2. CLUSTER FILTER (Optional but recommended)
    AND tag IN ('login', 'purchase')
GROUP BY 1
ORDER BY 2 DESC;
