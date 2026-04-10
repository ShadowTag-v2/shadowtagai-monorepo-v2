from dataclasses import dataclass



@dataclass
class EleganceMetrics:
    """
    Steve Jobs Elegance Metrics for DTE.

    Philosophy: Perfection is not when there's nothing left to add,
    but when there's nothing left to remove.
    """

    simplicity_score: float = 0.0
    clarity_score: float = 0.0
    conciseness_score: float = 0.0
    verb_density: float = 0.0
    format_consistency: float = 0.0

    @property
    def total_elegance(self) -> float:
        """Weighted elegance score (0-1)"""
        weights = {
            "simplicity": 0.3,
            "clarity": 0.25,
            "conciseness": 0.2,
            "verb_density": 0.15,
            "format": 0.1,
        }
        return (
            self.simplicity_score * weights["simplicity"]
            + self.clarity_score * weights["clarity"]
            + self.conciseness_score * weights["conciseness"]
            + self.verb_density * weights["verb_density"]
            + self.format_consistency * weights["format"]
        )
