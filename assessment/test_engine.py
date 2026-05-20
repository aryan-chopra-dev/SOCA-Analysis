from datetime import datetime


DIFFICULTY_WEIGHT = {"easy": 1.0, "medium": 1.5, "hard": 2.0}


class TestEngine:
    """Grades diagnostic attempts and exposes explainable per-topic metrics."""

    def evaluate(self, question_set: dict, answers: list[str], time_taken_seconds: list[int]) -> dict:
        questions = question_set["questions"]
        rows = []
        correct_count = 0
        solved_weight = 0.0
        total_weight = 0.0
        hard_correct = 0
        hard_total = 0
        for idx, question in enumerate(questions):
            selected = answers[idx] if idx < len(answers) else ""
            correct = selected == question["correct_answer"]
            weight = DIFFICULTY_WEIGHT.get(question["difficulty"], 1.0)
            total_weight += weight
            if correct:
                correct_count += 1
                solved_weight += weight
            if question["difficulty"] == "hard":
                hard_total += 1
                hard_correct += int(correct)
            rows.append({
                "question": question["question"],
                "difficulty": question["difficulty"],
                "selected_answer": selected,
                "correct_answer": question["correct_answer"],
                "is_correct": correct,
                "time_taken_seconds": time_taken_seconds[idx] if idx < len(time_taken_seconds) else 0,
                "explanation": question["explanation"],
            })
        accuracy = round((correct_count / len(questions)) * 100) if questions else 0
        difficulty_handling = round((solved_weight / total_weight) * 100) if total_weight else 0
        avg_time = round(sum(time_taken_seconds) / len(time_taken_seconds)) if time_taken_seconds else 0
        conceptual_weakness = round(100 - accuracy)
        return {
            "topic": question_set["topic"],
            "subject": question_set.get("subject", ""),
            "evaluated_at": datetime.utcnow().isoformat() + "Z",
            "accuracy": accuracy,
            "difficulty_handling": difficulty_handling,
            "average_time_seconds": avg_time,
            "hard_question_accuracy": round((hard_correct / hard_total) * 100) if hard_total else 0,
            "conceptual_weakness_score": conceptual_weakness,
            "question_results": rows,
        }
