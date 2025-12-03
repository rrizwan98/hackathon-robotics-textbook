#!/usr/bin/env python
# Simple test to print agent responses

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
print("AGENT RESPONSE TEST")
print("="*80 + "\n")

try:
    from backend.src.agents.tools import list_available_textbooks_fn
    print("✅ Tools imported successfully\n")
    
    print("Testing: list_available_textbooks_fn()")
    print("-"*80)
    result = list_available_textbooks_fn()
    print(f"\nResult:\n{result}\n")
    print("="*80 + "\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting Agent Query...")
print("="*80 + "\n")

try:
    from backend.src.agents.textbook_agent import run_agent_async
    
    async def test_query():
        query = "What textbooks are available?"
        print(f"Query: {query}\n")
        print("-"*80)
        
        response = await run_agent_async(query)
        print(f"\nAgent Response:\n{response}\n")
        print("="*80 + "\n")
    
    asyncio.run(test_query())
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test completed!\n")

