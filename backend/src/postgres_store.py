"""
PostgreSQL Store implementation for OpenAI ChatKit Server.
This handles persistent thread and message storage in Neon PostgreSQL.
"""

import json
import asyncio
from typing import Any, List, Optional
from datetime import datetime

import asyncpg
from chatkit.store import Store, NotFoundError
from chatkit.types import (
    ThreadMetadata, 
    ThreadItem, 
    Page, 
    Attachment,
    UserMessageItem,
    AssistantMessageItem,
    UserMessageTextContent,
    AssistantMessageContent,
    InferenceOptions,
)


class PostgreSQLStore(Store[Any]):
    """PostgreSQL implementation of ChatKit Store for persistent chat sessions."""
    
    def __init__(self, database_url: str):
        """
        Initialize the PostgreSQL store.
        
        Args:
            database_url: PostgreSQL connection URL
        """
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None
        self._connected = False
    
    async def initialize(self) -> None:
        """Initialize the database connection pool and create tables."""
        # Parse the database URL and handle SSL
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=1,
            max_size=10,
            ssl='require'
        )
        self._connected = True
        
        # Create tables if they don't exist
        await self._create_tables()
    
    async def _create_tables(self) -> None:
        """Create the required database tables if they don't exist."""
        async with self.pool.acquire() as conn:
            # Create threads table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_threads (
                    id VARCHAR(255) PRIMARY KEY,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    metadata JSONB DEFAULT '{}'::jsonb
                )
            """)
            
            # Create items table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_items (
                    id VARCHAR(255) PRIMARY KEY,
                    thread_id VARCHAR(255) NOT NULL REFERENCES chat_threads(id) ON DELETE CASCADE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    item_type VARCHAR(50) NOT NULL,
                    content JSONB NOT NULL,
                    CONSTRAINT fk_thread FOREIGN KEY (thread_id) REFERENCES chat_threads(id) ON DELETE CASCADE
                )
            """)
            
            # Create index for faster thread item lookups
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_items_thread_id 
                ON chat_items(thread_id, created_at)
            """)
            
            # Create attachments table (optional, for future use)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_attachments (
                    id VARCHAR(255) PRIMARY KEY,
                    thread_id VARCHAR(255),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    data JSONB NOT NULL
                )
            """)
    
    def is_connected(self) -> bool:
        """Check if the store is connected to the database."""
        return self._connected and self.pool is not None
    
    async def get_table_names(self) -> List[str]:
        """Get list of table names in the database."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            return [row['table_name'] for row in rows]
    
    async def close(self) -> None:
        """Close the database connection pool."""
        if self.pool:
            await self.pool.close()
            self._connected = False
    
    async def cleanup_test_data(self) -> None:
        """Clean up test data (threads starting with 'test_')."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                DELETE FROM chat_threads WHERE id LIKE 'test_%'
            """)
    
    # ============== Thread Operations ==============
    
    async def load_thread(self, thread_id: str, context: Any) -> ThreadMetadata:
        """Load a thread by ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM chat_threads WHERE id = $1",
                thread_id
            )
            
            if not row:
                raise NotFoundError(f"Thread {thread_id} not found")
            
            return ThreadMetadata(
                id=row['id'],
                created_at=row['created_at'],
            )
    
    async def save_thread(self, thread: ThreadMetadata, context: Any) -> None:
        """Save or update a thread."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO chat_threads (id, created_at, updated_at)
                VALUES ($1, $2, $2)
                ON CONFLICT (id) DO UPDATE SET updated_at = $2
            """, thread.id, thread.created_at or datetime.now())
    
    async def delete_thread(self, thread_id: str, context: Any) -> None:
        """Delete a thread and all its items."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM chat_threads WHERE id = $1",
                thread_id
            )
    
    async def load_threads(
        self, 
        limit: int, 
        after: str | None, 
        order: str, 
        context: Any
    ) -> Page[ThreadMetadata]:
        """Load multiple threads with pagination."""
        async with self.pool.acquire() as conn:
            order_dir = "DESC" if order == "desc" else "ASC"
            
            if after:
                # Get the created_at of the 'after' thread
                after_row = await conn.fetchrow(
                    "SELECT created_at FROM chat_threads WHERE id = $1",
                    after
                )
                if after_row:
                    if order == "desc":
                        rows = await conn.fetch(f"""
                            SELECT * FROM chat_threads 
                            WHERE created_at < $1
                            ORDER BY created_at {order_dir}
                            LIMIT $2
                        """, after_row['created_at'], limit + 1)
                    else:
                        rows = await conn.fetch(f"""
                            SELECT * FROM chat_threads 
                            WHERE created_at > $1
                            ORDER BY created_at {order_dir}
                            LIMIT $2
                        """, after_row['created_at'], limit + 1)
                else:
                    rows = []
            else:
                rows = await conn.fetch(f"""
                    SELECT * FROM chat_threads 
                    ORDER BY created_at {order_dir}
                    LIMIT $1
                """, limit + 1)
            
            has_more = len(rows) > limit
            threads = [
                ThreadMetadata(
                    id=row['id'],
                    created_at=row['created_at'],
                )
                for row in rows[:limit]
            ]
            
            return Page(data=threads, has_more=has_more)
    
    # ============== Item Operations ==============
    
    def _serialize_item(self, item: ThreadItem) -> dict:
        """Serialize a ThreadItem to JSON-compatible dict."""
        content_list = []
        if hasattr(item, 'content') and item.content:
            for c in item.content:
                if hasattr(c, 'text'):
                    content_list.append({
                        'type': getattr(c, 'type', 'text'),
                        'text': c.text
                    })
                else:
                    content_list.append({'type': getattr(c, 'type', 'unknown')})
        
        return {
            'id': item.id,
            'thread_id': item.thread_id,
            'created_at': item.created_at.isoformat() if item.created_at else None,
            'type': item.type,
            'content': content_list
        }
    
    def _deserialize_item(self, row: dict) -> ThreadItem:
        """Deserialize a database row to a ThreadItem."""
        item_type = row['item_type']
        content_data = row['content'] if isinstance(row['content'], list) else json.loads(row['content']) if row['content'] else []
        
        if item_type == 'user_message':
            content_list = []
            for c in content_data:
                content_list.append(UserMessageTextContent(
                    text=c.get('text', '')
                ))
            
            return UserMessageItem(
                id=row['id'],
                thread_id=row['thread_id'],
                created_at=row['created_at'],
                type=item_type,
                content=content_list,
                inference_options=InferenceOptions()
            )
        else:  # assistant_message
            content_list = []
            for c in content_data:
                content_list.append(AssistantMessageContent(
                    text=c.get('text', '')
                ))
            
            return AssistantMessageItem(
                id=row['id'],
                thread_id=row['thread_id'],
                created_at=row['created_at'],
                type=item_type,
                content=content_list
            )
    
    async def save_item(
        self, 
        thread_id: str, 
        item: ThreadItem, 
        context: Any
    ) -> None:
        """Save or update a thread item."""
        serialized = self._serialize_item(item)
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO chat_items (id, thread_id, created_at, item_type, content)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (id) DO UPDATE SET content = $5
            """, 
            item.id, 
            thread_id, 
            item.created_at or datetime.now(),
            item.type,
            json.dumps(serialized['content'])
            )
    
    async def add_thread_item(
        self, 
        thread_id: str, 
        item: ThreadItem, 
        context: Any
    ) -> None:
        """Add a new item to a thread (alias for save_item)."""
        await self.save_item(thread_id, item, context)
    
    async def load_item(
        self, 
        thread_id: str, 
        item_id: str, 
        context: Any
    ) -> ThreadItem:
        """Load a specific item from a thread."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM chat_items 
                WHERE id = $1 AND thread_id = $2
            """, item_id, thread_id)
            
            if not row:
                raise NotFoundError(f"Item {item_id} not found in thread {thread_id}")
            
            return self._deserialize_item(row)
    
    async def load_thread_items(
        self, 
        thread_id: str, 
        after: str | None, 
        limit: int, 
        order: str, 
        context: Any
    ) -> Page[ThreadItem]:
        """Load items from a thread with pagination."""
        async with self.pool.acquire() as conn:
            order_dir = "DESC" if order == "desc" else "ASC"
            
            if after:
                # Get the created_at of the 'after' item
                after_row = await conn.fetchrow(
                    "SELECT created_at FROM chat_items WHERE id = $1",
                    after
                )
                if after_row:
                    if order == "desc":
                        rows = await conn.fetch(f"""
                            SELECT * FROM chat_items 
                            WHERE thread_id = $1 AND created_at < $2
                            ORDER BY created_at {order_dir}
                            LIMIT $3
                        """, thread_id, after_row['created_at'], limit + 1)
                    else:
                        rows = await conn.fetch(f"""
                            SELECT * FROM chat_items 
                            WHERE thread_id = $1 AND created_at > $2
                            ORDER BY created_at {order_dir}
                            LIMIT $3
                        """, thread_id, after_row['created_at'], limit + 1)
                else:
                    rows = []
            else:
                rows = await conn.fetch(f"""
                    SELECT * FROM chat_items 
                    WHERE thread_id = $1
                    ORDER BY created_at {order_dir}
                    LIMIT $2
                """, thread_id, limit + 1)
            
            has_more = len(rows) > limit
            items = [self._deserialize_item(row) for row in rows[:limit]]
            
            return Page(data=items, has_more=has_more)
    
    async def delete_thread_item(
        self, 
        thread_id: str, 
        item_id: str, 
        context: Any
    ) -> None:
        """Delete a specific item from a thread."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                DELETE FROM chat_items 
                WHERE id = $1 AND thread_id = $2
            """, item_id, thread_id)
    
    # ============== Attachment Operations ==============
    
    async def save_attachment(self, attachment: Attachment, context: Any) -> None:
        """Save an attachment."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO chat_attachments (id, data)
                VALUES ($1, $2)
                ON CONFLICT (id) DO UPDATE SET data = $2
            """, attachment.id, json.dumps({'id': attachment.id}))
    
    async def load_attachment(self, attachment_id: str, context: Any) -> Attachment:
        """Load an attachment by ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM chat_attachments WHERE id = $1",
                attachment_id
            )
            
            if not row:
                raise NotFoundError(f"Attachment {attachment_id} not found")
            
            # Return a minimal Attachment object
            return Attachment(id=row['id'])
    
    async def delete_attachment(self, attachment_id: str, context: Any) -> None:
        """Delete an attachment."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM chat_attachments WHERE id = $1",
                attachment_id
            )

