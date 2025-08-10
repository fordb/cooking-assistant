"""
Tests for simplified user identity management system.
"""

import pytest

from src.core.user_identity import (
    UserIdentityManager, UserProfile, UserIdentificationError,
    get_identity_manager, create_user, get_user_from_session
)


class TestUserProfile:
    """Test UserProfile dataclass."""
    
    def test_user_profile_creation(self):
        """Test creating user profile."""
        profile = UserProfile(user_id="test-123")
        
        assert profile.user_id == "test-123"
        assert profile.recipe_count == 0


class TestUserIdentityManager:
    """Test UserIdentityManager class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.manager = UserIdentityManager()
    
    def test_create_user(self):
        """Test creating user."""
        profile = self.manager.create_user()
        
        assert profile.user_id is not None
        assert len(profile.user_id) == 36  # UUID4 string length
        assert profile.recipe_count == 0
        assert profile.user_id in self.manager._users
    
    def test_get_user_exists(self):
        """Test getting existing user."""
        profile = self.manager.create_user()
        retrieved = self.manager.get_user(profile.user_id)
        assert retrieved == profile
    
    def test_get_user_not_exists(self):
        """Test getting non-existent user."""
        result = self.manager.get_user("non-existent-id")
        assert result is None
    
    def test_create_session_success(self):
        """Test creating session."""
        profile = self.manager.create_user()
        session_id = self.manager.create_session(profile.user_id)
        
        assert session_id is not None
        assert len(session_id) == 36  # UUID4 string length
        assert session_id in self.manager._sessions
    
    def test_create_session_user_not_found(self):
        """Test creating session for non-existent user."""
        with pytest.raises(UserIdentificationError, match="User not found"):
            self.manager.create_session("non-existent-id")
    
    def test_get_user_from_session_success(self):
        """Test getting user from session."""
        profile = self.manager.create_user()
        session_id = self.manager.create_session(profile.user_id)
        
        retrieved = self.manager.get_user_from_session(session_id)
        assert retrieved == profile
    
    def test_get_user_from_session_invalid(self):
        """Test getting user from invalid session."""
        result = self.manager.get_user_from_session("invalid-session-id")
        assert result is None
    
    def test_increment_recipe_count_success(self):
        """Test incrementing recipe count."""
        profile = self.manager.create_user()
        assert profile.recipe_count == 0
        
        success = self.manager.increment_recipe_count(profile.user_id)
        assert success is True
        assert profile.recipe_count == 1
        
        # Test multiple increments
        self.manager.increment_recipe_count(profile.user_id)
        assert profile.recipe_count == 2
    
    def test_increment_recipe_count_user_not_found(self):
        """Test incrementing count for non-existent user."""
        success = self.manager.increment_recipe_count("non-existent")
        assert success is False


class TestSingletonPattern:
    """Test singleton pattern."""
    
    def test_singleton_instance(self):
        """Test singleton returns same instance."""
        manager1 = get_identity_manager()
        manager2 = get_identity_manager()
        assert manager1 is manager2


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def setup_method(self):
        """Reset singleton for clean tests."""
        import src.core.user_identity
        src.core.user_identity._identity_manager = None
    
    def test_create_user_convenience(self):
        """Test create_user convenience function."""
        profile = create_user()
        assert profile.user_id is not None
        assert profile.recipe_count == 0
    
    def test_get_user_from_session_convenience(self):
        """Test get_user_from_session convenience function."""
        manager = get_identity_manager()
        profile = manager.create_user()
        session_id = manager.create_session(profile.user_id)
        
        retrieved = get_user_from_session(session_id)
        assert retrieved == profile
        
        not_found = get_user_from_session("invalid-session")
        assert not_found is None