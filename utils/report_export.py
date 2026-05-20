import json
from io import BytesIO


def build_pdf_report(report: dict) -> bytes:
    """Create a compact PDF SOCA report. Falls back to plain bytes if reportlab is absent."""

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    except Exception:
        return json.dumps(report, indent=2).encode("utf-8")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, title="SOCA Analysis Report")
    styles = getSampleStyleSheet()
    story = [Paragraph("SOCA Analysis Report", styles["Title"]), Spacer(1, 12)]

    profile = report["profile"]
    story.append(Paragraph(f"Student: {profile['student_name']} | Level: {profile.get('current_level', 'N/A')} | Target: {profile['target_attempt']}", styles["Normal"]))
    story.append(Paragraph(f"Stress: {profile['stress_level']} | Discipline: {profile['discipline_score']}/100", styles["Normal"]))
    story.append(Spacer(1, 12))

    for section in ["strengths", "opportunities", "challenges", "action_plan"]:
        story.append(Paragraph(section.replace("_", " ").title(), styles["Heading2"]))
        for item in report["soca"][section]:
            story.append(Paragraph(f"- {item}", styles["BodyText"]))
        story.append(Spacer(1, 8))

    topic_reports = report.get("topic_assessment", {}).get("topic_reports", [])
    if topic_reports:
        story.append(Paragraph("Topic Diagnostic Summary", styles["Heading2"]))
        for item in topic_reports[:8]:
            story.append(Paragraph(
                f"{item.get('topic', 'Unknown')}: Accuracy {item.get('accuracy', 0)}%, Confidence {item.get('confidence', 'Medium')}, "
                f"Readiness {item.get('readiness_score', 0)}, Progress {item.get('workflow_progress', 0)}%",
                styles["BodyText"],
            ))

    doc.build(story)
    return buffer.getvalue()
