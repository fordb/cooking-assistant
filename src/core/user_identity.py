"""
User identity management system for conversational recipe management.
Handles user identification, session management, and basic user data storage.
"""

from typing import Dict, Optional, Any
from enum import Enum
import uuid
import time
from dataclasses import dataclass, asdict
from datetime import datetime

from src.common.config import get_logger
from src.common.exceptions import CookingAssistantError

logger = get_logger(__name__)


class UserIdentificationError(CookingAssistantError):
    """Exception raised during user identification operations."""
    pass


class UserStatus(Enum):
    """User session status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    NEW = "new"


@dataclass
class UserProfile:
    """User profile data structure."""
    user_id: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    created_at: float = None
    last_active: float = None
    status: UserStatus = UserStatus.NEW
    preferences: Dict[str, Any] = None
    recipe_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
        if self.last_active is None:
            self.last_active = time.time()
        if self.preferences is None:
            self.preferences = {}


class UserIdentityManager:
    """
    Manages user identity and session data for conversational recipe management.
    Provides simple in-memory storage for development/demo purposes.
    """
    
    def __init__(self):
        """Initialize the user identity manager."""
        self._users: Dict[str, UserProfile] = {}
        self._session_to_user: Dict[str, str] = {}
        
    def create_user(self, display_name: Optional[str] = None, email: Optional[str] = None) -> UserProfile:
        """
        Create a new user profile.
        
        Args:
            display_name: Optional display name for the user
            email: Optional email for the user
            
        Returns:
            Created user profile
        """
        user_id = str(uuid.uuid4())
        
        profile = UserProfile(
            user_id=user_id,
            display_name=display_name,
            email=email,
            status=UserStatus.NEW
        )
        
        self._users[user_id] = profile
        logger.info(f"Created new user profile: {user_id}")
        
        return profile
    
    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """
        Get user profile by ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            User profile if found, None otherwise
        """
        return self._users.get(user_id)
    
    def update_user_activity(self, user_id: str) -> bool:
        """
        Update user's last activity timestamp.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if updated successfully, False if user not found
        """
        user = self._users.get(user_id)
        if user:
            user.last_active = time.time()
            user.status = UserStatus.ACTIVE
            return True
        return False
    
    def create_session(self, user_id: str) -> str:
        """
        Create a new session for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Session ID
            
        Raises:
            UserIdentificationError: If user not found
        """
        if user_id not in self._users:
            raise UserIdentificationError(f"User not found: {user_id}")
            
        session_id = str(uuid.uuid4())
        self._session_to_user[session_id] = user_id
        
        # Update user activity
        self.update_user_activity(user_id)
        
        logger.info(f"Created session {session_id} for user {user_id}")
        return session_id
    
    def get_user_from_session(self, session_id: str) -> Optional[UserProfile]:
        """
        Get user profile from session ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            User profile if found, None otherwise
        """
        user_id = self._session_to_user.get(session_id)
        if user_id:
            return self.get_user(user_id)
        return None
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences.
        
        Args:
            user_id: User identifier
            preferences: Preferences dictionary to merge
            
        Returns:
            True if updated successfully, False if user not found
        """
        user = self._users.get(user_id)
        if user:
            user.preferences.update(preferences)
            self.update_user_activity(user_id)
            return True
        return False
    
    def increment_recipe_count(self, user_id: str) -> bool:
        """
        Increment user's recipe count.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if updated successfully, False if user not found
        """
        user = self._users.get(user_id)
        if user:
            user.recipe_count += 1
            self.update_user_activity(user_id)
            return True
        return False
    
    def get_user_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user statistics.
        
        Args:
            user_id: User identifier
            
        Returns:
            Statistics dictionary if user found, None otherwise
        """
        user = self._users.get(user_id)
        if user:
            return {
                'user_id': user.user_id,
                'recipe_count': user.recipe_count,
                'created_at': datetime.fromtimestamp(user.created_at).isoformat(),
                'last_active': datetime.fromtimestamp(user.last_active).isoformat(),
                'status': user.status.value,
                'preferences': user.preferences
            }
        return None
    
    def list_users(self) -> Dict[str, Dict[str, Any]]:
        """
        List all users (for admin/debug purposes).
        
        Returns:
            Dictionary of user data
        """
        return {
            user_id: asdict(profile) 
            for user_id, profile in self._users.items()
        }


# Module-level singleton instance for performance
_identity_manager: Optional[UserIdentityManager] = None


def get_identity_manager() -> UserIdentityManager:
    """Get or create the singleton identity manager instance."""
    global _identity_manager
    if _identity_manager is None:
        _identity_manager = UserIdentityManager()
    return _identity_manager


# Convenience functions for easy integration
def create_user(display_name: Optional[str] = None, email: Optional[str] = None) -> UserProfile:
    """Create a new user profile."""
    manager = get_identity_manager()
    return manager.create_user(display_name, email)


def get_user(user_id: str) -> Optional[UserProfile]:
    """Get user profile by ID."""
    manager = get_identity_manager()
    return manager.get_user(user_id)


def create_session(user_id: str) -> str:
    """Create a new session for a user."""
    manager = get_identity_manager()
    return manager.create_session(user_id)


def get_user_from_session(session_id: str) -> Optional[UserProfile]:
    """Get user profile from session ID."""
    manager = get_identity_manager()
    return manager.get_user_from_session(session_id)