-- SeatJudge "Liquid Inventory" Schema (Austin Pilot)
-- Powered by Judge #6 v2.0

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. VENUES (The physical space)
CREATE TABLE venues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL DEFAULT 'Austin',
    capacity INT NOT NULL,
    timezone VARCHAR(50) DEFAULT 'America/Chicago',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. SECTIONS (Logical grouping)
CREATE TABLE sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    venue_id UUID REFERENCES venues(id),
    name VARCHAR(50) NOT NULL,
    base_price_modifier DECIMAL(3, 2) DEFAULT 1.00 -- 1.0 = standard, 1.5 = VIP
);

-- 3. SEATS (The inventory unit)
-- Status: 'AVAILABLE', 'HELD', 'BOOKED', 'LOCKED' (Judge blocked)
CREATE TABLE seats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    section_id UUID REFERENCES sections(id),
    row_label VARCHAR(10),
    seat_number VARCHAR(10),
    status VARCHAR(20) DEFAULT 'AVAILABLE',
    current_price DECIMAL(10, 2), -- Dynamic price
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. EVENTS (Time-bound inventory instantiation)
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    venue_id UUID REFERENCES venues(id),
    name VARCHAR(255) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE
);

-- 5. RISK SCORES (Judge #6 Integration)
-- Stores real-time risk assessments for users, venues, or specific transactions
CREATE TABLE risk_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL, -- 'USER', 'VENUE', 'TRANSACTION'
    entity_id UUID NOT NULL,
    score INT NOT NULL, -- 0-100 (100 = High Risk/Block)
    reason TEXT,
    decision_packet BYTEA, -- PNKLN Binary Packet
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. ACTIVE DEFENSE (Trigger)
-- Auto-lock seats if high risk detected associated with a booking attempt
CREATE OR REPLACE FUNCTION audit_risk() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.score > 80 THEN
        -- Logic to freeze associated assets would go here
        -- For now, just log to console/notify
        RAISE NOTICE 'HIGH RISK DETECTED: % (Score: %)', NEW.entity_id, NEW.score;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_risk_audit
AFTER INSERT ON risk_scores
FOR EACH ROW EXECUTE FUNCTION audit_risk();
