import sys

from config.prompts import EXECUTIVE_PROMPT
from pnkln_core.services.vertex_ai import run_task
from pnkln_core.utils.router import route_task


def main():
    """Main entrypoint for the pnkln system.
    Takes a task description from the command line, routes it, and passes it to the executive agent.
    """
    if len(sys.argv) < 2:
        print("Usage: python main.py <task_description>")
        raise SystemExit(1)

    task_description = sys.argv[1]

    # Route the task to determine the primary agent/domain
    target_domain = route_task(task_description)
    print(f"Task routed to domain: {target_domain}")

    # Format the prompt for the executive agent
    final_prompt = EXECUTIVE_PROMPT["user"].format(task=task_description)

    print("\n--- Sending task to executive agent ---")
    # Execute the task
    try:
        response = run_task(final_prompt)
        print("\n--- Agent Response ---")
        print(response)
    except Exception as e:
        print(f"\nError executing task: {e}")
        print("(Ensure you have authenticated with GCP and have the correct permissions)")

    print("\n----------------------")


if __name__ == "__main__":
    main()
