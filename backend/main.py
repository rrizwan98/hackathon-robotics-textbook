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

# Valid textbook sections available for chat
VALID_TEXTBOOK_SECTIONS = [
    "Introduction to Physical AI & Humanoid Robotics",
    "Robot Operating System 2 (ROS2)"
]

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
            
            # Get textbook name from context (passed via query parameter)
            textbook_name = None
            if context and isinstance(context, dict):
                textbook_name = context.get('textbook_name')
            
            # Normalize textbook_name for comparison (trim whitespace)
            normalized_textbook_name = None
            if textbook_name:
                normalized_textbook_name = textbook_name.strip()
            
            # Debug logging
            print(f"[ChatKit] User query: '{user_query}'")
            print(f"[ChatKit] Received textbook_name: '{textbook_name}'")
            print(f"[ChatKit] Normalized textbook_name: '{normalized_textbook_name}'")
            print(f"[ChatKit] Valid sections: {VALID_TEXTBOOK_SECTIONS}")
            
            # Validate textbook_name if provided
            if normalized_textbook_name:
                # Check if textbook_name is in the valid list (exact match after normalization)
                if normalized_textbook_name not in VALID_TEXTBOOK_SECTIONS:
                    print(f"[ChatKit] ERROR: '{normalized_textbook_name}' not in valid sections!")
                    # Return error message for invalid textbook section
                    error_message = (
                        "I apologize, but the website is currently under development. "
                        "Chat functionality is only available for the following sections:\n\n"
                        "1. Introduction to Physical AI & Humanoid Robotics\n"
                        "2. Robot Operating System 2 (ROS2)\n\n"
                        "Please navigate to one of these sections to use the chat feature."
                    )
                    
                    # Create assistant message with error
                    msg_id = f"msg_{uuid.uuid4().hex[:12]}"
                    content_block = AssistantMessageContent(
                        type="output_text", 
                        text=error_message
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
                    return
                else:
                    print(f"[ChatKit] SUCCESS: '{normalized_textbook_name}' is valid!")
            
            # Call our Textbook Agent
            try:
                if normalized_textbook_name:
                    full_query = f"{user_query} --textbook {normalized_textbook_name}"
                else:
                    full_query = user_query
                    
                print(f"[ChatKit] Calling agent with query: '{full_query}'")
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
        
        Textbook name can be passed via:
        1. X-Textbook-Name header (primary method)
        2. textbook_name query parameter (fallback)
        """
        from urllib.parse import unquote
        
        # Try to get textbook name from header first
        textbook_name = request.headers.get('X-Textbook-Name', '')
        
        # Fallback to query parameter
        if not textbook_name:
            textbook_name = request.query_params.get('textbook_name', '')
        
        # Decode URL-encoded name
        if textbook_name:
            textbook_name = unquote(textbook_name)
        
        # Log for debugging
        print(f"[ChatKit] Received request - Textbook: '{textbook_name}'")
        
        # Validate textbook_name if provided
        if textbook_name and textbook_name.strip():
            if textbook_name not in VALID_TEXTBOOK_SECTIONS:
                print(f"[ChatKit] WARNING: Invalid textbook_name received: '{textbook_name}'")
        
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
