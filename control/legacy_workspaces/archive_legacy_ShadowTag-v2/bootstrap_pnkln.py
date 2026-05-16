# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
from pathlib import Path

ROOT = "pnkln"

structure = {
    "pnkln": {
        "README.md": "# pnkln agent platform\n",
        "requirements.txt": """fastapi\nuvicorn\nollama\nchromadb\nnetworkx\npydantic\nrequests\npython-dotenv\n""",
        "config.yaml": """runtime: local\nmodel:\n  local: llama3\n  vertex: gemini-2.5-flash-lite\n""",
        "main.py": """\nfrom core.runtime import AgentRuntime\n\nruntime = AgentRuntime()\nruntime.start()\n""",
        "core": {
            "orchestrator.py": """\nclass Orchestrator:\n\n    def __init__(self, agents):\n        self.agents = agents\n\n    def run(self, task):\n\n        result = task\n\n        for agent in self.agents:\n            result = agent.run(result)\n\n        return result\n""",
            "runtime.py": """\nfrom agents.research_agent import ResearchAgent\nfrom agents.coding_agent import CodingAgent\nfrom agents.experiment_agent import ExperimentAgent\nfrom core.orchestrator import Orchestrator\nfrom models.model_router import ModelRouter\n\nclass AgentRuntime:\n\n    def __init__(self):\n\n        model = ModelRouter()\n\n        agents = [\n            ResearchAgent(model),\n            CodingAgent(model),\n            ExperimentAgent(model)\n        ]\n\n        self.orchestrator = Orchestrator(agents)\n\n    def start(self):\n\n        task = input("Enter task: ")\n\n        result = self.orchestrator.run(task)\n\n        print(result)\n""",
        },
        "agents": {
            "base_agent.py": """\nclass BaseAgent:\n\n    def __init__(self, model):\n        self.model = model\n""",
            "research_agent.py": """\nfrom agents.base_agent import BaseAgent\n\nclass ResearchAgent(BaseAgent):\n\n    def run(self, task):\n\n        prompt = f"Research the topic: {task}"\n\n        return self.model.generate(prompt)\n""",
            "coding_agent.py": """\nfrom agents.base_agent import BaseAgent\n\nclass CodingAgent(BaseAgent):\n\n    def run(self, task):\n\n        prompt = f"Write code for: {task}"\n\n        return self.model.generate(prompt)\n""",
            "experiment_agent.py": """\nfrom agents.base_agent import BaseAgent\n\nclass ExperimentAgent(BaseAgent):\n\n    def run(self, task):\n\n        return f"Experiment executed on: {task}"\n""",
        },
        "models": {
            "model_router.py": """\nimport yaml\nfrom models.local_llama import LocalLLM\n\nclass ModelRouter:\n\n    def __init__(self):\n\n        config = yaml.safe_load(open("config.yaml"))\n\n        if config["runtime"] == "local":\n            self.model = LocalLLM()\n        else:\n            from models.vertex_llm import VertexLLM\n            self.model = VertexLLM()\n\n    def generate(self, prompt):\n\n        return self.model.generate(prompt)\n""",
            "local_llama.py": """\nimport ollama\n\nclass LocalLLM:\n\n    def generate(self, prompt):\n\n        response = ollama.chat(\n            model="llama3",\n            messages=[{"role":"user","content":prompt}]\n        )\n\n        return response["message"]["content"]\n""",
            "vertex_llm.py": """\nfrom vertexai.generative_models import GenerativeModel\n\nclass VertexLLM:\n\n    def __init__(self):\n        self.model = GenerativeModel("gemini-2.5-flash-lite")\n\n    def generate(self, prompt):\n\n        return self.model.generate_content(prompt).text\n""",
        },
        "memory": {
            "vector_store.py": """\nimport chromadb\n\nclass VectorStore:\n\n    def __init__(self):\n\n        self.client = chromadb.Client()\n\n        self.collection = self.client.create_collection("pnkln")\n\n    def add(self, text):\n\n        self.collection.add(documents=[text])\n\n    def search(self, query):\n\n        return self.collection.query(query_texts=[query])\n""",
            "artifact_store.py": """\nimport json\n\ndef save_artifact(name, data):\n\n    with open(f"artifacts/{name}.json","w") as f:\n\n        json.dump(data,f)\n""",
        },
        "tools": {"terminal_tool.py": """\nimport subprocess\n\ndef run_command(cmd):\n\n    return subprocess.run(cmd, shell=True)\n"""},
        "local": {"run_local.sh": """\nollama serve\npython main.py\n"""},
        "cloud": {"Dockerfile": """\nFROM python:3.11\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD ["python","main.py"]\n"""},
        "artifacts": {},
    }
}


def create(path, tree):
    for name, content in tree.items():
        p = Path(path) / name
        if isinstance(content, dict):
            os.makedirs(p, exist_ok=True)
            create(p, content)
        else:
            with open(p, "w") as f:
                f.write(content)


if __name__ == "__main__":
    create(".", structure)
    print("pnkln project generated.")
