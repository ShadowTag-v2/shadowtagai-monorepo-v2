import asyncio
import uuid

# Configuration
MAX_CONCURRENT_MONKEYS = 5  # The "Bouncer" for your API Quota


async def spawn_monkey(sem: asyncio.Semaphore, task: str):
    """Spawns a single monkey process, respecting the semaphore limit."""
    async with sem:
        mission_id = str(uuid.uuid4())[:8]
        print(f"🌖 [Swarm] Dispatching Monkey {mission_id}...")

        # We use asyncio.create_subprocess_exec for non-blocking I/O
        # The Monkey inherits the HTTP_PROXY env vars from the Nix shell
        proc = await asyncio.create_subprocess_exec(
            "python",
            "src/monkey.py",
            mission_id,
            task,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode == 0:
            print(f"✅ [Swarm] Monkey {mission_id} returned successfully.")
            return mission_id
        print(f"❌ [Swarm] Monkey {mission_id} died.")
        print(stderr.decode())
        return None


async def run_swarm(tasks: list[str]):
    """The Main Loop: Takes a list of raw tasks and manages the fleet."""
    sem = asyncio.Semaphore(MAX_CONCURRENT_MONKEYS)

    print(f"🚀 [Command] Releasing Swarm on {len(tasks)} targets.")
    print(f"🛑 [Safety] Concurrency Cap: {MAX_CONCURRENT_MONKEYS} active agents.")

    # Create a future for every task
    futures = [spawn_monkey(sem, task) for task in tasks]

    # Wait for the entire fleet to return
    results = await asyncio.gather(*futures)

    print(f"\n🏁 [Command] Swarm recovered. {len([r for r in results if r])} successful missions.")


if __name__ == "__main__":
    # Example Usage: This would be called by your Main Agent
    # In a real run, these come from the user's prompt
    dummy_targets = [f"Generate unit test for module_{i}" for i in range(10)]

    try:
        asyncio.run(run_swarm(dummy_targets))
    except KeyboardInterrupt:
        print("\n[Abort] Recalling the swarm...")
