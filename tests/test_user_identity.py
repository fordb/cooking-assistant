"""
Tests for user identity management system.
"""

import pytest
import time
from unittest.mock import patch

from src.core.user_identity import (
    UserIdentityManager, UserProfile, UserStatus, UserIdentificationError,
    get_identity_manager, create_user, get_user, create_session, get_user_from_session
)


class TestUserProfile:
    """Test UserProfile dataclass."""
    
    def test_user_profile_creation_minimal(self):
        """Test creating user profile with minimal data."""
        profile = UserProfile(user_id="test-123")
        
        assert profile.user_id == "test-123"
        assert profile.display_name is None
        assert profile.email is None
        assert profile.status == UserStatus.NEW
        assert profile.preferences == {}
        assert profile.recipe_count == 0
        assert isinstance(profile.created_at, float)
        assert isinstance(profile.last_active, float)
    
    def test_user_profile_creation_full(self):
        """Test creating user profile with all data."""
        preferences = {"theme": "dark", "notifications": True}
        profile = UserProfile(
            user_id="test-456",
            display_name="Test User",
            email="test@example.com",
            status=UserStatus.ACTIVE,
            preferences=preferences,
            recipe_count=5
        )
        
        assert profile.user_id == "test-456"
        assert profile.display_name == "Test User"
        assert profile.email == "test@example.com"
        assert profile.status == UserStatus.ACTIVE
        assert profile.preferences == preferences
        assert profile.recipe_count == 5


class TestUserIdentityManager:
    """Test UserIdentityManager class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.manager = UserIdentityManager()
    
    def test_manager_initialization(self):
        """Test manager initializes properly."""
        assert isinstance(self.manager._users, dict)
        assert isinstance(self.manager._session_to_user, dict)
        assert len(self.manager._users) == 0
        assert len(self.manager._session_to_user) == 0
    
    def test_create_user_minimal(self):
        """Test creating user with minimal data."""
        profile = self.manager.create_user()
        
        assert profile.user_id is not None
        assert len(profile.user_id) == 36  # UUID4 string length
        assert profile.display_name is None
        assert profile.email is None
        assert profile.status == UserStatus.NEW
        assert profile.recipe_count == 0
        
        # Check user was stored
        assert profile.user_id in self.manager._users
        assert self.manager._users[profile.user_id] == profile
    
    def test_create_user_with_data(self):
        """Test creating user with display name and email."""
        profile = self.manager.create_user(
            display_name="John Doe",
            email="john@example.com"
        )
        
        assert profile.display_name == "John Doe"
        assert profile.email == "john@example.com"
        assert profile.status == UserStatus.NEW
    
    def test_get_user_exists(self):
        """Test getting existing user."""
        profile = self.manager.create_user(display_name="Test User")
        
        retrieved = self.manager.get_user(profile.user_id)
        assert retrieved == profile
        assert retrieved.display_name == "Test User"
    
    def test_get_user_not_exists(self):
        """Test getting non-existent user."""
        result = self.manager.get_user("non-existent-id")
        assert result is None
    
    def test_update_user_activity_success(self):
        """Test updating user activity successfully."""
        profile = self.manager.create_user()
        original_time = profile.last_active
        
        # Wait a small amount to ensure time difference
        time.sleep(0.01)
        
        success = self.manager.update_user_activity(profile.user_id)
        assert success is True
        assert profile.last_active > original_time
        assert profile.status == UserStatus.ACTIVE
    
    def test_update_user_activity_user_not_found(self):
        """Test updating activity for non-existent user."""
        success = self.manager.update_user_activity("non-existent-id")
        assert success is False
    
    def test_create_session_success(self):
        """Test creating session successfully."""
        profile = self.manager.create_user()
        
        session_id = self.manager.create_session(profile.user_id)
        
        assert session_id is not None
        assert len(session_id) == 36  # UUID4 string length
        assert session_id in self.manager._session_to_user
        assert self.manager._session_to_user[session_id] == profile.user_id
        assert profile.status == UserStatus.ACTIVE
    
    def test_create_session_user_not_found(self):
        """Test creating session for non-existent user."""
        with pytest.raises(UserIdentificationError, match="User not found"):
            self.manager.create_session("non-existent-id")
    
    def test_get_user_from_session_success(self):
        """Test getting user from valid session."""
        profile = self.manager.create_user(display_name="Session User")
        session_id = self.manager.create_session(profile.user_id)
        
        retrieved = self.manager.get_user_from_session(session_id)
        assert retrieved == profile
        assert retrieved.display_name == "Session User"
    
    def test_get_user_from_session_invalid(self):
        """Test getting user from invalid session."""
        result = self.manager.get_user_from_session("invalid-session-id")
        assert result is None
    
    def test_update_user_preferences_success(self):
        """Test updating user preferences successfully."""
        profile = self.manager.create_user()
        preferences = {"theme": "dark", "notifications": False}
        
        success = self.manager.update_user_preferences(profile.user_id, preferences)
        assert success is True
        assert profile.preferences == preferences
        assert profile.status == UserStatus.ACTIVE
    
    def test_update_user_preferences_merge(self):
        """Test preferences are merged, not replaced."""
        profile = self.manager.create_user()
        profile.preferences = {"existing": "value"}
        
        new_prefs = {"theme": "dark"}
        success = self.manager.update_user_preferences(profile.user_id, new_prefs)
        
        assert success is True
        assert profile.preferences == {"existing": "value", "theme": "dark"}
    
    def test_update_user_preferences_user_not_found(self):
        """Test updating preferences for non-existent user."""
        success = self.manager.update_user_preferences("non-existent", {"theme": "dark"})
        assert success is False
    
    def test_increment_recipe_count_success(self):
        """Test incrementing recipe count successfully."""
        profile = self.manager.create_user()
        assert profile.recipe_count == 0
        
        success = self.manager.increment_recipe_count(profile.user_id)
        assert success is True
        assert profile.recipe_count == 1
        assert profile.status == UserStatus.ACTIVE
        
        # Test multiple increments
        self.manager.increment_recipe_count(profile.user_id)
        self.manager.increment_recipe_count(profile.user_id)
        assert profile.recipe_count == 3
    
    def test_increment_recipe_count_user_not_found(self):
        """Test incrementing count for non-existent user."""
        success = self.manager.increment_recipe_count("non-existent")
        assert success is False
    
    def test_get_user_stats_success(self):
        """Test getting user statistics successfully."""
        profile = self.manager.create_user(display_name="Stats User")
        profile.recipe_count = 5
        profile.preferences = {"theme": "light"}
        
        stats = self.manager.get_user_stats(profile.user_id)
        
        assert stats is not None
        assert stats['user_id'] == profile.user_id
        assert stats['recipe_count'] == 5
        assert stats['status'] == 'new'
        assert stats['preferences'] == {"theme": "light"}
        assert 'created_at' in stats
        assert 'last_active' in stats
    
    def test_get_user_stats_user_not_found(self):
        """Test getting stats for non-existent user."""
        stats = self.manager.get_user_stats("non-existent")
        assert stats is None
    
    def test_list_users_empty(self):
        """Test listing users when none exist."""
        users = self.manager.list_users()
        assert users == {}
    
    def test_list_users_with_data(self):
        """Test listing users with data."""
        profile1 = self.manager.create_user(display_name="User One")
        profile2 = self.manager.create_user(display_name="User Two")
        
        users = self.manager.list_users()
        
        assert len(users) == 2
        assert profile1.user_id in users
        assert profile2.user_id in users
        assert users[profile1.user_id]['display_name'] == "User One"
        assert users[profile2.user_id]['display_name'] == "User Two"


class TestSingletonPattern:
    """Test singleton pattern for identity manager."""
    
    def test_singleton_instance(self):
        """Test that get_identity_manager returns same instance."""
        manager1 = get_identity_manager()
        manager2 = get_identity_manager()
        
        assert manager1 is manager2
        assert isinstance(manager1, UserIdentityManager)
    
    def test_singleton_persistence(self):
        """Test that data persists across singleton calls."""
        manager1 = get_identity_manager()
        profile = manager1.create_user(display_name="Persistent User")
        
        manager2 = get_identity_manager()
        retrieved = manager2.get_user(profile.user_id)
        
        assert retrieved is not None
        assert retrieved.display_name == "Persistent User"


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def setup_method(self):
        """Reset singleton for clean tests."""
        import src.core.user_identity
        src.core.user_identity._identity_manager = None
    
    def test_create_user_convenience(self):
        """Test create_user convenience function."""
        profile = create_user(display_name="Convenience User")
        
        assert profile.display_name == "Convenience User"
        assert profile.user_id is not None
    
    def test_get_user_convenience(self):
        """Test get_user convenience function."""
        profile = create_user(display_name="Get User Test")
        
        retrieved = get_user(profile.user_id)
        assert retrieved == profile
        
        not_found = get_user("non-existent")
        assert not_found is None
    
    def test_create_session_convenience(self):
        """Test create_session convenience function."""
        profile = create_user()
        
        session_id = create_session(profile.user_id)
        assert session_id is not None
        assert len(session_id) == 36
    
    def test_get_user_from_session_convenience(self):
        """Test get_user_from_session convenience function."""
        profile = create_user(display_name="Session Test")
        session_id = create_session(profile.user_id)
        
        retrieved = get_user_from_session(session_id)
        assert retrieved == profile
        assert retrieved.display_name == "Session Test"
        
        not_found = get_user_from_session("invalid-session")
        assert not_found is None
    
    def test_session_flow_integration(self):
        """Test full session flow integration."""
        # Create user
        profile = create_user(display_name="Integration User", email="test@example.com")
        assert profile.status == UserStatus.NEW
        
        # Create session (should make user active)
        session_id = create_session(profile.user_id)
        assert profile.status == UserStatus.ACTIVE
        
        # Retrieve user from session
        retrieved = get_user_from_session(session_id)
        assert retrieved.display_name == "Integration User"
        assert retrieved.email == "test@example.com"
        assert retrieved.status == UserStatus.ACTIVE