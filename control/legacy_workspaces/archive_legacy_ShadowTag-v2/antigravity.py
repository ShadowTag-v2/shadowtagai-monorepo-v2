# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import asyncio
import sys
import re
from datetime import datetime
import os

# --- CONFIGURATION ---
# Default to a safe 'echo' command if not specified, usually replaced by node agent
AGENT_COMMAND = os.environ.get("ANTIGRAVITY_AGENT_CMD", "node src/agents/scientific/scientific_agent.py")
NUM_AGENTS = int(os.environ.get("ANTIGRAVITY_NUM_AGENTS", 4))

# The "Brain" - Strategy Mapping
STRATEGIES = {
    "IDLE": (
        "Pick the next bead you can actually do usefully now and start coding on it immediately; "
        "communicate what you're doing to the other agents via agent mail."
    ),
    "WORKING": "Keep going, doing useful work! and communicate!",
    "REVIEW": (
        "Great, now I want you to carefully read over all of the new code you just wrote "
        "and other existing code you just modified with 'fresh eyes' looking super carefully "
        "for any obvious bugs, errors, problems, issues, confusion, etc."
    ),
    "COORDINATE": (
        "Be sure to check your agent mail and to promptly respond if needed to any messages; "
        "thereafter proceed meticulously with the plan, doing all of your remaining unfinished tasks systematically "
        "and continuing to notate your progress in-line in the plan document, via beads, and via agent mail messages. "
        "Don't get stuck in 'communication purgatory' where nothing is getting done; be proactive about starting tasks "
        "that need to be done, but inform your fellow agents via messages when you do so and notate that in-line in the plan document. "
        "When you're really not sure what to do, pick the next bead that you can usefully work on and get started."
    ),
    "AUDIT": (
        "Ok can you now turn your attention to reviewing the code written by your fellow agents "
        "and checking for any issues, bugs, errors, problems, inefficiencies, security problems, reliability issues, etc. "
        "and carefully diagnose their underlying root causes using first-principle analysis and thereafter fix or revise them if necessary? "
        "Don't restrict yourself to the latest commits, cast a wider net and go super deep!"
    ),
    "ERROR": ("Diagnose and fix the error you just encountered; if blocked, send agent mail requesting assistance with specific context."),
}


class AgentProcess:
    def __init__(self, id, command):
        self.id = id
        self.command = command
        self.process = None
        self.state = "STARTING"
        self.last_activity = datetime.now()

    async def start(self):
        """Spawns the subprocess."""
        print(f"[{self.id}] 🚀 Launching antigravity...")
        # Use shell=True to handle complex command strings
        self.process = await asyncio.create_subprocess_shell(
            self.command, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        # Start reading loops
        asyncio.create_task(self.monitor_output(self.process.stdout, "stdout"))
        asyncio.create_task(self.monitor_output(self.process.stderr, "stderr"))

    async def monitor_output(self, stream, stream_name):
        """Reads output line by line and triggers state changes."""
        while True:
            line = await stream.readline()
            if not line:
                break

            text = line.decode("utf-8", errors="replace").strip()
            if not text:
                continue

            # Print to main console with tag so you can see what's happening
            # (VS Code handles ANSI colors well)
            print(f"\033[94m[{self.id}]\033[0m {text}")

            self.last_activity = datetime.now()
            await self.analyze_state(text)

    async def analyze_state(self, text):
        """The Logic: Regex matching to detect state and auto-feed."""
        text_lower = text.lower()

        new_state = None
        if re.search(r"error|exception|failed|fatal|crash", text_lower):
            new_state = "ERROR"
        elif re.search(r"waiting|idle|ready|listening|command", text_lower):
            new_state = "IDLE"
        elif re.search(r"reviewing|checking|audit|analyzing", text_lower):
            new_state = "REVIEW"
        elif re.search(r"writing|implementing|coding|modifying|generating", text_lower):
            new_state = "WORKING"

        # If state changed or we hit a specific trigger, act
        if new_state and new_state != self.state:
            self.state = new_state
            # Optional: Auto-response logic could go here
            # For now, we just update state for the global broadcaster

            # AUTO-FEED LOOP (The "Selbst" part)
            # If agent says "Waiting for command", immediately feed it work
            if new_state == "IDLE":
                await self.send_instruction("IDLE")

    async def send_instruction(self, strategy_key):
        """Writes to the agent's Standard Input (stdin)."""
        if strategy_key not in STRATEGIES:
            return

        msg = STRATEGIES[strategy_key]
        print(f"\033[92m[{self.id}] ⚡ INJECTING: {strategy_key}\033[0m")

        # Write the message + newline (Enter key)
        if self.process and self.process.stdin:
            self.process.stdin.write(msg.encode() + b"\n")
            await self.process.stdin.drain()


async def main():
    agents = [AgentProcess(f"Agent-{i + 1}", AGENT_COMMAND) for i in range(NUM_AGENTS)]

    # Start all agents
    await asyncio.gather(*(agent.start() for agent in agents))

    print("--- 🌌 ANTIGRAVITY ENGINE ONLINE ---")
    print("Commands: 'audit', 'stop', 'review', 'idle', 'status'")

    # Main Input Loop (The Controller)
    # Allows you to type commands into the VS Code terminal to control the swarm
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    while True:
        # Read from USER input (VS Code terminal)
        line = await reader.readline()
        if not line:
            break
        command = line.decode().strip().lower()

        if command == "stop":
            print("🛑 Stopping all agents...")
            for a in agents:
                try:
                    if a.process:
                        a.process.terminate()
                except:
                    pass
            break

        elif command == "status":
            for a in agents:
                print(f"[{a.id}] State: {a.state} | Last Active: {a.last_activity.strftime('%H:%M:%S')}")

        elif command.upper() in STRATEGIES:
            # BROADCAST TO ALL
            print(f"📢 BROADCASTING [{command.upper()}] to fleet...")
            for a in agents:
                await a.send_instruction(command.upper())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
