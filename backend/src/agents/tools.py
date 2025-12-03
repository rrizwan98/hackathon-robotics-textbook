# backend/src/agents/tools.py
"""
Tools for the Textbook Agent.
These tools allow the agent to query and interact with uploaded textbook files.
"""

import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from agents import function_tool

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

# --- Configuration ---
UPLOAD_FILES_METADATA_PATH = os.path.join("backend", "data", "gemini_files.json")
MODEL_NAME = "gemini-2.5-flash-lite"


def _load_gemini_files_metadata() -> list:
    """
    Load the uploaded Gemini files metadata from the JSON file.
    """
    if not os.path.exists(UPLOAD_FILES_METADATA_PATH):
        return []
    with open(UPLOAD_FILES_METADATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


@function_tool
def list_available_textbooks() -> str:
    """
    List all available textbooks that have been uploaded to Gemini.
    Returns a formatted list of textbook names and their topics.
    
    Use this tool when the user asks about what textbooks or chapters are available,
    or when you need to know what content can be queried.
    """
    files_data = _load_gemini_files_metadata()
    
    if not files_data:
        return "No textbooks have been uploaded yet. Please upload textbooks first using the upload script."
    
    textbooks_list = []
    for i, file_info in enumerate(files_data, 1):
        display_name = file_info.get("display_name", "Unknown")
        file_path = file_info.get("path", "Unknown path")
        textbooks_list.append(f"{i}. {display_name}")
    
    return "Available Textbooks:\n" + "\n".join(textbooks_list)


@function_tool
def query_textbook(question: str, textbook_name: str = None) -> str:
    print(f"\n--- Tool Call: query_textbook ---")
    print(f"  Question: {question}")
    print(f"  Textbook Name: {textbook_name}")
    print(f"-----------------------------------\n")
    """
    Query a specific textbook or all textbooks with a question.
    Uses Gemini API to answer questions based on the uploaded textbook content.
    
    Args:
        question: The question to ask about the textbook content.
        textbook_name: Optional. The name of the specific textbook to query. 
                      If not provided, queries all available textbooks.
    
    Returns:
        The answer from the AI based on the textbook content.
    
    Use this tool when the user asks specific questions about:
    - Physical AI and Humanoid Robotics
    - ROS2 (Robot Operating System 2)
    - Any content from the uploaded textbooks
    """
    files_data = _load_gemini_files_metadata()
    
    if not files_data:
        return "No textbooks have been uploaded yet. Cannot answer the question."
    
    # Find the relevant file(s)
    target_files = []
    
    if textbook_name:
        # Search for specific textbook
        for file_info in files_data:
            if textbook_name.lower() in file_info.get("display_name", "").lower():
                target_files.append(file_info)
    else:
        # Use all textbooks
        target_files = files_data
    
    if not target_files:
        available = ", ".join([f.get("display_name", "Unknown") for f in files_data])
        return f"Could not find textbook matching '{textbook_name}'. Available textbooks: {available}"
    
    try:
        # Retrieve the file objects from Gemini
        gemini_files = []
        for file_info in target_files:
            file_name = file_info.get("file_name")
            if file_name:
                gemini_file = client.files.get(name=file_name)
                gemini_files.append(gemini_file)
        
        if not gemini_files:
            return "Could not retrieve the textbook files from Gemini."
        
        # Build the content for the query
        contents = [question] + gemini_files
        
        # Generate the response
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents
        )
        
        return response.text
        
    except Exception as e:
        return f"Error querying textbook: {str(e)}"


@function_tool
def get_textbook_summary(textbook_name: str = None) -> str:
    print(f"\n--- Tool Call: get_textbook_summary ---")
    print(f"  Textbook Name: {textbook_name}")
    print(f"---------------------------------------\n")
    """
    Get a summary of a specific textbook or all textbooks.
    
    Args:
        textbook_name: Optional. The name of the specific textbook to summarize.
                      If not provided, summarizes all available textbooks.
    
    Returns:
        A summary of the textbook content.
    
    Use this tool when the user asks for a summary or overview of the textbook content.
    """
    return query_textbook(
        question="Please provide a brief summary of the main topics covered in this document.",
        textbook_name=textbook_name
    )


# Export all tools
TEXTBOOK_TOOLS = [
    list_available_textbooks,
    query_textbook,
    get_textbook_summary
]

