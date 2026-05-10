# V2X Mesh - Quick Start Guide

Get a V2X mesh network running locally in 10 minutes.

## Prerequisites


- Python 3.11+

- Docker (optional)

- Redis (optional, for persistence)

## Local Development Setup

### 1. Install Dependencies

```bash
cd services/v2x-mesh
pip install -r requirements.txt

```

### 2. Run Mesh Gateway

```bash

# Start the API server

python api.py

```

The gateway will start on:

- HTTP API: http://localhost:8010

- WebSocket: ws://localhost:8011

- Metrics: http://localhost:8012

### 3. Test the API

**Health check**:

```bash
curl http://localhost:8010/health

```

**Broadcast an event**:

```bash
curl -X POST http://localhost:8010/v1/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "hard_brake",
    "severity": 8,
    "description": "Emergency braking detected",
    "position": [37.7749, -122.4194, 10.0],
    "affected_radius_m": 1000
  }'

```

**Add a map feature**:

```bash
curl -X POST http://localhost:8010/v1/map/features \
  -H "Content-Type: application/json" \
  -d '{
    "feature_type": "work_zone",
    "geometry": {
      "type": "Point",
      "coordinates": [-122.4194, 37.7749]
    },
    "properties": {
      "name": "Road Construction",
      "severity": "high"
    }
  }'

```

**Get mesh statistics**:

```bash
curl http://localhost:8010/v1/mesh/stats

```

### 4. WebSocket Stream

```bash

# Install wscat if needed

npm install -g wscat

# Connect to stream

wscat -c ws://localhost:8011/v1/mesh/stream

```

## Run with Docker

```bash

# Build image

docker build -t v2x-mesh:local .

# Run container

docker run -p 8010:8010 -p 8011:8011 -p 8012:8012 v2x-mesh:local

```

## Simulate Multiple Vehicles

Create a test script to simulate multiple vehicles communicating:

```python
import asyncio
from vehicle_client import VehicleClient, V2XClientConfig, VehicleState
import time

async def simulate_vehicle(vehicle_id: str, position: tuple):
    config = V2XClientConfig(
        vehicle_id=vehicle_id,
        vehicle_type="car"
    )

    client = VehicleClient(config=config)
    await client.start()

    # Update state
    state = VehicleState(
        vehicle_id=vehicle_id,
        vehicle_type="car",
        position=position + (10.0,),
        velocity=(15.0, 0.0, 0.0),
        heading=90.0,
        acceleration=(0.0, 0.0, 0.0),
        timestamp=time.time(),
        capabilities=["fsd", "v2x", "gpu_edge"]
    )
    client.update_vehicle_state(state)

    # Broadcast event after 5 seconds
    await asyncio.sleep(5)
    await client.broadcast_event(
        event_type="hard_brake",
        severity=8,
        description=f"Event from {vehicle_id}"
    )

    # Run for 30 seconds
    await asyncio.sleep(25)
    await client.stop()

async def main():
    # Simulate 3 vehicles
    vehicles = [
        ("VEHICLE-001", (37.7749, -122.4194)),
        ("VEHICLE-002", (37.7750, -122.4195)),
        ("VEHICLE-003", (37.7751, -122.4196))
    ]

    tasks = [simulate_vehicle(vid, pos) for vid, pos in vehicles]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

```

Save as `simulate.py` and run:

```bash
python simulate.py

```

## Testing Edge Reasoning

```python
import asyncio
from edge_reasoning import EdgeReasoningPipeline, AttentionContext
import time

async def test_edge_reasoning():
    context = AttentionContext(
        vehicle_position=(37.7749, -122.4194),
        vehicle_velocity=(15.0, 0.0),
        vehicle_heading=90.0
    )

    pipeline = EdgeReasoningPipeline(context, use_gpu=False)

    # Test messages
    messages = [
        {
            "event_type": "hard_brake",
            "position": (37.7750, -122.4190),  # Close
            "timestamp": int(time.time() * 1000),
            "severity": 8
        },
        {
            "event_type": "traffic_jam",
            "position": (37.7800, -122.4200),  # Far
            "timestamp": int(time.time() * 1000) - 5000,
            "severity": 3
        }
    ]

    result = await pipeline.process_mesh_messages(messages)

    print(f"Original: {result['original_count']} messages")
    print(f"Filtered: {result['filtered_count']} messages")
    print(f"Reduction: {result['reduction_pct']:.1f}%")
    print(f"\nFiltered messages:")
    for msg in result['filtered_messages']:
        print(f"  - {msg['event_type']} (severity={msg['severity']})")

asyncio.run(test_edge_reasoning())

```

## Testing CRDT Map Sync

```python
from crdt_mapping import CRDTMapStore, MapFeature
import uuid
import time

# Create two map stores (simulating two vehicles)

store1 = CRDTMapStore(node_id="vehicle-001")
store2 = CRDTMapStore(node_id="vehicle-002")

# Vehicle 1 adds a work zone

feature1 = MapFeature(
    feature_id=str(uuid.uuid4()),
    feature_type="work_zone",
    geometry={"type": "Point", "coordinates": [-122.4194, 37.7749]},
    properties={"name": "Construction Zone", "severity": "high"},
    created_at=int(time.time() * 1000),
    updated_at=int(time.time() * 1000),
    creator_node="vehicle-001"
)

delta1 = store1.create_delta("add", feature1)
print(f"Vehicle 1 created delta: {delta1.delta_id}")

# Vehicle 2 adds a hazard

feature2 = MapFeature(
    feature_id=str(uuid.uuid4()),
    feature_type="hazard",
    geometry={"type": "Point", "coordinates": [-122.4195, 37.7750]},
    properties={"name": "Road Debris", "severity": "medium"},
    created_at=int(time.time() * 1000),
    updated_at=int(time.time() * 1000),
    creator_node="vehicle-002"
)

delta2 = store2.create_delta("add", feature2)
print(f"Vehicle 2 created delta: {delta2.delta_id}")

# Sync: Vehicle 1 receives delta from Vehicle 2

store1.apply_delta(delta2)

# Sync: Vehicle 2 receives delta from Vehicle 1

store2.apply_delta(delta1)

# Both stores should now have both features

print(f"\nVehicle 1 features: {store1.stats['active_features']}")
print(f"Vehicle 2 features: {store2.stats['active_features']}")

# Query features in area

features = store1.query_area(
    min_lat=37.774,
    max_lat=37.776,
    min_lon=-122.420,
    max_lon=-122.418
)

print(f"\nFeatures in area: {len(features)}")
for f in features:
    print(f"  - {f.feature_type}: {f.properties.get('name')}")

```

## Performance Testing

Use `hey` or `ab` to load test the API:

```bash

# Install hey

go install github.com/rakyll/hey@latest

# Load test event broadcasting (100 requests, 10 concurrent)

hey -n 100 -c 10 -m POST \
  -H "Content-Type: application/json" \
  -d '{"event_type":"test","severity":5,"description":"Load test","position":[37.7749,-122.4194,10.0]}' \
  http://localhost:8010/v1/events

# Results should show:

# - Mean latency: 45-75ms

# - Success rate: >99%

```

## Monitoring

Access Prometheus metrics:

```bash
curl http://localhost:8012/metrics

```

Key metrics to watch:

- `v2x_active_peers`: Should increase as vehicles join

- `v2x_messages_processed_total`: Should increment with activity

- `v2x_fsd_interventions_total`: Critical safety interventions

## Troubleshooting

**Import errors**:

```bash

# Make sure you're in the right directory

cd services/v2x-mesh

# Install all dependencies

pip install -r requirements.txt

```

**Port already in use**:

```bash

# Find process using port 8010

lsof -i :8010

# Kill it

kill -9 <PID>

```

**WebSocket connection fails**:

- Check firewall settings

- Verify port 8011 is open

- Try `ws://` not `wss://` for local testing

## Next Steps


1. **Read the full documentation**: [README.md](README.md)

2. **Deploy to GKE**: See deployment guide in README

3. **Explore the code**:

   - `armp_protocol.py` - Core protocol

   - `gossip_protocol.py` - Mesh networking

   - `vehicle_client.py` - On-vehicle client

   - `edge_reasoning.py` - GPU optimization

   - `crdt_mapping.py` - Collaborative mapping


4. **Join the community**: Slack #v2x-mesh

---

**Questions?** Open an issue or reach out on Slack.
