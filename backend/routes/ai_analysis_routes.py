from flask import Blueprint, jsonify

from services.ai_analysis_service import (
    create_ai_analysis,
    get_ai_analysis
)

ai_analysis_bp = Blueprint(
    "ai_analysis",
    __name__
)


@ai_analysis_bp.route(
    "/api/analysis/generate/<int:interview_id>",
    methods=["POST"]
)
def generate(interview_id):

    analysis = create_ai_analysis(interview_id)

    return jsonify({

        "message": "AI Analysis Generated",

        "analysis": analysis.to_dict()

    }), 201


@ai_analysis_bp.route(
    "/api/analysis/<int:interview_id>",
    methods=["GET"]
)
def fetch(interview_id):

    analysis = get_ai_analysis(interview_id)

    if analysis is None:

        return jsonify({

            "message": "Analysis Not Found"

        }), 404

    return jsonify(
        analysis.to_dict()
    )