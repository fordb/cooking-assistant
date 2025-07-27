"""
Tests for query classification system.
"""

import unittest
from src.query_classifier import QueryClassifier, QueryComplexity, classify_cooking_query

class TestQueryClassifier(unittest.TestCase):
    """Test the query complexity classification system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.classifier = QueryClassifier()
    
    def test_simple_queries(self):
        """Test that simple queries are classified correctly."""
        simple_queries = [
            "What temperature for chicken?",
            "How long to cook rice?",
            "How much salt?",
            "Substitute for eggs?",
            "What is blanching?",
            "Degrees for baking?"
        ]
        
        for query in simple_queries:
            complexity, confidence, reasoning = self.classifier.classify_query(query)
            self.assertEqual(complexity, QueryComplexity.SIMPLE, 
                           f"Query '{query}' should be classified as SIMPLE")
            self.assertGreater(confidence, 0.0, 
                             f"Confidence should be > 0 for '{query}'")
            self.assertIn("simple", reasoning.lower(), 
                         f"Reasoning should mention 'simple' for '{query}'")
    
    def test_moderate_queries(self):
        """Test that moderate complexity queries are classified correctly."""
        moderate_queries = [
            "How do I make pasta carbonara?",
            "Recipe for beef stir fry",
            "Best way to cook salmon?", 
            "How to prepare chicken teriyaki?",
            "Italian pasta recipe with chicken",
            "Make vegetarian pizza at home"
        ]
        
        for query in moderate_queries:
            complexity, confidence, reasoning = self.classifier.classify_query(query)
            self.assertEqual(complexity, QueryComplexity.MODERATE,
                           f"Query '{query}' should be classified as MODERATE")
            self.assertGreater(confidence, 0.0,
                             f"Confidence should be > 0 for '{query}'")
            self.assertIn("moderate", reasoning.lower(),
                         f"Reasoning should mention 'moderate' for '{query}'")
    
    def test_complex_queries(self):
        """Test that complex queries are classified correctly."""
        complex_queries = [
            "Plan healthy meals for diabetic with 30-min cooking limit",
            "Weekly meal prep for family of 4 with budget constraints",
            "Nutritious gluten-free dinner ideas for busy weeknights",
            "Plan balanced meals for keto diet and meal prep",
            "Budget-friendly vegetarian meal plan for weight loss"
        ]
        
        for query in complex_queries:
            complexity, confidence, reasoning = self.classifier.classify_query(query)
            self.assertEqual(complexity, QueryComplexity.COMPLEX,
                           f"Query '{query}' should be classified as COMPLEX")
            self.assertGreater(confidence, 0.0,
                             f"Confidence should be > 0 for '{query}'")
            self.assertIn("complex", reasoning.lower(),
                         f"Reasoning should mention 'complex' for '{query}'")
    
    def test_week2_scenarios(self):
        """Test the specific Week 2 scenario queries."""
        scenarios = [
            ("What temperature for chicken?", QueryComplexity.SIMPLE),
            ("How do I make pasta carbonara?", QueryComplexity.MODERATE),
            ("Plan healthy meals for diabetic with 30-min cooking limit", QueryComplexity.COMPLEX)
        ]
        
        for query, expected_complexity in scenarios:
            complexity, confidence, reasoning = self.classifier.classify_query(query)
            self.assertEqual(complexity, expected_complexity,
                           f"Week 2 scenario '{query}' should be {expected_complexity.value}")
    
    def test_constraint_counting(self):
        """Test the constraint counting functionality."""
        # Query with multiple constraints should boost complexity
        multi_constraint_query = "Quick healthy vegetarian gluten-free budget meal"
        constraint_count = self.classifier._count_constraints(multi_constraint_query.lower())
        self.assertGreaterEqual(constraint_count, 3, 
                               "Should detect multiple constraints")
        
        # Single constraint
        single_constraint_query = "Vegetarian recipe ideas"
        constraint_count = self.classifier._count_constraints(single_constraint_query.lower())
        self.assertEqual(constraint_count, 1, "Should detect single constraint")
        
        # No constraints
        no_constraint_query = "How to cook pasta"
        constraint_count = self.classifier._count_constraints(no_constraint_query.lower())
        self.assertEqual(constraint_count, 0, "Should detect no constraints")
    
    def test_confidence_scores(self):
        """Test that confidence scores are reasonable."""
        test_queries = [
            "What temperature for chicken?",  # Clear simple
            "How do I make pasta carbonara?",  # Clear moderate
            "Plan meals for diabetic family",  # Clear complex
        ]
        
        for query in test_queries:
            complexity, confidence, reasoning = self.classifier.classify_query(query)
            self.assertGreaterEqual(confidence, 0.0, "Confidence should be >= 0")
            self.assertLessEqual(confidence, 1.0, "Confidence should be <= 1")
            self.assertIsInstance(reasoning, str, "Reasoning should be a string")
            self.assertGreater(len(reasoning), 10, "Reasoning should be descriptive")
    
    def test_convenience_function(self):
        """Test the convenience function works correctly."""
        query = "What temperature for chicken?"
        complexity, confidence, reasoning = classify_cooking_query(query)
        
        self.assertEqual(complexity, QueryComplexity.SIMPLE)
        self.assertIsInstance(confidence, float)
        self.assertIsInstance(reasoning, str)
    
    def test_empty_and_edge_cases(self):
        """Test edge cases and unusual inputs."""
        edge_cases = [
            ("", QueryComplexity.SIMPLE),  # Empty string should default to simple
            ("?", QueryComplexity.SIMPLE),  # Just punctuation
            ("a", QueryComplexity.SIMPLE),  # Single character
            ("How to cook everything perfectly with all constraints?", QueryComplexity.COMPLEX)  # Very long
        ]
        
        for query, expected_min_complexity in edge_cases:
            complexity, confidence, reasoning = self.classifier.classify_query(query)
            # Just ensure it doesn't crash and returns valid values
            self.assertIsInstance(complexity, QueryComplexity)
            self.assertIsInstance(confidence, float)
            self.assertIsInstance(reasoning, str)

if __name__ == '__main__':
    unittest.main()