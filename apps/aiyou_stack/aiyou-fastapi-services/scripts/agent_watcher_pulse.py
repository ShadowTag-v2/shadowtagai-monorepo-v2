import os

from google.cloud import firestore

# Lock to shadowtag-omega-v2 or env var
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v2")
db = firestore.Client(project=PROJECT_ID)


def pulse_agent_position(current_task_id, file_path):
    print(f">>> 🤖 AGENT_WATCHER: Pulse at {file_path}")

    # Update the Agent Node in Velocity Lake
    agent_ref = db.collection("internal_monitoring").document("antigravity_agent_01")
    agent_ref.set(
        {
            "label": "Antigravity Agent",
            "current_task": current_task_id,
            "last_touched_file": file_path,
            "last_pulse": firestore.SERVER_TIMESTAMP,
            "vibe": "operational",
        },
    )

    # Create a transient 'Observation' edge in the graph
    # We use a fixed ID so it updates rather than accumulates infinitely if that's the goal,
    # or random ID for history. Using fixed 'agent_pulse' for 'current state' visualization.
    db.collection("graph_edges").document("agent_pulse").set(
        {
            "source": "antigravity_agent_01",
            "target": current_task_id,  # Links Agent to the ORCID or Task node it is fixed on
            "type": "observing",
            "transient": True,
        },
    )


if __name__ == "__main__":
    # Simulate the agent moving to your Researcher Profile
    pulse_agent_position("orcid_0001", "graph/views.py")
