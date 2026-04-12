class GAASAutopilot:
    def calculate_path(self, waypoints, wind):
        print(f"    [GAAS] Computing path for {len(waypoints)} waypoints with wind {wind}kts...")
        MAX_WIND = 30
        if wind > MAX_WIND:
            return "ABORT_WIND_LIMIT"
        if not waypoints:
            return "HOVER_MODE"
        return "PATH_OPTIMIZED"
