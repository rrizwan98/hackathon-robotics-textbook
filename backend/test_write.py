with open("test_output.txt", "w") as f:
    f.write("Step 1: Starting\n")
    try:
        from agents import function_tool
        f.write("Step 2: function_tool imported\n")
    except Exception as e:
        f.write(f"Step 2: Error: {e}\n")
    
    try:
        from google import genai
        f.write("Step 3: genai imported\n")
    except Exception as e:
        f.write(f"Step 3: Error: {e}\n")
    
    try:
        from backend.src.agents.tools import TEXTBOOK_TOOLS
        f.write(f"Step 4: TEXTBOOK_TOOLS imported: {len(TEXTBOOK_TOOLS)} tools\n")
    except Exception as e:
        f.write(f"Step 4: Error: {e}\n")
    
    f.write("Done\n")

