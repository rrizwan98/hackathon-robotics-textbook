# backend/src/scripts/embed_textbook_gemini.py

import os
import json
import glob
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file.")
genai.configure(api_key=API_KEY)

def get_embedding(text: str) -> list[float]:
    """
    Generates an embedding for the given text using the Gemini embedding model.
    """
    model = "models/embedding-001" # This is the Gemini embedding model
    response = genai.embed_content(model=model, content=text)
    return response['embedding']

def embed_textbook_content(docs_dir: str, output_path: str):
    """
    Loads Markdown files, generates embeddings, and stores them in a JSON file.
    """
    embeddings_data = {}
    markdown_files = glob.glob(os.path.join(docs_dir, '**/*.md'), recursive=True)

    print(f"Found {len(markdown_files)} markdown files in {docs_dir}")

    for file_path in markdown_files:
        allowed_files = [
            "intro.md", "intro-ur.md",
            "ros2.md", "ros2-ur.md",
        ]
        # Get just the filename from file_path
        filename = os.path.basename(file_path)

        if filename not in allowed_files:
            print(f"Skipping file as not in allowed list: {file_path}")
            continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract text content (can be extended to split into chunks and add metadata)
            # For this task, we'll embed the whole file content.
            text_content = content

            if text_content.strip(): # Only embed if there is actual text content
                embedding = get_embedding(text_content)
                relative_path = os.path.relpath(file_path, docs_dir)
                embeddings_data[relative_path] = embedding
                print(f"Embedded: {relative_path}")
            else:
                print(f"Skipping empty file: {file_path}")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(embeddings_data, f, indent=2)
    print(f"Embeddings saved to {output_path}")

if __name__ == "__main__":
    FRONTEND_DOCS_DIR = os.path.join("frontend", "docs") # Path to Docusaurus docs
    OUTPUT_JSON_PATH = os.path.join("backend", "data", "embeddings.json")

    # Ensure frontend/docs directory exists
    if not os.path.exists(FRONTEND_DOCS_DIR):
        print(f"Error: Frontend docs directory not found at {FRONTEND_DOCS_DIR}")
        exit(1)

    embed_textbook_content(FRONTEND_DOCS_DIR, OUTPUT_JSON_PATH)
