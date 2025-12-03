# backend/tests/test_agent_print_responses.py
"""
Test script to run agent queries and print responses.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

# Load environment variables
load_dotenv()

from backend.src.agents.textbook_agent import run_agent_async
from backend.src.agents.tools import list_available_textbooks_fn, query_textbook_fn


async def test_agent_queries():
    """Test agent with various queries and print responses."""
    
    print("\n" + "="*80)
    print("AGENT RESPONSE TEST - PRINTING RESULTS")
    print("="*80 + "\n")
    
    # Test queries
    test_queries = [
        "What textbooks are available?",
        "What is Physical AI?",
        "Tell me about ROS2 from the textbook.",
        "Hello! How can you help me?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'─'*80}")
        print(f"Query {i}: {query}")
        print(f"{'─'*80}")
        
        try:
            print("\n⏳ Processing query...\n")
            response = await run_agent_async(query)
            
            print(f"✅ Agent Response:\n")
            print(response)
            print(f"\n{'─'*80}\n")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
            import traceback
            traceback.print_exc()
            print(f"{'─'*80}\n")
    
    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80 + "\n")


def test_tools_directly():
    """Test tools directly and print results."""
    
    print("\n" + "="*80)
    print("TOOLS DIRECT TEST - PRINTING RESULTS")
    print("="*80 + "\n")
    
    # Test list textbooks
    print(f"\n{'─'*80}")
    print("Tool: list_available_textbooks_fn()")
    print(f"{'─'*80}\n")
    
    try:
        result = list_available_textbooks_fn()
        print(f"✅ Result:\n{result}\n")
        print(f"{'─'*80}\n")
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        print(f"{'─'*80}\n")
    
    # Test query textbook
    print(f"\n{'─'*80}")
    print("Tool: query_textbook_fn('What is Physical AI?', 'Introduction')")
    print(f"{'─'*80}\n")
    
    try:
        result = query_textbook_fn(
            question="What is Physical AI?",
            textbook_name="Introduction"
        )
        print(f"✅ Result:\n{result}\n")
        print(f"{'─'*80}\n")
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        print(f"{'─'*80}\n")
    
    print("\n" + "="*80)
    print("TOOLS TEST COMPLETED")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n🚀 Starting Agent Tests...\n")
    
    # Test tools directly first
    test_tools_directly()
    
    # Test agent queries
    print("\n" + "="*80)
    print("NOW TESTING AGENT QUERIES (This may take a moment...)")
    print("="*80 + "\n")
    
    asyncio.run(test_agent_queries())
    
    print("\n✅ All tests completed!\n")

