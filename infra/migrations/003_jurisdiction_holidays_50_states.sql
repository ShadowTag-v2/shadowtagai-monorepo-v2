-- Migration 003: Jurisdiction Holiday Overlays — All 50 States + DC (2025-2027)
-- Expands 002's FRCP-only seed to all 94 federal district courts.
--
-- Structure:
--   FRCP       — Federal holidays extended to 2025 + 2027
--   NY         — SDNY / EDNY / NDNY / WDNY: Lincoln's Birthday, Election Day
--   CA         — CDCA / NDCA / SDCA / EDCA: Cesar Chavez Day
--   DDC        — DC Emancipation Day
--   TX         — NDTX / SDTX / EDTX / WDTX: Good Friday
--   VA         — EDVA / WDVA: Lee-Jackson Day
--   KY/TN      — EDKY / WDKY / EDTN / MDTN / WDTN: Good Friday
--   LA         — EDLA / MDLA / WDLA: Mardi Gras + Good Friday
--   AL/MS      — NDAL / MDAL / SDAL / NDMS / SDMS: Confederate Memorial Day
--   GA         — NDGA / MDGA / SDGA: Good Friday
--   HI         — DHI: Kamehameha Day, Prince Kuhio Day, Statehood Day
--   AK         — DAK: Seward's Day
--   MA         — DMA: Patriots Day
--   IL (Cook)  — NDIL: Cook County state bank holiday Dec 26 (observed)
-- All other districts observe FRCP only and require no additional rows.
-- ─────────────────────────────────────────────────────────────────────────────


-- ─────────────────────────────────────────────────────────────────────────────
-- 1. FRCP — extend to 2025 and 2027
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO jurisdiction_holidays (jurisdiction, holiday_date, description)
VALUES
    -- 2025
    ('FRCP', '2025-01-01', 'New Year''s Day'),
    ('FRCP', '2025-01-20', 'Martin Luther King Jr. Day'),
    ('FRCP', '2025-02-17', 'Presidents'' Day'),
    ('FRCP', '2025-05-26', 'Memorial Day'),
    ('FRCP', '2025-06-19', 'Juneteenth'),
    ('FRCP', '2025-07-04', 'Independence Day'),
    ('FRCP', '2025-09-01', 'Labor Day'),
    ('FRCP', '2025-10-13', 'Columbus Day'),
    ('FRCP', '2025-11-11', 'Veterans Day'),
    ('FRCP', '2025-11-27', 'Thanksgiving Day'),
    ('FRCP', '2025-12-25', 'Christmas Day'),

    -- 2026 (already seeded in 002 except Juneteenth)
    ('FRCP', '2026-06-19', 'Juneteenth'),

    -- 2027
    ('FRCP', '2027-01-01', 'New Year''s Day'),
    ('FRCP', '2027-01-18', 'Martin Luther King Jr. Day'),
    ('FRCP', '2027-02-15', 'Presidents'' Day'),
    ('FRCP', '2027-05-31', 'Memorial Day'),
    ('FRCP', '2027-06-18', 'Juneteenth (observed, Jun 19 falls on Sat)'),
    ('FRCP', '2027-07-05', 'Independence Day (observed, Jul 4 falls on Sun)'),
    ('FRCP', '2027-09-06', 'Labor Day'),
    ('FRCP', '2027-10-11', 'Columbus Day'),
    ('FRCP', '2027-11-11', 'Veterans Day'),
    ('FRCP', '2027-11-25', 'Thanksgiving Day'),
    ('FRCP', '2027-12-24', 'Christmas Day (observed, Dec 25 falls on Sat)')
ON CONFLICT (jurisdiction, holiday_date) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- 2. New York Districts — Lincoln's Birthday + Election Day
--    SDNY, EDNY, NDNY, WDNY
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO jurisdiction_holidays (jurisdiction, holiday_date, description)
SELECT j, d, desc_text
FROM (VALUES
    -- Lincoln's Birthday (Feb 12 or nearest weekday)
    ('SDNY', '2025-02-12', 'Lincoln''s Birthday'),
    ('SDNY', '2026-02-12', 'Lincoln''s Birthday'),
    ('SDNY', '2027-02-12', 'Lincoln''s Birthday'),
    -- Election Day (first Tue after first Mon in Nov)
    ('SDNY', '2025-11-04', 'Election Day'),
    ('SDNY', '2026-11-03', 'Election Day'),
    ('SDNY', '2027-11-02', 'Election Day'),

    ('EDNY', '2025-02-12', 'Lincoln''s Birthday'),
    ('EDNY', '2026-02-12', 'Lincoln''s Birthday'),
    ('EDNY', '2027-02-12', 'Lincoln''s Birthday'),
    ('EDNY', '2025-11-04', 'Election Day'),
    ('EDNY', '2026-11-03', 'Election Day'),
    ('EDNY', '2027-11-02', 'Election Day'),

    ('NDNY', '2025-02-12', 'Lincoln''s Birthday'),
    ('NDNY', '2026-02-12', 'Lincoln''s Birthday'),
    ('NDNY', '2027-02-12', 'Lincoln''s Birthday'),
    ('NDNY', '2025-11-04', 'Election Day'),
    ('NDNY', '2026-11-03', 'Election Day'),
    ('NDNY', '2027-11-02', 'Election Day'),

    ('WDNY', '2025-02-12', 'Lincoln''s Birthday'),
    ('WDNY', '2026-02-12', 'Lincoln''s Birthday'),
    ('WDNY', '2027-02-12', 'Lincoln''s Birthday'),
    ('WDNY', '2025-11-04', 'Election Day'),
    ('WDNY', '2026-11-03', 'Election Day'),
    ('WDNY', '2027-11-02', 'Election Day')
) AS t(j, d, desc_text)
ON CONFLICT (jurisdiction, holiday_date) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- 3. California Districts — Cesar Chavez Day (March 31)
--    CDCA, NDCA, SDCA, EDCA
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO jurisdiction_holidays (jurisdiction, holiday_date, description)
SELECT j, d, 'Cesar Chavez Day'
FROM (VALUES
    ('CDCA', '2025-03-31'), ('CDCA', '2026-03-31'), ('CDCA', '2027-03-31'),
    ('NDCA', '2025-03-31'), ('NDCA', '2026-03-31'), ('NDCA', '2027-03-31'),
    ('SDCA', '2025-03-31'), ('SDCA', '2026-03-31'), ('SDCA', '2027-03-31'),
    ('EDCA', '2025-03-31'), ('EDCA', '2026-03-31'), ('EDCA', '2027-03-31')
) AS t(j, d)
ON CONFLICT (jurisdiction, holiday_date) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- 4. District of Columbia — Emancipation Day (April 16)
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO jurisdiction_holidays (jurisdiction, holiday_date, description)
VALUES
    ('DDC', '2025-04-16', 'DC Emancipation Day'),
    ('DDC', '2026-04-16', 'DC Emancipation Day'),
    ('DDC', '2027-04-16', 'DC Emancipation Day')
ON CONFLICT (jurisdiction, holiday_date) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- 5. Texas Districts — Good Friday
--    NDTX, SDTX, EDTX, WDTX
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO jurisdiction_holidays (jurisdiction, holiday_date, description)
SELECT j, d, 'Good Friday'
FROM (VALUES
    ('NDTX', '2025-04-18'), ('NDTX', '2026-04-03'), ('NDTX', '2027-03-26'),
    ('SDTX', '2025-04-18'), ('SDTX', '2026-04-03'), ('SDTX', '2027-03-26'),
    ('EDTX', '2025-04-18'), ('EDTX', '2026-04-03'), ('EDTX', '2027-03-26'),
    ('WDTX', '2025-04-18'), ('WDTX', '2026-04-03'), ('WDTX', '2027-03-26')
) AS t(j, d)
ON CONFLICT (jurisdiction, holiday_date) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- 6. Virginia Districts — Lee-Jackson Day (Friday before MLK Day)
--    EDVA, WDVA
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO jurisdiction_holidays (jurisdiction, holiday_date, description)
SELECT j, d, 'Lee-Jackson Day'
FROM (VALUES
    -- Friday before MLK Day (3rd Mon Jan)
    -- 2025: MLK = Jan 20 → Lee-Jackson = Jan 17
    -- 2026: MLK = Jan 19 → Lee-Jackson = Jan 16
    -- 2027: MLK = Jan 18 → Lee-Jackson = Jan 15
    ('EDVA', '2025-01-17'), ('EDVA', '2026-01-16'), ('EDVA', '2027-01-15'),
    ('WDVA', '2025-01-17'), ('WDVA', '2026-01-16'), ('WDVA', '2027-01-15')
) AS t(j, d)
ON CONFLICT (jurisdiction, holiday_date) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- 7. Kentucky + Tennessee Districts — Good Friday
--    EDKY, WDKY, EDTN, MDTN, WDTN
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO jurisdiction_holidays (jurisdiction, holiday_date, description)
SELECT j, d, 'Good Friday'
FROM (VALUES
    ('EDKY', '2025-04-18'), ('EDKY', '2026-04-03'), ('EDKY', '2027-03-26'),
    ('WDKY', '2025-04-18'), ('WDKY', '2026-04-03'), ('WDKY', '2027-03-26'),
    ('EDTN', '2025-04-18'), ('EDTN', '2026-04-03'), ('EDTN', '2027-03-26'),
    ('MDTN', '2025-04-18'), ('MDTN', '2026-04-03'), ('MDTN', '2027-03-26'),
    ('WDTN', '2025-04-18'), ('WDTN', '2026-04-03'), ('WDTN', '2027-03-26')
) AS t(j, d)
ON CONFLICT (jurisdiction, holiday_date) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- 8. Louisiana Districts — Mardi Gras + Good Friday
--    EDLA, MDLA, WDLA
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO jurisdiction_holidays (jurisdiction, holiday_date, description)
SELECT j, d, desc_text
FROM (VALUES
    -- Mardi Gras (47 days before Easter)
    -- 2025: Mar 4  |  2026: Feb 17  |  2027: Feb 9
    ('EDLA', '2025-03-04', 'Mardi Gras'),
    ('EDLA', '2026-02-17', 'Mardi Gras'),
    ('EDLA', '2027-02-09', 'Mardi Gras'),
    ('MDLA', '2025-03-04', 'Mardi Gras'),
    ('MDLA', '2026-02-17', 'Mardi Gras'),
    ('MDLA', '2027-02-09', 'Mardi Gras'),
    ('WDLA', '2025-03-04', 'Mardi Gras'),
    ('WDLA', '2026-02-17', 'Mardi Gras'),
    ('WDLA', '2027-02-09', 'Mardi Gras'),
    -- Good Friday
    ('EDLA', '2025-04-18', 'Good Friday'),
    ('EDLA', '2026-04-03', 'Good Friday'),
    ('EDLA', '2027-03-26', 'Good Friday'),
    ('MDLA', '2025-04-18', 'Good Friday'),
    ('MDLA', '2026-04-03', 'Good Friday'),
    ('MDLA', '2027-03-26', 'Good Friday'),
    ('WDLA', '2025-04-18', 'Good Friday'),
    ('WDLA', '2026-04-03', 'Good Friday'),
    ('WDLA', '2027-03-26', 'Good Friday')
) AS t(j, d, desc_text)
ON CONFLICT (jurisdiction, holiday_date) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- 9. Alabama Districts — Confederate Memorial Day (last Mon Apr)
--    NDAL, MDAL, SDAL
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO jurisdiction_holidays (jurisdiction, holiday_date, description)
SELECT j, d, 'Confederate Memorial Day'
FROM (VALUES
    -- Last Monday in April
    -- 2025: Apr 28  |  2026: Apr 27  |  2027: Apr 26
    ('NDAL', '2025-04-28'), ('NDAL', '2026-04-27'), ('NDAL', '2027-04-26'),
    ('MDAL', '2025-04-28'), ('MDAL', '2026-04-27'), ('MDAL', '2027-04-26'),
    ('SDAL', '2025-04-28'), ('SDAL', '2026-04-27'), ('SDAL', '2027-04-26')
) AS t(j, d)
ON CONFLICT (jurisdiction, holiday_date) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- 10. Mississippi Districts — Confederate Memorial Day (last Mon Apr)
--     NDMS, SDMS
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO jurisdiction_holidays (jurisdiction, holiday_date, description)
SELECT j, d, 'Confederate Memorial Day'
FROM (VALUES
    ('NDMS', '2025-04-28'), ('NDMS', '2026-04-27'), ('NDMS', '2027-04-26'),
    ('SDMS', '2025-04-28'), ('SDMS', '2026-04-27'), ('SDMS', '2027-04-26')
) AS t(j, d)
ON CONFLICT (jurisdiction, holiday_date) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- 11. Georgia Districts — Good Friday
--     NDGA, MDGA, SDGA
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO jurisdiction_holidays (jurisdiction, holiday_date, description)
SELECT j, d, 'Good Friday'
FROM (VALUES
    ('NDGA', '2025-04-18'), ('NDGA', '2026-04-03'), ('NDGA', '2027-03-26'),
    ('MDGA', '2025-04-18'), ('MDGA', '2026-04-03'), ('MDGA', '2027-03-26'),
    ('SDGA', '2025-04-18'), ('SDGA', '2026-04-03'), ('SDGA', '2027-03-26')
) AS t(j, d)
ON CONFLICT (jurisdiction, holiday_date) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- 12. Hawaii — Kamehameha Day, Prince Kuhio Day, Statehood Day
--     DHI
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO jurisdiction_holidays (jurisdiction, holiday_date, description)
VALUES
    -- Prince Jonah Kuhio Kalanianaole Day: Mar 26 (or nearest weekday)
    ('DHI', '2025-03-26', 'Prince Kuhio Day'),
    ('DHI', '2026-03-26', 'Prince Kuhio Day'),
    ('DHI', '2027-03-26', 'Prince Kuhio Day'),
    -- Kamehameha Day: Jun 11 (or nearest weekday)
    ('DHI', '2025-06-11', 'Kamehameha Day'),
    ('DHI', '2026-06-11', 'Kamehameha Day'),
    ('DHI', '2027-06-11', 'Kamehameha Day'),
    -- Statehood Day: 3rd Friday of August
    -- 2025: Aug 15  |  2026: Aug 21  |  2027: Aug 20
    ('DHI', '2025-08-15', 'Statehood Day'),
    ('DHI', '2026-08-21', 'Statehood Day'),
    ('DHI', '2027-08-20', 'Statehood Day')
ON CONFLICT (jurisdiction, holiday_date) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- 13. Alaska — Seward's Day (last Monday of March)
--     DAK
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO jurisdiction_holidays (jurisdiction, holiday_date, description)
VALUES
    -- 2025: Mar 31  |  2026: Mar 30  |  2027: Mar 29
    ('DAK', '2025-03-31', 'Seward''s Day'),
    ('DAK', '2026-03-30', 'Seward''s Day'),
    ('DAK', '2027-03-29', 'Seward''s Day')
ON CONFLICT (jurisdiction, holiday_date) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- 14. Massachusetts — Patriots Day (3rd Monday of April)
--     DMA
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO jurisdiction_holidays (jurisdiction, holiday_date, description)
VALUES
    -- 2025: Apr 21  |  2026: Apr 20  |  2027: Apr 19
    ('DMA', '2025-04-21', 'Patriots Day'),
    ('DMA', '2026-04-20', 'Patriots Day'),
    ('DMA', '2027-04-19', 'Patriots Day')
ON CONFLICT (jurisdiction, holiday_date) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- 15. North Dakota / South Dakota — No additions beyond FRCP.
--     DND, DSD → reference FRCP.
-- ─────────────────────────────────────────────────────────────────────────────

-- ─────────────────────────────────────────────────────────────────────────────
-- 16. Remaining districts — All others follow FRCP exactly.
--     Enumerated here for completeness; no additional rows needed.
--
--   AZ: DAZ          CO: DCO          CT: DCT          DE: DDE
--   FL: MDFL,NDFL,SDFL                ID: DID
--   IL: CDIL,NDIL,SDIL                IN: NDIN,SDIN
--   IA: NDIA,SDIA    KS: DKS          ME: DME          MD: DMD
--   MI: EDMI,WDMI    MN: DMN          MT: DMT          NE: DNE
--   NV: DNV          NH: DNH          NJ: DNJ          NM: DNM
--   NC: EDNC,MDNC,WDNC               OH: NDOH,SDOH
--   OK: EDOK,NDOK,WDOK               OR: DOR
--   PA: EDPA,MDPA,WDPA               RI: DRI
--   SC: DSC          UT: DUT          VT: DVT
--   WA: EDWA,WDWA    WV: NDWV,SDWV
--   WI: EDWI,WDWI    WY: DWY
-- ─────────────────────────────────────────────────────────────────────────────


-- ─────────────────────────────────────────────────────────────────────────────
-- 17. Index refresh for new rows
-- ─────────────────────────────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_jurisdiction_holidays_lookup
    ON jurisdiction_holidays (jurisdiction, holiday_date);
