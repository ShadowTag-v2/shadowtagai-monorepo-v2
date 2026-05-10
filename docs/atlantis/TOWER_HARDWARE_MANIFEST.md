# PNKLN Tower Node Manifest (v1.0)

**Date:** Dec 8, 2025
**Standard:** NEMA 4X / IP66
**Cooling:** Passive 2-Phase Direct-to-Chip (Zero Maintenance)

## 1. Enclosure


* **Model:** NEMA 4X Stainless Steel or Molded Fiberglass (Ref: Tripp Lite SmartRack or OCC Fiber Enclosure).

* **Rating:** IP66 (Dust tight, powerful water jets).

* **Mounting:** Pole-mount compatible (300ft elevation rated).

* **Security:** Tamper-proof locks + optical intrusion sensor.

## 2. Compute Module (The "Brain")


* **Server:** Ruggedized Edge Node (e.g., Dell PowerEdge XR4000 or similar OEM).

* **Accelerator:** NVIDIA L4 or L40S (Low profile, high inference).

* **Cooling System:** **Passive 2-Phase Immersion/Direct-to-Chip** (e.g., Seguente COLDWARE).

    * *Why:* No fans = No vibration/noise. Self-regulating coolant circulation via heat. PUE 1.02.

* **Power:** -48V DC (Telecom Standard) with internal DC-DC conversion.

## 3. Connectivity (The "Nervous System")


* **Primary:** 10Gbps Fiber SFP+ (Tower Backhaul).

* **Secondary:** Starlink Flat High Performance (Mounted on enclosure exterior).

    * *Jitter Buffer:* Configured to 25ms.

    * *Cable:* Max 25m run to PSU.

## 4. Power & Backup


* **Input:** -48V DC Telecom Power.

* **Backup:** 2kWh Li-Ion "Blade" Battery (15 min run-time for graceful shutdown).
