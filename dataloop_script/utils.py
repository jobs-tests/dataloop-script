from datetime import datetime
import json
import os
from dataloop_script.constants import image_dir, annotation_dir, annotation_file_name


def load_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


def format_unix_timestamp() -> str:
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    time_array = datetime.utcfromtimestamp(timestamp)
    return time_array.strftime("%Y-%m-%d %H:%M:%S")


def setup_file_paths():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    images_folder = os.path.join(current_directory, image_dir)
    annotation_file_path = os.path.join(
        current_directory,
        annotation_dir,
        annotation_file_name
    )
    return images_folder, annotation_file_path