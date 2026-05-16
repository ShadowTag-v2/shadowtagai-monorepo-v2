# Looker Studio Integration Guide

## Overview

This guide explains how to connect the **Gemini Ingestion Layer** metrics (stored in BigQuery) to **Looker Studio** for the AM Briefing dashboard.

## Prerequisites



1. **GCP Project**: `pnkln-project`


2. **BigQuery Dataset**: `pnkln_ingestion`


3. **Table**: `ingestion_metrics` (created using `scripts/bigquery_schema.json`)

## Steps to Connect

### 1. Create Data Source



1. Open [Looker Studio](https://lookerstudio.google.com/).


2. Click **Create** > **Data Source**.


3. Select **BigQuery**.


4. Navigate to: `pnkln-project` > `pnkln_ingestion` > `ingestion_metrics`.


5. Click **Connect**.

### 2. Configure Fields



- Ensure `timestamp` is recognized as **Date & Time**.


- Ensure `items_ingested`, `tier_*_count`, and `total_cost_usd` are **Numbers**.


- Create a calculated field `Tier 1 %`: `tier_1_count / items_ingested`.

### 3. Create Dashboard



1. **Scorecards**:


    - Total Items (Today)


    - Average Relevance Score


    - Quality Gates Passed (Boolean)


2. **Time Series Charts**:


    - Items Ingested over Time


    - Cost per Run over Time


3. **Pie Chart**:


    - Tier Distribution (Tier 1 vs Tier 2 vs Tier 3)

## Automation

The BigQuery table is populated automatically by the `GeminiIngestionLayer` at the end of every run (Step 5: Record metrics).
