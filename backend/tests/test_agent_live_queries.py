# backend/tests/test_agent_live_queries.py
"""
Live test cases that print agent responses for verification.
Run with: pytest backend/tests/test_agent_live_queries.py -v -s
"""

import os
import sys
import pytest
import asyncio
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

# Load environment variables
load_dotenv()

from backend.src.agents.textbook_agent import run_agent_async
from backend.src.agents.tools import list_available_textbooks_fn, query_textbook_fn


class TestAgentLiveQueries:
    """Live tests that print agent responses."""
    
    def test_list_textbooks_tool(self):
        """Test list textbooks tool and print result."""
        print("\n" + "="*80)
        print("TEST: List Available Textbooks Tool")
        print("="*80 + "\n")
        
        result = list_available_textbooks_fn()
        
        print("Query: list_available_textbooks_fn()")
        print("-"*80)
        print(f"\n✅ Result:\n{result}\n")
        print("="*80 + "\n")
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Available Textbooks" in result
    
    @pytest.mark.asyncio
    async def test_agent_query_available_textbooks(self):
        """Test agent query about available textbooks."""
        print("\n" + "="*80)
        print("TEST: Agent Query - What textbooks are available?")
        print("="*80 + "\n")
        
        query = "What textbooks are available?"
        print(f"Query: {query}\n")
        print("-"*80)
        print("\n⏳ Processing...\n")
        
        try:
            response = await run_agent_async(query)
            
            print(f"✅ Agent Response:\n{response}\n")
            print("="*80 + "\n")
            
            assert response is not None
            assert len(response) > 0
            
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")
            import traceback
            traceback.print_exc()
            print("="*80 + "\n")
            raise
    
    @pytest.mark.asyncio
    async def test_agent_query_physical_ai(self):
        """Test agent query about Physical AI."""
        print("\n" + "="*80)
        print("TEST: Agent Query - What is Physical AI?")
        print("="*80 + "\n")
        
        query = "What is Physical AI?"
        print(f"Query: {query}\n")
        print("-"*80)
        print("\n⏳ Processing...\n")
        
        try:
            response = await run_agent_async(query)
            
            print(f"✅ Agent Response:\n{response}\n")
            print("="*80 + "\n")
            
            assert response is not None
            assert len(response) > 0
            
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")
            import traceback
            traceback.print_exc()
            print("="*80 + "\n")
            raise
    
    @pytest.mark.asyncio
    async def test_agent_query_ros2(self):
        """Test agent query about ROS2 from textbook."""
        print("\n" + "="*80)
        print("TEST: Agent Query - Tell me about ROS2 from the textbook")
        print("="*80 + "\n")
        
        query = "Tell me about ROS2 from the textbook."
        print(f"Query: {query}\n")
        print("-"*80)
        print("\n⏳ Processing...\n")
        
        try:
            response = await run_agent_async(query)
            
            print(f"✅ Agent Response:\n{response}\n")
            print("="*80 + "\n")
            
            assert response is not None
            assert len(response) > 0
            
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")
            import traceback
            traceback.print_exc()
            print("="*80 + "\n")
            raise
    
    def test_query_textbook_tool_direct(self):
        """Test query textbook tool directly."""
        print("\n" + "="*80)
        print("TEST: Query Textbook Tool (Direct)")
        print("="*80 + "\n")
        
        question = "What is Physical AI?"
        textbook_name = "Introduction"
        
        print(f"Question: {question}")
        print(f"Textbook: {textbook_name}\n")
        print("-"*80)
        print("\n⏳ Processing...\n")
        
        try:
            result = query_textbook_fn(question=question, textbook_name=textbook_name)
            
            print(f"✅ Result:\n{result}\n")
            print("="*80 + "\n")
            
            assert isinstance(result, str)
            assert len(result) > 0
            
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")
            import traceback
            traceback.print_exc()
            print("="*80 + "\n")
            # Don't fail if API key is missing
            if "API" not in str(e) and "key" not in str(e).lower():
                raise

