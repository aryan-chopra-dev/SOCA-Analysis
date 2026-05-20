from assessment.confidence_analyzer import ConfidenceAnalyzer
from assessment.question_generator import QuestionGenerator
from assessment.readiness_scorer import ReadinessScorer
from assessment.test_engine import TestEngine


class TopicAssessmentPipeline:
    """Orchestrates question generation, grading, readiness, workflow progress, and flags."""

    def __init__(self) -> None:
        self.generator = QuestionGenerator()
        self.test_engine = TestEngine()
        self.confidence = ConfidenceAnalyzer()
        self.readiness = ReadinessScorer()

    def generate_tests(self, topic_tracking: dict) -> dict:
        tests = {}
        for subject, payload in topic_tracking.items():
            for topic in payload.get("completed", []):
                tests[topic] = self.generator.generate(subject, topic)
        return tests

    def evaluate(self, topic_tracking: dict, generated_tests: dict, attempts: dict) -> dict:
        topic_reports = []
        for subject, payload in topic_tracking.items():
            for topic in payload.get("completed", []):
                if attempts and topic not in attempts:
                    continue
                question_set = generated_tests.get(topic) or self.generator.generate(subject, topic)
                topic_meta = payload.get("topic_details", {}).get(topic, {})
                attempt = attempts.get(topic, {})
                answer_values = attempt.get("answers", [])
                time_values = attempt.get("time_taken_seconds", [0]*5)
                test_result = self.test_engine.evaluate(question_set, answer_values, time_values)
                
                confidence = self.confidence.analyze(topic_meta.get("confidence", "Medium"), test_result["accuracy"])
                
                workflow_stages = topic_meta.get("workflow_stages", [])
                workflow_progress = round((len(workflow_stages) / 11) * 100) if workflow_stages else 0
                
                # Analyze workflow gaps
                gaps = []
                if "Video Lectures" not in workflow_stages:
                    gaps.append("Video Lectures")
                if "NCERT" not in workflow_stages:
                    gaps.append("NCERT")
                if "Reference book" not in workflow_stages:
                    gaps.append("Reference book")
                if not any(ex in workflow_stages for ex in ["Exercise 1 (JEE Mains Easy)", "Exercise 1A (JEE Mains Hard)"]):
                    gaps.append("Exercise 1/1A")
                if not any(ex in workflow_stages for ex in ["Exercise 2 (JEE Advanced Easy)", "Exercise 2A (JEE Advanced Hard)"]):
                    gaps.append("Exercise 2/2A")
                if "PYQs" not in workflow_stages:
                    gaps.append("PYQs")
                if "Topic Wise Test" not in workflow_stages:
                    gaps.append("Topic Wise Test")
                if not any(t in workflow_stages for t in ["Minor Tests", "Major Tests"]):
                    gaps.append("Minor/Major Tests")
                
                readiness = self.readiness.score(
                    test_result["accuracy"],
                    confidence["confidence_alignment"],
                    workflow_progress,
                    test_result["difficulty_handling"],
                )
                
                flags = self._flags(confidence, workflow_progress, test_result, gaps)
                
                topic_reports.append({
                    "subject": subject,
                    "topic": topic,
                    "completion_status": "completed",
                    "confidence": confidence["confidence_label"],
                    "workflow_stages": workflow_stages,
                    "workflow_progress": workflow_progress,
                    "workflow_gaps": gaps,
                    **test_result,
                    **confidence,
                    **readiness,
                    "flags": flags,
                    "weak_areas": self._weak_areas(topic, flags, gaps),
                    "recommendations": self._recommendations(topic, flags, gaps),
                })
        return {
            "topic_reports": topic_reports,
            "summary": self._summary(topic_reports, topic_tracking),
            "roadmap": self._roadmap(topic_reports, topic_tracking),
        }

    def _flags(self, confidence: dict, workflow_progress: int, test_result: dict, gaps: list[str]) -> list[str]:
        flags = []
        if confidence["flag"] != "aligned":
            flags.append(confidence["flag"])
        if workflow_progress < 50:
            flags.append("workflow_progress_low")
        if test_result["hard_question_accuracy"] < 50:
            flags.append("advanced_problem_solving_weakness")
        if test_result["conceptual_weakness_score"] >= 50:
            flags.append("conceptual_clarity_gap")
        if "NCERT" in gaps or "Video Lectures" in gaps:
            flags.append("foundation_theory_gap")
        if "PYQs" in gaps:
            flags.append("pyq_exposure_gap")
        if "Topic Wise Test" in gaps or "Minor/Major Tests" in gaps:
            flags.append("test_practice_gap")
        return flags

    def _weak_areas(self, topic: str, flags: list[str], gaps: list[str]) -> list[str]:
        areas = []
        if "foundation_theory_gap" in flags:
            areas.append(f"{topic} core theory (Video/NCERT)")
        if "advanced_problem_solving_weakness" in flags:
            areas.append(f"Advanced {topic} application (Exercise 2/2A)")
        if "conceptual_clarity_gap" in flags:
            areas.append(f"Basic concepts of {topic}")
        if "pyq_exposure_gap" in flags:
            areas.append(f"JEE PYQ alignment in {topic}")
        if "test_practice_gap" in flags:
            areas.append(f"{topic} mock testing exposure")
        return areas or [f"{topic} practice coverage"]

    def _recommendations(self, topic: str, flags: list[str], gaps: list[str]) -> list[str]:
        recs = []
        if "foundation_theory_gap" in flags:
            recs.append(f"Watch Video Lectures and read NCERT for {topic} before doing sheets.")
        if "advanced_problem_solving_weakness" in flags:
            recs.append(f"Complete Exercise 2 (Advanced Easy) and 2A (Advanced Hard) for {topic}.")
        if "overconfidence" in flags:
            recs.append(f"Take a timed Topic Wise Test in {topic} to calibrate your performance.")
        if "pyq_exposure_gap" in flags:
            recs.append(f"Solve all past 5 years PYQs for {topic}.")
        if "test_practice_gap" in flags:
            recs.append(f"Attempt Topic Wise Test, Minor, and Major Tests for {topic}.")
        
        # default recommendation
        if not recs:
            recs.append(f"Maintain regular revision and practice Exercise 1A & 2 for {topic}.")
        return recs

    def _summary(self, reports: list[dict], topic_tracking: dict) -> dict:
        if not reports:
            return {
                "average_readiness": 0,
                "weak_topics": [],
                "strong_topics": [],
                "revision_priority": [],
                "subject_mastery": {},
            }
        weak = [item["topic"] for item in reports if item["readiness_score"] < 60]
        strong = [item["topic"] for item in reports if item["readiness_score"] >= 80]
        
        # Prioritize topics with low readiness and major workflow gaps
        priority = sorted(reports, key=lambda item: (item["readiness_score"], len(item["workflow_gaps"])))
        subject_mastery = {}
        for item in reports:
            subject_mastery.setdefault(item["subject"], []).append(item["readiness_score"])
        subject_mastery = {subject: round(sum(scores) / len(scores)) for subject, scores in subject_mastery.items()}
        return {
            "average_readiness": round(sum(item["readiness_score"] for item in reports) / len(reports)),
            "weak_topics": weak,
            "strong_topics": strong,
            "revision_priority": [item["topic"] for item in priority[:5]],
            "subject_mastery": subject_mastery,
            "completion_counts": {
                subject: {
                    "completed": len(payload.get("completed", [])),
                    "partial": len(payload.get("partial", [])),
                    "untouched": len(payload.get("untouched", [])),
                }
                for subject, payload in topic_tracking.items()
            },
        }

    def _roadmap(self, reports: list[dict], topic_tracking: dict) -> list[dict]:
        roadmap = []
        for report in sorted(reports, key=lambda item: item["readiness_score"]):
            roadmap.append({
                "topic": report["topic"],
                "priority": "High" if report["readiness_score"] < 60 else "Medium",
                "next_action": report["recommendations"][0],
                "workflow_progress": f"{report['workflow_progress']}%",
            })
        for subject, payload in topic_tracking.items():
            for topic in payload.get("partial", [])[:2]:
                roadmap.append({"topic": topic, "priority": "Medium", "next_action": f"Complete core theory and examples for {topic}.", "workflow_progress": "0%"})
        return roadmap[:8]
