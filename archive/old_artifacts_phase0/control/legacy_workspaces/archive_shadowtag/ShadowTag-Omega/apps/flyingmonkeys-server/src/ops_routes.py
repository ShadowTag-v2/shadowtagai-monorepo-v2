
import subprocess

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class CommandRequest(BaseModel):
    command: str
    cwd: str = "."
    background: bool = False

@router.post("/exec")
async def execute_shell(req: CommandRequest):
    """
    God Mode Endpoint: Executes arbitrary shell commands.
    Strictly for usage by Antigravity Orchestrator via fmshell.
    """
    try:
        # Resolve CWD relative to project root if needed, but for now trust absolute or explicit
        working_dir = req.cwd

        if req.background:
            # Fire and forget (risky but needed for long migrations)
            subprocess.Popen(req.command, shell=True, cwd=working_dir)
            return {"status": "background_started", "command": req.command}
        else:
            # Synchronous execution
            result = subprocess.run(
                req.command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True
            )
            return {
                "status": "completed",
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
