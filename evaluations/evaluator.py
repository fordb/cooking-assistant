"""
Core evaluation logic for recipe generation quality assessment.
"""

import time
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dataclasses import dataclass
from config import OPENAI_API_KEY
from src.models import Recipe
from src.recipe_generator import generate_recipe
from src.config import get_logger

logger = get_logger(__name__)


@dataclass
class EvaluationScore:
    """Single evaluation metric score with reasoning."""
    metric: str
    score: int  # 1-5 scale
    reasoning: str
    

@dataclass
class RecipeEvaluation:
    """Complete evaluation results for a single recipe."""
    test_case: str
    template_type: str
    recipe: Optional[Recipe]
    scores: List[EvaluationScore]
    performance_metrics: Dict[str, Any]
    error: Optional[str] = None
    
    @property
    def average_score(self) -> float:
        """Calculate average quality score."""
        if not self.scores:
            return 0.0
        return sum(score.score for score in self.scores) / len(self.scores)


class RecipeEvaluator:
    """Main recipe evaluation class using LLM-as-a-judge."""
    
    def __init__(self, judge_model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.judge_model = judge_model
        self.evaluation_prompt = self._create_evaluation_prompt()
    
    def _create_evaluation_prompt(self) -> str:
        """Create the evaluation prompt for LLM-as-a-judge."""
        return """You are a professional chef and culinary instructor tasked with evaluating AI-generated recipes. 

Rate the recipe on these 4 dimensions using a 1-5 scale:

1. **Culinary Logic** (1-5): Does this recipe make culinary sense? Are techniques appropriate, seasoning balanced, and ingredient combinations logical?

2. **Ingredient Usage** (1-5): Are ALL provided ingredients used meaningfully in the recipe? Not just added as garnish, but integral to the dish?

3. **Instruction Clarity** (1-5): Are the cooking steps clear, properly sequenced, and actionable for a home cook?

4. **Overall Quality** (1-5): Would you personally cook and serve this recipe? Does it seem like it would taste good?

For each dimension, provide:
- Score (1-5 where 5 is excellent)
- Brief reasoning (1-2 sentences)

RECIPE TO EVALUATE:
Ingredients Used: {ingredients}
Template Type: {template_type}

{recipe_json}

Respond in this exact JSON format:
{{
    "culinary_logic": {{"score": X, "reasoning": "explanation"}},
    "ingredient_usage": {{"score": X, "reasoning": "explanation"}},  
    "instruction_clarity": {{"score": X, "reasoning": "explanation"}},
    "overall_quality": {{"score": X, "reasoning": "explanation"}}
}}"""

    def evaluate_recipe(self, ingredients: str, template_type: str = "basic", **kwargs) -> RecipeEvaluation:
        """Evaluate a single recipe generation."""
        start_time = time.time()
        error = None
        recipe = None
        scores = []
        
        # Performance tracking
        performance_metrics = {
            "start_time": start_time,
            "generation_time": 0,
            "evaluation_time": 0,
            "total_tokens": 0,
            "success": False
        }
        
        try:
            # Generate recipe
            recipe = generate_recipe(ingredients, template_type, **kwargs)
            generation_time = time.time() - start_time
            performance_metrics["generation_time"] = generation_time
            performance_metrics["success"] = True
            
            # Evaluate with LLM judge
            eval_start = time.time()
            scores = self._judge_recipe(ingredients, template_type, recipe)
            eval_time = time.time() - eval_start
            performance_metrics["evaluation_time"] = eval_time
            
        except Exception as e:
            error = str(e)
            performance_metrics["success"] = False
        
        performance_metrics["total_time"] = time.time() - start_time
        
        return RecipeEvaluation(
            test_case=ingredients,
            template_type=template_type,
            recipe=recipe,
            scores=scores,
            performance_metrics=performance_metrics,
            error=error
        )
    
    def _judge_recipe(self, ingredients: str, template_type: str, recipe: Recipe) -> List[EvaluationScore]:
        """Use LLM to judge recipe quality."""
        prompt = self.evaluation_prompt.format(
            ingredients=ingredients,
            template_type=template_type,
            recipe_json=recipe.model_dump_json(indent=2)
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.judge_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1  # Low temperature for consistent evaluation
            )
            
            result_text = response.choices[0].message.content
            
            # Parse the JSON response
            result = json.loads(result_text)
            
            # Convert to EvaluationScore objects
            scores = []
            for metric, data in result.items():
                scores.append(EvaluationScore(
                    metric=metric.replace('_', ' ').title(),
                    score=data["score"],
                    reasoning=data["reasoning"]
                ))
            
            return scores
            
        except Exception as e:
            # Fallback to error score if evaluation fails
            return [EvaluationScore(
                metric="Evaluation Error",
                score=0,
                reasoning=f"Failed to evaluate: {str(e)}"
            )]
    
    def batch_evaluate(self, test_cases: List[Dict[str, Any]]) -> List[RecipeEvaluation]:
        """Evaluate multiple recipe generations."""
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"Evaluating {i}/{len(test_cases)}: {test_case['ingredients']}")
            
            result = self.evaluate_recipe(
                ingredients=test_case["ingredients"],
                template_type=test_case.get("template_type", "basic"),
                **test_case.get("kwargs", {})
            )
            
            results.append(result)
        
        return results