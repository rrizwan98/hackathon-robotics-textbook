"""
Tests for PostgreSQL Store implementation for ChatKit.
TDD approach - writing tests first before implementation.
"""

import pytest
import pytest_asyncio
import asyncio
import os
from datetime import datetime
from unittest.mock import patch, AsyncMock

# Set test database URL (will be overridden in CI/CD)
# Using the full Neon PostgreSQL URL with correct hostname
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://neondb_owner:npg_YnMftjp19BIH@ep-hidden-resonance-ahue1b4u-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

# Alternative: Load from environment or use direct URL
# The URL provided by user: postgresql://neondb_owner:npg_YnMftjp19BIH@ep-hidden-resonance-ahue1b4u-pooler.c-3.us-east-1.aws.neon.tech/neondb


@pytest.fixture
def database_url():
    """Provide the database URL for tests."""
    return TEST_DATABASE_URL


@pytest_asyncio.fixture
async def postgres_store(database_url):
    """Create and initialize a PostgreSQL store for testing."""
    from backend.src.postgres_store import PostgreSQLStore
    
    store = PostgreSQLStore(database_url)
    await store.initialize()
    
    yield store
    
    # Cleanup: delete test data
    await store.cleanup_test_data()
    await store.close()


class TestPostgreSQLStoreConnection:
    """Test database connection functionality."""
    
    @pytest.mark.asyncio
    async def test_store_initialization(self, database_url):
        """Test that store can connect to PostgreSQL."""
        from backend.src.postgres_store import PostgreSQLStore
        
        store = PostgreSQLStore(database_url)
        await store.initialize()
        
        assert store.is_connected()
        
        await store.close()
    
    @pytest.mark.asyncio
    async def test_tables_created(self, postgres_store):
        """Test that required tables are created on initialization."""
        tables = await postgres_store.get_table_names()
        
        assert "chat_threads" in tables
        assert "chat_items" in tables


class TestThreadOperations:
    """Test thread CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_save_and_load_thread(self, postgres_store):
        """Test saving and loading a thread."""
        from chatkit.types import ThreadMetadata
        
        thread_id = f"test_thread_{datetime.now().timestamp()}"
        thread = ThreadMetadata(
            id=thread_id,
            created_at=datetime.now(),
        )
        
        # Save thread
        await postgres_store.save_thread(thread, context=None)
        
        # Load thread
        loaded_thread = await postgres_store.load_thread(thread_id, context=None)
        
        assert loaded_thread.id == thread_id
    
    @pytest.mark.asyncio
    async def test_load_nonexistent_thread_raises_error(self, postgres_store):
        """Test that loading a non-existent thread raises NotFoundError."""
        from chatkit.store import NotFoundError
        
        with pytest.raises(NotFoundError):
            await postgres_store.load_thread("nonexistent_thread_id", context=None)
    
    @pytest.mark.asyncio
    async def test_delete_thread(self, postgres_store):
        """Test deleting a thread."""
        from chatkit.types import ThreadMetadata
        from chatkit.store import NotFoundError
        
        thread_id = f"test_thread_delete_{datetime.now().timestamp()}"
        thread = ThreadMetadata(
            id=thread_id,
            created_at=datetime.now(),
        )
        
        # Save and then delete
        await postgres_store.save_thread(thread, context=None)
        await postgres_store.delete_thread(thread_id, context=None)
        
        # Should raise error when trying to load
        with pytest.raises(NotFoundError):
            await postgres_store.load_thread(thread_id, context=None)
    
    @pytest.mark.asyncio
    async def test_load_threads_pagination(self, postgres_store):
        """Test loading multiple threads with pagination."""
        from chatkit.types import ThreadMetadata
        
        # Create multiple threads
        thread_ids = []
        for i in range(5):
            thread_id = f"test_thread_pagination_{i}_{datetime.now().timestamp()}"
            thread = ThreadMetadata(
                id=thread_id,
                created_at=datetime.now(),
            )
            await postgres_store.save_thread(thread, context=None)
            thread_ids.append(thread_id)
        
        # Load with limit
        page = await postgres_store.load_threads(
            limit=3, 
            after=None, 
            order="desc", 
            context=None
        )
        
        assert len(page.data) <= 3


class TestItemOperations:
    """Test thread item CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_save_and_load_item(self, postgres_store):
        """Test saving and loading a thread item."""
        from chatkit.types import ThreadMetadata, UserMessageItem, UserMessageTextContent, InferenceOptions
        
        # First create a thread
        thread_id = f"test_thread_items_{datetime.now().timestamp()}"
        thread = ThreadMetadata(
            id=thread_id,
            created_at=datetime.now(),
        )
        await postgres_store.save_thread(thread, context=None)
        
        # Create and save an item
        item_id = f"test_item_{datetime.now().timestamp()}"
        content = UserMessageTextContent(text="Hello, world!")
        item = UserMessageItem(
            id=item_id,
            thread_id=thread_id,
            created_at=datetime.now(),
            type="user_message",
            content=[content],
            inference_options=InferenceOptions()
        )
        
        await postgres_store.save_item(thread_id, item, context=None)
        
        # Load the item
        loaded_item = await postgres_store.load_item(thread_id, item_id, context=None)
        
        assert loaded_item.id == item_id
    
    @pytest.mark.asyncio
    async def test_load_thread_items(self, postgres_store):
        """Test loading all items in a thread."""
        from chatkit.types import ThreadMetadata, UserMessageItem, UserMessageTextContent, InferenceOptions
        
        # Create thread
        thread_id = f"test_thread_load_items_{datetime.now().timestamp()}"
        thread = ThreadMetadata(
            id=thread_id,
            created_at=datetime.now(),
        )
        await postgres_store.save_thread(thread, context=None)
        
        # Add multiple items
        for i in range(3):
            item_id = f"test_item_{i}_{datetime.now().timestamp()}"
            content = UserMessageTextContent(text=f"Message {i}")
            item = UserMessageItem(
                id=item_id,
                thread_id=thread_id,
                created_at=datetime.now(),
                type="user_message",
                content=[content],
                inference_options=InferenceOptions()
            )
            await postgres_store.save_item(thread_id, item, context=None)
        
        # Load items
        page = await postgres_store.load_thread_items(
            thread_id=thread_id,
            after=None,
            limit=10,
            order="asc",
            context=None
        )
        
        assert len(page.data) == 3
    
    @pytest.mark.asyncio
    async def test_delete_thread_item(self, postgres_store):
        """Test deleting a thread item."""
        from chatkit.types import ThreadMetadata, UserMessageItem, UserMessageTextContent, InferenceOptions
        from chatkit.store import NotFoundError
        
        # Create thread
        thread_id = f"test_thread_delete_item_{datetime.now().timestamp()}"
        thread = ThreadMetadata(
            id=thread_id,
            created_at=datetime.now(),
        )
        await postgres_store.save_thread(thread, context=None)
        
        # Create item
        item_id = f"test_item_delete_{datetime.now().timestamp()}"
        content = UserMessageTextContent(text="To be deleted")
        item = UserMessageItem(
            id=item_id,
            thread_id=thread_id,
            created_at=datetime.now(),
            type="user_message",
            content=[content],
            inference_options=InferenceOptions()
        )
        await postgres_store.save_item(thread_id, item, context=None)
        
        # Delete item
        await postgres_store.delete_thread_item(thread_id, item_id, context=None)
        
        # Should raise error when trying to load
        with pytest.raises(NotFoundError):
            await postgres_store.load_item(thread_id, item_id, context=None)


class TestSessionPersistence:
    """Test that chat sessions persist across store instances."""
    
    @pytest.mark.asyncio
    async def test_session_persists_after_reconnect(self, database_url):
        """Test that data persists when store is closed and reopened."""
        from backend.src.postgres_store import PostgreSQLStore
        from chatkit.types import ThreadMetadata, UserMessageItem, UserMessageTextContent, InferenceOptions
        
        thread_id = f"test_persist_{datetime.now().timestamp()}"
        item_id = f"test_persist_item_{datetime.now().timestamp()}"
        
        # First session: create thread and item
        store1 = PostgreSQLStore(database_url)
        await store1.initialize()
        
        thread = ThreadMetadata(
            id=thread_id,
            created_at=datetime.now(),
        )
        await store1.save_thread(thread, context=None)
        
        content = UserMessageTextContent(text="Persistent message")
        item = UserMessageItem(
            id=item_id,
            thread_id=thread_id,
            created_at=datetime.now(),
            type="user_message",
            content=[content],
            inference_options=InferenceOptions()
        )
        await store1.save_item(thread_id, item, context=None)
        
        await store1.close()
        
        # Second session: verify data persists
        store2 = PostgreSQLStore(database_url)
        await store2.initialize()
        
        loaded_thread = await store2.load_thread(thread_id, context=None)
        assert loaded_thread.id == thread_id
        
        loaded_item = await store2.load_item(thread_id, item_id, context=None)
        assert loaded_item.id == item_id
        
        # Cleanup
        await store2.delete_thread(thread_id, context=None)
        await store2.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

