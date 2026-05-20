import json
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from assessment.question_generator import QuestionGenerator
from assessment.topic_assessment import TopicAssessmentPipeline
from agents.academic_agent import AcademicAgent
from agents.behavioral_agent import BehavioralAgent
from agents.recommendation_agent import RecommendationAgent
from agents.wellness_agent import WellnessAgent
from kg.knowledge_graph import JEETopicKnowledgeGraph
from llm.soca_generator import SOCAGenerator
from rag.retrieve import RAGRetriever
from scoring.scoring_engine import ScoringEngine
from utils.report_export import build_pdf_report


DATA_DIR = Path("data")
FEEDBACK_FILE = DATA_DIR / "feedback.jsonl"
RESPONSES_FILE = DATA_DIR / "latest_response.json"
TOPICS_FILE = DATA_DIR / "jee_topics.json"
PAGES = [
    "Student Profile",
    "Academic Proficiency",
    "Study Behaviour",
    "Topic Diagnostic Test",
    "Assessment Report",
]
TIME_MANAGEMENT_OPTIONS = {
    "Often run out of time": 2,
    "Usually finish just on time": 3,
    "Finish with time to spare": 5,
}
PROBLEM_SOLVING_OPTIONS = {
    "Need hints for standard problems": 2,
    "Can solve standard problems independently": 3,
    "Can solve mixed multi-concept problems": 5,
}
REVISION_OPTIONS = {
    "Rarely revise weekly": 1,
    "Revise important topics weekly": 4,
    "Follow a fixed revision plan": 7,
}


st.set_page_config(page_title="SOCA Analysis", page_icon=":material/school:", layout="wide")


def init_state() -> None:
    st.session_state.setdefault("page_index", 0)
    st.session_state.setdefault("submitted", False)
    st.session_state.setdefault("report", None)
    st.session_state.setdefault("raw_response", None)
    st.session_state.setdefault("student_profile_data", {})
    st.session_state.setdefault("academic_data", {})
    st.session_state.setdefault("behavior_data", {})
    st.session_state.setdefault("diagnostic_data", {})


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def append_feedback(payload: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with FEEDBACK_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


@st.cache_data(show_spinner=False)
def load_topics() -> dict:
    return json.loads(TOPICS_FILE.read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def generate_topic_test(subject: str, topic: str) -> dict:
    return QuestionGenerator().generate(subject, topic)


@st.cache_resource(show_spinner=False)
def load_rag():
    return RAGRetriever()


def load_pipeline():
    return {
        "scoring": ScoringEngine(),
        "academic": AcademicAgent(),
        "behavioral": BehavioralAgent(),
        "wellness": WellnessAgent(),
        "kg": JEETopicKnowledgeGraph(),
        "rag": load_rag(),
        "soca": SOCAGenerator(),
        "topic_assessment": TopicAssessmentPipeline(),
    }


def render_progress() -> None:
    current = st.session_state.page_index
    cols = st.columns(len(PAGES))
    for idx, page in enumerate(PAGES):
        marker = "Current" if idx == current else "Done" if idx < current else "Next"
        cols[idx].button(f"{marker}: {page}", key=f"jump_{idx}", on_click=set_page, args=(idx,), use_container_width=True)
    st.progress((current + 1) / len(PAGES))

    # Inject JavaScript to color-code Done (Green), Current (Yellow), and Next (Slate Grey) buttons in the parent DOM
    import streamlit.components.v1 as components
    components.html(
        f"""
        <!-- Page Index: {current} -->
        <script>
        const styleNavButtons = () => {{
            const doc = window.parent.document;
            const buttons = doc.querySelectorAll('button');
            buttons.forEach(btn => {{
                const text = (btn.innerText || btn.textContent || "").trim();
                if (text.startsWith('Done:')) {{
                    btn.style.setProperty('background-color', '#2ecc71', 'important');
                    btn.style.setProperty('color', '#ffffff', 'important');
                    btn.style.setProperty('border', 'none', 'important');
                    btn.style.setProperty('font-weight', 'normal', 'important');
                }} else if (text.startsWith('Current:')) {{
                    btn.style.setProperty('background-color', '#f1c40f', 'important');
                    btn.style.setProperty('color', '#000000', 'important');
                    btn.style.setProperty('font-weight', 'bold', 'important');
                    btn.style.setProperty('border', 'none', 'important');
                }} else if (text.startsWith('Next:')) {{
                    btn.style.setProperty('background-color', '#1e293b', 'important');
                    btn.style.setProperty('color', '#94a3b8', 'important');
                    btn.style.setProperty('border', '1px solid #334155', 'important');
                    btn.style.setProperty('font-weight', 'normal', 'important');
                }}
            }});
        }};
        
        // Execute immediately and periodically to handle React re-renders
        styleNavButtons();
        setInterval(styleNavButtons, 100);
        </script>
        """,
        height=0,
        width=0
    )


def set_page(index: int) -> None:
    persist_current_page()
    st.session_state.page_index = max(0, min(index, len(PAGES) - 1))


def persist_current_page() -> None:
    page = PAGES[st.session_state.get("page_index", 0)]
    if page == "Student Profile":
        st.session_state.student_profile_data = {
            "student_name": st.session_state.get("student_name", ""),
            "current_level": st.session_state.get("current_level", ""),
            "target_attempt": st.session_state.get("target_attempt", ""),
        }
    elif page == "Academic Proficiency":
        st.session_state.academic_data = collect_academic_data_from_widgets()
    elif page == "Study Behaviour":
        st.session_state.behavior_data = {
            "time_management_category": st.session_state.get("time_management_category", "Usually finish just on time"),
            "revision_category": st.session_state.get("revision_category", "Revise important topics weekly"),
            "problem_solving_category": st.session_state.get("problem_solving_category", "Can solve standard problems independently"),
            "mock_test_frequency": st.session_state.get("mock_test_frequency", "Fortnightly"),
            "study_techniques": st.session_state.get("study_techniques", ["Formula notebook", "Video lectures"]),
            "resources": st.session_state.get("resources", ["Coaching modules", "PYQs", "YouTube"]),
            "short_answer_blocker": st.session_state.get("short_answer_blocker", ""),
        }
    elif page == "Topic Diagnostic Test":
        st.session_state.diagnostic_data = collect_diagnostic_data_from_widgets()


def navigation_controls() -> None:
    st.divider()
    back, middle, next_col = st.columns([1, 2, 1])
    with back:
        if st.session_state.page_index > 0 and st.button("Back", use_container_width=True):
            persist_current_page()
            st.session_state.page_index -= 1
            st.rerun()
    with middle:
        if st.session_state.page_index == 4:
            if st.button("Back to Subject and Topic Selection", use_container_width=True):
                persist_current_page()
                st.session_state.page_index = 3
                st.rerun()
    with next_col:
        if st.session_state.page_index < 4:
            is_valid = True
            if st.session_state.page_index == 0:
                name = st.session_state.get("student_name", "").strip()
                lvl = st.session_state.get("current_level")
                att = st.session_state.get("target_attempt")
                if not name or not lvl or not att:
                    is_valid = False
            
            if st.button("Next", type="primary", use_container_width=True, disabled=not is_valid):
                persist_current_page()
                st.session_state.page_index += 1
                if st.session_state.page_index == 4:
                    generate_report()
                st.rerun()


def render_student_profile_page() -> None:
    saved = st.session_state.get("student_profile_data", {})
    st.markdown("### Student Profile")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.text_input("Name*", value=saved.get("student_name", ""), placeholder="Enter student name", key="student_name")
    with c2:
        levels = ["Class 10th", "Class 11th", "Class 12th", "Dropper"]
        saved_level = saved.get("current_level")
        st.selectbox("Current level*", levels, index=levels.index(saved_level) if saved_level in levels else None, placeholder="Select current class/level", key="current_level")
    with c3:
        attempts = ["JEE Main 2027", "JEE Advanced 2027", "JEE Main 2028", "JEE Advanced 2028"]
        saved_attempt = saved.get("target_attempt")
        st.selectbox("Target attempt*", attempts, index=attempts.index(saved_attempt) if saved_attempt in attempts else None, placeholder="Select target exam", key="target_attempt")
    
    # Check if required fields are filled
    name = st.session_state.get("student_name", "").strip()
    lvl = st.session_state.get("current_level")
    att = st.session_state.get("target_attempt")
    if not name or not lvl or not att:
        st.warning("⚠️ Name, Current level, and Target attempt are required fields. Please fill them to proceed.")


def render_academic_page() -> None:
    topics_db = load_topics()
    saved = st.session_state.get("academic_data", {})
    st.markdown("### Academic Proficiency")
    
    STAGES = [
        "Video Lectures",
        "NCERT",
        "Reference book",
        "Exercise 1 (JEE Mains Easy)",
        "Exercise 1A (JEE Mains Hard)",
        "Exercise 2 (JEE Advanced Easy)",
        "Exercise 2A (JEE Advanced Hard)",
        "PYQs",
        "Topic Wise Test",
        "Minor Tests",
        "Major Tests"
    ]
    
    for subject, topics in topics_db.items():
        with st.expander(subject, expanded=subject == "Physics"):
            subject_saved = saved.get(subject, {})
            st.multiselect(f"{subject} weak topics", topics, default=subject_saved.get("weak_topics", topics[:1]), key=f"{subject}_weak")
            completed = st.multiselect(f"{subject}: completed units/topics", topics, default=subject_saved.get("completed", topics[:2]), key=f"{subject}_completed")

            for topic in completed:
                details = subject_saved.get("topic_details", {}).get(topic, {})
                st.write(f"**{topic} Completed Stages**")
                
                # Check for existing workflow list or default to a couple of items
                saved_stages = details.get("workflow_stages", ["Video Lectures", "NCERT"])
                st.multiselect(
                    f"Stages completed for {topic}",
                    STAGES,
                    default=saved_stages,
                    key=f"{topic}_workflow"
                )


def collect_academic_data_from_widgets() -> dict:
    academic = {}
    for subject, topics in load_topics().items():
        completed = st.session_state.get(f"{subject}_completed", [])
        untouched = [t for t in topics if t not in completed]
        details = {}
        for topic in completed:
            details[topic] = {
                "confidence": "Medium",
                "workflow_stages": st.session_state.get(f"{topic}_workflow", []),
            }
        academic[subject] = {
            "score": infer_subject_score(subject, completed),
            "weak_topics": st.session_state.get(f"{subject}_weak", []),
            "completed": completed,
            "partial": [],
            "untouched": untouched,
            "topic_details": details,
        }
    return academic


def infer_subject_score(subject: str, completed: list[str]) -> int:
    total = max(1, len(load_topics().get(subject, [])))
    return round((len(completed) / total) * 100)


def render_study_behaviour_page() -> None:
    saved = st.session_state.get("behavior_data", {})
    st.markdown("### Study Behaviour")
    b1, b2, b3 = st.columns(3)
    with b1:
        time_options = list(TIME_MANAGEMENT_OPTIONS)
        val = saved.get("time_management_category", "Usually finish just on time")
        idx = time_options.index(val) if val in time_options else 1
        st.selectbox("Time management", time_options, index=idx, key="time_management_category")
    with b2:
        problem_options = list(PROBLEM_SOLVING_OPTIONS)
        val = saved.get("problem_solving_category", "Can solve standard problems independently")
        idx = problem_options.index(val) if val in problem_options else 1
        st.selectbox("Problem solving", problem_options, index=idx, key="problem_solving_category")
    with b3:
        revision_options = list(REVISION_OPTIONS)
        val = saved.get("revision_category", "Revise important topics weekly")
        idx = revision_options.index(val) if val in revision_options else 1
        st.selectbox("Revision consistency", revision_options, index=idx, key="revision_category")

    c1, c2 = st.columns(2)
    with c1:
        st.multiselect(
            "Study techniques used",
            ["NCERT reading", "Formula notebook", "Error log", "Active recall", "Spaced revision", "Timed practice", "Video lectures"],
            default=saved.get("study_techniques", ["Formula notebook", "Video lectures"]),
            key="study_techniques",
        )
        st.multiselect(
            "Learning resources",
            ["Coaching modules", "NCERT", "PYQs", "YouTube", "Test series", "Doubt-solving app", "Reference books"],
            default=saved.get("resources", ["Coaching modules", "PYQs", "YouTube"]),
            key="resources",
        )
    with c2:
        st.text_area(
            "What is the biggest blocker in your preparation right now?",
            value=saved.get("short_answer_blocker", "I understand concepts but lose marks in mixed-topic tests because I panic and skip revision."),
            height=110,
            key="short_answer_blocker",
        )


def get_topic_tracking() -> dict:
    if st.session_state.get("academic_data"):
        return {
            subject: {
                "completed": payload.get("completed", []),
                "partial": [],
                "untouched": payload.get("untouched", []),
                "topic_details": payload.get("topic_details", {}),
            }
            for subject, payload in st.session_state.academic_data.items()
        }
    topic_tracking = {}
    for subject, topics in load_topics().items():
        completed = st.session_state.get(f"{subject}_completed", [])
        untouched = [t for t in topics if t not in completed]
        details = {}
        for topic in completed:
            details[topic] = {
                "confidence": "Medium",
                "workflow_stages": st.session_state.get(f"{topic}_workflow", []),
            }
        topic_tracking[subject] = {"completed": completed, "partial": [], "untouched": untouched, "topic_details": details}
    return topic_tracking


def collect_diagnostic_data_from_widgets() -> dict:
    topic_subjects = completed_topic_subject_map()
    selected_topics = [topic for topic in st.session_state.get("diagnostic_topics", []) if topic in topic_subjects]
    
    # Retrieve existing accumulated data or start fresh
    accumulated = st.session_state.get("diagnostic_data", {})
    accumulated_selected = set(accumulated.get("selected_topics", []))
    accumulated_tests = dict(accumulated.get("diagnostic_tests", {}))
    accumulated_attempts = dict(accumulated.get("diagnostic_attempts", {}))

    # Clean up any topics that are no longer completed
    accumulated_selected = {t for t in accumulated_selected if t in topic_subjects}
    for topic in list(accumulated_tests.keys()):
        if topic not in topic_subjects:
            accumulated_tests.pop(topic, None)
            accumulated_attempts.pop(topic, None)

    for topic in selected_topics:
        accumulated_selected.add(topic)
        subject = topic_subjects[topic]
        question_set = generate_topic_test(subject, topic)
        accumulated_tests[topic] = question_set
        
        # Capture current widget state answers
        answers = [st.session_state.get(f"{topic}_q_{idx}_value", "") for idx in range(1, 6)]
        
        # Only overwrite if the user has actually answered something in the UI,
        # or if we don't have answers saved yet.
        has_new_answers = any(ans != "" for ans in answers)
        if has_new_answers or topic not in accumulated_attempts:
            accumulated_attempts[topic] = {
                "answers": answers,
                "time_taken_seconds": [
                    question_set["questions"][idx - 1].get("estimated_time_seconds", 120)
                    for idx in range(1, 6)
                ],
            }
            
    return {
        "selected_topics": list(accumulated_selected),
        "diagnostic_tests": accumulated_tests,
        "diagnostic_attempts": accumulated_attempts
    }


def completed_topic_subject_map() -> dict:
    mapping = {}
    for subject, payload in get_topic_tracking().items():
        for topic in payload.get("completed", []):
            mapping[topic] = subject
    return mapping


def render_topic_diagnostic_page() -> None:
    st.markdown("### Subject and Topic Selection")
    topic_subjects = completed_topic_subject_map()
    subject_filter = st.radio("Subject filter", ["All", "Mathematics", "Physics", "Chemistry"], horizontal=True, key="diagnostic_subject_filter")
    available = [topic for topic, subject in topic_subjects.items() if subject_filter == "All" or subject == subject_filter]

    if not available:
        st.info("No completed topics are available for this filter. Go back to Academic Proficiency and mark a topic as completed.")
        return

    saved_diagnostic = st.session_state.get("diagnostic_data", {})
    selected_default = [topic for topic in saved_diagnostic.get("selected_topics", available[:1]) if topic in available]
    
    col1, col2 = st.columns([5, 1])
    with col1:
        selected = st.multiselect("Choose topic assessments", available, default=selected_default or available[:1], key="diagnostic_topics")
    with col2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("Reset attempts", use_container_width=True, help="Clear all stored test attempts and start fresh"):
            st.session_state.diagnostic_data = {}
            st.session_state.diagnostic_topics = []
            st.rerun()

    selected = [topic for topic in selected if topic in available]
    if not selected:
        st.warning("Select at least one topic to attempt.")
        return

    for topic in selected:
        subject = topic_subjects[topic]
        question_set = generate_topic_test(subject, topic)
        st.markdown(f"#### {subject}: {topic}")
        for idx, question in enumerate(question_set["questions"], start=1):
            labels = [f"{letter}. {option}" for letter, option in zip(["A", "B", "C", "D"], question["options"])]
            selected_answer = st.radio(
                f"Q{idx} [{question['difficulty'].title()}] {question['question']}",
                labels,
                index=None,
                key=f"{topic}_q_{idx}",
            )
            st.session_state[f"{topic}_q_{idx}_value"] = selected_answer.split(".", 1)[0] if selected_answer else ""


def build_response() -> dict:
    topic_subjects = completed_topic_subject_map()
    diagnostic_snapshot = st.session_state.get("diagnostic_data", {})
    selected_topics = [topic for topic in diagnostic_snapshot.get("selected_topics", st.session_state.get("diagnostic_topics", [])) if topic in topic_subjects]
    diagnostic_tests = dict(diagnostic_snapshot.get("diagnostic_tests", {}))
    diagnostic_attempts = dict(diagnostic_snapshot.get("diagnostic_attempts", {}))
    if not diagnostic_tests or not diagnostic_attempts:
        for topic in selected_topics:
            subject = topic_subjects[topic]
            question_set = generate_topic_test(subject, topic)
            diagnostic_tests[topic] = question_set
            diagnostic_attempts[topic] = {
                "answers": [st.session_state.get(f"{topic}_q_{idx}_value", "") for idx in range(1, 6)],
                "time_taken_seconds": [
                    question_set["questions"][idx - 1].get("estimated_time_seconds", 120)
                    for idx in range(1, 6)
                ],
            }
    student_snapshot = st.session_state.get("student_profile_data", {})
    academic_snapshot = st.session_state.get("academic_data", {})
    behavior_snapshot = st.session_state.get("behavior_data", {})

    return {
        "student": {
            "name": student_snapshot.get("student_name", st.session_state.get("student_name", "")) or "Student",
            "current_level": student_snapshot.get("current_level", st.session_state.get("current_level", "")) or "Class 12th",
            "target_attempt": student_snapshot.get("target_attempt", st.session_state.get("target_attempt", "")) or "JEE Main 2027",
        },
        "academic": {
            "physics_proficiency": academic_snapshot.get("Physics", {}).get("score", st.session_state.get("Physics_score", 64)),
            "chemistry_proficiency": academic_snapshot.get("Chemistry", {}).get("score", st.session_state.get("Chemistry_score", 58)),
            "math_proficiency": academic_snapshot.get("Mathematics", {}).get("score", st.session_state.get("Mathematics_score", 72)),
            "weak_topics": (
                academic_snapshot.get("Physics", {}).get("weak_topics", st.session_state.get("Physics_weak", []))
                + academic_snapshot.get("Chemistry", {}).get("weak_topics", st.session_state.get("Chemistry_weak", []))
                + academic_snapshot.get("Mathematics", {}).get("weak_topics", st.session_state.get("Mathematics_weak", []))
            ),
        },
        "behavior": {
            "weekly_hours": 35,
            "time_management_rating": TIME_MANAGEMENT_OPTIONS.get(behavior_snapshot.get("time_management_category", "Usually finish just on time"), 3),
            "revision_days_per_week": REVISION_OPTIONS.get(behavior_snapshot.get("revision_category", "Revise important topics weekly"), 4),
            "problem_solving_rating": PROBLEM_SOLVING_OPTIONS.get(behavior_snapshot.get("problem_solving_category", "Can solve standard problems independently"), 3),
            "mock_test_frequency": behavior_snapshot.get("mock_test_frequency", st.session_state.get("mock_test_frequency", "Fortnightly")),
            "mock_anxiety_rating": 2,
            "sleep_quality_rating": 3,
            "study_techniques": behavior_snapshot.get("study_techniques", st.session_state.get("study_techniques", ["Formula notebook", "Video lectures"])),
            "resources": behavior_snapshot.get("resources", st.session_state.get("resources", ["Coaching modules", "PYQs", "YouTube"])),
            "confidence_rating": 3,
            "short_answer_blocker": behavior_snapshot.get("short_answer_blocker", st.session_state.get("short_answer_blocker", "")),
        },
        "topic_tracking": get_topic_tracking(),
        "diagnostic_tests": diagnostic_tests,
        "diagnostic_attempts": diagnostic_attempts,
        "metadata": {"created_at": datetime.utcnow().isoformat() + "Z"},
    }


def run_pipeline(response: dict) -> dict:
    pipeline = load_pipeline()
    profile = pipeline["scoring"].build_profile(response)
    topic_assessment = pipeline["topic_assessment"].evaluate(
        response.get("topic_tracking", {}),
        response.get("diagnostic_tests", {}),
        response.get("diagnostic_attempts", {}),
    )
    profile["topic_assessment_summary"] = topic_assessment["summary"]
    profile["weak_topics"] = sorted(set(profile["weak_topics"] + topic_assessment["summary"].get("weak_topics", [])))
    academic = pipeline["academic"].analyze(profile)
    behavioral = pipeline["behavioral"].analyze(profile)
    wellness = pipeline["wellness"].analyze(profile)
    kg_insights = pipeline["kg"].analyze_weak_topics(profile["weak_topics"])
    retrieved = pipeline["rag"].retrieve(profile, top_k=5)
    recommendation = RecommendationAgent().analyze(profile, academic, behavioral, wellness, kg_insights, retrieved)
    soca = pipeline["soca"].generate(profile, {
        "academic": academic,
        "behavioral": behavioral,
        "wellness": wellness,
        "recommendation": recommendation,
        "topic_assessment": topic_assessment,
    }, retrieved, kg_insights)
    return {
        "profile": profile,
        "agents": {"academic": academic, "behavioral": behavioral, "wellness": wellness, "recommendation": recommendation},
        "knowledge_graph": kg_insights,
        "retrieved_recommendations": retrieved,
        "topic_assessment": topic_assessment,
        "soca": soca,
    }


def generate_report() -> None:
    response = build_response()
    save_json(RESPONSES_FILE, response)
    st.session_state.raw_response = response
    st.session_state.report = run_pipeline(response)
    st.session_state.submitted = True


def render_report(report: dict) -> None:
    profile = report["profile"]
    soca = report["soca"]
    st.markdown(f"## {profile['student_name']}'s AI Skill Assessment")
    st.caption(f"**Current Level**: {profile.get('current_level', 'N/A')} | **Target**: {profile.get('target_attempt', 'N/A')}")

    # SOCA Report first as the primary focus
    st.markdown("### 🎯 SOCA Report")
    tabs = st.tabs(["Strengths", "Opportunities", "Challenges", "Action Plan"])
    for tab, key in zip(tabs, ["strengths", "opportunities", "challenges", "action_plan"]):
        with tab:
            for item in soca[key]:
                st.write(f"- {item}")

    st.markdown("---")
    st.markdown("### Overall Academic & Study Metrics")
    score_df = pd.DataFrame([
        {"Metric": "Physics", "Score": profile["physics_score"]},
        {"Metric": "Chemistry", "Score": profile["chemistry_score"]},
        {"Metric": "Mathematics", "Score": profile["math_score"]},
        {"Metric": "Discipline", "Score": profile["discipline_score"]},
        {"Metric": "Time Management", "Score": profile["time_management_score"]},
        {"Metric": "Revision", "Score": profile["revision_consistency_score"]},
    ])
    
    # Premium color grading
    premium_scale = ["#FF5A5F", "#FFB85C", "#00A896"]
    
    fig = px.bar(
        score_df, 
        x="Metric", 
        y="Score", 
        range_y=[0, 100], 
        text="Score", 
        color="Score", 
        color_continuous_scale=premium_scale
    )
    st.plotly_chart(fig, use_container_width=True)

    render_knowledge_graph(report)
    render_topic_assessment(report)
    render_exports(report)


def render_knowledge_graph(report: dict) -> None:
    """Render three separate subject knowledge graphs with hierarchical layout."""
    from kg.knowledge_graph import JEETopicKnowledgeGraph

    kg_insights = report.get("knowledge_graph", {})
    weak_topics = set(report["profile"].get("weak_topics", []))

    prereq_gaps: set[str] = set()
    future_risks: set[str] = set()
    for prereqs in kg_insights.get("prerequisite_gaps", {}).values():
        prereq_gaps.update(prereqs)
    for risks in kg_insights.get("future_risk_topics", {}).values():
        future_risks.update(risks)

    st.markdown("---")
    st.markdown("### 🕸️ Topic Prerequisite Knowledge Graph")
    st.caption(
        "Topics flow **left → right** from foundational to advanced. "
        "Arrows show which topics you must master before moving on."
    )

    # ---- Legend ----
    l1, l2, l3, l4 = st.columns(4)
    l1.markdown("🔴 **Your Weak Topic**")
    l2.markdown("🟠 **Must Fix First** (prerequisite)")
    l3.markdown("🟡 **At Risk** (affected downstream)")
    l4.markdown("⬜ **Mastered / Neutral**")

    def _node_style(node: str) -> tuple[str, int, str]:
        """Return (color, size, badge) for a node."""
        if node in weak_topics:
            return "#FF5A5F", 28, "⚠️ Your Weak Topic"
        if node in prereq_gaps:
            return "#FFB85C", 22, "🔧 Fix This First"
        if node in future_risks:
            return "#f1c40f", 18, "⚡ At Risk if Gap Persists"
        return "#334155", 16, "✅ Mastered / Neutral"

    def _hierarchical_pos(G: "nx.DiGraph") -> dict[str, tuple[float, float]]:  # noqa: F821
        """Assign x by topological depth, y evenly spread per column."""
        try:
            order = list(nx.topological_sort(G))
        except Exception:
            order = list(G.nodes())
        depth: dict[str, int] = {}
        for node in order:
            preds = list(G.predecessors(node))
            depth[node] = max((depth[p] for p in preds), default=-1) + 1
        # Group by depth column
        cols: dict[int, list[str]] = {}
        for node, d in depth.items():
            cols.setdefault(d, []).append(node)
        pos: dict[str, tuple[float, float]] = {}
        max_col = max(cols) if cols else 0
        for col, nodes in cols.items():
            x = col / max(max_col, 1)
            for i, node in enumerate(nodes):
                y = (i + 1) / (len(nodes) + 1)
                pos[node] = (x, y)
        return pos

    def _build_subject_fig(subject: str, accent: str) -> "go.Figure":  # noqa: F821
        kg = JEETopicKnowledgeGraph()
        subject_nodes = {n for n, s in kg.SUBJECT_MAP.items() if s == subject}

        G = nx.DiGraph()
        for parent, child in kg.edges:
            if parent in subject_nodes and child in subject_nodes:
                G.add_edge(parent, child)
        # Add isolated nodes that belong to subject but have no edges
        for n in subject_nodes:
            if n not in G:
                G.add_node(n)

        pos = _hierarchical_pos(G)

        # Edge traces with arrows
        edge_x: list = []
        edge_y: list = []
        for parent, child in G.edges():
            if parent in pos and child in pos:
                x0, y0 = pos[parent]
                x1, y1 = pos[child]
                edge_x += [x0, x1, None]
                edge_y += [y0, y1, None]

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(width=2, color="#475569"),
            hoverinfo="none",
        )

        # Arrow annotations for direction
        annotations = []
        for parent, child in G.edges():
            if parent in pos and child in pos:
                x0, y0 = pos[parent]
                x1, y1 = pos[child]
                annotations.append(dict(
                    ax=x0, ay=y0, x=x1, y=y1,
                    xref="x", yref="y", axref="x", ayref="y",
                    showarrow=True,
                    arrowhead=3, arrowsize=1.4, arrowwidth=1.5,
                    arrowcolor="#94a3b8",
                ))

        # Node traces
        nx_list, ny_list, texts, colors, sizes, hovers = [], [], [], [], [], []
        for node in G.nodes():
            if node not in pos:
                continue
            x, y = pos[node]
            nx_list.append(x)
            ny_list.append(y)
            texts.append(node)
            color, size, badge = _node_style(node)
            colors.append(color)
            sizes.append(size)
            hovers.append(f"<b>{node}</b><br>{badge}<br>Subject: {subject}")

        node_trace = go.Scatter(
            x=nx_list,
            y=ny_list,
            mode="markers+text",
            text=texts,
            textposition="top center",
            textfont=dict(size=11, color="#f1f5f9"),
            hovertext=hovers,
            hoverinfo="text",
            marker=dict(
                size=sizes,
                color=colors,
                line=dict(width=2, color="#0f172a"),
                symbol="circle",
            ),
        )

        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                paper_bgcolor="#0f172a",
                plot_bgcolor="#111827",
                showlegend=False,
                hovermode="closest",
                annotations=annotations,
                margin=dict(b=40, l=40, r=40, t=30),
                xaxis=dict(
                    showgrid=False, zeroline=False, showticklabels=False,
                    range=[-0.1, 1.1],
                ),
                yaxis=dict(
                    showgrid=False, zeroline=False, showticklabels=False,
                    range=[0, 1],
                ),
                height=380,
            ),
        )
        return fig

    try:
        import networkx as nx  # noqa: F811

        tab_ph, tab_ch, tab_ma = st.tabs(["⚛️ Physics", "🧪 Chemistry", "📐 Mathematics"])

        with tab_ph:
            st.plotly_chart(_build_subject_fig("Physics", "#38bdf8"), use_container_width=True)

        with tab_ch:
            st.plotly_chart(_build_subject_fig("Chemistry", "#34d399"), use_container_width=True)

        with tab_ma:
            st.plotly_chart(_build_subject_fig("Mathematics", "#a78bfa"), use_container_width=True)

    except Exception as e:
        st.info(f"Graph rendering unavailable: {e}. Showing table view instead.")

    # ---- Prerequisite gap table ----
    rows = []
    for topic, prereqs in kg_insights.get("prerequisite_gaps", {}).items():
        future = kg_insights.get("future_risk_topics", {}).get(topic, [])
        rows.append(
            {
                "Weak Topic": topic,
                "Fix These First (Prerequisites)": ", ".join(prereqs) if prereqs else "—",
                "Topics at Risk if Unfixed": ", ".join(future[:5]) if future else "—",
            }
        )
    if rows:
        st.markdown("#### Prerequisite Gap Analysis")
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    elif not weak_topics:
        st.success("No weak topics detected — great job! All prerequisite chains look intact.")
    else:
        st.info("No prerequisite chain data found for the detected weak topics.")




def render_topic_assessment(report: dict) -> None:
    topic_reports = report.get("topic_assessment", {}).get("topic_reports", [])
    summary = report.get("topic_assessment", {}).get("summary", {})
    if not topic_reports:
        st.info("No topic diagnostic was attempted. Go back to Subject and Topic Selection to take a test.")
        return

    st.markdown("### Topic-Wise Diagnostic Intelligence")
    df = pd.DataFrame(topic_reports)
    if not df.empty and "question_results" in df.columns:
        df["correct"] = df["question_results"].apply(lambda rows: sum(1 for row in rows if row["is_correct"]))
    else:
        df["correct"] = 0
    for col in ["subject", "topic", "correct", "accuracy", "readiness_score", "workflow_progress"]:
        if col not in df.columns:
            df[col] = 0
    st.write("**Topic Test Scorecard**")
    st.dataframe(
        df[["subject", "topic", "correct", "accuracy", "readiness_score", "workflow_progress"]].rename(
            columns={
                "subject": "Subject",
                "topic": "Topic",
                "correct": "Correct out of 5",
                "accuracy": "Accuracy %",
                "readiness_score": "Readiness Score",
                "workflow_progress": "Progress %",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
    a, b = st.columns([1.1, 1])
    premium_scale = ["#FF5A5F", "#FFB85C", "#00A896"]
    with a:
        heatmap_data = df.pivot_table(index="subject", columns="topic", values="readiness_score", aggfunc="mean")
        fig = px.imshow(heatmap_data, text_auto=True, aspect="auto", color_continuous_scale=premium_scale, zmin=0, zmax=100, title="Topic Readiness Heatmap")
        st.plotly_chart(fig, use_container_width=True)
    with b:
        mastery_df = pd.DataFrame([{"Subject": s, "Mastery": v} for s, v in summary.get("subject_mastery", {}).items()])
        if not mastery_df.empty:
            fig = px.bar(mastery_df, x="Subject", y="Mastery", range_y=[0, 100], text="Mastery", color="Mastery", color_continuous_scale=premium_scale)
            st.plotly_chart(fig, use_container_width=True)

    alerts = df[df["readiness_score"] < 60].sort_values("readiness_score")
    if not alerts.empty:
        st.markdown("### Weak Topic Alerts")
        for _, row in alerts.iterrows():
            st.warning(f"{row['topic']}: {row['correct']}/5 correct, readiness {row['readiness_score']}, progress {row['workflow_progress']}%")

    roadmap = pd.DataFrame(report.get("topic_assessment", {}).get("roadmap", []))
    if not roadmap.empty:
        st.markdown("### Topic Roadmap")
        st.dataframe(roadmap, use_container_width=True, hide_index=True)

    st.markdown("### Per-Topic Detail")
    for item in topic_reports:
        topic_name = item.get("topic", "Unknown")
        readiness_val = item.get("readiness_score", 0)
        with st.expander(f"{topic_name} - readiness {readiness_val}"):
            m1, m2, m3, m4 = st.columns(4)
            correct = sum(1 for row in item.get("question_results", []) if row.get("is_correct"))
            m1.metric("Correct", f"{correct}/5")
            m2.metric("Accuracy", f"{item.get('accuracy', 0)}%")
            m3.metric("Readiness", readiness_val)
            m4.metric("Progress", f"{item.get('workflow_progress', 0)}%")
            st.write("**Weak Areas**")
            for area in item["weak_areas"]:
                st.write(f"- {area}")
            st.write("**Recommendations**")
            for rec in item["recommendations"]:
                st.write(f"- {rec}")


def render_exports(report: dict) -> None:
    with st.expander("Structured AI agent analysis"):
        st.json(report["agents"])

    d1, d2 = st.columns(2)
    report_json = json.dumps(report, indent=2)
    d1.download_button("Download JSON report", report_json, file_name="jee_soca_report.json", mime="application/json")
    d2.download_button("Download PDF report", build_pdf_report(report), file_name="jee_soca_report.pdf", mime="application/pdf")


def load_sample_into_state() -> None:
    sample = json.loads((DATA_DIR / "sample_responses.json").read_text(encoding="utf-8"))[0]
    st.session_state.student_profile_data = {
        "student_name": sample["student"]["name"],
        "current_level": "Class 12th",
        "target_attempt": "JEE Main 2027",
    }
    st.session_state.behavior_data = {
        "time_management_category": "Usually finish just on time",
        "revision_category": "Revise important topics weekly",
        "problem_solving_category": "Can solve standard problems independently",
        "mock_test_frequency": sample["behavior"]["mock_test_frequency"],
        "study_techniques": sample["behavior"]["study_techniques"],
        "resources": sample["behavior"]["resources"],
        "short_answer_blocker": sample["behavior"]["short_answer_blocker"],
    }
    st.session_state.student_name = sample["student"]["name"]
    st.session_state.current_level = "Class 12th"
    st.session_state.target_attempt = "JEE Main 2027"
    st.session_state.Physics_score = sample["academic"]["physics_proficiency"]
    st.session_state.Chemistry_score = sample["academic"]["chemistry_proficiency"]
    st.session_state.Mathematics_score = sample["academic"]["math_proficiency"]
    academic_data = {}
    weak_topics = set(sample["academic"].get("weak_topics", []))
    scores = {
        "Physics": sample["academic"]["physics_proficiency"],
        "Chemistry": sample["academic"]["chemistry_proficiency"],
        "Mathematics": sample["academic"]["math_proficiency"],
    }
    for subject, payload in sample.get("topic_tracking", {}).items():
        completed_topics = payload.get("completed", [])
        untouched_topics = [t for t in load_topics()[subject] if t not in completed_topics]
        details = {}
        for topic in completed_topics:
            details[topic] = {
                "confidence": "Medium",
                "workflow_stages": ["Video Lectures", "NCERT", "Exercise 1 (JEE Mains Easy)", "PYQs"],
            }
        academic_data[subject] = {
            "score": scores[subject],
            "weak_topics": [topic for topic in load_topics()[subject] if topic in weak_topics],
            "completed": completed_topics,
            "partial": [],
            "untouched": untouched_topics,
            "topic_details": details,
        }
        st.session_state[f"{subject}_completed"] = completed_topics
        st.session_state[f"{subject}_partial"] = []
        st.session_state[f"{subject}_untouched"] = untouched_topics
        for topic in completed_topics:
            st.session_state[f"{topic}_workflow"] = ["Video Lectures", "NCERT", "Exercise 1 (JEE Mains Easy)", "PYQs"]
    st.session_state.academic_data = academic_data
    st.session_state.diagnostic_topics = list(sample.get("diagnostic_attempts", {}).keys())[:2]
    st.session_state.diagnostic_data = {
        "selected_topics": list(sample.get("diagnostic_attempts", {}).keys())[:2],
        "diagnostic_tests": sample.get("diagnostic_tests", {}),
        "diagnostic_attempts": sample.get("diagnostic_attempts", {}),
    }
    st.session_state.raw_response = sample
    st.session_state.report = run_pipeline(sample)
    st.session_state.submitted = True
    st.session_state.page_index = 4


def main() -> None:
    init_state()
    st.title("SOCA Analysis")

    with st.sidebar:
        st.header("Navigation")
        if st.button("Load sample response", use_container_width=True):
            load_sample_into_state()
            st.rerun()
        if st.button("Regenerate assessment report", use_container_width=True):
            persist_current_page()
            generate_report()
            st.session_state.page_index = 4
            st.rerun()

    render_progress()
    page = PAGES[st.session_state.page_index]
    if page == "Student Profile":
        render_student_profile_page()
    elif page == "Academic Proficiency":
        render_academic_page()
    elif page == "Study Behaviour":
        render_study_behaviour_page()
    elif page == "Topic Diagnostic Test":
        render_topic_diagnostic_page()
    else:
        if not st.session_state.report:
            generate_report()
        render_report(st.session_state.report)

    navigation_controls()


if __name__ == "__main__":
    main()
