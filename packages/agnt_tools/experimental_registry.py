import asyncio
import psutil
import subprocess

class ExperimentalToolRegistry:
    """Implements the 11 feature-gated tools revealed in Claude Code."""

    @staticmethod
    async def execute_sleep(duration_ms: int):
        print(f"💤 [SleepTool] Agent yielding thread for {duration_ms}ms...")
        await asyncio.sleep(duration_ms / 1000.0)
        return {"status": "awake"}

    @staticmethod
    def execute_terminal_capture(pane_id: str):
        print(f"🖥️ [TerminalCapture] Capturing active buffer from {pane_id}...")
        res = subprocess.run(["tmux", "capture-pane", "-p", "-t", pane_id], capture_output=True, text=True)
        return res.stdout

    @staticmethod
    def execute_list_peers():
        peers = []
        for p in psutil.process_iter(['pid', 'name', 'cmdline']):
            if p.info.get('cmdline') and 'antigravity' in ' '.join(p.info['cmdline']):
                peers.append({"pid": p.info['pid'], "role": "sibling_agent"})
        return {"active_peers": peers, "tengu_board_status": "Online"}

    @staticmethod
    def execute_ctx_inspect(history: list):
        current_tokens = len(str(history)) / 4
        return {
            "used_tokens": current_tokens,
            "budget_remaining": 1000000 - current_tokens,
            "recommendation": "SAFE" if current_tokens < 800000 else "TRIGGER_COMPACT"
        }
