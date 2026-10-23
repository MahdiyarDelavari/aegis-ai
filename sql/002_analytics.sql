SELECT
    label,
    COUNT(*) AS total_flows,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM network_flows
WHERE source_split = 'training'
GROUP BY label
ORDER BY label;


SELECT
    attack_cat,
    COUNT(*) AS total,
    ROUND(AVG(dur)::NUMERIC, 3) AS avg_duration
FROM network_flows
WHERE source_split = 'training'
  AND label = 1
GROUP BY attack_cat
ORDER BY total DESC;


SELECT
    proto,
    COUNT(*) AS total_flows,
    SUM(sbytes) AS total_source_bytes,
    SUM(dbytes) AS total_destination_bytes
FROM network_flows
WHERE source_split = 'training'
GROUP BY proto
ORDER BY total_flows DESC
LIMIT 10;


SELECT
    run_id,
    status,
    processed_flows,
    rejected_rows,
    finished_at - started_at AS duration
FROM pipeline_runs
ORDER BY run_id DESC
LIMIT 10;


SELECT
    source_id,
    proto,
    label,
    extra_features ->> 'sttl' AS source_ttl
FROM network_flows
WHERE source_split = 'training'
LIMIT 10;


