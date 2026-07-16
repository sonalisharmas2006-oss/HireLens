from database.db import db

from models.report import Report
from models.interview import Interview
from models.ai_analysis import AIAnalysis


def generate_report(interview_id):

    print("========== REPORT SERVICE ==========")
    print("Interview ID:", interview_id)

    interview = Interview.query.get(interview_id)

    if interview is None:
        print("❌ Interview not found")
        return None

    analysis = AIAnalysis.query.filter_by(
        interview_id=interview_id
    ).first()

    if analysis is None:
        print("❌ AI Analysis not found")
        return None

    report = Report.query.filter_by(
        interview_id=interview_id
    ).first()

    feedback = []

    if analysis.confidence_score < 80:
        feedback.append("• Improve your confidence while answering questions.")

    if analysis.eye_contact_score < 80:
        feedback.append("• Maintain better eye contact with the interviewer.")

    if analysis.voice_confidence < 80:
        feedback.append("• Speak louder and more confidently.")

    if analysis.smile_score < 75:
        feedback.append("• Smile naturally to create a positive impression.")

    if analysis.posture_score < 80:
        feedback.append("• Maintain an upright posture throughout the interview.")

    if analysis.filler_words > 5:
        feedback.append("• Reduce filler words like 'um', 'uh', and 'like'.")

    if analysis.speaking_speed < 120:
        feedback.append("• Try speaking a little faster.")

    if analysis.speaking_speed > 150:
        feedback.append("• Slow down your speaking speed for better clarity.")

    if len(feedback) == 0:
        feedback.append(
            "Excellent interview performance! Keep practicing to maintain consistency."
        )

    suggestions = (
        f"Overall AI Score: {analysis.overall_score}/100\n\n"

        f"Emotion: {analysis.emotion}\n"

        f"Confidence Score: {analysis.confidence_score}\n"

        f"Eye Contact Score: {analysis.eye_contact_score}\n"

        f"Voice Confidence: {analysis.voice_confidence}\n"

        f"Speaking Speed: {analysis.speaking_speed} WPM\n"

        f"Filler Words: {analysis.filler_words}\n"

        f"Posture Score: {analysis.posture_score}\n"

        f"Smile Score: {analysis.smile_score}\n\n"

        f"Feedback:\n\n"

        + "\n".join(feedback)
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

    return Report.query.filter_by(
        interview_id=interview_id
    ).first()