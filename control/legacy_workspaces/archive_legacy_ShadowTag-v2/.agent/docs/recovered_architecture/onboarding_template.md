# Client Onboarding & Async Queue Template

## Overview

This template codifies the exact sequence we used to close **AcmeCorp** and **StealthFin** deals. It can be reused for the remaining pilot customers to accelerate revenue capture.

## Steps



1. **DocuSign Contract**


   - Send contract via DocuSign.


   - Capture signed timestamp (e.g., `18:07 PST`).


2. **Lock MRR**


   - Record monthly recurring revenue (MRR) in the billing system.


   - Set tier (e.g., *monitored tier*), term, and start date.


3. **Priority Async Queue**


   - Add a line‑item `priority async queue` to the customer's profile.


   - Flag the queue to run **first** in every background run (global priority flag).


4. **Invoice & Payment**


   - Generate first invoice (covering Dec + Jan prepaid).


   - Process payment via card and confirm receipt.


5. **Data Ingestion (if applicable)**


   - Provide S3 bucket details.


   - Customer uploads dataset (e.g., `11.3 TB` compliance data).


6. **Background Job Launch**


   - Trigger the initial background job.


   - Send the **teleport URL** to the customer for real‑time monitoring.


7. **Monitoring & Reporting**


   - Enable monitored‑tier dashboards.


   - Share progress screenshots / phone‑friendly view.


8. **Follow‑up**


   - CFO/Stakeholder feedback loop.


   - Prepare referral outreach for additional portfolio.

## Automation Tips



- Store step timestamps in a JSON log (`onboarding_log.json`).


- Use a small Bash/Python script to auto‑populate the template with client‑specific values.


- Schedule a daily reminder to send the next pilot’s onboarding email.

## Expected Impact



- **Avg. MRR per pilot**: $8‑9 k


- **Target by Friday**: > $45 k new MRR from async + teleport pilots.

---
*Generated on 2025‑11‑23 by Antigravity.*
