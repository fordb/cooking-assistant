"""
Tests for configuration system.
"""

import unittest
import os
from src.config import (
    CookingAssistantConfig,
    get_config,
    get_query_config,
    get_memory_config,
    get_recipe_config,
    get_prompt_config,
    get_openai_config,
    get_ui_config,
    get_test_config,
    reload_config
)


class TestCookingAssistantConfig(unittest.TestCase):
    """Test configuration system functionality."""
    
    def test_default_configuration_values(self):
        """Test that default configuration values are set correctly."""
        config = CookingAssistantConfig()
        
        # Test query classification config
        self.assertEqual(config.query_classification.SIMPLE_WORD_COUNT_THRESHOLD, 6)
        self.assertEqual(config.query_classification.COMPLEX_WORD_COUNT_THRESHOLD, 15)
        self.assertEqual(config.query_classification.KEYWORD_MATCH_SCORE, 0.2)
        
        # Test recipe config
        self.assertEqual(config.recipe.MIN_INGREDIENTS, 2)
        self.assertEqual(config.recipe.MIN_INSTRUCTIONS, 3)
        self.assertEqual(config.recipe.DEFAULT_PREP_TIME, 15)
        self.assertEqual(config.recipe.DEFAULT_COOK_TIME, 30)
        
        # Test OpenAI config
        self.assertEqual(config.openai.SIMPLE_TEMPERATURE, 0.3)
        self.assertEqual(config.openai.COMPLEX_TEMPERATURE, 0.7)
        self.assertEqual(config.openai.DEFAULT_MODEL, "gpt-3.5-turbo")
        
        # Test UI config
        self.assertEqual(config.ui.SEPARATOR_LENGTH, 60)
        self.assertEqual(config.ui.SHORT_SEPARATOR_LENGTH, 40)
    
    def test_config_sections_access(self):
        """Test that configuration sections are accessible."""
        query_config = get_query_config()
        memory_config = get_memory_config()
        recipe_config = get_recipe_config()
        prompt_config = get_prompt_config()
        openai_config = get_openai_config()
        ui_config = get_ui_config()
        test_config = get_test_config()
        
        # Verify sections are not None
        self.assertIsNotNone(query_config)
        self.assertIsNotNone(memory_config)
        self.assertIsNotNone(recipe_config)
        self.assertIsNotNone(prompt_config)
        self.assertIsNotNone(openai_config)
        self.assertIsNotNone(ui_config)
        self.assertIsNotNone(test_config)
        
        # Test specific values
        self.assertEqual(query_config.MIN_CONSTRAINTS_FOR_COMPLEX, 2)
        self.assertEqual(memory_config.RECENT_TOPICS_LIMIT, 5)
        self.assertEqual(recipe_config.MAX_SERVINGS, 50)
        self.assertEqual(prompt_config.DEFAULT_EXAMPLES_COUNT, 3)
        self.assertEqual(openai_config.SIMPLE_MAX_TOKENS, 150)
        self.assertEqual(ui_config.MEMORY_SEPARATOR_LENGTH, 30)
        self.assertEqual(test_config.EXPECTED_RECIPE_COUNT, 15)
    
    def test_environment_variable_override(self):
        """Test that environment variables override default values."""
        # Set environment variables
        os.environ['OPENAI_MODEL'] = 'gpt-4'
        os.environ['MAX_EXAMPLES'] = '5'
        os.environ['SIMPLE_TEMPERATURE'] = '0.1'
        os.environ['COMPLEX_TEMPERATURE'] = '0.9'
        
        try:
            # Reload config to pick up environment variables
            config = CookingAssistantConfig.from_env()
            
            self.assertEqual(config.openai.DEFAULT_MODEL, 'gpt-4')
            self.assertEqual(config.prompts.DEFAULT_EXAMPLES_COUNT, 5)
            self.assertEqual(config.openai.SIMPLE_TEMPERATURE, 0.1)
            self.assertEqual(config.openai.COMPLEX_TEMPERATURE, 0.9)
            
        finally:
            # Clean up environment variables
            del os.environ['OPENAI_MODEL']
            del os.environ['MAX_EXAMPLES']
            del os.environ['SIMPLE_TEMPERATURE']
            del os.environ['COMPLEX_TEMPERATURE']
    
    def test_config_to_dict(self):
        """Test configuration serialization to dictionary."""
        config = CookingAssistantConfig()
        config_dict = config.to_dict()
        
        self.assertIsInstance(config_dict, dict)
        self.assertIn('query_classification', config_dict)
        self.assertIn('conversation_memory', config_dict)
        self.assertIn('recipe', config_dict)
        self.assertIn('prompts', config_dict)
        self.assertIn('openai', config_dict)
        self.assertIn('ui', config_dict)
        self.assertIn('testing', config_dict)
        
        # Check nested values
        self.assertEqual(config_dict['query_classification']['SIMPLE_WORD_COUNT_THRESHOLD'], 6)
        self.assertEqual(config_dict['recipe']['MIN_INGREDIENTS'], 2)
    
    def test_global_config_functions(self):
        """Test global configuration access functions."""
        global_config = get_config()
        self.assertIsInstance(global_config, CookingAssistantConfig)
        
        # Test reload function
        reloaded_config = reload_config()
        self.assertIsInstance(reloaded_config, CookingAssistantConfig)
    
    def test_configuration_consistency(self):
        """Test that configuration values are consistent across the system."""
        # Test that magic numbers we replaced match config values
        query_config = get_query_config()
        self.assertEqual(query_config.SIMPLE_WORD_COUNT_THRESHOLD, 6)
        self.assertEqual(query_config.COMPLEX_WORD_COUNT_THRESHOLD, 15)
        self.assertEqual(query_config.KEYWORD_MATCH_SCORE, 0.2)
        self.assertEqual(query_config.MULTIPLE_MATCHES_BONUS, 0.1)
        
        recipe_config = get_recipe_config()
        self.assertEqual(recipe_config.MIN_INGREDIENTS, 2)
        self.assertEqual(recipe_config.MIN_INSTRUCTIONS, 3)
        self.assertEqual(recipe_config.DEFAULT_PREP_TIME, 15)
        self.assertEqual(recipe_config.DEFAULT_COOK_TIME, 30)
        
        openai_config = get_openai_config()
        self.assertEqual(openai_config.SIMPLE_TEMPERATURE, 0.3)
        self.assertEqual(openai_config.COMPLEX_TEMPERATURE, 0.7)
        self.assertEqual(openai_config.SIMPLE_MAX_TOKENS, 150)
        self.assertEqual(openai_config.COMPLEX_MAX_TOKENS, 800)


if __name__ == '__main__':
    unittest.main()