#!/usr/bin/env python
"""
Simple script to test agent queries and print responses.
Run with: python backend/run_agent_test.py
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Load environment variables
load_dotenv()

print("\n" + "="*80)
print("AGENT QUERY TEST - PRINTING RESPONSES")
print("="*80 + "\n")

# Test 1: List Textbooks Tool
print("\n" + "─"*80)
print("TEST 1: List Available Textbooks Tool")
print("─"*80 + "\n")

try:
    from backend.src.agents.tools import list_available_textbooks_fn
    result = list_available_textbooks_fn()
    print(f"✅ Result:\n{result}\n")
except Exception as e:
    print(f"❌ Error: {e}\n")
    import traceback
    traceback.print_exc()

# Test 2: Agent Query
print("\n" + "─"*80)
print("TEST 2: Agent Query - What textbooks are available?")
print("─"*80 + "\n")

async def test_agent_query():
    try:
        from backend.src.agents.textbook_agent import run_agent_async
        
        query = "What textbooks are available?"
        print(f"Query: {query}\n")
        print("⏳ Processing...\n")
        
        response = await run_agent_async(query)
        print(f"✅ Agent Response:\n{response}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}\n")
        import traceback
        traceback.print_exc()

# Test 3: Another Agent Query
print("\n" + "─"*80)
print("TEST 3: Agent Query - What is Physical AI?")
print("─"*80 + "\n")

async def test_agent_query2():
    try:
        from backend.src.agents.textbook_agent import run_agent_async
        
        query = "What is Physical AI?"
        print(f"Query: {query}\n")
        print("⏳ Processing...\n")
        
        response = await run_agent_async(query)
        print(f"✅ Agent Response:\n{response}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}\n")
        import traceback
        traceback.print_exc()

# Run async tests
if __name__ == "__main__":
    asyncio.run(test_agent_query())
    print("\n" + "="*80 + "\n")
    asyncio.run(test_agent_query2())
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETED")
    print("="*80 + "\n")

