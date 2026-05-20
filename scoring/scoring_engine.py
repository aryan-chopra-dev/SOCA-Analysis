import hashlib
from typing import Any


class ScoringEngine:
    """Converts raw questionnaire data into a normalized, explainable profile."""

    MOCK_FREQUENCY_SCORE = {
        "Rarely": 20,
        "Monthly": 40,
        "Fortnightly": 60,
        "Weekly": 80,
        "Twice a week": 90,
    }

    def build_profile(self, response: dict[str, Any]) -> dict[str, Any]:
        academic = response["academic"]
        behavior = response["behavior"]

        revision = round((behavior["revision_days_per_week"] / 7) * 100)
        time_management = behavior["time_management_rating"] * 20
        confidence = behavior["confidence_rating"] * 20
        problem_solving = behavior["problem_solving_rating"] * 20
        mock_score = self.MOCK_FREQUENCY_SCORE.get(behavior["mock_test_frequency"], 40)
        discipline = round((revision * 0.35) + (time_management * 0.3) + (mock_score * 0.2) + (min(behavior["weekly_hours"], 70) / 70 * 100 * 0.15))

        stress_numeric = round((behavior["mock_anxiety_rating"] * 18) + ((6 - behavior["sleep_quality_rating"]) * 10))
        stress_level = "high" if stress_numeric >= 75 else "moderate" if stress_numeric >= 45 else "low"

        patterns: list[str] = []
        if revision < 55:
            patterns.append("inconsistent_revision")
        if behavior["mock_anxiety_rating"] >= 4:
            patterns.append("high_mock_anxiety")
        if time_management < 60:
            patterns.append("time_leakage")
        if "Error log" not in behavior["study_techniques"]:
            patterns.append("missing_error_log")

        # Derived composite scores for Metrics & Analytics page
        avg_subject = round((academic["physics_proficiency"] + academic["chemistry_proficiency"] + academic["math_proficiency"]) / 3)
        readiness_score = min(100, round(avg_subject * 0.45 + discipline * 0.3 + (100 - min(stress_numeric, 100)) * 0.15 + revision * 0.1))

        readiness_labels = [
            (90, "Peak Performer"),
            (80, "Highly Capable"),
            (70, "On Track"),
            (60, "Needs Focus"),
            (0,  "Needs Significant Work"),
        ]
        readiness_interpretation = next(label for threshold, label in readiness_labels if readiness_score >= threshold)

        confidence_alignment = round((confidence / 100) * 50 + (avg_subject / 100) * 50)
        confidence_gap = abs(confidence - avg_subject)
        if confidence_gap <= 15:
            confidence_status = "ALIGNED"
            confidence_interpretation = "Confidence and accuracy levels are calibrated perfectly."
        elif confidence > avg_subject:
            confidence_status = "OVERCONFIDENT"
            confidence_interpretation = f"Confidence ({confidence}%) exceeds subject scores ({avg_subject}%). Risk of exam-day shock."
        else:
            confidence_status = "UNDERCONFIDENT"
            confidence_interpretation = f"Subject scores ({avg_subject}%) exceed stated confidence ({confidence}%). Build momentum with easier wins."

        wellness_raw = round((7 - behavior["mock_anxiety_rating"]) * 10 + behavior["sleep_quality_rating"] * 8)
        wellness_score = min(100, max(0, wellness_raw))
        burnout_risk = "HIGH" if behavior["mock_anxiety_rating"] >= 4 and behavior["sleep_quality_rating"] <= 2 else \
                       "MODERATE" if behavior["mock_anxiety_rating"] >= 3 or behavior["sleep_quality_rating"] <= 3 else "NORMAL"

        profile_id = hashlib.sha1(str(response).encode("utf-8")).hexdigest()[:12]
        return {
            "profile_id": profile_id,
            "student_name": response["student"]["name"],
            "current_level": response["student"].get("current_level", "Class 12th"),
            "target_attempt": response["student"]["target_attempt"],
            "physics_score": academic["physics_proficiency"],
            "chemistry_score": academic["chemistry_proficiency"],
            "math_score": academic["math_proficiency"],
            "stress_score": min(stress_numeric, 100),
            "stress_level": stress_level,
            "discipline_score": min(discipline, 100),
            "time_management_score": time_management,
            "time_management": "strong" if time_management >= 75 else "moderate" if time_management >= 50 else "weak",
            "confidence_score": confidence,
            "revision_consistency_score": revision,
            "problem_solving_score": problem_solving,
            "readiness_score": readiness_score,
            "readiness_interpretation": readiness_interpretation,
            "confidence_alignment": confidence_alignment,
            "confidence_status": confidence_status,
            "confidence_interpretation": confidence_interpretation,
            "wellness_score": wellness_score,
            "burnout_risk": burnout_risk,
            "weak_topics": academic["weak_topics"],
            "behavioral_patterns": patterns,
            "study_techniques": behavior["study_techniques"],
            "resources": behavior["resources"],
            "short_answer_blocker": behavior["short_answer_blocker"],
        }
