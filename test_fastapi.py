import httpx
import asyncio
import json
import time
import subprocess
import os
import sys

async def test_chat_endpoint():
    url = "http://127.0.0.1:8000/chat"
    headers = {"Content-Type": "application/json"}
    payload = {
        "query": "What are the core concepts of Physical AI?",
        "textbook_name": "Physical AI"
    }

    print(f"Sending request to {url} with payload: {payload}")
    try:
        async with httpx.AsyncClient() as client:
            max_retries = 15 # Increased retries
            for i in range(max_retries):
                try:
                    response = await client.post(url, headers=headers, json=payload, timeout=60.0)
                    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx) 
                    
                    response_data = response.json()
                    print(f"Received response: {json.dumps(response_data, indent=2)}")

                    assert "response" in response_data, "Response does not contain 'response' key"
                    assert isinstance(response_data["response"], str), "Response value is not a string"
                    assert len(response_data["response"]) > 0, "Response is empty"
                    print("Test passed: Received a valid response from the agent.")
                    return True
                except httpx.ConnectError:
                    print(f"Attempt {i+1}/{max_retries}: Connection failed. Retrying in 2 seconds...")
                    await asyncio.sleep(2)
            print("Max retries reached. Could not connect to FastAPI server.")
            return False
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

async def main():
    process = None
    try:
        print("Starting FastAPI server...")
        # Explicitly call python -m uvicorn
        command = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
        # Use subprocess.CREATE_NEW_PROCESS_GROUP on Windows to allow termination of the entire process group
        preexec_fn = None
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            creationflags = 0

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=creationflags)
        
        # Give the server a moment to start up
        print("Waiting for FastAPI server to initialize...")
        await asyncio.sleep(7) # Increased sleep time
        
        success = await test_chat_endpoint()
        stdout, stderr = process.communicate(timeout=5)
        print("\n--- FastAPI Server Stdout ---")
        print(stdout)
        print("\n--- FastAPI Server Stderr ---")
        print(stderr)
        
        if not success:
            exit(1) # Exit with error code if test fails

    except Exception as e:
        print(f"An error occurred during server startup or test execution: {e}")
        exit(1)
    finally:
        if process and process.poll() is None:
            print("Stopping FastAPI server...")
            if sys.platform == "win32":
                # On Windows, terminate the process group
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)])
            else:
                process.terminate()
            process.wait(timeout=5)
            if process.poll() is None:
                process.kill()
            print("FastAPI server stopped.")
        # Removed os.remove("test_fastapi.py") from here
        


if __name__ == "__main__":
    asyncio.run(main())
