class RecommendationAgent:
    """Combines profile, agent, graph, and RAG evidence into prioritized strategies."""

    def analyze(self, profile: dict, academic: dict, behavioral: dict, wellness: dict, kg: dict, retrieved: list[dict]) -> dict:
        recommendations = [
            f"Prioritize {academic['weakest_subject']} for the next 14 days with alternate-day practice blocks.",
            "Convert every mock error into one concept tag and one corrective drill.",
        ]
        if kg["foundational_topics"]:
            recommendations.append(f"Repair prerequisites first: {', '.join(kg['foundational_topics'][:4])}.")
        if wellness["stress_level"] == "high":
            recommendations.append("Use shorter timed sections before full mocks to rebuild test confidence.")
        return {
            "agent": "recommendation_agent",
            "priority_recommendations": recommendations,
            "evidence_chunks_used": [item["id"] for item in retrieved],
            "personalization_basis": {
                "weak_topics": profile["weak_topics"],
                "behavioral_patterns": profile["behavioral_patterns"],
                "kg_foundations": kg["foundational_topics"],
            },
        }
