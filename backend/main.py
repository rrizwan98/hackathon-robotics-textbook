# backend/main.py
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.src.agents.textbook_agent import run_agent_async

app = FastAPI(
    title="Textbook Agent API",
    description="API for querying the Textbook Agent about Physical AI, Humanoid Robotics, and ROS2.",
    version="1.0.0",
)

class QueryRequest(BaseModel):
    query: str
    textbook_name: Optional[str] = None

@app.post("/chat")
async def chat_with_agent(request: QueryRequest):
    """
    Chat with the Textbook Agent.
    """
    try:
        agent_query = request.query
        if request.textbook_name:
            agent_query = f"{request.query} --textbook {request.textbook_name}"
        
        response = await run_agent_async(agent_query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
