# 🤖 OpenAI ChatKit Implementation Prompt

## Copy-Paste Prompt for Any LLM:

---

**Meri existing website/app mein OpenAI ChatKit integrate karna hai. Ye Pure ChatKit implementation honi chahiye (no custom React UI). Neeche complete reference code diya gaya hai - isko follow karte huye meri website mein implement karo.**

---

## 📋 REQUIREMENTS:

1. **Frontend**: Next.js (App Router) with TypeScript
2. **Backend**: FastAPI (Python) with ChatKit Server
3. **Features**: 
   - Bottom-right corner mein floating chat button
   - Click karne par ChatKit widget open ho
   - Backend se streaming responses
   - Pure OpenAI ChatKit theme (customizable)

---

## 🏗️ ARCHITECTURE:

```
User clicks chat → ChatKit Widget → /api/chatkit (Next.js Proxy) → FastAPI /chatkit endpoint → Agent Response
```

---

## 📁 REQUIRED FILES:

### FILE 1: `package.json` (Frontend Dependencies)

```json
{
  "name": "my-chatkit-app",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "@openai/chatkit": "^1.1.0",
    "@openai/chatkit-react": "^1.3.0",
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "typescript": "^5"
  }
}
```

---

### FILE 2: `components/ChatWidget.tsx` (Pure ChatKit Widget)

```tsx
'use client';

import { useState } from 'react';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import type { ChatKitOptions } from '@openai/chatkit-react';

// ChatKit Configuration - Customize as needed
const chatKitOptions: ChatKitOptions = {
  api: {
    url: '/api/chatkit',
    domainKey: 'dev',
  },
  theme: {
    colorScheme: 'light',
    radius: 'round',
    density: 'normal',
    color: {
      grayscale: { hue: 123, tint: 0, shade: -2 },
      accent: { primary: '#1a1919', level: 1 },
      surface: { background: '#bec2cb', foreground: '#ffffff' }
    },
    typography: {
      baseSize: 16,
      fontFamily: '"OpenAI Sans", system-ui, sans-serif',
      fontFamilyMono: 'ui-monospace, monospace',
      fontSources: [
        {
          family: 'OpenAI Sans',
          src: 'https://cdn.openai.com/common/fonts/openai-sans/v2/OpenAISans-Regular.woff2',
          weight: 400,
          style: 'normal',
          display: 'swap'
        }
      ]
    }
  },
  composer: {
    placeholder: 'Type your message...',
    attachments: { enabled: false },
  },
  startScreen: {
    greeting: '',
    prompts: [],
  },
};

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const chatKit = useChatKit(chatKitOptions);

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          style={{
            position: 'fixed',
            bottom: '16px',
            right: '16px',
            zIndex: 9999,
            backgroundColor: '#2563eb',
            color: 'white',
            borderRadius: '50%',
            padding: '16px',
            border: 'none',
            cursor: 'pointer',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          }}
          aria-label="Open chat"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </button>
      )}

      {/* ChatKit Widget Container */}
      {isOpen && (
        <div style={{
          position: 'fixed',
          bottom: '16px',
          right: '16px',
          zIndex: 9999,
          width: '384px',
          height: '600px',
          borderRadius: '16px',
          overflow: 'hidden',
          boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)',
        }}>
          {/* Close Button */}
          <button
            onClick={() => setIsOpen(false)}
            style={{
              position: 'absolute',
              top: '8px',
              right: '8px',
              zIndex: 10,
              backgroundColor: '#374151',
              color: 'white',
              borderRadius: '50%',
              padding: '8px',
              border: 'none',
              cursor: 'pointer',
            }}
            aria-label="Close chat"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          
          {/* Pure ChatKit Component */}
          <ChatKit
            control={chatKit.control}
            style={{ height: '100%', width: '100%', border: 'none', borderRadius: '16px' }}
          />
        </div>
      )}
    </>
  );
}
```

---

### FILE 3: `app/api/chatkit/route.ts` (API Proxy Route)

```typescript
import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL || 'http://localhost:8000';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
};

export async function OPTIONS() {
  return new NextResponse(null, { status: 200, headers: corsHeaders });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.text();
    
    const response = await fetch(`${FASTAPI_BASE_URL}/chatkit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: body,
    });

    if (response.headers.get('content-type')?.includes('text/event-stream')) {
      return new Response(response.body, {
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
          ...corsHeaders,
        },
      });
    }

    const data = await response.text();
    return new NextResponse(data, {
      status: response.status,
      headers: { 'Content-Type': 'application/json', ...corsHeaders },
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to connect to chat backend', details: String(error) },
      { status: 500, headers: corsHeaders }
    );
  }
}
```

---

### FILE 4: `app/layout.tsx` (Add ChatKit Script)

```tsx
import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";

export const metadata: Metadata = {
  title: "My App",
  description: "My app with ChatKit",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <Script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          strategy="beforeInteractive"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

---

### FILE 5: `app/page.tsx` (Import ChatWidget)

```tsx
'use client';

import ChatWidget from '../components/ChatWidget';

export default function HomePage() {
  return (
    <div>
      {/* Your existing page content here */}
      <h1>My Website</h1>
      
      {/* ChatKit Widget - add this at the end */}
      <ChatWidget />
    </div>
  );
}
```

---

### FILE 6: `.env.local` (Environment Variables)

```env
FASTAPI_BASE_URL=http://localhost:8000
```

---

## 🐍 BACKEND FILES (FastAPI + Python):

### FILE 7: `requirements.txt` or `pyproject.toml` dependencies

```
fastapi
uvicorn
openai-agents
chatkit
python-dotenv
```

---

### FILE 8: `src/main.py` (FastAPI Entry Point)

```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from src.chatkit_store import InMemoryStore
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.types import ThreadMetadata, UserMessageItem, ThreadItemAddedEvent, ThreadItemDoneEvent, AssistantMessageItem, AssistantMessageContent
from typing import AsyncIterator, Any
from datetime import datetime
import uuid

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MyChatKitServer(ChatKitServer):
    def __init__(self, store):
        super().__init__(store=store)

    async def respond(
        self, 
        thread: ThreadMetadata, 
        input_user_message: UserMessageItem | None, 
        context: Any
    ) -> AsyncIterator[Any]:
        """Handle user messages and return response."""
        
        # Extract user query
        user_query = "Hello"
        if input_user_message and input_user_message.content:
            for content_block in input_user_message.content:
                if hasattr(content_block, 'text'):
                    user_query = content_block.text
                    break

        # TODO: Replace this with your actual agent/LLM call
        # Example: agent_response = await your_agent.chat(user_query)
        agent_response = f"You said: {user_query}"  # Replace with real response
        
        # Create assistant message
        msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        content_block = AssistantMessageContent(type="output_text", text=agent_response)
        assistant_msg = AssistantMessageItem(
            id=msg_id,
            thread_id=thread.id,
            created_at=datetime.now(),
            type="assistant_message",
            content=[content_block]
        )
        
        yield ThreadItemAddedEvent(type="thread.item.added", item=assistant_msg)
        yield ThreadItemDoneEvent(type="thread.item.done", item=assistant_msg)


# Initialize
store = InMemoryStore()
chatkit_server = MyChatKitServer(store)


@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    """ChatKit API endpoint."""
    body = await request.body()
    result = await chatkit_server.process(body, context=None)
    
    if isinstance(result, StreamingResult):
        async def generate():
            async for chunk in result:
                yield chunk
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "Access-Control-Allow-Origin": "*"}
        )
    else:
        return Response(
            content=result.json,
            media_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
```

---

### FILE 9: `src/chatkit_store.py` (In-Memory Store)

```python
from typing import Any
from datetime import datetime
from chatkit.store import Store, NotFoundError
from chatkit.types import ThreadMetadata, ThreadItem, Page, Attachment


class InMemoryStore(Store[Any]):
    """Simple in-memory implementation of ChatKit Store."""
    
    def __init__(self):
        self.threads: dict[str, ThreadMetadata] = {}
        self.items: dict[str, dict[str, ThreadItem]] = {}
        self.attachments: dict[str, Attachment] = {}
    
    async def load_thread(self, thread_id: str, context: Any) -> ThreadMetadata:
        if thread_id not in self.threads:
            raise NotFoundError(f"Thread {thread_id} not found")
        return self.threads[thread_id]
    
    async def save_thread(self, thread: ThreadMetadata, context: Any) -> None:
        self.threads[thread.id] = thread
        if thread.id not in self.items:
            self.items[thread.id] = {}
    
    async def load_thread_items(self, thread_id: str, after: str | None, limit: int, order: str, context: Any) -> Page[ThreadItem]:
        if thread_id not in self.items:
            return Page(data=[], has_more=False)
        
        items_list = list(self.items[thread_id].values())
        if order == "desc":
            items_list = items_list[::-1]
        
        if after:
            after_idx = -1
            for i, item in enumerate(items_list):
                if item.id == after:
                    after_idx = i
                    break
            if after_idx >= 0:
                items_list = items_list[after_idx + 1:]
        
        has_more = len(items_list) > limit
        return Page(data=items_list[:limit], has_more=has_more)
    
    async def save_attachment(self, attachment: Attachment, context: Any) -> None:
        self.attachments[attachment.id] = attachment
    
    async def load_attachment(self, attachment_id: str, context: Any) -> Attachment:
        if attachment_id not in self.attachments:
            raise NotFoundError(f"Attachment {attachment_id} not found")
        return self.attachments[attachment_id]
    
    async def delete_attachment(self, attachment_id: str, context: Any) -> None:
        if attachment_id in self.attachments:
            del self.attachments[attachment_id]
    
    async def load_threads(self, limit: int, after: str | None, order: str, context: Any) -> Page[ThreadMetadata]:
        threads_list = list(self.threads.values())
        threads_list.sort(key=lambda t: t.created_at or datetime.min, reverse=(order == "desc"))
        
        if after:
            after_idx = -1
            for i, thread in enumerate(threads_list):
                if thread.id == after:
                    after_idx = i
                    break
            if after_idx >= 0:
                threads_list = threads_list[after_idx + 1:]
        
        has_more = len(threads_list) > limit
        return Page(data=threads_list[:limit], has_more=has_more)
    
    async def add_thread_item(self, thread_id: str, item: ThreadItem, context: Any) -> None:
        if thread_id not in self.items:
            self.items[thread_id] = {}
        self.items[thread_id][item.id] = item
    
    async def save_item(self, thread_id: str, item: ThreadItem, context: Any) -> None:
        if thread_id not in self.items:
            self.items[thread_id] = {}
        self.items[thread_id][item.id] = item
    
    async def load_item(self, thread_id: str, item_id: str, context: Any) -> ThreadItem:
        if thread_id not in self.items or item_id not in self.items[thread_id]:
            raise NotFoundError(f"Item {item_id} not found in thread {thread_id}")
        return self.items[thread_id][item_id]
    
    async def delete_thread(self, thread_id: str, context: Any) -> None:
        if thread_id in self.threads:
            del self.threads[thread_id]
        if thread_id in self.items:
            del self.items[thread_id]
    
    async def delete_thread_item(self, thread_id: str, item_id: str, context: Any) -> None:
        if thread_id in self.items and item_id in self.items[thread_id]:
            del self.items[thread_id][item_id]
```

---

## 🚀 SETUP COMMANDS:

### Frontend Setup:
```bash
cd your-frontend-folder
npm install
npm run dev
# Runs on http://localhost:3000
```

### Backend Setup:
```bash
cd your-backend-folder
pip install fastapi uvicorn chatkit python-dotenv
# OR with uv:
uv sync

# Run server:
uvicorn src.main:app --reload --port 8000
# Runs on http://localhost:8000
```

---

## ✅ VERIFICATION:

1. Backend running on `http://localhost:8000`
2. Frontend running on `http://localhost:3000`
3. Open frontend → Click chat button (bottom-right)
4. Send message → Should get response

---

## 🎨 THEME CUSTOMIZATION:

ChatKitOptions mein ye customize kar sakte ho:

```typescript
theme: {
  colorScheme: 'dark',  // 'light' | 'dark'
  radius: 'pill',       // 'sharp' | 'round' | 'pill'
  density: 'compact',   // 'compact' | 'normal' | 'relaxed'
  color: {
    accent: { primary: '#your-color' }
  }
}
```

---

**Ab in files ko meri existing website mein integrate kar do. Meri website [DESCRIBE YOUR WEBSITE TECH STACK HERE] hai.**

---

