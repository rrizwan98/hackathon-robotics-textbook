# backend/tests/test_gemini_file_api.py

import os
import json
import warnings
import pytest
from google import genai
from dotenv import load_dotenv

# Suppress deprecation warnings from dependencies
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

# if not API_KEY:
#     raise ValueError("GEMINI_API_KEY not found in .env file.")
# client = Client(api_key=API_KEY)

# --- Configuration ---
UPLOAD_FILES_METADATA_PATH = os.path.join("backend", "data", "gemini_files.json")
MODEL_NAME = "gemini-2.5-flash-lite"

@pytest.fixture(scope="module")
def gemini_files_data():
    """
    Loads the uploaded Gemini files metadata.
    """
    if not os.path.exists(UPLOAD_FILES_METADATA_PATH):
        pytest.fail(f"Gemini files metadata not found at {UPLOAD_FILES_METADATA_PATH}. "
                    "Please run upload_textbook_files_gemini.py first.")
    with open(UPLOAD_FILES_METADATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_qa_against_intro_chapter(gemini_files_data):
    """
    Tests a QA query against the 'Introduction to Physical AI & Humanoid Robotics' file.
    """
    intro_file_entry = None
    for entry in gemini_files_data:
        if "Introduction to Physical AI & Humanoid Robotics" == entry.get("display_name", ""):
            intro_file_entry = entry
            break

    if not intro_file_entry:
        pytest.fail("Could not find 'Introduction to Physical AI & Humanoid Robotics' entry in gemini_files.json.")

    file_name = intro_file_entry["file_name"]

    # Retrieve the file object from Gemini (optional, but good for verification)
    try:
        gemini_file = client.files.get(name=file_name)
        print(f"\nRetrieved Gemini File: {gemini_file.display_name} (State: {gemini_file.state})")
    except Exception as e:
        pytest.fail(f"Could not retrieve Gemini file '{file_name}': {e}")

    # A clear question about the chapter content
    question = "What is the primary focus of Physical AI mentioned in this document?"

    print(f"Sending QA query: '{question}' to model '{MODEL_NAME}' with file '{file_name}'...")
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                question,
                gemini_file
            ]
        )
        response_text = response.text
        print(f"\n{'='*200}")
        print(f"AI Response:")
        print(f"{'='*200}")
        print(response_text)
        print(f"{'='*200}\n")

        assert response_text.strip() != "", "Response text should not be empty."

    except Exception as e:
        pytest.fail(f"Error generating content: {e}")

# How to run the test:
# First, ensure you have pytest installed: pip install pytest
# Second, run the upload script: python backend/src/scripts/upload_textbook_files_gemini.py
# Finally, run pytest from the root directory: pytest backend/tests/test_gemini_file_api.py

