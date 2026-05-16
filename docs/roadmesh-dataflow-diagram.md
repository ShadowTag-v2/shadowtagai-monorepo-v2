# RoadMesh Data Flow Diagram
## Visual Architecture for Technical Presentations

---

## 1. High-Level System Data Flow

```mermaid
graph TB
    subgraph SENSORS["🔍 SENSOR SUITE"]
        L[LiDAR<br/>128-beam<br/>20Hz<br/>115 Mbps]
        C[Cameras<br/>8× 8MP<br/>30fps<br/>15.4 Gbps]
        R[Radar<br/>5× 77GHz<br/>20Hz<br/>40 Kbps]
        I[IMU/GNSS<br/>1kHz<br/>48 Kbps]
    end

    subgraph PERCEPTION["🧠 PERCEPTION (35ms)"]
        BEV[BEV Fusion<br/>Transformer<br/>256×200×200 grid]
        OBJ[3D Object Detection<br/>~100 objects<br/>72.3% AP]
        SEG[Semantic Segmentation<br/>20 classes<br/>68.1% IoU]
        OCC[Occupancy Prediction<br/>256×200×200×16<br/>Probabilistic]
    end

    subgraph WORLD["🗺️ WORLD REPRESENTATION (8ms)"]
        GRAPH[RoadMesh Graph<br/>GNN Processing<br/>~500 waypoints<br/>~100 agents]
        TOPO[Dynamic Topology<br/>10Hz update<br/>4 edge types]
    end

    subgraph FORECAST["🔮 FORECASTING (22ms)"]
        TRAJ[Multi-Agent Trajectories<br/>6 modes per agent<br/>8s horizon<br/>1.8m ADE]
        OCC4D[4D Occupancy<br/>80 time steps<br/>45.3% IoU]
    end

    subgraph PLANNING["🎯 PLANNING (35ms)"]
        ROUTE[Global Route<br/>A* on graph<br/>1Hz]
        BEHAVIOR[Behavioral FSM<br/>5Hz<br/>Maneuver selection]
        LOCAL[Trajectory Optimization<br/>Diffusion + Sampling<br/>10Hz]
    end

    subgraph CONTROL["⚙️ CONTROL (10ms)"]
        MPC[Model Predictive Control<br/>100Hz<br/>2s horizon]
        SAFETY[Safety Governor<br/>Emergency brake<br/>Constraint checking]
    end

    subgraph ACTUATORS["🚗 ACTUATORS"]
        THR[Throttle]
        BRK[Brake]
        STR[Steering]
        CAN[CAN Bus<br/>100Hz]
    end

    subgraph CLOUD["☁️ GOOGLE CLOUD"]
        VLM[VLM Inference<br/>GPT-4V/Claude<br/>0.1Hz<br/>2-5s latency]
        TRAIN[Model Training<br/>TPU v5 Pods<br/>Weekly updates]
        STORE[Data Lake<br/>500TB+<br/>Fleet learning]
    end

    %% Data flow connections
    L --> BEV
    C --> BEV
    R --> BEV
    I --> BEV

    BEV --> OBJ
    BEV --> SEG
    BEV --> OCC

    OBJ --> GRAPH
    SEG --> GRAPH
    OCC --> GRAPH

    GRAPH --> TOPO
    TOPO --> TRAJ
    TRAJ --> OCC4D

    GRAPH --> ROUTE
    OCC4D --> BEHAVIOR
    ROUTE --> BEHAVIOR
    BEHAVIOR --> LOCAL

    LOCAL --> MPC
    MPC --> SAFETY

    SAFETY --> THR
    SAFETY --> BRK
    SAFETY --> STR
    SAFETY --> CAN

    %% Cloud connections
    C -.->|Triggered<br/>0.1Hz| VLM
    VLM -.->|Scene understanding| GRAPH

    GRAPH -.->|Telemetry<br/>10KB/s| STORE
    STORE -.->|Training data| TRAIN
    TRAIN -.->|Model updates<br/>Weekly| BEV

    style SENSORS fill:#e1f5ff
    style PERCEPTION fill:#fff4e1
    style WORLD fill:#e1ffe1
    style FORECAST fill:#ffe1f5
    style PLANNING fill:#f5e1ff
    style CONTROL fill:#ffe1e1
    style ACTUATORS fill:#e1e1e1
    style CLOUD fill:#f0f0f0
```

---

## 2. Detailed Perception Pipeline

```mermaid
graph LR
    subgraph INPUT["Synchronized Inputs (10Hz)"]
        L1[LiDAR Point Cloud<br/>2.4M points]
        C1[8× Camera Images<br/>8MP each]
        R1[Radar Targets<br/>512 tracks]
        I1[IMU/GNSS<br/>Ego pose]
    end

    subgraph BACKBONE["Feature Extraction"]
        PP[PointPillars<br/>LiDAR → 64×512×512]
        RN[ResNet-50<br/>Camera → 8×256×64×64]
        RadNet[RadarNet<br/>Radar → 64×256×256]
        MLP1[MLP<br/>IMU → 128-dim]
    end

    subgraph FUSION["BEV Fusion Transformer"]
        LSS[Lift-Splat-Shoot<br/>Camera → BEV]
        VOX[Voxel Projection<br/>LiDAR → BEV]
        XATTN[Cross-Attention<br/>4 layers]
        BEV_OUT[BEV Features<br/>256×200×200<br/>100m × 100m]
    end

    subgraph HEADS["Task Heads"]
        H1[3D Detection<br/>Bounding boxes]
        H2[Segmentation<br/>Per-pixel classes]
        H3[Occupancy<br/>Probabilistic grid]
        H4[Lane Graph<br/>Topology extraction]
    end

    L1 --> PP --> VOX
    C1 --> RN --> LSS
    R1 --> RadNet --> XATTN
    I1 --> MLP1 --> XATTN

    VOX --> XATTN
    LSS --> XATTN
    XATTN --> BEV_OUT

    BEV_OUT --> H1
    BEV_OUT --> H2
    BEV_OUT --> H3
    BEV_OUT --> H4

    H1 --> OUT[Perception Output]
    H2 --> OUT
    H3 --> OUT
    H4 --> OUT

    style INPUT fill:#e1f5ff
    style BACKBONE fill:#fff4e1
    style FUSION fill:#e1ffe1
    style HEADS fill:#ffe1f5
```

---

## 3. RoadMesh Graph Structure

```mermaid
graph TB
    subgraph GRAPH["RoadMesh Dynamic Graph"]
        subgraph NODES["Nodes (~650 total)"]
            N1[Waypoint Nodes<br/>~500 active<br/>Lane centerlines<br/>128-dim features]
            N2[Agent Nodes<br/>~100 dynamic<br/>Vehicles/pedestrians<br/>Velocity + intent]
            N3[Landmark Nodes<br/>~50 static<br/>Traffic lights/signs<br/>Semantic attributes]
        end

        subgraph EDGES["Edges (~1,500 total)"]
            E1[Spatial<br/>Distance, curvature<br/>Waypoint ↔ Waypoint]
            E2[Traversability<br/>Cost, risk<br/>Directional]
            E3[Interaction<br/>K-NN k=5<br/>Agent ↔ Agent]
            E4[Association<br/>Proximity <10m<br/>Agent ↔ Waypoint]
        end
    end

    subgraph GNN["Graph Neural Network (4 layers)"]
        GNN1[GraphConv 128→256]
        GNN2[GraphConv 256→256]
        GNN3[GraphConv 256→512]
        GNN4[GraphConv 512→512]
    end

    subgraph OUTPUT["Graph Output"]
        O1[Enriched Node Embeddings<br/>512-dim<br/>Spatial + semantic context]
        O2[Edge Costs<br/>Traversability weights<br/>Dynamic updates]
    end

    N1 --> GNN1
    N2 --> GNN1
    N3 --> GNN1
    E1 --> GNN1
    E2 --> GNN1
    E3 --> GNN1
    E4 --> GNN1

    GNN1 --> GNN2 --> GNN3 --> GNN4

    GNN4 --> O1
    GNN4 --> O2

    O1 --> PLAN[To Planning]
    O2 --> PLAN

    style NODES fill:#e1ffe1
    style EDGES fill:#ffe1e1
    style GNN fill:#fff4e1
    style OUTPUT fill:#f5e1ff
```

---

## 4. Planning Hierarchy

```mermaid
graph TB
    subgraph L1["Layer 1: Global Route (1Hz)"]
        START[Start Position]
        GOAL[Goal Position]
        ASTAR[A* Search<br/>Coarse graph<br/>500m+ horizon]
        ROUTE[Waypoint Sequence]
    end

    subgraph L2["Layer 2: Behavioral (5Hz)"]
        FSM[Finite State Machine]
        STATE1[Follow Lane]
        STATE2[Change Lane]
        STATE3[Yield]
        STATE4[Overtake]
        STATE5[Park]
        MANEUVER[High-level Maneuver<br/>+ Constraints]
    end

    subgraph L3["Layer 3: Local Trajectory (10Hz)"]
        INPUT_L3[Inputs:<br/>Maneuver<br/>Occupancy forecast<br/>Agent trajectories]

        DIFF[Diffusion Planner<br/>Learned distribution<br/>10 denoising steps]
        SAMPLE[Sampling Planner<br/>200 candidates<br/>Cost evaluation]
        GRAPH_SEARCH[Graph Search<br/>Spatiotemporal A*<br/>Dynamic costs]

        SELECT[Trajectory Selection<br/>Safety + Comfort]
        TRAJ[Ego Trajectory<br/>80 points × 8s]
    end

    subgraph CTRL["Control (100Hz)"]
        MPC_CTRL[Model Predictive Control<br/>2s horizon<br/>QP optimization]
        CMD[Actuator Commands<br/>Throttle, Brake, Steering]
    end

    START --> ASTAR
    GOAL --> ASTAR
    ASTAR --> ROUTE

    ROUTE --> FSM
    FSM --> STATE1
    FSM --> STATE2
    FSM --> STATE3
    FSM --> STATE4
    FSM --> STATE5

    STATE1 --> MANEUVER
    STATE2 --> MANEUVER
    STATE3 --> MANEUVER
    STATE4 --> MANEUVER
    STATE5 --> MANEUVER

    MANEUVER --> INPUT_L3
    INPUT_L3 --> DIFF
    INPUT_L3 --> SAMPLE
    INPUT_L3 --> GRAPH_SEARCH

    DIFF --> SELECT
    SAMPLE --> SELECT
    GRAPH_SEARCH --> SELECT
    SELECT --> TRAJ

    TRAJ --> MPC_CTRL
    MPC_CTRL --> CMD

    style L1 fill:#e1f5ff
    style L2 fill:#e1ffe1
    style L3 fill:#fff4e1
    style CTRL fill:#ffe1e1
```

---

## 5. Compute Allocation (Edge Device)

```mermaid
pie title "NVIDIA Orin AGX - 254 TOPS Allocation"
    "Perception (BEV + Detection)" : 180
    "Forecasting (Trajectories + Occupancy)" : 35
    "Graph Neural Network" : 25
    "Planning (Optimization)" : 14
    "System Overhead" : 10
```

```mermaid
pie title "Memory Usage - 64 GB Available"
    "Perception (Models + Activations)" : 12
    "Forecasting Models" : 4
    "Graph Storage + History" : 2
    "Planning Buffers" : 1.5
    "Sensor Data Buffers" : 8
    "System (OS + Drivers)" : 4
    "Available Headroom" : 32.5
```

---

## 6. Latency Budget Breakdown

```mermaid
gantt
    title End-to-End Latency Budget (100ms target)
    dateFormat X
    axisFormat %L ms

    section Sensors
    Data Acquisition           :0, 5

    section Preprocessing
    Sync + Calibration        :5, 5

    section Perception
    BEV Fusion                :10, 25
    Object Detection          :35, 10
    Segmentation              :35, 5

    section World Rep
    Graph Update              :45, 5
    GNN Inference             :50, 3

    section Forecasting
    Agent Prediction          :53, 15
    Occupancy Forecast        :68, 7

    section Planning
    Behavioral Planning       :75, 10
    Trajectory Optimization   :85, 15

    section Control
    MPC Solve                 :100, 5
```

---

## 7. Foundation Model Integration Flow

```mermaid
sequenceDiagram
    participant Edge as Edge Device
    participant Detect as Anomaly Detection
    participant Pack as Data Packager
    participant Cloud as Google Cloud VLM
    participant Graph as RoadMesh Graph

    Edge->>Detect: Perception output (10Hz)
    Detect->>Detect: Check confidence scores

    alt Low confidence (<0.5) OR Novel object
        Detect->>Pack: Trigger VLM query
        Pack->>Pack: Select key frame
        Pack->>Pack: Compress (8MP→1MP)
        Pack->>Pack: Add context (BEV overlay)
        Pack->>Cloud: Upload image + prompt

        Cloud->>Cloud: VLM inference (2-5s)
        Cloud->>Cloud: Generate structured output

        Cloud->>Edge: Return JSON analysis
        Edge->>Graph: Add virtual obstacles
        Graph->>Graph: Update edge costs
        Graph->>Edge: Re-plan trajectory
    else High confidence
        Detect->>Edge: Continue normal operation
    end

    Note over Edge,Cloud: Frequency: 0.1-1 Hz (triggered)
    Note over Cloud: Cost: $0.01/query (~$24/vehicle/month)
```

---

## 8. Deployment Architecture

```mermaid
graph TB
    subgraph FLEET["Vehicle Fleet (1000+ vehicles)"]
        V1[Vehicle 1<br/>NVIDIA Orin<br/>RoadMesh Stack]
        V2[Vehicle 2<br/>NVIDIA Orin<br/>RoadMesh Stack]
        V3[Vehicle N<br/>NVIDIA Orin<br/>RoadMesh Stack]
    end

    subgraph NETWORK["Network Layer"]
        MODEM[4G/5G Modem<br/>Bidirectional]
    end

    subgraph GCP["Google Cloud Platform"]
        subgraph INGEST["Ingestion"]
            PUBSUB[Cloud Pub/Sub<br/>Telemetry stream]
            GCS[Cloud Storage<br/>Data lake: 500TB+]
            FLOW[Dataflow<br/>Stream processing]
        end

        subgraph TRAIN_LAYER["Training"]
            TPU[Vertex AI<br/>TPU v5 Pods]
            GPU[A100 GPU × 32<br/>Perception training]
            BQ[BigQuery<br/>Analytics]
            AR[Artifact Registry<br/>Model versioning]
        end

        subgraph INFERENCE["Inference"]
            VLM_CLOUD[VLM Endpoints<br/>GPT-4V / Claude 3.5]
            API[Cloud Run<br/>API services]
            CDN[Cloud CDN<br/>Model distribution]
        end

        subgraph MGMT["Fleet Management"]
            DASH[Telemetry Dashboard<br/>Grafana]
            DEPLOY[Model Deployment<br/>A/B testing]
            INCIDENT[Incident Analysis<br/>Failure logs]
        end
    end

    V1 -->|10KB/s telemetry| MODEM
    V2 -->|10KB/s telemetry| MODEM
    V3 -->|10KB/s telemetry| MODEM

    MODEM --> PUBSUB
    PUBSUB --> FLOW
    FLOW --> GCS

    GCS --> TPU
    GCS --> GPU
    GCS --> BQ

    TPU --> AR
    GPU --> AR
    AR --> CDN

    CDN -.->|Model updates<br/>Weekly| MODEM
    MODEM -.->|5GB/week| V1
    MODEM -.->|5GB/week| V2
    MODEM -.->|5GB/week| V3

    V1 -.->|VLM query<br/>0.1Hz| VLM_CLOUD
    V2 -.->|VLM query<br/>0.1Hz| VLM_CLOUD
    V3 -.->|VLM query<br/>0.1Hz| VLM_CLOUD

    VLM_CLOUD -.->|Scene analysis<br/>2-5s| MODEM

    FLOW --> DASH
    FLOW --> INCIDENT
    AR --> DEPLOY

    style FLEET fill:#e1f5ff
    style NETWORK fill:#e1e1e1
    style INGEST fill:#fff4e1
    style TRAIN_LAYER fill:#e1ffe1
    style INFERENCE fill:#ffe1f5
    style MGMT fill:#f5e1ff
```

---

## 9. Safety Architecture Layers

```mermaid
graph TB
    subgraph PRIMARY["Primary: RoadMesh Planning"]
        P1[Graph-based Planning<br/>Diffusion model<br/>99.9% reliability target]
    end

    subgraph SECONDARY["Secondary: Rule-based Fallback"]
        P2[Simple Obstacle Avoidance<br/>Triggers on timeout >100ms]
    end

    subgraph TERTIARY["Tertiary: Emergency Braking"]
        P3[Hardware FPGA<br/>Independent sensors<br/><20ms reaction]
    end

    subgraph QUATERNARY["Quaternary: Human Takeover"]
        P4[Steering torque sensor<br/>Brake pedal override<br/>Instant disengagement]
    end

    subgraph ULTIMATE["Ultimate: Mechanical Failsafe"]
        P5[Watchdog timer<br/>Spring-loaded brake]
    end

    P1 -->|Planning failure| P2
    P2 -->|Fallback failure| P3
    P3 -->|System failure| P4
    P4 -->|All else fails| P5

    P5 --> SAFE[VEHICLE STOPPED SAFELY]

    style PRIMARY fill:#e1ffe1
    style SECONDARY fill:#fff4e1
    style TERTIARY fill:#ffe1e1
    style QUATERNARY fill:#ffe1f5
    style ULTIMATE fill:#f5e1e1
    style SAFE fill:#90EE90
```

---

## 10. Data Flow Summary Table

| Stage | Input | Processing | Output | Latency | Compute |
|-------|-------|------------|--------|---------|---------|
| **Sensors** | Physical world | Synchronization | Raw data (16 Gbps) | 5ms | N/A |
| **Perception** | Sensor data | BEV fusion + heads | Objects, occupancy, lanes | 35ms | 180 TOPS |
| **World Rep** | Perception output | GNN on graph | Enriched graph (512-dim) | 8ms | 25 TOPS |
| **Forecasting** | Graph + history | Multi-agent prediction | Trajectories (8s horizon) | 22ms | 35 TOPS |
| **Planning** | Forecast + graph | Diffusion/sampling | Ego trajectory (80 pts) | 35ms | 14 TOPS |
| **Control** | Planned trajectory | MPC optimization | Actuator commands | 10ms | <1 TOPS |
| **TOTAL** | Sensors → Actuators | Full pipeline | Control @ 100Hz | **95ms** | **254 TOPS** |

---

## 11. Performance Metrics Summary

### Accuracy
- **3D Object Detection AP:** 72.3% (vs industry 68-75%)
- **BEV Segmentation IoU:** 68.1% (vs industry 62-70%)
- **Lane Detection F1:** 91.2% (vs industry 88-93%)
- **Trajectory ADE (8s):** 1.8m (vs industry 2.1-2.5m)
- **Planning Success Rate:** 94.7%
- **Collision Rate:** 0.003/mile (target <0.01)

### Efficiency
- **End-to-End Latency:** 95ms (target <100ms)
- **Power Consumption:** 53W (edge device)
- **Memory Usage:** 20 GB (of 64 GB available)
- **Data Rate:** 500 GB/hour per vehicle

### Cost
- **Hardware (per vehicle):** $12,700 (target $6,500 at scale)
- **Cloud (per vehicle/month):** $35
- **Training (per model):** $138K/month (fleet-wide)

---

## Appendix: Legend

### Diagram Color Coding
- 🔵 **Blue (Sensors/Input):** Physical sensors and data acquisition
- 🟡 **Yellow (Processing):** Computation and inference
- 🟢 **Green (Representation):** Data structures and graphs
- 🟣 **Purple (Output):** Planning and control
- ⚪ **Gray (Actuators):** Physical vehicle control
- ☁️ **Cloud (Training/Inference):** Off-vehicle computation

### Performance Icons
- ⏱️ **Latency:** Time from input to output
- 💾 **Memory:** RAM usage
- ⚡ **Compute:** TOPS (AI operations)
- 📊 **Throughput:** Data rate or frequency
- 💰 **Cost:** Hardware or cloud expense

---

**Document Version:** 1.0
**Rendering:** Best viewed in Mermaid-compatible markdown viewers (GitHub, GitLab, VS Code with extension)
**For Presentations:** Export diagrams as PNG/SVG using Mermaid CLI or online editor
**Contact:** RoadMesh Technologies - Technical Team
