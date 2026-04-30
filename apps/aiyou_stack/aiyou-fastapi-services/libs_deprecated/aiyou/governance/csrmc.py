def execute_logic(state, crit):
    return "FIGHT_THROUGH" if state == "RED" and crit == "COMBAT" else "DISCONNECT"
