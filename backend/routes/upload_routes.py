from flask import Blueprint, request, jsonify

from services.upload_service import save_video

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/api/upload/video", methods=["POST"])
def upload_video():

    if "video" not in request.files:

        return jsonify({
            "message": "No video uploaded"
        }), 400

    video = request.files["video"]

    filename = save_video(video)

    return jsonify({

        "message": "Video Uploaded Successfully",

        "filename": filename

    }), 200