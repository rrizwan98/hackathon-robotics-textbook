# backend/tests/test_agent_simple_print.py
"""
Simple test cases to test agent and print responses.
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


class TestAgentSimple:
    """Simple tests to verify agent works correctly."""
    
    @pytest.mark.asyncio
    async def test_agent_query_1(self):
        """Test 1: Agent query about available textbooks."""
        query = "What textbooks are available?"
        
        print("\n" + "="*80)
        print("TEST 1: AGENT QUERY - What textbooks are available?")
        print("="*80 + "\n")
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
    async def test_agent_query_2(self):
        """Test 2: Agent query about Physical AI."""
        query = "What is Physical AI?"
        
        print("\n" + "="*80)
        print("TEST 2: AGENT QUERY - What is Physical AI?")
        print("="*80 + "\n")
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

