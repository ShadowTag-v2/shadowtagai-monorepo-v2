import time

from agents.autoresearch import AgentState


class ComputerUseSpawner:
    """Manages Docker containers for Flying n-autoresearch/Kosmos/BioAgents agents.
    Enables VNC and Browser access for each agent.
    """

    def __init__(self, base_image: str = "anthropics/anthropic-quickstarts:computer-use-demo"):
        self.base_image = base_image

    def spawn_agent_container(self, agent: AgentState) -> str:
        """Spawns a Docker container for a single agent.
        Returns the container ID.
        """
        container_name = f"flying_monkey_{agent.name}"
        vnc_port = agent.vnc_port
        http_port = 8000 + (vnc_port - 5900)  # Map HTTP port based on agent index

        cmd = [
            "docker",
            "run",
            "-d",
            "--name",
            container_name,
            "-p",
            f"{vnc_port}:5900",
            "-p",
            f"{http_port}:8501",
            "-e",
            f"WIDTH={agent.display_num * 1024}",
            "-e",
            "HEIGHT=768",
            self.base_image,
        ]

        print(f"Spawning container for {agent.name} on port {vnc_port}...")
        # In a real run, we would execute this:
        # result = subprocess.run(cmd, capture_output=True, text=True)
        # if result.returncode == 0:
        #     agent.container_id = result.stdout.strip()
        #     return agent.container_id

        # Mock for now to avoid exploding the user's machine with 600 containers
        mock_id = f"cnt_{agent.name}_{int(time.time())}"
        agent.container_id = mock_id
        return mock_id

    def spawn_shift(self, agents: list[AgentState]):
        """Spawns containers for a shift of agents"""
        print(f"Initializing resources for {len(agents)} agents...")
        for agent in agents:
            if agent.computer_use:
                self.spawn_agent_container(agent)
        print("Shift initialization complete.")

    def cleanup_containers(self, agents: list[AgentState]):
        """Stops and removes containers"""
        print("Cleaning up agent containers...")
        for agent in agents:
            if agent.container_id:
                # subprocess.run(["docker", "rm", "-f", agent.container_id])
                agent.container_id = ""
        print("Cleanup complete.")
