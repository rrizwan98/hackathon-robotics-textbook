# backend/main.py
import uvicorn
import uuid
from datetime import datetime
from typing import AsyncIterator, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from backend.src.agents.textbook_agent import run_agent_async
from backend.src.chatkit_store import InMemoryStore

# Import ChatKit Server components
try:
    from chatkit.server import ChatKitServer, StreamingResult
    from chatkit.types import (
        ThreadMetadata, 
        UserMessageItem, 
        ThreadItemAddedEvent, 
        ThreadItemDoneEvent, 
        AssistantMessageItem, 
        AssistantMessageContent
    )
    CHATKIT_AVAILABLE = True
except ImportError:
    CHATKIT_AVAILABLE = False
    print("Warning: chatkit package not installed. ChatKit endpoint will not be available.")


app = FastAPI(
    title="Textbook Agent API",
    description="API for querying the Textbook Agent about Physical AI, Humanoid Robotics, and ROS2.",
    version="1.0.0",
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str
    textbook_name: Optional[str] = None


# ============== Original Chat Endpoint ==============

@app.post("/chat")
async def chat_with_agent(request: QueryRequest):
    """
    Chat with the Textbook Agent (simple JSON endpoint).
    """
    try:
        agent_query = request.query
        if request.textbook_name:
            agent_query = f"{request.query} --textbook {request.textbook_name}"
        
        response = await run_agent_async(agent_query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== OpenAI ChatKit Server ==============

if CHATKIT_AVAILABLE:
    
    class TextbookChatKitServer(ChatKitServer):
        """ChatKit Server that integrates with our Textbook Agent."""
        
        def __init__(self, store):
            super().__init__(store=store)

        async def respond(
            self, 
            thread: ThreadMetadata, 
            input_user_message: UserMessageItem | None, 
            context: Any
        ) -> AsyncIterator[Any]:
            """Handle user messages and return response from Textbook Agent."""
            
            # Extract user query from the message
            user_query = "Hello"
            if input_user_message and input_user_message.content:
                for content_block in input_user_message.content:
                    if hasattr(content_block, 'text'):
                        user_query = content_block.text
                        break
            
            # Get textbook name from context (passed via headers)
            textbook_name = None
            if context and isinstance(context, dict):
                textbook_name = context.get('textbook_name')
            
            # Call our Textbook Agent
            try:
                if textbook_name:
                    full_query = f"{user_query} --textbook {textbook_name}"
                else:
                    full_query = user_query
                    
                agent_response = await run_agent_async(full_query)
            except Exception as e:
                agent_response = f"I apologize, but I encountered an error: {str(e)}. Please try again."
            
            # Create assistant message
            msg_id = f"msg_{uuid.uuid4().hex[:12]}"
            content_block = AssistantMessageContent(
                type="output_text", 
                text=agent_response
            )
            assistant_msg = AssistantMessageItem(
                id=msg_id,
                thread_id=thread.id,
                created_at=datetime.now(),
                type="assistant_message",
                content=[content_block]
            )
            
            # Yield events for ChatKit protocol
            yield ThreadItemAddedEvent(type="thread.item.added", item=assistant_msg)
            yield ThreadItemDoneEvent(type="thread.item.done", item=assistant_msg)


    # Initialize ChatKit Store and Server
    chatkit_store = InMemoryStore()
    chatkit_server = TextbookChatKitServer(chatkit_store)


    @app.post("/chatkit")
    async def chatkit_endpoint(request: Request):
        """
        OpenAI ChatKit API endpoint.
        This is the pure ChatKit protocol endpoint that the ChatKit widget connects to.
        """
        # Extract textbook name from custom header
        textbook_name = request.headers.get('X-Textbook-Name', '')
        if textbook_name:
            from urllib.parse import unquote
            textbook_name = unquote(textbook_name)
        
        # Create context with textbook info
        context = {'textbook_name': textbook_name} if textbook_name else None
        
        # Process the ChatKit request
        body = await request.body()
        result = await chatkit_server.process(body, context=context)
        
        if isinstance(result, StreamingResult):
            async def generate():
                async for chunk in result:
                    yield chunk
            
            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache", 
                    "Connection": "keep-alive", 
                    "Access-Control-Allow-Origin": "*"
                }
            )
        else:
            return Response(
                content=result.json,
                media_type="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )


    @app.options("/chatkit")
    async def chatkit_options():
        """Handle CORS preflight for ChatKit endpoint."""
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, X-Textbook-Name",
            }
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
