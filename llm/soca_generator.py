import json
import os
from pathlib import Path


class SOCAGenerator:
    """Prompt-engineered SOCA generator with an optional HuggingFace model backend."""

    def __init__(self, model_name: str = "microsoft/Phi-3-mini-4k-instruct") -> None:
        self.prompt_template = Path("prompts/soca_prompt.txt").read_text(encoding="utf-8")
        self.pipeline = None
        if os.getenv("USE_LOCAL_LLM", "").lower() not in {"1", "true", "yes"}:
            return
        try:
            from transformers import pipeline

            self.pipeline = pipeline("text-generation", model=model_name, max_new_tokens=700)
        except Exception:
            self.pipeline = None

    def generate(self, profile: dict, agent_outputs: dict, retrieved_chunks: list[dict], kg_insights: dict) -> dict:
        prompt = self.prompt_template.format(
            profile=json.dumps(profile, indent=2),
            agent_outputs=json.dumps(agent_outputs, indent=2),
            retrieved_chunks=json.dumps(retrieved_chunks, indent=2),
            kg_insights=json.dumps(kg_insights, indent=2),
        )
        if self.pipeline:
            try:
                generated = self.pipeline(prompt)[0]["generated_text"]
                parsed = self._extract_json(generated)
                if parsed:
                    return parsed
            except Exception:
                pass
        return self._fallback_soca(profile, agent_outputs, retrieved_chunks, kg_insights)

    def _extract_json(self, text: str) -> dict | None:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            return None
        try:
            payload = json.loads(text[start : end + 1])
            required = {"strengths", "opportunities", "challenges", "action_plan"}
            return payload if required.issubset(payload) else None
        except json.JSONDecodeError:
            return None

    def _fallback_soca(self, profile: dict, agent_outputs: dict, retrieved_chunks: list[dict], kg_insights: dict) -> dict:
        academic = agent_outputs.get("academic", {})
        behavioral = agent_outputs.get("behavioral", {})
        wellness = agent_outputs.get("wellness", {})
        
        strongest = academic.get("strongest_subject", "Physics").title()
        weakest = academic.get("weakest_subject", "Mathematics").title()
        foundations = ", ".join(kg_insights.get("foundational_topics", [])[:3])
        
        topic_summary = profile.get("topic_assessment_summary", {})
        strong_topics = topic_summary.get("strong_topics", [])
        weak_topics = topic_summary.get("weak_topics", [])
        
        topic_reports = agent_outputs.get("topic_assessment", {}).get("topic_reports", [])
        if not topic_reports and "topic_assessment" in profile:
            topic_reports = profile["topic_assessment"].get("topic_reports", [])
            
        workflow_strengths = []
        workflow_opportunities = []
        workflow_challenges = []
        
        theory_gap_topics = []
        mains_gap_topics = []
        advanced_gap_topics = []
        test_gap_topics = []
        
        for report in topic_reports:
            t_name = report.get("topic", "Unknown")
            stages = report.get("workflow_stages", [])
            gaps = report.get("workflow_gaps", [])
            r_score = report.get("readiness_score", 0)
            
            if r_score >= 75:
                stages_done = [s for s in ["Video Lectures", "NCERT", "PYQs"] if s in stages]
                workflow_strengths.append(
                    f"Strong conceptual base in {t_name} (Readiness {r_score}%) with {', '.join(stages_done or stages[:2])} completed."
                )
            else:
                # Classify gaps for dynamic action plan
                if "NCERT" in gaps or "Video Lectures" in gaps:
                    theory_gap_topics.append(t_name)
                    workflow_challenges.append(f"Conceptual foundation gap in {t_name}: Missing Video Lectures/NCERT.")
                if "PYQs" in gaps or "Exercise 1/1A" in gaps:
                    mains_gap_topics.append(t_name)
                    workflow_opportunities.append(f"Mains Practice Gap in {t_name}: Needs Exercise 1/1A or PYQ practice.")
                if "Exercise 2/2A" in gaps:
                    advanced_gap_topics.append(t_name)
                    workflow_opportunities.append(f"Advanced Practice Gap in {t_name}: Missing Exercise 2/2A sheets.")
                if "Topic Wise Test" in gaps or "Minor/Major Tests" in gaps:
                    test_gap_topics.append(t_name)
                    workflow_challenges.append(f"Testing Exposure Gap in {t_name}: Missing Topic/Minor/Major Tests.")

        # 1. STRENGTHS
        strengths = [
            f"{strongest} is your leading subject (Score: {profile.get(strongest.lower() + '_score', 70)}/100), providing a strong anchor for your confidence.",
            f"Problem-solving stamina rating is {profile.get('problem_solving_score', 60)}/100, indicating good potential for higher-difficulty segments."
        ]
        
        # Add study technique strengths
        techniques = profile.get("study_techniques", [])
        if "Error log" in techniques:
            strengths.append("Maintaining an active error log helps systematically eliminate recurring mistakes.")
        if "Active recall" in techniques or "Spaced revision" in techniques:
            strengths.append("Active recall or spaced revision practices are enhancing long-term memory retention.")
            
        # Add workflow strengths
        if workflow_strengths:
            strengths.extend(workflow_strengths[:2])
        elif strong_topics:
            strengths.append(f"Solid topic-level understanding demonstrated in: {', '.join(strong_topics[:3])}.")
        else:
            strengths.append("Steady execution on foundational homework and assignments.")
            
        # 2. OPPORTUNITIES
        opportunities = [
            f"Systematically raise your {weakest} score (currently {profile.get(weakest.lower() + '_score', 50)}/100) using structured, topic-level learning loops."
        ]
        if foundations:
            opportunities.append(f"Strengthen foundational prerequisites in: {foundations} to unlock advanced topics.")
            
        if workflow_opportunities:
            opportunities.extend(workflow_opportunities[:2])
            
        # Add resources opportunities
        resources = profile.get("resources", [])
        if "PYQs" not in resources:
            opportunities.append("Opportunity: Integrate past 5-10 years Chapter-wise PYQs as core practice material.")
        if "Test series" not in resources:
            opportunities.append("Opportunity: Enroll in a standard test series to adapt to computerized testing environments.")
            
        # 3. CHALLENGES
        stress_level = profile.get("stress_level", "Medium")
        challenges = [
            f"High anxiety or stress levels ({stress_level} stress) require targeted recovery intervals to prevent performance dips."
        ]
        
        # Behavioral challenges
        patterns = behavioral.get("patterns", [])
        if "inconsistent_revision" in patterns:
            challenges.append("Inconsistent revision schedule leads to decay of older topics before major tests.")
        if "high_mock_anxiety" in patterns:
            challenges.append("Mock test anxiety triggers cognitive blocks, causing silly errors on familiar concepts.")
        if "missing_error_log" in patterns:
            challenges.append("Absence of an error log results in repeating identical calculation and concept errors.")
            
        if workflow_challenges:
            challenges.extend(workflow_challenges[:2])
        elif weak_topics:
            challenges.append(f"Foundational cracks detected in weak topics: {', '.join(weak_topics[:3])}.")

        # 4. ACTION PLAN
        action_plan = []
        
        # Custom theory action
        if theory_gap_topics:
            action_plan.append(f"Theory Fix (Days 1-3): Focus on conceptual rebuilding. Watch video lectures and read NCERT for: {', '.join(theory_gap_topics[:2])}.")
        else:
            action_plan.append("Concepts: Maintain concept maps and formula notebooks for active recall of critical formulas.")
            
        # Custom Mains practice action
        if mains_gap_topics:
            action_plan.append(f"Mains Practice (Days 4-7): Complete Exercise 1 (Easy) and 1A (Hard) for: {', '.join(mains_gap_topics[:2])}, and finish their PYQs.")
        else:
            action_plan.append("Mains Practice: Ensure daily practice includes at least 15-20 mixed PYQs from all completed topics.")
            
        # Custom Advanced practice action
        if advanced_gap_topics:
            action_plan.append(f"Advanced Target (Week 2): Solve Exercise 2 (Advanced Easy) & 2A (Advanced Hard) questions for: {', '.join(advanced_gap_topics[:2])}.")
        else:
            action_plan.append("Advanced Target: Dedicate 2 hours every weekend to solving multi-concept questions from reference books.")
            
        # Custom testing action
        if test_gap_topics:
            action_plan.append(f"Test Practice (Weekly): Attempt a timed 45-minute Topic-Wise Test for: {', '.join(test_gap_topics[:2])} to build speed.")
        else:
            action_plan.append("Test Practice: Take a weekly mini-test to practice time-allocation and question-skipping strategies.")
            
        # Behavioral/Stress action
        if stress_level in ["High", "Very High"] or "high_mock_anxiety" in patterns:
            action_plan.append("Mental Strategy: Practice mindfulness before starting tests, maintain a strict 7-hour sleep cycle, and avoid overnight cramming.")
        elif "missing_error_log" in patterns:
            action_plan.append("Routine: Start a physical error notebook. For every mistake, write the question, the concept missed, and the correct step.")
        else:
            action_plan.append("Routine: Review your mistake logs every Sunday evening and re-attempt all bookmarked hard questions.")
            
        return {
            "strengths": strengths[:4],
            "opportunities": opportunities[:4],
            "challenges": challenges[:4],
            "action_plan": action_plan,
        }
