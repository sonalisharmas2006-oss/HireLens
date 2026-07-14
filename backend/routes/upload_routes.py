from flask import Blueprint, request, jsonify

from services.upload_service import save_video
from services.interview_service import update_video

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/api/upload/video", methods=["POST"])
def upload_video():

    if "video" not in request.files:

        return jsonify({
            "message": "Video file missing"
        }), 400

    interview_id = request.form.get("interview_id")

    if not interview_id:

        return jsonify({
            "message": "Interview ID missing"
        }), 400

    video = request.files["video"]

    filepath = save_video(video)

    interview = update_video(
        interview_id,
        filepath
    )

    if interview is None:

        return jsonify({
            "message": "Interview not found"
        }), 404

    return jsonify({

        "message": "Video Uploaded Successfully",

        "interview": interview.to_dict()

    })