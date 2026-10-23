CREATE TABLE IF NOT EXISTS network_flows (
    source_split TEXT NOT NULL
        CHECK (source_split IN ('training', 'testing')),
    source_id BIGINT NOT NULL,

    label SMALLINT NOT NULL
        CHECK (label IN (0, 1)),

    attack_cat TEXT,
    proto TEXT,
    service TEXT,
    state TEXT,

    dur DOUBLE PRECISION NOT NULL CHECK (dur >= 0),
    sbytes BIGINT NOT NULL CHECK (sbytes >= 0),
    dbytes BIGINT NOT NULL CHECK (dbytes >= 0),
    spkts BIGINT NOT NULL CHECK (spkts >= 0),
    dpkts BIGINT NOT NULL CHECK (dpkts >= 0),

    extra_features JSONB NOT NULL DEFAULT '{}'::jsonb,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (source_split, source_id)
);

CREATE TABLE IF NOT EXISTS rejected_records (
    source_split TEXT NOT NULL,
    source_id BIGINT NOT NULL,
    reject_reason TEXT NOT NULL,
    payload JSONB NOT NULL,

    rejected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (source_split, source_id, reject_reason)
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    pipeline_name TEXT NOT NULL,
    source_split TEXT NOT NULL,

    status TEXT NOT NULL
        CHECK (status IN ('running', 'succeeded', 'failed')),

    processed_flows INTEGER NOT NULL DEFAULT 0,
    rejected_rows INTEGER NOT NULL DEFAULT 0,

    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,

    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_flows_label
    ON network_flows (label);

CREATE INDEX IF NOT EXISTS idx_flows_attack
    ON network_flows (attack_cat);

CREATE INDEX IF NOT EXISTS idx_flows_proto
    ON network_flows (proto);