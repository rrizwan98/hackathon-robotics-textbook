# backend/src/scripts/upload_textbook_files_gemini.py

import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

# if not API_KEY:
#     raise ValueError("GEMINI_API_KEY not found in .env file.")
# client = Client(api_key=API_KEY)

# --- Configuration ---
FRONTEND_DOCS_DIR = os.path.join("frontend", "docs")
UPLOAD_FILES_METADATA_PATH = os.path.join("backend", "data", "gemini_files.json")

# Define the files to upload with their display names
# Using only English versions as specified in the task for now
files_to_upload = [
    {
        "path": os.path.join(FRONTEND_DOCS_DIR, "intro.md"),
        "display_name": "Introduction to Physical AI & Humanoid Robotics"
    },
    {
        "path": os.path.join(FRONTEND_DOCS_DIR, "ros2.md"),
        "display_name": "Robot Operating System 2 (ROS2)"
    }
]

def upload_files_to_gemini():
    """
    Uploads specified Markdown files to Gemini File API and saves their references locally.
    """
    uploaded_files_info = []

    print("Starting file upload to Gemini File API...")

    for file_info in files_to_upload:
        file_path = file_info["path"]
        display_name = file_info["display_name"]

        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}. Skipping.")
            continue

        try:
            print(f"Uploading '{display_name}' from '{file_path}'...")
            uploaded_file = client.files.upload(
                file=file_path,
                config=types.UploadFileConfig(
                    display_name=display_name,
                    mime_type="text/markdown"
                )
            )
            print(f"Successfully uploaded: {uploaded_file.display_name} (ID: {uploaded_file.name})")

            uploaded_files_info.append({
                "path": file_path,
                "display_name": display_name,
                "file_name": uploaded_file.name # This is the Gemini File API reference
            })

        except Exception as e:
            print(f"Error uploading '{display_name}' ({file_path}): {e}")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(UPLOAD_FILES_METADATA_PATH), exist_ok=True)

    with open(UPLOAD_FILES_METADATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(uploaded_files_info, f, indent=2)
    print(f"Uploaded files metadata saved to {UPLOAD_FILES_METADATA_PATH}")

if __name__ == "__main__":
    # How to run:
    # python backend/src/scripts/upload_textbook_files_gemini.py
    upload_files_to_gemini()
