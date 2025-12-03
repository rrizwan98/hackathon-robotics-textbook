# backend/src/agents/__init__.py
"""
Agents module for the textbook application.
Contains the textbook agent and its tools.
"""

from backend.src.agents.textbook_agent import (
    create_textbook_agent,
    run_agent_async,
    run_agent_sync,
    SYSTEM_INSTRUCTIONS,
    MODEL_NAME
)

from backend.src.agents.tools import (
    list_available_textbooks,
    query_textbook,
    get_textbook_summary,
    TEXTBOOK_TOOLS
)

__all__ = [
    "create_textbook_agent",
    "run_agent_async", 
    "run_agent_sync",
    "SYSTEM_INSTRUCTIONS",
    "MODEL_NAME",
    "list_available_textbooks",
    "query_textbook",
    "get_textbook_summary",
    "TEXTBOOK_TOOLS"
]

