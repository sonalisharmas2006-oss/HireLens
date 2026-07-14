import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads/videos"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def save_video(video):

    filename = secure_filename(video.filename)

    filepath = os.path.join(UPLOAD_FOLDER, filename)

    video.save(filepath)

    return filename