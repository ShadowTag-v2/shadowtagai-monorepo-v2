import os
import sqlite3
import threading

# DOCTRINE: Cor.113 (Whitepaper)
# LEVEL: 2+ (Tool-Invoking, Orchestrated)
# COMPONENT: Orchestration / Nervous System


# World Model: SQLite for state (whitepaper persistence)
def init_world_model(db_name="wp_gemini_kosmos.db"):
    # Ensure config directory exists if we move this, but for now root/src relative
    db_path = os.path.join(os.path.dirname(__file__), "..", "data", db_name)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT)")
    conn.commit()
    return conn


def update_world_model(conn, key, value):
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO state (key, value) VALUES (?, ?)", (key, value))
    conn.commit()


def get_world_model(conn, key):
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM state WHERE key=?", (key,))
    result = cursor.fetchone()
    return result[0] if result else None


# Mock Gemini LLM: Whitepaper levels sim (brain modes)
# TODO: Connect this to `atomic_core.py` real Vertex calls
def gemini_llm_router(prompt, level=2, mode="auto"):
    # time.sleep(0.1)  # Latency simulation
    effective_mode = "pro" if level > 2 or "plan" in prompt else mode if mode != "auto" else "flash"

    # Simulation Logic for "Bootstrap Beauty"
    if "Reason" in prompt:
        return f"Thought (level {level}, {effective_mode}): Plan steps for {prompt.split(': ')[1] if ': ' in prompt else prompt}."
    if "Act" in prompt:
        return f"Action: Orchestrate {prompt.split(': ')[1] if ': ' in prompt else prompt}."
    if "Synthesize" in prompt:
        return f"Report (Immersive): Visual system insight - {prompt.split(': ')[1] if ': ' in prompt else prompt}."
    return "Agent output"


# Tools: Whitepaper hands (extend w/ connectors)
def data_analysis_tool(input_text):
    return f"Analysis (System): Breakdown in {input_text}."


def literature_search_tool(input_text):
    return f"Literature (Tool): Insights on {input_text}."


tools = {"DataAnalysis": data_analysis_tool, "LiteratureSearch": literature_search_tool}


# ReAct Loop: Whitepaper orchestration (<20 lines)
def react_loop(conn, objective, max_steps=5, agent_level=2, gemini_mode="auto"):
    state = get_world_model(conn, "current_state") or objective
    for _step in range(max_steps):
        thought = gemini_llm_router(f"Reason: {state}", level=agent_level, mode=gemini_mode)
        action_str = gemini_llm_router(f"Act: {thought}", level=agent_level, mode=gemini_mode)

        if "Action:" in action_str:
            try:
                # Naive parsing from snippet
                parts = action_str.split(" ")
                if len(parts) > 2:
                    tool_name = parts[2].split(".")[0]
                    tool_input = state.split(" ")[-1]  # Simplified input logic

                    if tool_name in tools:
                        observation = tools[tool_name](tool_input)
                        state += f"\nObservation: {observation}"
                        update_world_model(conn, "current_state", state)
            except Exception as e:
                print(f"[Kosmos::Error] Loop glitch: {e}")

    return state


# Parallel Agent Runner: Multi-agent collaboration
def run_agent_thread(conn, agent_type, objective, cycle_id, agent_level, gemini_mode):
    # Each thread needs its own cursor usually, but SQLite objects can be shared if checked_same_thread=False
    # Better to act on shared state
    state = get_world_model(conn, "current_state") or objective
    new_state = react_loop(conn, state, agent_level=agent_level, gemini_mode=gemini_mode)
    result = (
        f"{agent_type} (cycle {cycle_id}, level {agent_level}, mode {gemini_mode}): {new_state}"
    )

    # Atomic Write?
    full_state = get_world_model(conn, "current_state") or ""
    update_world_model(conn, "current_state", full_state + "\n" + result)
    print(result)  # Ops log


# Main Kosmos Runner: Whitepaper system phases
def run_kosmos_system(objective, dataset, num_cycles=3):
    conn = init_world_model()
    update_world_model(conn, "current_state", f"Objective: {objective}\nDataset: {dataset}")
    reports = []

    print(f"⚡ KOSMOS SYSTEM ONLINE. Objective: {objective}")

    for cycle in range(1, num_cycles + 1):
        print(f"  > Cycle {cycle}/{num_cycles}...")
        threads = []
        # Multi-Agent Symphony: Proactive Planning (Pro) + Standard Search (Flash)
        for agent_type, mode, level in [
            ("DataAnalysis", "pro", 3),
            ("LiteratureSearch", "flash", 2),
        ]:
            t = threading.Thread(
                target=run_agent_thread,
                args=(conn, agent_type, objective, cycle, level, mode),
            )
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        state = get_world_model(conn, "current_state")
        report = gemini_llm_router(f"Synthesize: {state}", level=4, mode="pro")
        reports.append(report)

    final_report = "\n".join(reports)
    print("Final Report (System View):\n" + final_report)
    conn.close()
    return final_report


if __name__ == "__main__":
    # Bootstrap Test
    run_kosmos_system("Hypothermia insights", "Metabolomics data", num_cycles=1)
