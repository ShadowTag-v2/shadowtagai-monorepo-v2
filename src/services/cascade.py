import time

class CascadeDetector:
    def __init__(self):
        self.strike_count = 0
        self.cooldown_until = 0
        
    def record_response(self, status_code, is_background=False):
        if status_code in (429, 529):
            if is_background: raise Exception("Background task bailed due to 529 cascade.")
            self.strike_count += 1
            if self.strike_count >= 3:
                self.cooldown_until = time.time() + 1800
                print("🚨 529 CASCADE DETECTED: Standard speed mode enforced for 30 min.")
        else:
            self.strike_count = 0
