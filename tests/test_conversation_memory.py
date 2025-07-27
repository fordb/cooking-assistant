"""
Tests for conversation memory management system.
"""

import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
from src.conversation_memory import (
    ConversationMemory, UserPreferences, ConversationTurn,
    get_conversation_memory, reset_conversation_memory
)

class TestUserPreferences(unittest.TestCase):
    """Test user preferences tracking."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.preferences = UserPreferences()
    
    def test_dietary_restriction_updates(self):
        """Test dietary restriction detection and updates."""
        query = "I'm vegetarian and need gluten-free options"
        updates = self.preferences.update_from_query(query)
        
        self.assertIn('vegetarian', self.preferences.dietary_restrictions)
        self.assertIn('gluten-free', self.preferences.dietary_restrictions)
        self.assertEqual(len(updates), 2)
        self.assertTrue(any('vegetarian' in update for update in updates))
        self.assertTrue(any('gluten-free' in update for update in updates))
    
    def test_cuisine_preference_updates(self):
        """Test cuisine preference detection."""
        query = "I love Italian and Mexican food"
        updates = self.preferences.update_from_query(query)
        
        self.assertIn('italian', self.preferences.cuisine_preferences)
        self.assertIn('mexican', self.preferences.cuisine_preferences)
        self.assertEqual(len(updates), 2)
    
    def test_skill_level_updates(self):
        """Test skill level detection."""
        # Test beginner
        query = "I'm a beginner cook, need easy recipes"
        updates = self.preferences.update_from_query(query)
        self.assertEqual(self.preferences.skill_level, 'beginner')
        self.assertTrue(any('beginner' in update for update in updates))
        
        # Test advanced
        self.preferences.skill_level = None  # Reset
        query = "I'm an expert chef looking for advanced techniques"
        updates = self.preferences.update_from_query(query)
        self.assertEqual(self.preferences.skill_level, 'advanced')
    
    def test_family_size_updates(self):
        """Test family size detection."""
        queries_and_sizes = [
            ("Cooking for family of 4", 4),
            ("Recipe serves 6 people", 6),
            ("Need to feed 8 people", 8)
        ]
        
        for query, expected_size in queries_and_sizes:
            preferences = UserPreferences()  # Fresh instance
            updates = preferences.update_from_query(query)
            self.assertEqual(preferences.family_size, expected_size)
            self.assertTrue(any(str(expected_size) in update for update in updates))
    
    def test_time_preference_updates(self):
        """Test cooking time preference detection."""
        query = "Need quick 30 minute meals"
        updates = self.preferences.update_from_query(query)
        
        self.assertEqual(self.preferences.cooking_time_preference, 'quick')
        self.assertTrue(any('quick' in update for update in updates))
    
    def test_budget_consciousness_updates(self):
        """Test budget consciousness detection."""
        query = "Looking for cheap budget-friendly meals"
        updates = self.preferences.update_from_query(query)
        
        self.assertTrue(self.preferences.budget_conscious)
        self.assertTrue(any('budget' in update for update in updates))
    
    def test_equipment_updates(self):
        """Test equipment detection."""
        query = "I have a slow cooker and air fryer"
        updates = self.preferences.update_from_query(query)
        
        self.assertIn('slow cooker', self.preferences.equipment_available)
        self.assertIn('air fryer', self.preferences.equipment_available)
        self.assertEqual(len(updates), 2)

class TestConversationMemory(unittest.TestCase):
    """Test conversation memory management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.memory = ConversationMemory()
    
    def test_conversation_turn_creation(self):
        """Test adding conversation turns."""
        user_query = "What temperature for chicken?"
        assistant_response = "Cook chicken to 165°F internal temperature."
        strategy = "zero_shot"
        complexity = "simple"
        
        initial_count = len(self.memory.conversation_history)
        self.memory.add_turn(user_query, assistant_response, strategy, complexity)
        
        self.assertEqual(len(self.memory.conversation_history), initial_count + 1)
        
        latest_turn = self.memory.conversation_history[-1]
        self.assertEqual(latest_turn.user_query, user_query)
        self.assertEqual(latest_turn.assistant_response, assistant_response)
        self.assertEqual(latest_turn.strategy_used, strategy)
        self.assertEqual(latest_turn.complexity, complexity)
    
    def test_topic_extraction(self):
        """Test topic extraction from queries."""
        queries_and_expected_topics = [
            ("How to bake chicken?", ["cooking_method:bake", "ingredient:chicken"]),
            ("Breakfast pasta recipe", ["meal_type:breakfast"]),
            ("Stir-fry vegetables for dinner", ["cooking_method:stir-fry", "meal_type:dinner"])
        ]
        
        for query, expected_topics in queries_and_expected_topics:
            topics = self.memory._extract_topics(query)
            for expected in expected_topics:
                self.assertIn(expected, topics, 
                            f"Expected topic '{expected}' not found in topics for query '{query}'")
    
    def test_followup_question_detection(self):
        """Test follow-up question detection."""
        followup_queries = [
            "What about using tofu instead?",
            "Can you also suggest side dishes?",
            "How about making it spicier?",
            "But what if I don't have an oven?"
        ]
        
        non_followup_queries = [
            "How to cook chicken?",
            "Recipe for pasta",
            "Vegetarian meal ideas"
        ]
        
        for query in followup_queries:
            self.assertTrue(self.memory._is_followup_question(query),
                          f"'{query}' should be detected as follow-up")
        
        for query in non_followup_queries:
            self.assertFalse(self.memory._is_followup_question(query),
                           f"'{query}' should not be detected as follow-up")
    
    def test_context_generation(self):
        """Test context generation for queries."""
        # Add some conversation history
        self.memory.add_turn(
            "I'm vegetarian and need quick meals",
            "Here are some quick vegetarian recipes...",
            "few_shot",
            "moderate"
        )
        
        context = self.memory.get_context_for_query("What about pasta dishes?")
        
        self.assertIn('preferences', context)
        self.assertIn('recent_topics', context)
        self.assertIn('session_length', context)
        self.assertEqual(context['session_length'], 1)
        
        # Check that vegetarian preference was captured
        self.assertIn('vegetarian', context['preferences'].dietary_restrictions)
    
    def test_recent_topics_tracking(self):
        """Test recent topics tracking."""
        # Add multiple turns with different topics
        turns = [
            ("How to bake chicken?", "baking response", "few_shot", "moderate"),
            ("Vegetarian pasta recipe", "pasta response", "few_shot", "moderate"),
            ("Quick breakfast ideas", "breakfast response", "zero_shot", "simple")
        ]
        
        for query, response, strategy, complexity in turns:
            self.memory.add_turn(query, response, strategy, complexity)
        
        recent_topics = self.memory._get_recent_topics(3)
        
        # Should include topics from all recent turns
        expected_topics = ["cooking_method:bake", "ingredient:chicken", "meal_type:breakfast"]
        for topic in expected_topics:
            self.assertIn(topic, recent_topics)
    
    def test_session_summary(self):
        """Test session summary generation."""
        # Add some conversation turns
        self.memory.add_turn("Test query 1", "Test response 1", "zero_shot", "simple")
        self.memory.add_turn("Test query 2", "Test response 2", "few_shot", "moderate")
        
        summary = self.memory.get_session_summary()
        
        self.assertIn('session_id', summary)
        self.assertIn('duration_minutes', summary)
        self.assertIn('turns_count', summary)
        self.assertIn('preferences', summary)
        self.assertIn('strategies_used', summary)
        
        self.assertEqual(summary['turns_count'], 2)
        self.assertIn('zero_shot', summary['strategies_used'])
        self.assertIn('few_shot', summary['strategies_used'])

class TestMemoryGlobalFunctions(unittest.TestCase):
    """Test global memory management functions."""
    
    def test_get_conversation_memory(self):
        """Test getting conversation memory instance."""
        memory1 = get_conversation_memory()
        memory2 = get_conversation_memory()
        
        # Since we removed global state, these should be different instances
        self.assertIsNot(memory1, memory2)
        self.assertIsInstance(memory1, ConversationMemory)
        self.assertIsInstance(memory2, ConversationMemory)
    
    def test_reset_conversation_memory(self):
        """Test resetting conversation memory."""
        # Reset function now just returns a new instance
        memory = reset_conversation_memory()
        
        # Should be a new clean instance
        self.assertIsInstance(memory, ConversationMemory)
        self.assertEqual(len(memory.conversation_history), 0)

class TestConversationTurn(unittest.TestCase):
    """Test conversation turn data structure."""
    
    def test_conversation_turn_creation(self):
        """Test creating conversation turns."""
        timestamp = datetime.now()
        turn = ConversationTurn(
            timestamp=timestamp,
            user_query="Test query",
            assistant_response="Test response",
            strategy_used="test_strategy",
            complexity="moderate",
            topics=["topic1", "topic2"]
        )
        
        self.assertEqual(turn.timestamp, timestamp)
        self.assertEqual(turn.user_query, "Test query")
        self.assertEqual(turn.assistant_response, "Test response")
        self.assertEqual(turn.strategy_used, "test_strategy")
        self.assertEqual(turn.complexity, "moderate")
        self.assertEqual(turn.topics, ["topic1", "topic2"])

if __name__ == '__main__':
    unittest.main()