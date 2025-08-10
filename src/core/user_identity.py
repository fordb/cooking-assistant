"""
Simple user identity management for conversational recipe management.
"""

from typing import Dict, Optional
import uuid
from dataclasses import dataclass

from src.common.exceptions import CookingAssistantError


class UserIdentificationError(CookingAssistantError):
    """Exception raised during user identification operations."""
    pass


@dataclass
class UserProfile:
    """Simple user profile."""
    user_id: str
    recipe_count: int = 0


class UserIdentityManager:
    """Simple user identity and session management."""
    
    def __init__(self):
        self._users: Dict[str, UserProfile] = {}
        self._sessions: Dict[str, str] = {}  # session_id -> user_id
        
    def create_user(self) -> UserProfile:
        """Create new user."""
        user_id = str(uuid.uuid4())
        profile = UserProfile(user_id=user_id)
        self._users[user_id] = profile
        return profile
    
    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Get user by ID."""
        return self._users.get(user_id)
    
    def create_session(self, user_id: str) -> str:
        """Create session for user."""
        if user_id not in self._users:
            raise UserIdentificationError(f"User not found: {user_id}")
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = user_id
        return session_id
    
    def get_user_from_session(self, session_id: str) -> Optional[UserProfile]:
        """Get user from session."""
        user_id = self._sessions.get(session_id)
        return self.get_user(user_id) if user_id else None
    
    def increment_recipe_count(self, user_id: str) -> bool:
        """Increment user's recipe count."""
        user = self._users.get(user_id)
        if user:
            user.recipe_count += 1
            return True
        return False


# Module-level singleton
_identity_manager: Optional[UserIdentityManager] = None


def get_identity_manager() -> UserIdentityManager:
    """Get singleton identity manager."""
    global _identity_manager
    if _identity_manager is None:
        _identity_manager = UserIdentityManager()
    return _identity_manager


# Convenience functions
def create_user() -> UserProfile:
    """Create new user."""
    return get_identity_manager().create_user()


def get_user_from_session(session_id: str) -> Optional[UserProfile]:
    """Get user from session."""
    return get_identity_manager().get_user_from_session(session_id)