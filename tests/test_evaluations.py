"""
Unit tests for the evaluation framework.
"""

import unittest
from unittest.mock import patch, MagicMock
from evaluations.test_cases import get_test_cases, get_test_case_summary
from evaluations.evaluator import RecipeEvaluator, EvaluationScore, RecipeEvaluation
from evaluations.results import EvaluationResults
from src.recipes.models import Recipe


class TestEvaluationFramework(unittest.TestCase):
    
    def test_get_test_cases_all(self):
        """Test getting all test cases."""
        test_cases = get_test_cases("all")
        self.assertGreater(len(test_cases), 20)  # Should have at least 20 test cases
        
        # Check that each test case has required fields
        for test_case in test_cases:
            self.assertIn("ingredients", test_case)
    
    def test_get_test_cases_by_category(self):
        """Test getting test cases by specific category."""
        basic_cases = get_test_cases("basic")
        quick_cases = get_test_cases("quick")
        
        self.assertGreater(len(basic_cases), 0)
        self.assertGreater(len(quick_cases), 0)
        
        # Verify category-specific content
        for case in quick_cases:
            self.assertEqual(case.get("template_type", "basic"), "quick")
    
    def test_get_test_case_summary(self):
        """Test test case summary statistics."""
        summary = get_test_case_summary()
        
        # Check expected structure
        expected_keys = ["basic", "quick", "dietary", "cuisine", "substitution", "edge_cases", "total"]
        for key in expected_keys:
            self.assertIn(key, summary)
            self.assertIsInstance(summary[key], int)
            self.assertGreaterEqual(summary[key], 0)
        
        # Total should equal sum of categories
        category_sum = sum(summary[key] for key in expected_keys[:-1])
        self.assertEqual(summary["total"], category_sum)
    
    def test_evaluation_score_structure(self):
        """Test EvaluationScore dataclass."""
        score = EvaluationScore(
            metric="Test Metric",
            score=4,
            reasoning="This is a test reasoning"
        )
        
        self.assertEqual(score.metric, "Test Metric")
        self.assertEqual(score.score, 4)
        self.assertEqual(score.reasoning, "This is a test reasoning")
    
    def test_recipe_evaluation_structure(self):
        """Test RecipeEvaluation dataclass."""
        # Create mock recipe
        mock_recipe = Recipe(
            title="Test Recipe",
            prep_time=10,
            cook_time=20,
            servings=4,
            difficulty="Beginner",
            ingredients=["ingredient1", "ingredient2"],
            instructions=["step1", "step2", "step3"]
        )
        
        scores = [
            EvaluationScore("Metric 1", 4, "Good"),
            EvaluationScore("Metric 2", 3, "Average")
        ]
        
        evaluation = RecipeEvaluation(
            test_case="test ingredients",
            template_type="basic",
            recipe=mock_recipe,
            scores=scores,
            performance_metrics={"time": 1.5}
        )
        
        self.assertEqual(evaluation.test_case, "test ingredients")
        self.assertEqual(evaluation.template_type, "basic")
        self.assertEqual(evaluation.recipe, mock_recipe)
        self.assertEqual(len(evaluation.scores), 2)
        self.assertEqual(evaluation.average_score, 3.5)  # (4 + 3) / 2
    
    def test_recipe_evaluator_initialization(self):
        """Test RecipeEvaluator initialization."""
        evaluator = RecipeEvaluator(judge_model="test-model")
        self.assertEqual(evaluator.judge_model, "test-model")
        self.assertIsNotNone(evaluator.evaluation_prompt)
        self.assertIn("culinary", evaluator.evaluation_prompt.lower())
    
    @patch('evaluations.evaluator.OpenAI')
    def test_evaluation_with_mock_api(self, mock_openai_class):
        """Test evaluation with mocked OpenAI API."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "culinary_logic": {"score": 4, "reasoning": "Makes sense"},
            "ingredient_usage": {"score": 5, "reasoning": "All ingredients used"},
            "instruction_clarity": {"score": 3, "reasoning": "Could be clearer"},
            "overall_quality": {"score": 4, "reasoning": "Would cook this"}
        }
        '''
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Mock CookingAssistant
        with patch('evaluations.evaluator.CookingAssistant') as mock_assistant_class:
            mock_assistant = MagicMock()
            mock_assistant.ask.return_value = {
                'response': '''
                {
                    "title": "Test Recipe",
                    "prep_time": 10,
                    "cook_time": 20,
                    "servings": 4,
                    "difficulty": "Beginner",
                    "ingredients": ["ingredient1", "ingredient2"],
                    "instructions": ["step1", "step2", "step3"]
                }
                ''',
                'strategy': 'test',
                'success': True
            }
            mock_assistant_class.return_value = mock_assistant
            
            evaluator = RecipeEvaluator()
            result = evaluator.evaluate_recipe("test ingredients")
            
            # Verify evaluation structure
            self.assertIsInstance(result, RecipeEvaluation)
            self.assertEqual(result.test_case, "test ingredients")
            self.assertEqual(result.template_type, "basic")
            self.assertIsNotNone(result.recipe)
            self.assertEqual(len(result.scores), 4)  # 4 evaluation metrics
            self.assertTrue(result.performance_metrics["success"])
    
    def test_evaluation_results_initialization(self):
        """Test EvaluationResults initialization."""
        results = EvaluationResults("test_results.json")
        self.assertEqual(results.results_file, "test_results.json")
        self.assertIn("evaluations/results", results.results_path)


if __name__ == '__main__':
    unittest.main()