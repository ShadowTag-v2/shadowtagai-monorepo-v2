import os
import sys

sys.path.append(os.path.abspath("../../../libs"))
from ShadowTag-v2.agents.consensus import consensus
from ShadowTag-v2.proxies.router import router
from arsenal.scribe.engine import scribe
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Task(BaseModel):
    query: str


@app.post("/dispatch")
def dispatch(t: Task):
    # 1. ROUTER (Uses Echo)
    route = router.dispatch(t.query)
    # 2. EXECUTE (Uses Vote if Swarm)
    res = consensus.vote(t.query) if route == "SWARM" else "Local Exec"
    return {"route": route, "result": res}


@app.post("/scribe")
def parse_doc(f: str):
    return {"md": scribe.parse_visual(f)}
