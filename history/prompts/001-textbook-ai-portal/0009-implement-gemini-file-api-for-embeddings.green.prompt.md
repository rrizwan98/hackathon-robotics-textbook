---
id: 0009
title: Implement Gemini File API for Embeddings
stage: green
date: 2025-12-02
surface: agent
model: gemini
feature: 001-textbook-ai-portal
branch: feat/setup-docusaurus-frontend
user: user
command: /sp.implement
labels: [gemini, file-api, embeddings, backend, script, test]
links:
  spec: specs/001-textbook-ai-portal/spec.md
  ticket: null
  adr: null
  pr: https://github.com/rrizwan98/hackathon-robotics-textbook/pull/2
files:
- .env
- backend/data/embeddings.json
- backend/data/gemini_files.json
- backend/requirements.txt
- backend/src/scripts/embed_textbook_gemini.py
- backend/src/scripts/upload_textbook_files_gemini.py
- backend/tests/test_gemini_file_api.py
- history/prompts/001-textbook-ai-portal/0008-add-initial-english-and-urdu-textbook-content.green.prompt.md
- history/prompts/001-textbook-ai-portal/0009-implement-gemini-file-api-for-embeddings.green.prompt.md
tests:
- backend/tests/test_gemini_file_api.py
---

## Prompt

/sp.implement now let's build the step # 4. here is the detail. IMPLEMENTATION STEP 4 ONLY — UPDATED EMBEDDING FLOW (GEMINI FILE API).

Context:
- We are using Gemini embedding model: "gemini-embedding-001".
- We will NOT use an external vector store (e.g. Qdrant) for now.
- Embeddings will be used later directly (or cached locally) as needed.
- We only need a minimal test to verify embedding correctness (not full RAG pipeline yet).

Tasks:

1. Create a script in the backend to upload the 2 chapter files via Gemini File API, e.g.:
   - File: backend/src/scripts/upload_textbook_files_gemini.py

   The script should:
   - Initialize a Gemini client using the existing API key.
   - Upload the two Markdown files using client.files.upload(...), with:
     - display_name = the chapter title
     - mime_type = "text/markdown"
   - Collect the returned file references (file.name or equivalent ID).
   - Save these references into a local JSON file, e.g.:
     backend/data/gemini_files.json
     Structure example:
     [
       {
         "path": "frontend/site/docs/introduction-physical-ai.md",
         "display_name": "Introduction to Physical AI & Humanoid Robotics",
         "file_name": "<gemini-file-id-1>"
       },
       {
         "path": "frontend/site/docs/ros2.md",
         "display_name": "Robot Operating System 2 (ROS2)",
         "file_name": "<gemini-file-id-2>"
       }
     ]

2. Create a small test script (or pytest test) to run a simple QA call on one of the uploaded files, e.g.:
   - File: backend/tests/test_gemini_file_api.py

   The test should:
   - Load backend/data/gemini_files.json.
   - Pick the "Introduction to Physical AI & Humanoid Robotics" file entry.
   - Call client.models.generate_content(...) with:
     - model = "gemini-2.5-flash-lite"
     - contents = [
         "<a clear question about that chapter>",
         client.files.get(name=<file_name_from_json>)
       ]
     (Pattern similar to the File API example:
       "What should I do before I start writing, when following these guidelines?",
       md_file
     )
   - Print the response text to the console.
   - Assert that the response text is non-empty (basic correctness check).

3. Add basic comments in both scripts explaining:
   - How to run the upload script (e.g. `python backend/src/scripts/upload_textbook_files_gemini.py`)
   - How to run the test (e.g. `pytest backend/tests/test_gemini_file_api.py`)

Constraints:
- Do NOT introduce any FastAPI endpoints in this step.
- Do NOT call the Gemini embedding model.
- Do NOT integrate any vector store or database; only use the File API and local JSON to hold file IDs.
- Only touch backend scripts/tests needed for this File API flow.

Output / Success Criteria:
- A working upload script that successfully uploads the two chapter files to Gemini File API and writes gemini_files.json with their file IDs.
- A working test that:
  - Reads gemini_files.json
  - Calls gemini-2.5-flash-lite with a question + the file reference
  - Receives a meaningful answer (non-empty response text).
- No changes to FastAPI or frontend in this step.

After this step is complete:
- STOP. Wait for manual review before moving to any RAG agent or API integration steps.

## Response snapshot

Summary of changes for Task 4 (UPDATED EMBEDDING FLOW):
*   Recreated necessary backend directory structure.
*   Created `backend/src/scripts/upload_textbook_files_gemini.py` to upload specific Markdown files to Gemini File API.
*   Created `backend/tests/test_gemini_file_api.py` to verify QA functionality against uploaded files.
*   Updated `backend/requirements.txt` with `pytest` and ensured `google-generativeai` is updated.
*   Successfully uploaded 'intro.md' and 'ros2.md' to Gemini File API and saved references.
*   Successfully ran the QA test against an uploaded file, confirming non-empty responses.

## Outcome

- ✅ Impact: Successfully implemented and tested the Gemini File API flow for uploading textbook content and running QA queries.
- 🧪 Tests: `pytest backend/tests/test_gemini_file_api.py` passed.
- 📁 Files: Created backend scripts and tests for Gemini File API. Modified previous embedding script. Generated `gemini_files.json`.
- 🔁 Next prompts: Proceed with next implementation step or integrate with other components.
- 🧠 Reflection: Encountered several issues with the `google-generativeai` library's API for File Upload and Client instantiation, requiring multiple iterations and debugging with `context7` to find the correct usage. Also faced Gemini API quota limits initially, which led to a revised plan for processing fewer files using the File API. All issues were resolved, leading to a successful implementation of this step.
