# MARKET & POLIS: THE PREDICTIVE ENGINE
> **Protocol**: KISSINGER-SOROS
> **Objective**: Synthesize Financial Modeling with High-Level Political Theory to predict market outcomes.

## 1. The Core Thesis
Markets do not move in a vacuum. They are downstream of Policy and Geopolitics.
To beat the market, we must predict the *rules of the game* before they change.
We combine **Quantitative Finance** (The "Soros" Engine) with **Political Science** (The "Kissinger" Engine).

## 2. The "Kissinger" Engine (Political Science)
We operationalize leading theories into Python classes for the Kosmos n-autoresearch/Kosmos/BioAgents to simulate.

### A. Selectorate Theory (Bueno de Mesquita)
*   **Logic**: Leaders want to survive. Their policy depends on `W` (Winning Coalition size) and `S` (Selectorate size).
*   **Application**: Predict sovereign debt defaults, tax policy changes, or trade wars based on a leader's need to payoff their coalition.
*   **Code**: `calculate_survival_probability(W, S, resources)`

### B. Expected Utility & Game Theory (Nash)
*   **Logic**: Actors act rationally to maximize utility WRT their risk profile.
*   **Application**: Predict outcome of mergers, sanctions, or treaties.
*   **Code**: `solve_nash_equilibrium(players, payoffs)`

### C. Lateral Pressure Theory (Choucri & North)
*   **Logic**: Expanding states require resources, leading to conflict.
*   **Application**: Predict commodity spikes (Oil, Lithim) based on expansionist state behavior.

## 3. The "Soros" Engine (Financial Modeling)
We use the cloud's infinite compute to run massive simulations.

### A. Monte Carlo Simulations
*   **Method**: Run 100,000 future scenarios based on volatility and drift.
*   **Application**: Portfolio Risk Assessment (VaR).

### B. NLP Sentiment Analysis (Vertex AI)
*   **Method**: Ingest thousands of news articles/earnings calls.
*   **Application**: Detect "Animal Spirits" before price action.

### C. Advanced Financials (DCF, LBO)
*   **DCF**: Discounted Cash Flow valuation adjusted for WACC (Risk).
*   **Connection**: WACC increases when "Grounding" finds CEO distraction (Yachts).

### D. Partisan Business Cycle
*   **Model**: Markets perform differently under Democrats vs. Republicans.
*   **Fold In**: Adjust Growth/Volatility assumptions based on election polls.

## 4. The "Looking Glass" Engine (Vertex AI Grounding)
We ground our models in physical reality using **Vertex AI Grounded Search**.
*   **Source**: Google Search (Public Records, News) & Enterprise Documents (SEC Filings via RAG).
*   **Target**: Senior Executives (CEO, CFO, CTO) list via EDGAR/LinkedIn.
*   **Signals & WACC Impact**:
    *   **"The Icarus Signal"**: Yacht/Jet on Note -> +2.5% WACC (Distraction/Leverage).
    *   **"The Bunker Signal"**: 2nd Mortgage -> +4.0% WACC (Liquidity Crisis).
    *   **"The Empire Signal"**: Cash Land Purchase -> -1.0% WACC (Confidence).
*   **Anomaly Detection**: BigQuery ML / Vertex AutoML scans for spending spikes vs. Stock Performance.

## 5. The Unified Workflow (`market_polis.py`)
1.  **Grounding (Vertex)**: Fetch live executive behaviors -> Calculate `wacc_penalty`.
2.  **Polis Analysis (Kissinger)**: Partisan Cycle (Polls) -> Adjust `growth_adj` / `volatility`.
3.  **Financial Analysis (Soros)**: DCF with specific Risk-Adjusted WACC.
4.  **Decision**: Buy/Sell/Hedge based on Valuation vs. Market Cap.

## 6. Deployment
Working directory: `kosmos_gcloud/market_polis.py` (GCloud Native).
