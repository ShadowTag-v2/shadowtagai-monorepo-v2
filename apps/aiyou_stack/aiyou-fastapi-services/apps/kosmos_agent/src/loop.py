import os

from google import genai
from google.genai import types
from rich.console import Console
from src.tracing import tracer

console = Console()


class KosmosAgent:
    def __init__(
        self,
        model_reasoning: str = "gemini-1.5-pro",
        model_tools: str = "gemini-1.5-flash",
    ):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = model_reasoning
        self.history = []

        self.system_prompt = """
        You are Kosmos, an autonomous AI scientist.
        You operate in a strict loop:
        1. THOUGHT: You reason about the current state and what needs to be done.
        2. ACTION: You utilize a tool/action to gather information or affect the world.
        3. OBSERVATION: You receive the output of your action.

        Your goal is to solve the user's research request thoroughly.
        Never jump to conclusions without evidence.
        """

    @tracer.start_as_current_span("agent_step")
    def step(self, input_text: str):
        """
        Executes a single step of the ReAct loop.
        """
        # Construct current context
        prompt = f"{self.system_prompt}\n\nHistory:\n"
        for msg in self.history:
            prompt += f"{msg['role']}: {msg['content']}\n"

        prompt += f"User: {input_text}\n"
        prompt += "Kosmos:"

        console.log("[bold blue]Thinking...[/bold blue]")

        # Generation Step
        with tracer.start_as_current_span("llm_call"):
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,  # Low temp for reasoning stability
                    max_output_tokens=1024,
                ),
            )

        output = response.text
        console.print(f"[green]Output:[/green] {output}")

        # Parse logic would go here (Simplified for scaffold)
        # In a full implementation, we would regex for "ACTION:"

        self.history.append({"role": "user", "content": input_text})
        self.history.append({"role": "model", "content": output})

        return output

    def run_loop(self, initial_goal: str):
        console.rule("[bold red]Kosmos Agent Started[/bold red]")
        console.log(f"Goal: {initial_goal}")

        current_input = initial_goal

        # Infinite loop simulation (controlled)
        for i in range(5):  # Limit to 5 steps for demo/scaffold
            with tracer.start_as_current_span(f"loop_iteration_{i}"):
                result = self.step(current_input)

                # Mock Observation for now
                if "ACTION" in result:
                    observation = "Mock Observation: Action executed successfully."
                    current_input = f"Observation: {observation}"
                    console.log(f"[yellow]{current_input}[/yellow]")
                else:
                    # If no action, maybe we are done or need more input
                    if "FINAL ANSWER" in result:
                        break
                    current_input = "Proceed with next thought."


if __name__ == "__main__":
    agent = KosmosAgent()
    agent.run_loop("Analyze the latest trends in Autonomous Agent architectures.")
