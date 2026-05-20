class BehavioralAgent:
    """Detects consistency, test-taking, and learning-process patterns."""

    def analyze(self, profile: dict) -> dict:
        patterns = profile["behavioral_patterns"]
        interventions = []
        if "inconsistent_revision" in patterns:
            interventions.append("Use a fixed 3-2-1 revision loop: 3 daily formulas, 2 solved examples, 1 error-log revisit.")
        if "missing_error_log" in patterns:
            interventions.append("Maintain an error log with mistake type, trigger concept, and next corrective action.")
        if "time_leakage" in patterns:
            interventions.append("Use 45-minute topic sprints followed by 10-minute review blocks.")
        return {
            "agent": "behavioral_agent",
            "patterns": patterns,
            "discipline_score": profile["discipline_score"],
            "recommended_habit_interventions": interventions,
            "consistency_risk": "high" if profile["discipline_score"] < 55 else "moderate" if profile["discipline_score"] < 75 else "low",
        }
