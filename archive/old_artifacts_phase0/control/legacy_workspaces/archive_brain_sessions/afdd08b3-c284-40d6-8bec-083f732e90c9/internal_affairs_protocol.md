# Internal Affairs Protocol: The "Red Shield"
**Classification: EYES ONLY / NOFORN**
**Objective:** Operationalize the "Counter-Espionage & Fraud (CEF)" module for the Sentinel System.

## 1. Strategic Pivot
Shift from "Alpha Generation" (Market) to "Anomaly Detection" (Internal).
**Target:** Insider Threats, Fake Vendors, Procurement Fraud, and Supply Chain Infiltration.

## 2. The Protocols

### A. The "Ding" Protocol (Insider Threat / Espionage)
**Target:** Data Exfiltration & Presence Discrepancy (Ref: Google/Linwei Ding).
**Logic:** `IF (Physical_Badge_Location != Digital_IP_Location) THEN FLAG.`
**Layers Active:**
- **Layer 1 (UEBA):** Chronicle SecOps correlates Physical Badge Logs vs. Digital Network/VPN Logs.
- **Layer 10 (Espionage):** DLP scans for mass PDF/Code extraction to personal cloud storage (GDrive, Dropbox).
**Implementation:**
- **Input:** HR Badge Swipes (SQL), VPN Logs (Splunk/Chronicle).
- **Engine:** BigQuery Anomaly Detection.
- **Action:** Immediate account lock via Identity-Aware Proxy (IAP).

### B. The "Ghost Ship" Protocol (Supply Chain Fraud)
**Target:** Fake Invoices & "Shell" Vendors.
**Logic:** `IF (Vendor_Address == Residential OR Warehouse_Activity == Zero) THEN BLOCK_PAYMENT.`
**Layers Active:**
- **Layer 9 (Supply Chain):** Validates physical logistics infrastructure.
- **Layer 15 (Anti-Crime):** Detects money laundering fronts.
**Implementation:**
- **Grounding:** Google Maps Platform (Places API + Aerial View).
- **Analysis:**
    - **Visual Audit:** "Is there a loading dock?" (Vision API on Satellite Imagery).
    - **Traffic Audit:** "Is there truck traffic?" (Maps Traffic Data).
    - **Physics Audit:** "Can a ship move from Shanghai to LA in 2 days?" (Impossible Physics Check).

### C. The "Kickback" Graph (Collusion Detection)
**Target:** Procurement Officers colliding with Vendors.
**Logic:** `IF (Employee_Spouse == Vendor_Owner) OR (Employee_IP == Vendor_Invoice_IP) THEN FLAG.`
**Layers Active:**
- **Layer 11 (Favoritism):** Detects conflict of interest.
- **Layer 15 (Anti-Crime):** Detects bribery/kickbacks.
**Implementation:**
- **Engine:** BigQuery Graph Link Analysis.
- **Data:** Internal HR Records + External "People Data" APIs.

## 3. The Dashboard (Internal Affairs)
**Zone A: RED FLAG FEED (Real-Time)**
- "ESPIONAGE ALERT: User [X] accessing [Y] files from [Z] location."
- "FRAUD ALERT: Vendor [A] address resolves to Residential."

**Zone B: PATTERN OF LIFE MAP (Long-Term)**
- Supply Chain Visualization (Green=Verified, Red=Ghost).
- Insider Risk Heatmap (Financial Stress Indicators).

## 4. Google Cloud Arsenal
| Protocol | Component | GCP Service |
| :--- | :--- | :--- |
| **Ding** | Identity | Identity-Aware Proxy (IAP) |
| **Ding** | Telemetry | Chronicle SecOps |
| **Ghost Ship** | Grounding | Google Maps (Places/Aerial) |
| **Kickback** | Graph | BigQuery + People API |
| **All** | AI Brain | Vertex AI (Gemini 3 Pro) |
