#!/usr/bin/env python
"""
Run 2 simple agent tests and print responses.
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

from backend.src.agents.textbook_agent import run_agent_async


async def test_1():
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
        print("✅ TEST 1 PASSED\n")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        print("="*80 + "\n")
        print("❌ TEST 1 FAILED\n")
        raise


async def test_2():
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
        print("✅ TEST 2 PASSED\n")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        print("="*80 + "\n")
        print("❌ TEST 2 FAILED\n")
        raise


async def main():
    """Run both tests."""
    print("\n" + "="*80)
    print("AGENT TEST SUITE - 2 TEST CASES")
    print("="*80)
    
    try:
        await test_1()
        await test_2()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*80 + "\n")
        
    except Exception as e:
        print("\n" + "="*80)
        print(f"❌ TESTS FAILED: {str(e)}")
        print("="*80 + "\n")
        raise


if __name__ == "__main__":
    asyncio.run(main())

