#!/usr/bin/env python
# Test import script

print("Step 1: Importing function_tool...")
from agents import function_tool
print("Step 2: function_tool imported successfully")

print("Step 3: Importing os and json...")
import os
import json
print("Step 4: os and json imported successfully")

print("Step 5: Importing genai...")
try:
    from google import genai
    from google.genai import types
    print("Step 6: genai imported successfully")
except Exception as e:
    print(f"Step 6: genai import failed: {e}")

print("Step 7: Testing function_tool decorator...")

@function_tool
def test_func() -> str:
    """Test function docstring"""
    return "hello"

print(f"Step 8: test_func = {test_func}")

print("Step 9: Importing TEXTBOOK_TOOLS from tools...")
try:
    from backend.src.agents.tools import TEXTBOOK_TOOLS
    print(f"Step 10: TEXTBOOK_TOOLS imported successfully: {TEXTBOOK_TOOLS}")
except Exception as e:
    print(f"Step 10: Import failed with error: {e}")

print("Done!")

