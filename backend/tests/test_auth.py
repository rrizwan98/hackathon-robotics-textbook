"""
Tests for User Authentication System.
TDD approach - writing tests first before implementation.

Tests cover:
1. User registration
2. User login with email/password
3. Session management per user email
4. Loading user's chat sessions
"""

import pytest
import pytest_asyncio
import asyncio
import os
from datetime import datetime
from unittest.mock import patch, AsyncMock

# Set test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://neondb_owner:npg_YnMftjp19BIH@ep-hidden-resonance-ahue1b4u-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
)


@pytest.fixture
def database_url():
    """Provide the database URL for tests."""
    return TEST_DATABASE_URL


@pytest_asyncio.fixture
async def auth_store(database_url):
    """Create and initialize an AuthStore for testing."""
    from backend.src.auth_store import AuthStore
    
    store = AuthStore(database_url)
    await store.initialize()
    
    yield store
    
    # Cleanup test data
    await store.cleanup_test_data()
    await store.close()


class TestUserRegistration:
    """Test user registration functionality."""
    
    @pytest.mark.asyncio
    async def test_register_new_user(self, auth_store):
        """Test registering a new user with email and password."""
        test_email = f"test_user_{datetime.now().timestamp()}@example.com"
        test_password = "securepassword123"
        
        # Register user
        user = await auth_store.register_user(
            email=test_email,
            password=test_password,
            name="Test User"
        )
        
        assert user is not None
        assert user['email'] == test_email
        assert user['name'] == "Test User"
        assert 'id' in user
        assert 'password_hash' not in user  # Should not expose password hash
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email_raises_error(self, auth_store):
        """Test that registering with duplicate email raises error."""
        from backend.src.auth_store import UserExistsError
        
        test_email = f"test_duplicate_{datetime.now().timestamp()}@example.com"
        test_password = "securepassword123"
        
        # Register first user
        await auth_store.register_user(
            email=test_email,
            password=test_password,
            name="First User"
        )
        
        # Attempt to register second user with same email
        with pytest.raises(UserExistsError):
            await auth_store.register_user(
                email=test_email,
                password=test_password,
                name="Second User"
            )
    
    @pytest.mark.asyncio
    async def test_register_validates_email_format(self, auth_store):
        """Test that invalid email format raises error."""
        from backend.src.auth_store import ValidationError
        
        with pytest.raises(ValidationError):
            await auth_store.register_user(
                email="invalid-email",
                password="securepassword123",
                name="Test User"
            )
    
    @pytest.mark.asyncio
    async def test_register_validates_password_length(self, auth_store):
        """Test that short password raises error."""
        from backend.src.auth_store import ValidationError
        
        test_email = f"test_password_{datetime.now().timestamp()}@example.com"
        
        with pytest.raises(ValidationError):
            await auth_store.register_user(
                email=test_email,
                password="short",  # Too short
                name="Test User"
            )


class TestUserLogin:
    """Test user login functionality."""
    
    @pytest.mark.asyncio
    async def test_login_with_valid_credentials(self, auth_store):
        """Test successful login with valid email and password."""
        test_email = f"test_login_{datetime.now().timestamp()}@example.com"
        test_password = "securepassword123"
        
        # Register user first
        await auth_store.register_user(
            email=test_email,
            password=test_password,
            name="Login Test User"
        )
        
        # Login
        result = await auth_store.login_user(
            email=test_email,
            password=test_password
        )
        
        assert result is not None
        assert 'user' in result
        assert 'token' in result
        assert result['user']['email'] == test_email
    
    @pytest.mark.asyncio
    async def test_login_with_invalid_password_fails(self, auth_store):
        """Test that login with wrong password fails."""
        from backend.src.auth_store import AuthenticationError
        
        test_email = f"test_invalid_pwd_{datetime.now().timestamp()}@example.com"
        test_password = "securepassword123"
        
        # Register user first
        await auth_store.register_user(
            email=test_email,
            password=test_password,
            name="Test User"
        )
        
        # Attempt login with wrong password
        with pytest.raises(AuthenticationError):
            await auth_store.login_user(
                email=test_email,
                password="wrongpassword"
            )
    
    @pytest.mark.asyncio
    async def test_login_with_nonexistent_email_fails(self, auth_store):
        """Test that login with non-existent email fails."""
        from backend.src.auth_store import AuthenticationError
        
        with pytest.raises(AuthenticationError):
            await auth_store.login_user(
                email="nonexistent@example.com",
                password="anypassword"
            )
    
    @pytest.mark.asyncio
    async def test_verify_token(self, auth_store):
        """Test token verification after login."""
        test_email = f"test_token_{datetime.now().timestamp()}@example.com"
        test_password = "securepassword123"
        
        # Register and login
        await auth_store.register_user(
            email=test_email,
            password=test_password,
            name="Token Test User"
        )
        
        result = await auth_store.login_user(
            email=test_email,
            password=test_password
        )
        
        # Verify token
        user = await auth_store.verify_token(result['token'])
        
        assert user is not None
        assert user['email'] == test_email


class TestUserSessionManagement:
    """Test user session (chat thread) management by email."""
    
    @pytest.mark.asyncio
    async def test_create_session_for_user(self, auth_store):
        """Test creating a chat session associated with a user's email."""
        test_email = f"test_session_{datetime.now().timestamp()}@example.com"
        test_password = "securepassword123"
        
        # Register user
        user = await auth_store.register_user(
            email=test_email,
            password=test_password,
            name="Session Test User"
        )
        
        # Create a chat session for this user
        session = await auth_store.create_user_session(
            user_email=test_email,
            session_name="Test Chat Session"
        )
        
        assert session is not None
        assert session['user_email'] == test_email
        assert session['name'] == "Test Chat Session"
        assert 'thread_id' in session
    
    @pytest.mark.asyncio
    async def test_get_user_sessions(self, auth_store):
        """Test retrieving all chat sessions for a user by email."""
        test_email = f"test_get_sessions_{datetime.now().timestamp()}@example.com"
        test_password = "securepassword123"
        
        # Register user
        await auth_store.register_user(
            email=test_email,
            password=test_password,
            name="Sessions Test User"
        )
        
        # Create multiple sessions
        await auth_store.create_user_session(
            user_email=test_email,
            session_name="Session 1"
        )
        await auth_store.create_user_session(
            user_email=test_email,
            session_name="Session 2"
        )
        await auth_store.create_user_session(
            user_email=test_email,
            session_name="Session 3"
        )
        
        # Get all sessions for user
        sessions = await auth_store.get_user_sessions(user_email=test_email)
        
        assert len(sessions) == 3
        assert all(s['user_email'] == test_email for s in sessions)
    
    @pytest.mark.asyncio
    async def test_sessions_persist_after_logout(self, auth_store):
        """Test that user's sessions persist after logout and are available on re-login."""
        test_email = f"test_persist_{datetime.now().timestamp()}@example.com"
        test_password = "securepassword123"
        
        # Register and login
        await auth_store.register_user(
            email=test_email,
            password=test_password,
            name="Persist Test User"
        )
        
        login_result = await auth_store.login_user(
            email=test_email,
            password=test_password
        )
        
        # Create sessions
        await auth_store.create_user_session(
            user_email=test_email,
            session_name="Persistent Session 1"
        )
        await auth_store.create_user_session(
            user_email=test_email,
            session_name="Persistent Session 2"
        )
        
        # Logout (invalidate token)
        await auth_store.logout_user(login_result['token'])
        
        # Login again
        new_login = await auth_store.login_user(
            email=test_email,
            password=test_password
        )
        
        # Sessions should still be there
        sessions = await auth_store.get_user_sessions(user_email=test_email)
        
        assert len(sessions) == 2
    
    @pytest.mark.asyncio
    async def test_delete_user_session(self, auth_store):
        """Test deleting a specific chat session."""
        test_email = f"test_delete_session_{datetime.now().timestamp()}@example.com"
        test_password = "securepassword123"
        
        # Register user
        await auth_store.register_user(
            email=test_email,
            password=test_password,
            name="Delete Test User"
        )
        
        # Create session
        session = await auth_store.create_user_session(
            user_email=test_email,
            session_name="To Be Deleted"
        )
        
        # Delete session
        await auth_store.delete_user_session(
            user_email=test_email,
            thread_id=session['thread_id']
        )
        
        # Sessions should be empty
        sessions = await auth_store.get_user_sessions(user_email=test_email)
        assert len(sessions) == 0
    
    @pytest.mark.asyncio
    async def test_rename_user_session(self, auth_store):
        """Test renaming a chat session."""
        test_email = f"test_rename_{datetime.now().timestamp()}@example.com"
        test_password = "securepassword123"
        
        # Register user
        await auth_store.register_user(
            email=test_email,
            password=test_password,
            name="Rename Test User"
        )
        
        # Create session
        session = await auth_store.create_user_session(
            user_email=test_email,
            session_name="Original Name"
        )
        
        # Rename session
        updated = await auth_store.rename_user_session(
            user_email=test_email,
            thread_id=session['thread_id'],
            new_name="New Name"
        )
        
        assert updated['name'] == "New Name"


class TestSessionIsolation:
    """Test that sessions are properly isolated between users."""
    
    @pytest.mark.asyncio
    async def test_user_cannot_access_other_user_sessions(self, auth_store):
        """Test that users can only access their own sessions."""
        user1_email = f"test_user1_{datetime.now().timestamp()}@example.com"
        user2_email = f"test_user2_{datetime.now().timestamp()}@example.com"
        test_password = "securepassword123"
        
        # Register both users
        await auth_store.register_user(
            email=user1_email,
            password=test_password,
            name="User 1"
        )
        await auth_store.register_user(
            email=user2_email,
            password=test_password,
            name="User 2"
        )
        
        # Create sessions for each user
        await auth_store.create_user_session(
            user_email=user1_email,
            session_name="User1 Session"
        )
        await auth_store.create_user_session(
            user_email=user2_email,
            session_name="User2 Session"
        )
        
        # Get sessions for user1
        user1_sessions = await auth_store.get_user_sessions(user_email=user1_email)
        
        # Get sessions for user2
        user2_sessions = await auth_store.get_user_sessions(user_email=user2_email)
        
        # Each user should only see their own sessions
        assert len(user1_sessions) == 1
        assert user1_sessions[0]['name'] == "User1 Session"
        
        assert len(user2_sessions) == 1
        assert user2_sessions[0]['name'] == "User2 Session"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

