"""
Tests for meta-prompting system.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.meta_prompting import (
    MetaPromptingSystem, PromptingStrategy, process_cooking_query
)
from src.query_classifier import QueryComplexity
from src.conversation_memory import ConversationMemory

class TestPromptingStrategy(unittest.TestCase):
    """Test the prompting strategy implementations."""
    
    def test_zero_shot_prompt_generation(self):
        """Test zero-shot prompt generation."""
        query = "What temperature for chicken?"
        prompt = PromptingStrategy.zero_shot_prompt(query)
        
        self.assertIsInstance(prompt, str)
        self.assertIn(query, prompt)
        self.assertIn("cooking assistant", prompt.lower())
        self.assertIn("directly and concisely", prompt.lower())
    
    def test_few_shot_prompt_generation(self):
        """Test few-shot prompt generation."""
        query = "How to make pasta carbonara?"
        
        with patch('src.examples.get_few_shot_examples') as mock_examples:
            mock_examples.return_value = "Example recipes..."
            
            # Also patch the select_prompt_template since it's used for ingredient-based queries
            with patch('src.meta_prompting.select_prompt_template') as mock_template:
                mock_template.return_value = f"Template with {query}"
                prompt = PromptingStrategy.few_shot_prompt(query)
        
        self.assertIsInstance(prompt, str)
        self.assertIn(query, prompt)
        # The function should either call examples directly or template system
        self.assertTrue(mock_examples.called or mock_template.called)
    
    def test_chain_of_thought_prompt_generation(self):
        """Test chain-of-thought prompt generation."""
        query = "Plan healthy meals for diabetic with 30-min cooking limit"
        prompt = PromptingStrategy.chain_of_thought_prompt(query)
        
        self.assertIsInstance(prompt, str)
        self.assertIn(query, prompt)
        self.assertIn("<thinking>", prompt)
        self.assertIn("CONSTRAINT ANALYSIS", prompt)
        self.assertIn("NUTRITIONAL CONSIDERATIONS", prompt)
        self.assertIn("Chef Marcus", prompt)

class TestMetaPromptingSystem(unittest.TestCase):
    """Test the meta-prompting system orchestration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the OpenAI client to avoid actual API calls
        with patch('src.meta_prompting.OpenAI') as mock_openai:
            self.mock_client = MagicMock()
            mock_openai.return_value = self.mock_client
            self.system = MetaPromptingSystem()
    
    def test_strategy_selection(self):
        """Test that correct strategies are selected for different complexities."""
        test_cases = [
            (QueryComplexity.SIMPLE, "zero_shot"),
            (QueryComplexity.MODERATE, "few_shot"),
            (QueryComplexity.COMPLEX, "chain_of_thought")
        ]
        
        for complexity, expected_strategy in test_cases:
            strategy_name, prompt = self.system._select_strategy(
                complexity, "test query", None
            )
            self.assertEqual(strategy_name, expected_strategy)
            self.assertIsInstance(prompt, str)
            self.assertGreater(len(prompt), 10)
    
    @patch('src.meta_prompting.MetaPromptingSystem._generate_response')
    def test_process_query_success(self, mock_generate):
        """Test successful query processing."""
        mock_generate.return_value = "Test response"
        
        query = "What temperature for chicken?"
        result = self.system.process_query(query)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['response'], "Test response")
        self.assertEqual(result['strategy'], "zero_shot")
        self.assertEqual(result['complexity'], "simple")
        self.assertIn('confidence', result)
        self.assertIn('reasoning', result)
    
    @patch('src.meta_prompting.MetaPromptingSystem._generate_response')
    def test_process_query_error_handling(self, mock_generate):
        """Test error handling in query processing."""
        mock_generate.side_effect = Exception("API Error")
        
        query = "What temperature for chicken?"
        result = self.system.process_query(query)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn("API Error", result['error'])
        self.assertIn("Sorry, I encountered an error", result['response'])
    
    def test_generate_response_parameters(self):
        """Test that response generation uses appropriate parameters."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Test simple query (should use lower temperature, fewer tokens)
        response = self.system._generate_response("test prompt", QueryComplexity.SIMPLE)
        
        self.assertEqual(response, "Test response")
        
        # Verify API was called with appropriate parameters
        call_args = self.mock_client.chat.completions.create.call_args
        self.assertEqual(call_args[1]['temperature'], 0.3)
        self.assertEqual(call_args[1]['max_tokens'], 150)
        
        # Test complex query (should use higher temperature, more tokens)
        self.system._generate_response("test prompt", QueryComplexity.COMPLEX)
        
        call_args = self.mock_client.chat.completions.create.call_args
        self.assertEqual(call_args[1]['temperature'], 0.7)
        self.assertEqual(call_args[1]['max_tokens'], 800)
    
    def test_ingredient_extraction(self):
        """Test ingredient extraction from queries."""
        test_cases = [
            ("How to cook chicken and rice?", "chicken, rice"),
            ("Recipe with beef and vegetables", "beef"),
            ("Make pasta with tomato sauce", "pasta, tomato"),
            ("No ingredients mentioned here", "")
        ]
        
        for query, expected in test_cases:
            result = MetaPromptingSystem._extract_ingredients(query)
            if expected:
                for ingredient in expected.split(', '):
                    self.assertIn(ingredient, result)
            else:
                self.assertEqual(result, "")
    
    def test_constraint_extraction(self):
        """Test constraint extraction from queries."""
        test_cases = [
            ("Vegetarian gluten-free quick meal", ["vegetarian", "gluten-free", "quick"]),
            ("Healthy budget-friendly dinner", ["healthy", "budget"]),
            ("Keto low-carb high-protein recipe", ["keto", "low-carb", "high-protein"]),
            ("Regular cooking recipe", [])
        ]
        
        for query, expected_constraints in test_cases:
            result = MetaPromptingSystem._extract_constraints(query)
            for constraint in expected_constraints:
                self.assertIn(constraint, result)
            if not expected_constraints:
                self.assertEqual(len(result), 0)

class TestProcessCookingQueryFunction(unittest.TestCase):
    """Test the convenience function for processing queries."""
    
    @patch('src.meta_prompting.MetaPromptingSystem')
    def test_process_cooking_query_function(self, mock_system_class):
        """Test the convenience function works correctly."""
        # Setup mock
        mock_system = MagicMock()
        mock_system.process_query.return_value = {
            'response': 'Test response',
            'strategy': 'zero_shot',
            'success': True
        }
        mock_system_class.return_value = mock_system
        
        # Test function
        query = "Test query"
        context = {"test": "context"}
        result = process_cooking_query(query, context)
        
        # Verify system was created and called correctly
        mock_system_class.assert_called_once()
        mock_system.process_query.assert_called_once_with(query, context)
        self.assertEqual(result['response'], 'Test response')
        self.assertEqual(result['strategy'], 'zero_shot')
        self.assertTrue(result['success'])

class TestWeek2Scenarios(unittest.TestCase):
    """Test the specific Week 2 scenarios work correctly."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('src.meta_prompting.OpenAI'):
            self.system = MetaPromptingSystem()
    
    @patch('src.meta_prompting.MetaPromptingSystem._generate_response')
    def test_week2_scenario_1_simple(self, mock_generate):
        """Test Week 2 scenario 1: simple query."""
        mock_generate.return_value = "Cook chicken to 165°F internal temperature."
        
        query = "What temperature for chicken?"
        result = self.system.process_query(query)
        
        self.assertEqual(result['strategy'], 'zero_shot')
        self.assertEqual(result['complexity'], 'simple')
        self.assertTrue(result['success'])
    
    @patch('src.meta_prompting.MetaPromptingSystem._generate_response')
    def test_week2_scenario_2_moderate(self, mock_generate):
        """Test Week 2 scenario 2: moderate query."""
        mock_generate.return_value = "Here's how to make pasta carbonara..."
        
        query = "How do I make pasta carbonara?"
        result = self.system.process_query(query)
        
        self.assertEqual(result['strategy'], 'few_shot')
        self.assertEqual(result['complexity'], 'moderate')
        self.assertTrue(result['success'])
    
    @patch('src.meta_prompting.MetaPromptingSystem._generate_response')
    def test_week2_scenario_3_complex(self, mock_generate):
        """Test Week 2 scenario 3: complex query."""
        mock_generate.return_value = "Here's a comprehensive meal plan..."
        
        query = "Plan healthy meals for diabetic with 30-min cooking limit"
        result = self.system.process_query(query)
        
        self.assertEqual(result['strategy'], 'chain_of_thought')
        self.assertEqual(result['complexity'], 'complex')
        self.assertTrue(result['success'])

if __name__ == '__main__':
    unittest.main()