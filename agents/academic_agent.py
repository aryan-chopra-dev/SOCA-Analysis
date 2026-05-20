class AcademicAgent:
    """Analyzes PCM performance and weak-topic clusters."""

    def analyze(self, profile: dict) -> dict:
        scores = {
            "physics": profile["physics_score"],
            "chemistry": profile["chemistry_score"],
            "mathematics": profile["math_score"],
        }
        weakest_subject = min(scores, key=scores.get)
        strongest_subject = max(scores, key=scores.get)
        urgent_topics = profile["weak_topics"][:5]
        return {
            "agent": "academic_agent",
            "strongest_subject": strongest_subject,
            "weakest_subject": weakest_subject,
            "urgent_topics": urgent_topics,
            "risk_level": "high" if scores[weakest_subject] < 55 else "moderate" if scores[weakest_subject] < 70 else "low",
            "explanation": f"{weakest_subject.title()} needs the highest support based on the normalized score profile.",
        }
