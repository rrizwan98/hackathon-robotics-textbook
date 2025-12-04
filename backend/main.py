# backend/main.py
import uvicorn
import uuid
import os
from datetime import datetime
from typing import AsyncIterator, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from backend.src.agents.textbook_agent import run_agent_async
from backend.src.postgres_store import PostgreSQLStore
from backend.src.auth_store import (
    AuthStore, 
    UserExistsError, 
    AuthenticationError, 
    ValidationError
)

# Neon PostgreSQL Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_YnMftjp19BIH@ep-hidden-resonance-ahue1b4u-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

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


# Valid textbook sections available for chat
VALID_TEXTBOOK_SECTIONS = [
    "Introduction to Physical AI & Humanoid Robotics",
    "Robot Operating System 2 (ROS2)"
]


# Global stores (initialized on startup)
chatkit_store: PostgreSQLStore | None = None
chatkit_server = None
auth_store: AuthStore | None = None


# Define TextbookChatKitServer early so it can be used in lifespan
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    global chatkit_store, chatkit_server, auth_store
    
    # Startup: Initialize PostgreSQL stores
    print(f"[Startup] Attempting to connect to PostgreSQL database...")
    
    # Initialize Auth store (with retry logic)
    try:
        auth_store = AuthStore(DATABASE_URL)
        print(f"[Startup] Initializing auth store (with retries)...")
        await auth_store.initialize(max_retries=3, retry_delay=2.0)
        print(f"[Startup] Auth store initialized successfully!")
    except Exception as e:
        print(f"[Startup] WARNING: Failed to initialize auth store after retries: {e}")
        print(f"[Startup] Auth features will be unavailable")
        auth_store = None
    
    if CHATKIT_AVAILABLE:
        try:
            chatkit_store = PostgreSQLStore(DATABASE_URL)
            await chatkit_store.initialize()
            print(f"[Startup] PostgreSQL connection established!")
            
            # Initialize ChatKit server with the store
            chatkit_server = TextbookChatKitServer(chatkit_store)
            print("[Startup] ChatKit server initialized with PostgreSQL store for persistent sessions!")
        except Exception as e:
            print(f"[Startup] WARNING: Failed to initialize ChatKit store: {e}")
            print(f"[Startup] ChatKit features will be unavailable")
            chatkit_store = None
            chatkit_server = None
    
    yield
    
    # Shutdown: Close PostgreSQL connections
    if auth_store:
        print("[Shutdown] Closing auth store connection...")
        await auth_store.close()
        
    if chatkit_store:
        print("[Shutdown] Closing ChatKit store connection...")
        await chatkit_store.close()
        print("[Shutdown] PostgreSQL connections closed.")


app = FastAPI(
    title="Textbook Agent API",
    description="API for querying the Textbook Agent about Physical AI, Humanoid Robotics, and ROS2.",
    version="1.0.0",
    lifespan=lifespan
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


# ============== Auth Request/Response Models ==============

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = ""


class LoginRequest(BaseModel):
    email: str
    password: str


class SessionCreateRequest(BaseModel):
    name: Optional[str] = "New Chat"


class SessionRenameRequest(BaseModel):
    name: str


class AuthResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


# ============== Auth Helper Functions ==============

async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Dependency to get the current authenticated user from the Authorization header.
    Returns user info if valid token, raises HTTPException otherwise.
    """
    if not auth_store:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Extract token from "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization format. Use 'Bearer <token>'")
    
    token = parts[1]
    
    user = await auth_store.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user


async def get_optional_user(authorization: Optional[str] = Header(None)):
    """
    Dependency to optionally get the current user.
    Returns user info if valid token, None otherwise.
    """
    if not authorization:
        return None
    
    try:
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        
        token = parts[1]
        return await auth_store.verify_token(token)
    except:
        return None


# ============== Health Check Endpoint ==============

@app.get("/health")
async def health_check():
    """
    Check the health of the API and database connections.
    """
    status = {
        "api": "healthy",
        "auth_store": "unavailable",
        "chatkit_store": "unavailable"
    }
    
    if auth_store and auth_store.is_connected():
        status["auth_store"] = "connected"
    
    if chatkit_store:
        status["chatkit_store"] = "connected"
    
    return status


@app.get("/stats/users")
async def get_user_stats():
    """
    Get statistics about registered users.
    """
    if not auth_store or not auth_store.is_connected():
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    
    try:
        stats = await auth_store.get_user_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


# ============== Authentication Endpoints ==============

@app.post("/auth/register", response_model=AuthResponse)
async def register_user(request: RegisterRequest):
    """
    Register a new user with email and password.
    """
    print(f"[Auth] Registration attempt for email: {request.email}")
    
    if not auth_store:
        print(f"[Auth] ERROR: Auth store not initialized")
        raise HTTPException(status_code=503, detail="Authentication service unavailable. Database connection failed.")
    
    if not auth_store.is_connected():
        print(f"[Auth] ERROR: Auth store not connected to database")
        raise HTTPException(status_code=503, detail="Authentication service disconnected. Please try again later.")
    
    try:
        user = await auth_store.register_user(
            email=request.email,
            password=request.password,
            name=request.name or ""
        )
        print(f"[Auth] User registered successfully: {request.email}")
        return AuthResponse(
            success=True,
            message="User registered successfully",
            data=user
        )
    except ValidationError as e:
        print(f"[Auth] Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except UserExistsError as e:
        print(f"[Auth] User already exists: {request.email}")
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        print(f"[Auth] Registration error: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@app.post("/auth/login", response_model=AuthResponse)
async def login_user(request: LoginRequest):
    """
    Login with email and password. Returns auth token.
    """
    print(f"[Auth] Login attempt for email: {request.email}")
    
    if not auth_store:
        print(f"[Auth] ERROR: Auth store not initialized")
        raise HTTPException(status_code=503, detail="Authentication service unavailable. Database connection failed.")
    
    if not auth_store.is_connected():
        print(f"[Auth] ERROR: Auth store not connected to database")
        raise HTTPException(status_code=503, detail="Authentication service disconnected. Please try again later.")
    
    try:
        result = await auth_store.login_user(
            email=request.email,
            password=request.password
        )
        print(f"[Auth] Login successful for: {request.email}")
        return AuthResponse(
            success=True,
            message="Login successful",
            data=result
        )
    except AuthenticationError as e:
        print(f"[Auth] Authentication failed for: {request.email}")
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        print(f"[Auth] Login error: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@app.post("/auth/logout", response_model=AuthResponse)
async def logout_user(authorization: str = Header(...)):
    """
    Logout and invalidate the auth token.
    """
    try:
        # Extract token from "Bearer <token>" format
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        
        token = parts[1]
        await auth_store.logout_user(token)
        
        return AuthResponse(
            success=True,
            message="Logged out successfully",
            data=None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/auth/me", response_model=AuthResponse)
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """
    Get the current authenticated user's info.
    """
    return AuthResponse(
        success=True,
        message="User info retrieved",
        data=user
    )


# ============== User Session Management Endpoints ==============

@app.get("/sessions", response_model=AuthResponse)
async def get_user_sessions(user: dict = Depends(get_current_user)):
    """
    Get all chat sessions for the authenticated user.
    """
    try:
        sessions = await auth_store.get_user_sessions(user_email=user['email'])
        return AuthResponse(
            success=True,
            message=f"Found {len(sessions)} sessions",
            data={"sessions": sessions}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sessions", response_model=AuthResponse)
async def create_user_session(
    request: SessionCreateRequest,
    user: dict = Depends(get_current_user)
):
    """
    Create a new chat session for the authenticated user.
    """
    try:
        session = await auth_store.create_user_session(
            user_email=user['email'],
            session_name=request.name or "New Chat"
        )
        return AuthResponse(
            success=True,
            message="Session created",
            data=session
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/sessions/{thread_id}", response_model=AuthResponse)
async def rename_user_session(
    thread_id: str,
    request: SessionRenameRequest,
    user: dict = Depends(get_current_user)
):
    """
    Rename a chat session.
    """
    try:
        session = await auth_store.rename_user_session(
            user_email=user['email'],
            thread_id=thread_id,
            new_name=request.name
        )
        return AuthResponse(
            success=True,
            message="Session renamed",
            data=session
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/sessions/{thread_id}", response_model=AuthResponse)
async def delete_user_session(
    thread_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Delete a chat session.
    """
    try:
        await auth_store.delete_user_session(
            user_email=user['email'],
            thread_id=thread_id
        )
        return AuthResponse(
            success=True,
            message="Session deleted",
            data=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== OpenAI ChatKit API Endpoints ==============

if CHATKIT_AVAILABLE:

    @app.post("/chatkit")
    async def chatkit_endpoint(request: Request):
        """
        OpenAI ChatKit API endpoint.
        This is the pure ChatKit protocol endpoint that the ChatKit widget connects to.
        
        Textbook name can be passed via:
        1. X-Textbook-Name header (primary method)
        2. textbook_name query parameter (fallback)
        
        User email for thread filtering can be passed via:
        1. X-User-Email header
        2. user_email query parameter
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
        
        # Get user_email for thread filtering
        user_email = request.headers.get('X-User-Email', '')
        if not user_email:
            user_email = request.query_params.get('user_email', '')
        if user_email:
            user_email = unquote(user_email)
        
        # Log for debugging
        print(f"[ChatKit] Received request - Textbook: '{textbook_name}', User: '{user_email}'")
        
        # Validate textbook_name if provided
        if textbook_name and textbook_name.strip():
            if textbook_name not in VALID_TEXTBOOK_SECTIONS:
                print(f"[ChatKit] WARNING: Invalid textbook_name received: '{textbook_name}'")
        
        # Create context with textbook info and user_email
        context = {
            'textbook_name': textbook_name or '',
            'user_email': user_email or ''
        }
        
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
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, X-Textbook-Name, X-User-Email",
            }
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
