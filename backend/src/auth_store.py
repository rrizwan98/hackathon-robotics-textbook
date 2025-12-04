"""
Authentication Store implementation for user management.
Handles user registration, login, and session management per email.
"""

import json
import uuid
import hashlib
import secrets
import re
from typing import Any, List, Optional, Dict
from datetime import datetime, timedelta

import asyncpg


# Custom exceptions
class UserExistsError(Exception):
    """Raised when attempting to register with an email that already exists."""
    pass


class AuthenticationError(Exception):
    """Raised when authentication fails (invalid credentials)."""
    pass


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class AuthStore:
    """PostgreSQL implementation for user authentication and session management."""
    
    def __init__(self, database_url: str):
        """
        Initialize the Auth store.
        
        Args:
            database_url: PostgreSQL connection URL
        """
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None
        self._connected = False
        self._token_expiry_hours = 24 * 7  # 7 days
    
    async def initialize(self, max_retries: int = 3, retry_delay: float = 2.0) -> None:
        """Initialize the database connection pool and create tables with retry logic."""
        import asyncio
        
        last_error = None
        for attempt in range(max_retries):
            try:
                self.pool = await asyncpg.create_pool(
                    self.database_url,
                    min_size=1,
                    max_size=10,
                    ssl='require',
                    timeout=30,
                    command_timeout=30
                )
                self._connected = True
                
                # Create tables if they don't exist
                await self._create_tables()
                return  # Success!
                
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"[AuthStore] Connection attempt {attempt + 1} failed: {e}")
                    print(f"[AuthStore] Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
        
        # All retries failed
        raise last_error
    
    async def _create_tables(self) -> None:
        """Create the required database tables if they don't exist."""
        async with self.pool.acquire() as conn:
            # Create users table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(255) PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    name VARCHAR(255),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Create index on email for faster lookups
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_email 
                ON users(email)
            """)
            
            # Create auth tokens table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS auth_tokens (
                    token VARCHAR(255) PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    is_valid BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Create user_sessions table (links users to chat threads)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id VARCHAR(255) PRIMARY KEY,
                    user_email VARCHAR(255) NOT NULL,
                    thread_id VARCHAR(255) NOT NULL,
                    name VARCHAR(255) DEFAULT 'New Chat',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    CONSTRAINT fk_user_email FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for user_sessions
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_sessions_email 
                ON user_sessions(user_email, created_at DESC)
            """)
    
    def is_connected(self) -> bool:
        """Check if the store is connected to the database."""
        return self._connected and self.pool is not None
    
    async def close(self) -> None:
        """Close the database connection pool."""
        if self.pool:
            await self.pool.close()
            self._connected = False
    
    async def cleanup_test_data(self) -> None:
        """Clean up test data (users with test_ prefix in email)."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                DELETE FROM users WHERE email LIKE 'test_%'
            """)
    
    # ============== Validation Helpers ==============
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _validate_password(self, password: str) -> bool:
        """Validate password strength (minimum 8 characters)."""
        return len(password) >= 8
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256((password + salt).encode())
        return f"{salt}:{hash_obj.hexdigest()}"
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash."""
        try:
            salt, hash_value = stored_hash.split(':')
            hash_obj = hashlib.sha256((password + salt).encode())
            return hash_obj.hexdigest() == hash_value
        except:
            return False
    
    def _generate_token(self) -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)
    
    # ============== User Registration ==============
    
    async def register_user(
        self, 
        email: str, 
        password: str, 
        name: str = ""
    ) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            email: User's email address
            password: User's password
            name: User's display name
            
        Returns:
            Dict with user info (without password hash)
            
        Raises:
            ValidationError: If email or password format is invalid
            UserExistsError: If email already exists
        """
        # Validate inputs
        if not self._validate_email(email):
            raise ValidationError("Invalid email format")
        
        if not self._validate_password(password):
            raise ValidationError("Password must be at least 8 characters")
        
        # Generate user ID and hash password
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        password_hash = self._hash_password(password)
        
        async with self.pool.acquire() as conn:
            # Check if email already exists
            existing = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1",
                email
            )
            
            if existing:
                raise UserExistsError(f"User with email {email} already exists")
            
            # Insert new user
            await conn.execute("""
                INSERT INTO users (id, email, password_hash, name, created_at, updated_at)
                VALUES ($1, $2, $3, $4, NOW(), NOW())
            """, user_id, email, password_hash, name)
        
        return {
            'id': user_id,
            'email': email,
            'name': name,
            'created_at': datetime.now().isoformat()
        }
    
    # ============== User Login ==============
    
    async def login_user(
        self, 
        email: str, 
        password: str
    ) -> Dict[str, Any]:
        """
        Authenticate a user and return a session token.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Dict with user info and auth token
            
        Raises:
            AuthenticationError: If credentials are invalid
        """
        async with self.pool.acquire() as conn:
            # Get user by email
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE email = $1",
                email
            )
            
            if not user:
                raise AuthenticationError("Invalid email or password")
            
            # Verify password
            if not self._verify_password(password, user['password_hash']):
                raise AuthenticationError("Invalid email or password")
            
            # Generate token
            token = self._generate_token()
            expires_at = datetime.now() + timedelta(hours=self._token_expiry_hours)
            
            # Store token
            await conn.execute("""
                INSERT INTO auth_tokens (token, user_id, created_at, expires_at, is_valid)
                VALUES ($1, $2, NOW(), $3, TRUE)
            """, token, user['id'], expires_at)
        
        return {
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name']
            },
            'token': token,
            'expires_at': expires_at.isoformat()
        }
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify an authentication token and return user info.
        
        Args:
            token: The auth token to verify
            
        Returns:
            User info dict if token is valid, None otherwise
        """
        async with self.pool.acquire() as conn:
            # Get token with user info
            row = await conn.fetchrow("""
                SELECT t.*, u.email, u.name 
                FROM auth_tokens t
                JOIN users u ON t.user_id = u.id
                WHERE t.token = $1 
                  AND t.is_valid = TRUE 
                  AND t.expires_at > NOW()
            """, token)
            
            if not row:
                return None
            
            return {
                'id': row['user_id'],
                'email': row['email'],
                'name': row['name']
            }
    
    async def logout_user(self, token: str) -> None:
        """
        Invalidate a user's token (logout).
        
        Args:
            token: The auth token to invalidate
        """
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE auth_tokens SET is_valid = FALSE WHERE token = $1
            """, token)
    
    # ============== User Session Management ==============
    
    async def create_user_session(
        self, 
        user_email: str, 
        session_name: str = "New Chat"
    ) -> Dict[str, Any]:
        """
        Create a new chat session for a user.
        
        Args:
            user_email: User's email address
            session_name: Name for the session
            
        Returns:
            Dict with session info including thread_id
        """
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        thread_id = f"thread_{uuid.uuid4().hex[:12]}"
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO user_sessions (id, user_email, thread_id, name, created_at, updated_at)
                VALUES ($1, $2, $3, $4, NOW(), NOW())
            """, session_id, user_email, thread_id, session_name)
        
        return {
            'id': session_id,
            'user_email': user_email,
            'thread_id': thread_id,
            'name': session_name,
            'created_at': datetime.now().isoformat()
        }
    
    async def get_user_sessions(
        self, 
        user_email: str, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get all chat sessions for a user.
        
        Args:
            user_email: User's email address
            limit: Maximum number of sessions to return
            
        Returns:
            List of session info dicts
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM user_sessions 
                WHERE user_email = $1 
                ORDER BY updated_at DESC
                LIMIT $2
            """, user_email, limit)
        
        return [
            {
                'id': row['id'],
                'user_email': row['user_email'],
                'thread_id': row['thread_id'],
                'name': row['name'],
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
            }
            for row in rows
        ]
    
    async def delete_user_session(
        self, 
        user_email: str, 
        thread_id: str
    ) -> None:
        """
        Delete a chat session.
        
        Args:
            user_email: User's email address (for authorization)
            thread_id: Thread ID to delete
        """
        async with self.pool.acquire() as conn:
            await conn.execute("""
                DELETE FROM user_sessions 
                WHERE user_email = $1 AND thread_id = $2
            """, user_email, thread_id)
    
    async def rename_user_session(
        self, 
        user_email: str, 
        thread_id: str, 
        new_name: str
    ) -> Dict[str, Any]:
        """
        Rename a chat session.
        
        Args:
            user_email: User's email address (for authorization)
            thread_id: Thread ID to rename
            new_name: New name for the session
            
        Returns:
            Updated session info
        """
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE user_sessions 
                SET name = $3, updated_at = NOW()
                WHERE user_email = $1 AND thread_id = $2
            """, user_email, thread_id, new_name)
            
            row = await conn.fetchrow("""
                SELECT * FROM user_sessions 
                WHERE user_email = $1 AND thread_id = $2
            """, user_email, thread_id)
        
        if row:
            return {
                'id': row['id'],
                'user_email': row['user_email'],
                'thread_id': row['thread_id'],
                'name': row['name'],
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
            }
        return {}
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user info by email.
        
        Args:
            email: User's email address
            
        Returns:
            User info dict or None if not found
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, email, name, created_at FROM users WHERE email = $1",
                email
            )
        
        if row:
            return {
                'id': row['id'],
                'email': row['email'],
                'name': row['name'],
                'created_at': row['created_at'].isoformat() if row['created_at'] else None
            }
        return None
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """
        Get statistics about users.
        
        Returns:
            Dict with user statistics
        """
        async with self.pool.acquire() as conn:
            # Total users count
            total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
            
            # Users registered today
            users_today = await conn.fetchval("""
                SELECT COUNT(*) FROM users 
                WHERE created_at >= CURRENT_DATE
            """)
            
            # Users registered this week
            users_this_week = await conn.fetchval("""
                SELECT COUNT(*) FROM users 
                WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
            """)
            
            # Active sessions count
            active_sessions = await conn.fetchval("""
                SELECT COUNT(*) FROM auth_tokens 
                WHERE is_valid = TRUE AND expires_at > NOW()
            """)
            
            # Total chat sessions
            total_chat_sessions = await conn.fetchval("SELECT COUNT(*) FROM user_sessions")
        
        return {
            'total_users': total_users or 0,
            'users_today': users_today or 0,
            'users_this_week': users_this_week or 0,
            'active_sessions': active_sessions or 0,
            'total_chat_sessions': total_chat_sessions or 0
        }

