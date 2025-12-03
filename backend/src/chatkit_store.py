"""
In-Memory Store implementation for OpenAI ChatKit Server.
This handles thread and message persistence for the chat widget.
"""

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
    
    async def load_thread_items(
        self, 
        thread_id: str, 
        after: str | None, 
        limit: int, 
        order: str, 
        context: Any
    ) -> Page[ThreadItem]:
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
    
    async def load_threads(
        self, 
        limit: int, 
        after: str | None, 
        order: str, 
        context: Any
    ) -> Page[ThreadMetadata]:
        threads_list = list(self.threads.values())
        threads_list.sort(
            key=lambda t: t.created_at or datetime.min, 
            reverse=(order == "desc")
        )
        
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
    
    async def add_thread_item(
        self, 
        thread_id: str, 
        item: ThreadItem, 
        context: Any
    ) -> None:
        if thread_id not in self.items:
            self.items[thread_id] = {}
        self.items[thread_id][item.id] = item
    
    async def save_item(
        self, 
        thread_id: str, 
        item: ThreadItem, 
        context: Any
    ) -> None:
        if thread_id not in self.items:
            self.items[thread_id] = {}
        self.items[thread_id][item.id] = item
    
    async def load_item(
        self, 
        thread_id: str, 
        item_id: str, 
        context: Any
    ) -> ThreadItem:
        if thread_id not in self.items or item_id not in self.items[thread_id]:
            raise NotFoundError(f"Item {item_id} not found in thread {thread_id}")
        return self.items[thread_id][item_id]
    
    async def delete_thread(self, thread_id: str, context: Any) -> None:
        if thread_id in self.threads:
            del self.threads[thread_id]
        if thread_id in self.items:
            del self.items[thread_id]
    
    async def delete_thread_item(
        self, 
        thread_id: str, 
        item_id: str, 
        context: Any
    ) -> None:
        if thread_id in self.items and item_id in self.items[thread_id]:
            del self.items[thread_id][item_id]

