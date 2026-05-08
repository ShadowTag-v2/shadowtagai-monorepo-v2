import uuid
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError

logger = logging.getLogger(__name__)


class AgentDelegatePoC:
    """
    A Proof of Concept tool that delegates a bounded sub-task to a sub-agent.
    Uses a ThreadPoolExecutor to handle concurrent delegations.
    """

    def __init__(self, main_agent_context, max_workers=5):
        self.main_agent_context = main_agent_context
        self.sub_agents = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def delegate_task(self, task_description: str, tools_allowed: list = None, timeout_seconds: int = 30) -> str:
        """
        Delegates a specific sub-task to a newly spawned agent executing in a background thread.
        """
        sub_agent_id = str(uuid.uuid4())
        logger.info(f"Spawning sub-agent {sub_agent_id} for task: {task_description[:50]}...")

        self.sub_agents[sub_agent_id] = {"status": "running", "task": task_description, "tools": tools_allowed or ["view_file", "grep_search"]}

        future = self.executor.submit(self._simulate_sub_agent_execution, sub_agent_id, task_description, tools_allowed)

        try:
            # Wait for the sub-agent to complete or timeout
            result = future.result(timeout=timeout_seconds)
            self.sub_agents[sub_agent_id]["status"] = "completed"
            self.sub_agents[sub_agent_id]["result"] = result
            status = "success"
        except TimeoutError:
            logger.warning(f"Sub-agent {sub_agent_id} timed out after {timeout_seconds}s.")
            self.sub_agents[sub_agent_id]["status"] = "timed_out"
            result = "Timeout exceeded."
            status = "timeout"
        except Exception as e:
            logger.error(f"Sub-agent {sub_agent_id} failed: {str(e)}")
            self.sub_agents[sub_agent_id]["status"] = "failed"
            result = f"Error: {str(e)}"
            status = "error"

        return json.dumps({"sub_agent_id": sub_agent_id, "status": status, "report": result})

    def _simulate_sub_agent_execution(self, agent_id: str, task: str, tools: list) -> str:
        """
        Simulates an actual LLM call and tool execution loop.
        """
        # Here we would initialize the LLM client (e.g., Vertex AI or Gemini API)
        # prompt = f"You are a sub-agent. Task: {task}. Tools: {tools}"
        # response = llm_client.generate_content(prompt)
        time.sleep(2)  # Simulate work duration

        # Mock LLM response
        return f"LLM execution complete for bounded task: '{task}'. Simulated tool usage: {tools}."


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    poc = AgentDelegatePoC(main_agent_context={})

    print("=== Bounded Sub-Agent Delegation PoC ===")
    while True:
        try:
            task = input("\nEnter task description to delegate (or 'exit' to quit): ").strip()
            if task.lower() in ("exit", "quit", "q"):
                print("Exiting.")
                break

            if not task:
                continue

            tools_input = input("Enter allowed tools (comma separated, default: view_file,grep_search): ").strip()
            if tools_input:
                tools_allowed = [t.strip() for t in tools_input.split(",")]
            else:
                tools_allowed = ["view_file", "grep_search"]

            timeout_input = input("Enter timeout in seconds (default: 30): ").strip()
            if timeout_input.isdigit():
                timeout_seconds = int(timeout_input)
            else:
                timeout_seconds = 30

            print(f"\nDelegating task: '{task}' with tools {tools_allowed} (Timeout: {timeout_seconds}s)")
            result = poc.delegate_task(task_description=task, tools_allowed=tools_allowed, timeout_seconds=timeout_seconds)
            print("Delegation Result:", result)
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except Exception as e:
            print(f"Error during interactive menu: {e}")
