# Operation GLOW UP: Swarm Orchestration

## Mission

**Objective**: Burn $2,600 in Google Cloud credits in 26 days by orchestrating a high-intensity swarm of AI agents.
**Method**: Army Troop Leading Procedures (TLP) adapted for autonomous coding swarms.
**Structure**: 3 Squads (Alpha, Bravo, Charlie) x 3 Units x 2 Agents (Cursor + Antigravity) = **18 Active Agents**.

## Components

### 1. The Boss (`agents/swarm_boss.py`)

- Implements the 8-Step TLP State Machine:

  1. Receive the Mission

  2. Issue Warning Order

  3. Make Tentative Plan

  4. Initiate Movement

  5. Conduct Reconnaissance (CRM Integration)

  6. Complete the Plan

  7. Issue the Order

  8. Supervise and Refine

- Manages the 3x3 Grid of Agents.

- Tracks "Credit Burn" (simulated Vertex AI usage).

### 2. The Dashboard (`agents/dashboard.py`)

- A TUI (Text User Interface) built with `rich`.

- Visualizes the status of all 18 agents in real-time.

- Shows the current TLP Step and Total Burn.

### 3. Execution (`run_operation_glow_up.py`)

- The entry point script.

- Initializes the Boss and launches the Dashboard.

## How to Run

```bash
python3 run_operation_glow_up.py

```

## Configuration

- **CRM**: The agents simulate querying the CRM for doctrine (TLP).

- **Vertex AI**: Currently simulated. To enable real credit burn, modify `agents/swarm_boss.py` to make actual API calls to `google-cloud-aiplatform` in the `_supervise` method.

## Next Steps

1. **Connect Real Vertex AI**: Replace the random burn logic in `swarm_boss.py` with actual `gemini-1.5-pro` inference calls.

2. **Headless Docker**: Integrate `computer_spawner.py` to spin up actual containers if needed (though Python threads are more efficient for pure API burning).
