class ReadinessScorer:
    """Weighted readiness metric for topic-level mastery."""

    def score(self, accuracy: int, confidence_alignment: int, workflow_progress: int, difficulty_handling: int) -> dict:
        readiness = round(
            (0.40 * accuracy)
            + (0.20 * confidence_alignment)
            + (0.20 * workflow_progress)
            + (0.20 * difficulty_handling)
        )
        if readiness >= 90:
            label = "Strong mastery"
        elif readiness >= 75:
            label = "Exam-ready but needs workflow gaps filled"
        elif readiness >= 50:
            label = "Moderate understanding"
        else:
            label = "Weak conceptual clarity"
        return {
            "readiness_score": max(0, min(100, readiness)),
            "readiness_interpretation": label,
            "formula": "0.40*Accuracy + 0.20*ConfidenceAlignment + 0.20*WorkflowProgress + 0.20*DifficultyHandling",
        }
