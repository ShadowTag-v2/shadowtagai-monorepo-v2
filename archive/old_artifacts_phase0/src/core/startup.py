import asyncio
import subprocess


async def parallel_bootstrap():
    """Fires macOS keychain reads in parallel before heavy ML imports."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "security", "find-generic-password", "-s", "ag_keys", stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        await asyncio.sleep(0.135)  # Hide heavy imports behind the read
        stdout, _ = await proc.communicate()
        return stdout
    except FileNotFoundError:
        return b""
