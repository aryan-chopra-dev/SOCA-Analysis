# backend/api.py
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to path to load assessment, agents, kg, rag, scoring, etc.
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

try:
    import networkx as nx
except ImportError:
    nx = None

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
from contextlib import asynccontextmanager

# Initialize RAGRetriever once at startup (loads embedding model once, not per-request)
_rag_retriever: RAGRetriever | None = None

def get_rag_retriever() -> RAGRetriever:
    global _rag_retriever
    if _rag_retriever is None:
        _rag_retriever = RAGRetriever()
    return _rag_retriever

@asynccontextmanager
async def lifespan(app_instance):
    """Pre-warm the RAGRetriever at startup so /evaluate is instant."""
    import logging
    logging.info("[SOCA] Pre-warming RAGRetriever (loading embedding model)...")
    get_rag_retriever()
    logging.info("[SOCA] RAGRetriever ready. First /evaluate will be fast.")
    yield

app = FastAPI(title="SOCA Analysis API", version="1.0.0", lifespan=lifespan)

# Setup CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175"
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = ROOT_DIR / "data"
FEEDBACK_FILE = DATA_DIR / "feedback.jsonl"
RESPONSES_FILE = DATA_DIR / "latest_response.json"
TOPICS_FILE = DATA_DIR / "jee_topics.json"

class FeedbackPayload(BaseModel):
    student_name: str
    feedback: str
    rating: int
    metadata: Dict[str, Any] = {}

class QuestionnairePayload(BaseModel):
    data: Dict[str, Any]


def _hierarchical_pos(G) -> dict:
    """Assign x by topological depth, y evenly spread per column."""
    if not nx:
        # Fallback coordinate mapping if networkx is missing
        nodes = list(G.nodes())
        return {node: (idx / max(1, len(nodes) - 1), 0.5) for idx, node in enumerate(nodes)}
    
    try:
        order = list(nx.topological_sort(G))
    except Exception:
        order = list(G.nodes())
    
    depth = {}
    for node in order:
        preds = list(G.predecessors(node))
        depth[node] = max((depth[p] for p in preds), default=-1) + 1
    
    # Group by depth column
    cols = {}
    for node, d in depth.items():
        cols.setdefault(d, []).append(node)
    
    pos = {}
    max_col = max(cols) if cols else 0
    for col, nodes in cols.items():
        x = col / max(max_col, 1)
        for i, node in enumerate(nodes):
            y = (i + 1) / (len(nodes) + 1)
            pos[node] = (x, y)
    return pos


def compute_kg_layout(weak_topics: list, prereq_gaps: dict, future_risks: dict) -> dict:
    """Computes coordinate positions for Physics, Chemistry, and Mathematics knowledge graphs."""
    kg = JEETopicKnowledgeGraph()
    weak_set = set(weak_topics)
    
    # Flatten prereq gaps and future risks into single sets
    gaps_set = set()
    for items in prereq_gaps.values():
        gaps_set.update(items)
        
    risks_set = set()
    for items in future_risks.values():
        risks_set.update(items)

    def build_subject_graph(subject: str) -> dict:
        subject_nodes = {n for n, s in kg.SUBJECT_MAP.items() if s == subject}
        
        G = nx.DiGraph() if nx else None
        edges = []
        for parent, child in kg.edges:
            if parent in subject_nodes and child in subject_nodes:
                edges.append({"source": parent, "target": child})
                if G is not None:
                    G.add_edge(parent, child)
        
        if G is not None:
            for n in subject_nodes:
                if n not in G:
                    G.add_node(n)
            pos = _hierarchical_pos(G)
            nodes_list = list(G.nodes())
        else:
            nodes_list = list(subject_nodes)
            pos = {node: (idx / max(1, len(nodes_list) - 1), 0.5) for idx, node in enumerate(nodes_list)}

        nodes = []
        for node in nodes_list:
            x, y = pos.get(node, (0.5, 0.5))
            
            # Styling attributes matching Streamlit color coding
            if node in weak_set:
                color = "#FF5A5F"
                size = 24
                badge = "⚠️ Your Weak Topic"
                status = "weak"
            elif node in gaps_set:
                color = "#FFB85C"
                size = 20
                badge = "🔧 Fix This First"
                status = "prereq_gap"
            elif node in risks_set:
                color = "#F1C40F"
                size = 18
                badge = "⚡ At Risk if Gap Persists"
                status = "future_risk"
            else:
                color = "#10B981"
                size = 14
                badge = "✅ Mastered / Neutral"
                status = "mastered"
                
            nodes.append({
                "id": node,
                "label": node,
                "x": x,
                "y": y,
                "color": color,
                "size": size,
                "badge": badge,
                "status": status
            })
            
        return {"nodes": nodes, "edges": edges}

    return {
        "Physics": build_subject_graph("Physics"),
        "Chemistry": build_subject_graph("Chemistry"),
        "Mathematics": build_subject_graph("Mathematics")
    }


def run_soca_pipeline(response_data: dict) -> dict:
    """Executes the standard, complete SOCA analysis pipeline."""
    scoring = ScoringEngine()
    topic_assessment_pipeline = TopicAssessmentPipeline()
    academic_agent = AcademicAgent()
    behavioral_agent = BehavioralAgent()
    wellness_agent = WellnessAgent()
    kg = JEETopicKnowledgeGraph()
    rag = get_rag_retriever()
    recommendation_agent = RecommendationAgent()
    soca_generator = SOCAGenerator()

    # Step 1: scoring and profiles
    profile = scoring.build_profile(response_data)
    
    # Step 2: topic evaluation
    topic_assessment = topic_assessment_pipeline.evaluate(
        response_data.get("topic_tracking", {}),
        response_data.get("diagnostic_tests", {}),
        response_data.get("diagnostic_attempts", {}),
    )
    
    profile["topic_assessment_summary"] = topic_assessment["summary"]
    profile["weak_topics"] = sorted(set(profile["weak_topics"] + topic_assessment["summary"].get("weak_topics", [])))
    
    # Step 3: agents
    academic = academic_agent.analyze(profile)
    behavioral = behavioral_agent.analyze(profile)
    wellness = wellness_agent.analyze(profile)
    
    # Step 4: knowledge graph & retrieval
    kg_insights = kg.analyze_weak_topics(profile["weak_topics"])
    retrieved = rag.retrieve(profile, top_k=5)
    
    # Step 5: recommendation and LLM report
    recommendation = recommendation_agent.analyze(profile, academic, behavioral, wellness, kg_insights, retrieved)
    soca = soca_generator.generate(
        profile,
        {
            "academic": academic,
            "behavioral": behavioral,
            "wellness": wellness,
            "recommendation": recommendation,
            "topic_assessment": topic_assessment,
        },
        retrieved,
        kg_insights
    )

    # Step 6: Layout coordinates for knowledge graphs
    kg_layouts = compute_kg_layout(
        profile["weak_topics"],
        kg_insights.get("prerequisite_gaps", {}),
        kg_insights.get("future_risk_topics", {})
    )

    return {
        "profile": profile,
        "agents": {
            "academic": academic,
            "behavioral": behavioral,
            "wellness": wellness,
            "recommendation": recommendation
        },
        "knowledge_graph": kg_insights,
        "knowledge_graph_layouts": kg_layouts,
        "retrieved_recommendations": retrieved,
        "topic_assessment": topic_assessment,
        "soca": soca,
    }


@app.get("/topics")
async def get_topics():
    try:
        if not TOPICS_FILE.exists():
            raise HTTPException(status_code=404, detail="jee_topics.json not found")
        return json.loads(TOPICS_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/questions")
async def get_questions(subject: str, topic: str):
    try:
        q_gen = QuestionGenerator()
        question_set = q_gen.generate(subject, topic)
        return question_set
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sample")
async def get_sample():
    try:
        sample_path = DATA_DIR / "sample_responses.json"
        if not sample_path.exists():
            raise HTTPException(status_code=404, detail="sample_responses.json not found")
        
        sample_data = json.loads(sample_path.read_text(encoding="utf-8"))
        if not sample_data:
            raise HTTPException(status_code=404, detail="Sample database empty")
        
        # Take the first sample response
        sample_response = sample_data[0]
        
        # Build diagnostic tests if missing from the JSON
        if "diagnostic_tests" not in sample_response or not sample_response["diagnostic_tests"]:
            diagnostic_tests = {}
            for topic in sample_response.get("diagnostic_attempts", {}).keys():
                # Locate subject in topics
                subject = "Physics"
                topics_db = json.loads(TOPICS_FILE.read_text(encoding="utf-8"))
                for sub, topics in topics_db.items():
                    if topic in topics:
                        subject = sub
                        break
                diagnostic_tests[topic] = QuestionGenerator().generate(subject, topic)
            sample_response["diagnostic_tests"] = diagnostic_tests

        # Pre-run report data
        report = run_soca_pipeline(sample_response)
        
        return {
            "response": sample_response,
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate")
async def evaluate_questionnaire(payload: QuestionnairePayload):
    try:
        # Save to latest response to keep history
        RESPONSES_FILE.parent.mkdir(parents=True, exist_ok=True)
        RESPONSES_FILE.write_text(json.dumps(payload.data, indent=2), encoding="utf-8")
        
        report = run_soca_pipeline(payload.data)
        return report
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pdf")
async def get_pdf_report(payload: Dict[str, Any]):
    try:
        # Expects payload to be the output of run_soca_pipeline
        pdf_bytes = build_pdf_report(payload)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=jee_soca_report.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
async def save_feedback(payload: FeedbackPayload):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        feedback_entry = {
            "student_name": payload.student_name,
            "feedback": payload.feedback,
            "rating": payload.rating,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": payload.metadata
        }
        with FEEDBACK_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(feedback_entry) + "\n")
        return {"status": "success", "message": "Feedback saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)

# Vercel serverless function entry point
handler = app
