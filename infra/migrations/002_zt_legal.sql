-- Migration 002: ZT.1 Zero-Touch Legal Deadline Management
-- Builds on top of 001_shadowtag_init.sql + core/lawtrack/schema.sql
-- Requires: uuid-ossp, pgcrypto (already enabled in schema.sql)

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. Deadline Extractions (AI-drafted, pending human review)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS deadline_extractions (
    extraction_id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    matter_id             UUID NOT NULL REFERENCES matters(matter_id) ON DELETE CASCADE,
    tenant_id             UUID NOT NULL REFERENCES tenants(tenant_id),
    -- Zero-Drift fields: exact traceability to source document
    trigger_event         TEXT NOT NULL,
    exhibit_citation_id   TEXT NOT NULL,  -- e.g. "Page 3, ¶12" or "Section IV.B"
    raw_date_text         TEXT,           -- date as literally written in filing
    -- Calculated fields
    trigger_date          DATE NOT NULL,  -- the date the clock starts
    calculated_due_date   DATE NOT NULL,
    days_to_respond       INTEGER NOT NULL CHECK (days_to_respond > 0),
    business_days_only    BOOLEAN NOT NULL DEFAULT false,
    jurisdiction          TEXT NOT NULL DEFAULT 'FRCP',
    jurisdiction_rule     TEXT,           -- e.g. "FRCP 12(a)(1)(A)(i)"
    -- Confidence + provenance
    confidence_score      FLOAT NOT NULL DEFAULT 0.0 CHECK (confidence_score BETWEEN 0 AND 1),
    source_filing_hash    TEXT,           -- SHA-256 of ingested filing for dedup
    -- Workflow state
    status                TEXT NOT NULL DEFAULT 'pending_approval'
                            CHECK (status IN ('pending_approval', 'approved', 'rejected')),
    -- Human verification (Agent-Drafted, Human-Verified)
    approved_by           UUID,           -- actor_id of attorney who approved
    approved_at           TIMESTAMP WITH TIME ZONE,
    approval_notes        TEXT,
    rejected_by           UUID,
    rejected_at           TIMESTAMP WITH TIME ZONE,
    rejection_reason      TEXT,
    -- Timestamps
    created_at            TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at            TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- RLS: attorneys see only their tenant's extractions
ALTER TABLE deadline_extractions ENABLE ROW LEVEL SECURITY;

CREATE INDEX IF NOT EXISTS idx_extractions_matter
    ON deadline_extractions (matter_id, status);

CREATE INDEX IF NOT EXISTS idx_extractions_due_date
    ON deadline_extractions (calculated_due_date)
    WHERE status = 'approved';

CREATE INDEX IF NOT EXISTS idx_extractions_tenant
    ON deadline_extractions (tenant_id, status);


-- ─────────────────────────────────────────────────────────────────────────────
-- 2. Reminder Schedule (cascading: -30d, -14d, -7d, -1d)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS deadline_reminders (
    reminder_id       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    extraction_id     UUID NOT NULL REFERENCES deadline_extractions(extraction_id) ON DELETE CASCADE,
    remind_at         TIMESTAMP WITH TIME ZONE NOT NULL,
    days_before       INTEGER NOT NULL CHECK (days_before IN (30, 14, 7, 1)),
    channel           TEXT NOT NULL DEFAULT 'email'
                        CHECK (channel IN ('email', 'slack', 'sms')),
    sent_at           TIMESTAMP WITH TIME ZONE,
    status            TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'sent', 'failed', 'suppressed')),
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reminders_remind_at
    ON deadline_reminders (remind_at)
    WHERE status = 'pending';


-- ─────────────────────────────────────────────────────────────────────────────
-- 3. Jurisdiction Holiday Overlays (local court closures beyond federal)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS jurisdiction_holidays (
    holiday_id    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    jurisdiction  TEXT NOT NULL,  -- e.g. "SDNY", "CDCA", "FRCP"
    holiday_date  DATE NOT NULL,
    description   TEXT NOT NULL,
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (jurisdiction, holiday_date)
);

-- Seed FRCP federal holidays 2026
INSERT INTO jurisdiction_holidays (jurisdiction, holiday_date, description)
VALUES
    ('FRCP', '2026-01-01', 'New Year''s Day'),
    ('FRCP', '2026-01-19', 'Martin Luther King Jr. Day'),
    ('FRCP', '2026-02-16', 'Presidents'' Day'),
    ('FRCP', '2026-05-25', 'Memorial Day'),
    ('FRCP', '2026-07-03', 'Independence Day (observed)'),
    ('FRCP', '2026-09-07', 'Labor Day'),
    ('FRCP', '2026-10-12', 'Columbus Day'),
    ('FRCP', '2026-11-11', 'Veterans Day'),
    ('FRCP', '2026-11-26', 'Thanksgiving Day'),
    ('FRCP', '2026-12-25', 'Christmas Day')
ON CONFLICT (jurisdiction, holiday_date) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- 4. Auto-generate cascading reminders when extraction is approved
-- ─────────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION fn_schedule_reminders()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    due_ts TIMESTAMP WITH TIME ZONE;
    offsets INTEGER[] := ARRAY[30, 14, 7, 1];
    d INTEGER;
BEGIN
    IF NEW.status = 'approved' AND OLD.status = 'pending_approval' THEN
        due_ts := NEW.calculated_due_date::TIMESTAMP WITH TIME ZONE
                    + INTERVAL '17 hours';  -- 5pm court close
        FOREACH d IN ARRAY offsets LOOP
            INSERT INTO deadline_reminders
                (extraction_id, remind_at, days_before, channel)
            VALUES
                (NEW.extraction_id, due_ts - (d || ' days')::INTERVAL, d, 'email')
            ON CONFLICT DO NOTHING;
        END LOOP;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_schedule_reminders
    AFTER UPDATE OF status ON deadline_extractions
    FOR EACH ROW
    EXECUTE FUNCTION fn_schedule_reminders();


-- ─────────────────────────────────────────────────────────────────────────────
-- 5. Immutable audit rows for every status change
-- ─────────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION fn_audit_extraction_change()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO audit_log (tenant_id, actor_id, action_type, target_record_id, metadata)
    VALUES (
        NEW.tenant_id,
        COALESCE(NEW.approved_by, NEW.rejected_by),
        'deadline_extraction_' || NEW.status,
        NEW.extraction_id,
        jsonb_build_object(
            'old_status', OLD.status,
            'new_status', NEW.status,
            'calculated_due_date', NEW.calculated_due_date,
            'exhibit_citation_id', NEW.exhibit_citation_id
        )
    );
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_audit_extraction
    BEFORE UPDATE ON deadline_extractions
    FOR EACH ROW
    EXECUTE FUNCTION fn_audit_extraction_change();
