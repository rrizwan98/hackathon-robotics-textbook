# backend/src/agents/textbook_agent.py
"""
Textbook Agent using OpenAI Agent SDK with LiteLLM for Gemini model.

This agent can:
1. Answer questions directly if it has the knowledge
2. Use tools to query textbook content when needed
3. List available textbooks
4. Provide summaries of textbook content
"""

import os
from dotenv import load_dotenv
from agents import Agent, Runner, set_default_openai_client
from agents.extensions.models.litellm_model import LitellmModel
from openai import AsyncOpenAI

import litellm

from backend.src.agents.tools import TEXTBOOK_TOOLS

# Load environment variables
load_dotenv()

# Configure LiteLLM to use Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini/gemini-2.5-flash-lite"

# Set the API key for LiteLLM
litellm.api_key = GEMINI_API_KEY
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY if GEMINI_API_KEY else ""


def create_litellm_client() -> AsyncOpenAI:
    """
    Create an AsyncOpenAI client configured to use LiteLLM proxy.
    """
    # LiteLLM provides OpenAI-compatible API
    return AsyncOpenAI(
        api_key="fake-key",  # LiteLLM doesn't need a real OpenAI key
        base_url="http://0.0.0.0:4000"  # Default LiteLLM proxy URL
    )


# Agent system instructions
SYSTEM_INSTRUCTIONS = """You are a helpful textbook assistant that helps users learn about Physical AI, Humanoid Robotics, and ROS2 (Robot Operating System 2).

Your capabilities:
1. Answer general questions about robotics, AI, and related topics from your own knowledge
2. Query specific textbook content when users ask about topics covered in the uploaded textbooks
3. List available textbooks and chapters
4. Provide summaries of textbook content

Guidelines:
- For general knowledge questions about robotics or AI, respond directly from your knowledge
- For specific questions about textbook content or when users explicitly ask about the textbooks, use the query_textbook tool
- When users ask what textbooks are available, use the list_available_textbooks tool
- When users ask for a summary of a textbook, use the get_textbook_summary tool
- Always be helpful, accurate, and educational in your responses
- IMPORTANT: Keep your responses concise and in one line when possible to avoid quote extension issues
- If you're not sure about something, say so and suggest using the textbook tools for accurate information

Available Topics in Textbooks:
- Introduction to Physical AI & Humanoid Robotics
- Robot Operating System 2 (ROS2)
"""


def create_textbook_agent() -> Agent:
    """
    Create and return the textbook agent configured with LiteLLM and Gemini model.
    """
    agent = Agent(
        name="TextbookAgent",
        instructions=SYSTEM_INSTRUCTIONS,
        model=LitellmModel(model="gemini/gemini-2.5-flash-lite", api_key=os.environ.get("GEMINI_API_KEY")),
        tools=TEXTBOOK_TOOLS
    )
    return agent


async def run_agent_async(query: str) -> str:
    """
    Run the textbook agent with a user query asynchronously.
    
    Args:
        query: The user's question or request
        
    Returns:
        The agent's response as a string
    """
    agent = create_textbook_agent()
    result = await Runner.run(agent, query)
    return result.final_output


def run_agent_sync(query: str) -> str:
    """
    Run the textbook agent with a user query synchronously.
    
    Args:
        query: The user's question or request
        
    Returns:
        The agent's response as a string
    """
    agent = create_textbook_agent()
    result = Runner.run_sync(agent, query)
    return result.final_output


# Main entry point for testing
if __name__ == "__main__":
    import asyncio
    
    # Example queries
    test_queries = [
        "What textbooks are available?",
        "What is ROS2?",
        "Explain the main concepts of Physical AI from the textbook."
    ]
    
    async def main():
        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            print(f"{'='*60}")
            response = await run_agent_async(query)
            print(f"Response: {response}")
    
    asyncio.run(main())

