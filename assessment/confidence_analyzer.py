CONFIDENCE_TO_SCORE = {"Low": 35, "Medium": 65, "High": 90}


class ConfidenceAnalyzer:
    """Compares self-reported confidence with diagnostic accuracy."""

    def analyze(self, confidence_label: str, accuracy: int) -> dict:
        confidence_score = CONFIDENCE_TO_SCORE.get(confidence_label, 50)
        gap = confidence_score - accuracy
        if gap >= 25:
            flag = "overconfidence"
            recommendation = "Recalibrate confidence through timed quizzes and error-log review."
        elif gap <= -25:
            flag = "confidence_building_needed"
            recommendation = "Accuracy is better than confidence; use small wins and mixed practice to build belief."
        else:
            flag = "aligned"
            recommendation = "Confidence and accuracy are broadly aligned."
        alignment = max(0, 100 - abs(gap))
        return {
            "confidence_label": confidence_label,
            "confidence_score": confidence_score,
            "accuracy": accuracy,
            "confidence_accuracy_gap": gap,
            "confidence_alignment": alignment,
            "flag": flag,
            "recommendation": recommendation,
        }
