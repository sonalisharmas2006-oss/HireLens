from database.db import db

from models.report import Report
from models.interview import Interview
from models.ai_analysis import AIAnalysis


def generate_report(interview_id):

    print("========== REPORT SERVICE ==========")
    print("Interview ID:", interview_id)

    interview = Interview.query.get(interview_id)
    print("Interview:", interview)

    if interview is None:
        print("❌ Interview not found")
        return None

    analysis = AIAnalysis.query.filter_by(
        interview_id=interview_id
    ).first()

    print("Analysis:", analysis)

    if analysis is None:
        print("❌ AI Analysis not found")
        return None

    report = Report.query.filter_by(
        interview_id=interview_id
    ).first()

    print("Existing Report:", report)

    suggestions = (
        f"Overall AI Score: {analysis.overall_score}\n"
        f"Emotion: {analysis.emotion}\n"
        f"Confidence Score: {analysis.confidence_score}\n"
        f"Eye Contact Score: {analysis.eye_contact_score}\n"
        f"Voice Confidence: {analysis.voice_confidence}\n"
        f"Speaking Speed: {analysis.speaking_speed}\n"
        f"Filler Words: {analysis.filler_words}\n"
        f"Posture Score: {analysis.posture_score}\n"
        f"Smile Score: {analysis.smile_score}\n"
        f"Suggestion: Maintain eye contact and avoid filler words."
    )

    if report:

        report.confidence_score = int(analysis.confidence_score)
        report.communication_score = int(analysis.voice_confidence)
        report.eye_contact = str(analysis.eye_contact_score)
        report.emotion = analysis.emotion
        report.filler_words = analysis.filler_words
        report.suggestions = suggestions

        print("✅ Existing report updated")

    else:

        report = Report(
            interview_id=interview_id,
            confidence_score=int(analysis.confidence_score),
            communication_score=int(analysis.voice_confidence),
            eye_contact=str(analysis.eye_contact_score),
            emotion=analysis.emotion,
            filler_words=analysis.filler_words,
            suggestions=suggestions
        )

        db.session.add(report)

        print("✅ New report created")

    interview.status = "Completed"

    db.session.commit()

    print("✅ Report saved successfully")

    return report


def get_report(interview_id):

    report = Report.query.filter_by(
        interview_id=interview_id
    ).first()

    print("Fetched Report:", report)

    return report