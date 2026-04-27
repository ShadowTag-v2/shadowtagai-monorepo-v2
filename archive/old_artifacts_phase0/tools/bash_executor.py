import os
import subprocess
import unicodedata
import tempfile
import asyncio
from typing import Tuple, Optional
from core.agent_context import get_agent_context, set_current_cwd
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.tools.bash_security import BashSecurityValidator

class BashExecutor:
    """
    A macOS-hardened bash execution environment for AI agents.
    Implements EPIC 1: The macOS Sandbox requirements.
    """
    
    def __init__(self):
        pass

    async def execute(self, command: str) -> Tuple[int, str, str]:
        """
        Executes a bash command, persisting the working directory (CWD)
        across invocations to support stateful shell sessions per-agent.
        """
        validator = BashSecurityValidator()
        try:
            validator.validate(command)
        except ValueError as e:
            return -1, "", str(e)

        agent_ctx = get_agent_context()
        cwd = agent_ctx.cwd_override or os.getcwd()
        
        # We need a unique tmp file per agent to avoid race conditions
        # when multiple async agents are running bash commands.
        tmp_cwd_file = f"/tmp/ag-cwd-snapshot-{agent_ctx.agent_id}.txt"
        
        # Claude Code CWD persistence trick:
        # 1. CD into the agent's tracked directory
        # 2. Run the user's command
        # 3. Always run `pwd -P` and dump it to our tmp file so we can track directory changes (like `cd ..`)
        # We also enforce CI=true to bypass interactive prompts where possible.
        wrapped_command = f"""
cd "{cwd}" && export CI=true DEBIAN_FRONTEND=noninteractive && eval {self._shell_quote(command)}
pwd -P >| "{tmp_cwd_file}"
"""
        
        try:
            # We use asyncio.create_subprocess_shell to run without blocking the event loop
            process = await asyncio.create_subprocess_shell(
                wrapped_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True,
                executable='/bin/bash'
            )
            
            stdout_bytes, stderr_bytes = await process.communicate()
            stdout = stdout_bytes.decode('utf-8', errors='replace')
            stderr = stderr_bytes.decode('utf-8', errors='replace')
            returncode = process.returncode
            
            # Post-execution: Read the new CWD
            if os.path.exists(tmp_cwd_file):
                with open(tmp_cwd_file, 'r') as f:
                    new_cwd_raw = f.read().strip()
                    
                # macOS APFS Unicode normalization (NFC)
                # Apple's filesystem returns decomposed NFD strings, which can cause
                # false "directory changed" triggers when compared to standard strings.
                new_cwd = unicodedata.normalize('NFC', new_cwd_raw)
                
                # Update the context variable for this specific agent
                set_current_cwd(new_cwd)
                
                # Cleanup the tmp file
                try:
                    os.remove(tmp_cwd_file)
                except Exception:
                    pass
                    
            return returncode, stdout, stderr

        except Exception as e:
            return -1, "", str(e)

    def _shell_quote(self, s: str) -> str:
        """
        Basic single quoting to safely wrap the user command inside our eval block.
        """
        # Replace ' with '"'"' to safely escape inside single quotes
        return "'" + s.replace("'", "'\"'\"'") + "'"

# Example usage function for demonstration
async def demo_execution():
    from core.agent_context import AgentContext, current_agent_context
    
    # Setup agent 1
    agent_token = current_agent_context.set(AgentContext(agent_id="agent-001"))
    executor = BashExecutor()
    
    await executor.execute("cd /tmp && mkdir -p test_ag && cd test_ag")
    print(f"Agent 1 CWD after cd: {get_agent_context().cwd_override}")
    
    current_agent_context.reset(agent_token)
