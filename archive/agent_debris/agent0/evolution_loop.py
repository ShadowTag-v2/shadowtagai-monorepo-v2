import time
import json
from .curriculum import CurriculumAgent
from .executor import ExecutorAgent
from .tools import atp_519_scan

class EvolutionLoop:
    """
    Orchestrates the co-evolution of Curriculum and Executor agents.
    """
    def __init__(self, iterations: int = 10):
        self.iterations = iterations
        self.curriculum = CurriculumAgent()
        self.executor = ExecutorAgent()
        self.results = []

    def run(self):
        print(f"Starting Agent0 Evolution Loop for {self.iterations} iterations...")

        difficulty = 0.1

        for i in range(self.iterations):
            print(f"\n--- Iteration {i+1}/{self.iterations} (Difficulty: {difficulty:.2f}) ---")

            # 1. Curriculum generates task
            task = self.curriculum.generate_task(i, difficulty)
            print(f"Scenario: {json.dumps(task.scenario)}")

            # 2. Executor generates rule
            rule_json = self.executor.generate_rule(task.scenario)
            print(f"Generated Rule: {rule_json}")

            # 3. Evaluate using Tool (ATP 5-19 Scan)
            scan_result = atp_519_scan(rule_json, json.dumps(task.scenario))
            print(f"Scan Result: {scan_result}")

            # 4. Feedback Loop
            # If detected (and expected violation), Executor wins -> Increase difficulty
            # If not detected (and expected violation), Curriculum wins -> Keep/Lower difficulty (or Executor learns)

            executor_success = scan_result["detected"] == task.expected_violation

            self.curriculum.feedback(task, executor_success)

            if executor_success:
                print(">> Executor SUCCESS (Caught the violation)")
                difficulty = min(1.0, difficulty + 0.1)
            else:
                print(">> Executor FAIL (Missed the violation)")
                difficulty = max(0.1, difficulty - 0.05)

            self.results.append({
                "iteration": i,
                "difficulty": difficulty,
                "executor_success": executor_success,
                "compression": scan_result["compression_ratio"]
            })

            time.sleep(0.1) # Simulate processing

        print("\nEvolution Loop Complete.")
        return self.results

if __name__ == "__main__":
    loop = EvolutionLoop(iterations=5)
    loop.run()
