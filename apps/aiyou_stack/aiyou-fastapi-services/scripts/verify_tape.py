import os

from src.antigravity.ironwood_mcp import TAPE_FILE, log_event, read_tape


def verify_scribe():
    print(f"Testing Scribe @ {TAPE_FILE}")

    # Clean slate
    if os.path.exists(TAPE_FILE):
        os.remove(TAPE_FILE)

    # 1. Simulating Events
    events = [
        ("Agent-007", "thought", "Initiating Universal Tape test."),
        ("Ironwood-TPU", "metric", "Core Temp: 35C"),
        ("Memory-Drive", "search", "Found 'The Book' in G-Drive"),
    ]

    print("Writing events...")
    for src, evt, content in events:
        res = log_event(src, evt, content)
        print(f"  {src}: {res}")

    # 2. Reading Tape
    print("Reading tape...")
    tape_content = read_tape()
    print("--- TAPE START ---")
    print(tape_content.strip())
    print("--- TAPE END ---")

    if "Agent-007" in tape_content and "35C" in tape_content:
        print("✅ SUCCESS: Universal Tape is Live.")
    else:
        print("❌ FAILURE: Data mismatch.")


if __name__ == "__main__":
    verify_scribe()
