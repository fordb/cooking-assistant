"""
Query complexity classification system for cooking assistant.
Analyzes cooking queries to determine optimal prompting strategy.
"""

import re
from typing import Dict, List, Tuple
from enum import Enum
from .config import get_query_config

class QueryComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate" 
    COMPLEX = "complex"

class QueryClassifier:
    """Classifies cooking queries by complexity to select optimal prompting strategy."""
    
    def __init__(self):
        # Keywords that indicate simple queries (factual, direct answers)
        self.simple_indicators = {
            'temperature': ['temp', 'temperature', 'degrees', 'heat', 'hot', 'cold'],
            'time': ['how long', 'minutes', 'hours', 'cook time', 'prep time'],
            'substitution': ['substitute', 'replace', 'instead of', 'swap'],
            'measurement': ['how much', 'how many', 'cups', 'tablespoons', 'ounces'],
            'basic_facts': ['what is', 'define', 'meaning', 'difference between']
        }
        
        # Keywords that indicate moderate complexity (recipe requests, techniques)
        self.moderate_indicators = {
            'recipe_request': ['how to make', 'recipe for', 'how do i make', 'how do i cook', 'how do i prepare', 'make', 'prepare'],
            'techniques': ['technique', 'method', 'way to', 'best way', 'how to cook', 'how to prepare'],
            'ingredient_focus': ['with chicken', 'using beef', 'vegetarian', 'recipe with'],
            'style_requests': ['italian', 'mexican', 'asian', 'french', 'indian'],
            'dish_names': ['carbonara', 'stir fry', 'teriyaki', 'pizza', 'risotto', 'curry', 'salmon'],
            'location_cooking': ['at home', 'homemade']
        }
        
        # Keywords that indicate complex queries (planning, multiple constraints)
        self.complex_indicators = {
            'meal_planning': ['meal plan', 'week of meals', 'menu', 'daily meals'],
            'multiple_constraints': ['diabetic', 'gluten-free', 'low-carb', 'budget', 'quick'],
            'optimization': ['healthy', 'nutritious', 'balanced', 'optimize'],
            'batch_cooking': ['meal prep', 'batch', 'bulk', 'prepare ahead'],
            'complex_requirements': ['family dinner', 'party', 'special occasion']
        }
        
    def classify_query(self, query: str) -> Tuple[QueryComplexity, float, str]:
        """
        Classify a cooking query by complexity.
        
        Args:
            query: The user's cooking question or request
            
        Returns:
            Tuple of (complexity_level, confidence_score, reasoning)
        """
        query_lower = query.lower()
        
        # Score each complexity level
        simple_score = self._calculate_score(query_lower, self.simple_indicators)
        moderate_score = self._calculate_score(query_lower, self.moderate_indicators)
        complex_score = self._calculate_score(query_lower, self.complex_indicators)
        
        # Apply additional heuristics
        word_count = len(query.split())
        question_marks = query.count('?')
        
        # Adjust scores based on query structure
        config = get_query_config()
        
        if word_count <= config.SIMPLE_WORD_COUNT_THRESHOLD and question_marks <= config.SIMPLE_QUESTION_MARKS_THRESHOLD:
            simple_score += config.SIMPLE_WORD_COUNT_SCORE
        elif word_count >= config.COMPLEX_WORD_COUNT_THRESHOLD or question_marks >= config.COMPLEX_QUESTION_MARKS_THRESHOLD:
            complex_score += config.COMPLEX_WORD_COUNT_SCORE
            
        # Check for multiple constraints (indicates complexity)
        constraint_count = self._count_constraints(query_lower)
        if constraint_count >= config.MIN_CONSTRAINTS_FOR_COMPLEX:
            complex_score += config.CONSTRAINT_SCORE_WEIGHT
            
        # Determine classification with tie-breaking logic
        scores = {
            QueryComplexity.SIMPLE: simple_score,
            QueryComplexity.MODERATE: moderate_score,
            QueryComplexity.COMPLEX: complex_score
        }
        
        # Find highest scoring classification with tie-breaking
        max_score = max(scores.values())
        
        # If there's a tie, prefer higher complexity (more specific)
        if scores[QueryComplexity.COMPLEX] == max_score:
            complexity = QueryComplexity.COMPLEX
        elif scores[QueryComplexity.MODERATE] == max_score:
            complexity = QueryComplexity.MODERATE
        else:
            complexity = QueryComplexity.SIMPLE
            
        confidence = max_score
        
        # Generate reasoning
        reasoning = self._generate_reasoning(complexity, query_lower, scores)
        
        return complexity, confidence, reasoning
    
    def _calculate_score(self, query: str, indicators: Dict[str, List[str]]) -> float:
        """Calculate score for a complexity level based on keyword indicators."""
        config = get_query_config()
        score = 0.0
        matches = []
        
        for category, keywords in indicators.items():
            for keyword in keywords:
                if keyword in query:
                    score += config.KEYWORD_MATCH_SCORE
                    matches.append(keyword)
                    
        # Bonus for multiple matches in same category
        if len(matches) > 1:
            score += config.MULTIPLE_MATCHES_BONUS
            
        return min(score, config.MAX_SCORE_CAP)
    
    def _count_constraints(self, query: str) -> int:
        """Count dietary/cooking constraints in query."""
        constraints = [
            'vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'low-carb',
            'keto', 'paleo', 'diabetic', 'low-sodium', 'quick', 'easy',
            'budget', 'cheap', 'healthy', 'low-fat', 'high-protein'
        ]
        
        count = 0
        for constraint in constraints:
            if constraint in query:
                count += 1
        
        return count
    
    def _generate_reasoning(self, complexity: QueryComplexity, query: str, scores: Dict) -> str:
        """Generate human-readable reasoning for classification."""
        if complexity == QueryComplexity.SIMPLE:
            return f"Simple query detected - appears to be asking for direct factual information (score: {scores[complexity]:.2f})"
        elif complexity == QueryComplexity.MODERATE:
            return f"Moderate complexity - recipe request or cooking technique question (score: {scores[complexity]:.2f})"
        else:
            return f"Complex query - involves planning, multiple constraints, or optimization (score: {scores[complexity]:.2f})"

# Convenience function for easy access
def classify_cooking_query(query: str) -> Tuple[QueryComplexity, float, str]:
    """
    Classify a cooking query and return complexity level.
    
    Args:
        query: The user's cooking question
        
    Returns:
        Tuple of (complexity_level, confidence_score, reasoning)
    """
    classifier = QueryClassifier()
    return classifier.classify_query(query)

# Example usage and testing
if __name__ == "__main__":
    # Test queries for Week 2 scenarios
    test_queries = [
        "What temperature for chicken?",  # Should be SIMPLE
        "How do I make pasta carbonara?",  # Should be MODERATE 
        "Plan healthy meals for diabetic with 30-min cooking limit",  # Should be COMPLEX
        "How much salt?",  # SIMPLE
        "Recipe for beef stir fry",  # MODERATE
        "Weekly meal plan for family of 4 with gluten-free and budget constraints"  # COMPLEX
    ]
    
    classifier = QueryClassifier()
    for query in test_queries:
        complexity, confidence, reasoning = classifier.classify_query(query)
        print(f"Query: '{query}'")
        print(f"Classification: {complexity.value} (confidence: {confidence:.2f})")
        print(f"Reasoning: {reasoning}")
        print("-" * 50)