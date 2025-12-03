#!/usr/bin/env python
"""
Test agent queries and print responses.
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

async def test_queries():
    try:
        from backend.src.agents.textbook_agent import run_agent_async
        
        test_queries = [
            "What textbooks are available?",
            "What is Physical AI?",
            "Tell me about ROS2 from the textbook."
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'─'*80}")
            print(f"Query {i}: {query}")
            print(f"{'─'*80}\n")
            print("⏳ Processing...\n")
            
            try:
                response = await run_agent_async(query)
                print(f"✅ Agent Response:\n{response}\n")
                print(f"{'─'*80}\n")
            except Exception as e:
                print(f"❌ Error: {str(e)}\n")
                import traceback
                traceback.print_exc()
                print(f"{'─'*80}\n")
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"❌ Import Error: {str(e)}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_queries())

