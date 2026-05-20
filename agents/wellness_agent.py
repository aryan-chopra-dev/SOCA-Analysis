class WellnessAgent:
    """Screens stress and burnout signals without making clinical claims."""

    def analyze(self, profile: dict) -> dict:
        supports = []
        if profile["stress_level"] == "high":
            supports.extend([
                "Take mocks in graded exposure: section tests before full tests.",
                "Add a 10-minute decompression routine after analysis before restarting study.",
            ])
        if "high_mock_anxiety" in profile["behavioral_patterns"]:
            supports.append("Practice two no-score mocks to reduce fear of result labels.")
        return {
            "agent": "wellness_agent",
            "stress_level": profile["stress_level"],
            "stress_score": profile["stress_score"],
            "burnout_risk": "watch" if profile["stress_score"] >= 70 else "normal",
            "supportive_actions": supports,
            "disclaimer": "This is educational wellness guidance, not medical diagnosis.",
        }
