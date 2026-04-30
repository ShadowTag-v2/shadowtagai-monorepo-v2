from .recursive_rlm import RecursiveAgent


class SummarizerAgent(RecursiveAgent):
    def summarize_diff(self, d):
        return self.solve(f"Summarize diff: {d[:2000]}")


summarizer = SummarizerAgent()
