"""
Meta-prompting system for cooking assistant.
Automatically selects optimal prompting strategies based on query complexity.
"""

from typing import Dict, Any, Optional, Tuple
from openai import OpenAI
from config import OPENAI_API_KEY
from src.query_classifier import QueryClassifier, QueryComplexity
from src.prompts import select_prompt_template
from src.exceptions import RecipeGenerationError
from src.config import get_openai_config, get_prompt_config
import json

class PromptingStrategy:
    """Defines different prompting strategies for different complexity levels."""
    
    @staticmethod
    def zero_shot_prompt(query: str, context: Optional[Dict] = None) -> str:
        """Simple, direct prompting for factual questions."""
        return f"""You are a knowledgeable cooking assistant. Answer this cooking question directly and concisely:

Question: {query}

Provide a clear, practical answer in 1-3 sentences. Focus on the specific information requested."""

    @staticmethod
    def few_shot_prompt(query: str, context: Optional[Dict] = None) -> str:
        """Recipe generation with examples for moderate complexity queries."""
        from src.examples import get_few_shot_examples
        
        # Extract ingredients if mentioned in query
        ingredients = MetaPromptingSystem._extract_ingredients(query)
        
        if ingredients:
            # Use existing template system for recipe generation
            return select_prompt_template("basic", ingredients=ingredients)
        else:
            # General cooking question with examples
            config = get_prompt_config()
            examples = get_few_shot_examples(config.QUICK_EXAMPLES_COUNT)
            return f"""You are a skilled cooking assistant. Here are some example recipes for reference:

{examples}

Now answer this cooking question with detailed, practical guidance:

Question: {query}

Provide step-by-step instructions or detailed explanation as appropriate."""

    @staticmethod  
    def chain_of_thought_prompt(query: str, context: Optional[Dict] = None) -> str:
        """Complex reasoning for multi-constraint planning problems."""
        constraints = MetaPromptingSystem._extract_constraints(query)
        
        return f"""You are Chef Marcus, an expert culinary consultant specializing in complex meal planning and dietary optimization.

Use structured reasoning to solve this complex cooking challenge:

<thinking>
Let me break down this request systematically:

1. CONSTRAINT ANALYSIS
   - What are the specific requirements and limitations?
   - Which constraints are mandatory vs. preferred?
   - Any potential conflicts between constraints?

2. NUTRITIONAL CONSIDERATIONS  
   - What dietary needs must be addressed?
   - How to balance nutrition within the constraints?
   - Any special considerations for health conditions?

3. PRACTICAL PLANNING
   - Time management and prep strategies
   - Equipment and skill level requirements
   - Shopping and ingredient accessibility

4. OPTIMIZATION STRATEGY
   - How to maximize nutrition/flavor within constraints?
   - What trade-offs or substitutions might be needed?
   - How to make this sustainable long-term?

5. SOLUTION SYNTHESIS
   - Specific recommendations that address all requirements
   - Practical implementation steps
   - Backup options or alternatives
</thinking>

Query: {query}
Detected constraints: {', '.join(constraints) if constraints else 'None specified'}

Provide a comprehensive solution with detailed reasoning and actionable recommendations."""

class MetaPromptingSystem:
    """Orchestrates prompting strategy selection based on query analysis."""
    
    def __init__(self):
        self.classifier = QueryClassifier()
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    def process_query(self, query: str, conversation_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a cooking query using optimal prompting strategy.
        
        Args:
            query: User's cooking question or request
            conversation_context: Optional context from conversation memory
            
        Returns:
            Dictionary with response, strategy used, and metadata
        """
        # Classify query complexity
        complexity, confidence, reasoning = self.classifier.classify_query(query)
        
        # Select and execute prompting strategy
        strategy_name, prompt = self._select_strategy(complexity, query, conversation_context)
        
        # Generate response
        try:
            response = self._generate_response(prompt, complexity)
            
            return {
                'response': response,
                'strategy': strategy_name,
                'complexity': complexity.value,
                'confidence': confidence,
                'reasoning': reasoning,
                'success': True
            }
            
        except Exception as e:
            return {
                'response': f"Sorry, I encountered an error: {str(e)}",
                'strategy': strategy_name,
                'complexity': complexity.value,
                'confidence': confidence,
                'reasoning': reasoning,
                'success': False,
                'error': str(e)
            }
    
    def _select_strategy(self, complexity: QueryComplexity, query: str, context: Optional[Dict]) -> Tuple[str, str]:
        """Select appropriate prompting strategy based on complexity."""
        
        if complexity == QueryComplexity.SIMPLE:
            strategy_name = "zero_shot"
            prompt = PromptingStrategy.zero_shot_prompt(query, context)
            
        elif complexity == QueryComplexity.MODERATE:
            strategy_name = "few_shot" 
            prompt = PromptingStrategy.few_shot_prompt(query, context)
            
        else:  # COMPLEX
            strategy_name = "chain_of_thought"
            prompt = PromptingStrategy.chain_of_thought_prompt(query, context)
            
        return strategy_name, prompt
    
    def _generate_response(self, prompt: str, complexity: QueryComplexity) -> str:
        """Generate response using OpenAI API."""
        
        # Adjust model parameters based on complexity
        config = get_openai_config()
        temperature = config.SIMPLE_TEMPERATURE if complexity == QueryComplexity.SIMPLE else config.COMPLEX_TEMPERATURE
        max_tokens = config.SIMPLE_MAX_TOKENS if complexity == QueryComplexity.SIMPLE else config.COMPLEX_MAX_TOKENS
        
        try:
            response = self.client.chat.completions.create(
                model=config.DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise RecipeGenerationError(f"Failed to generate response: {e}")
    
    @staticmethod
    def _extract_ingredients(query: str) -> str:
        """Extract ingredient mentions from query."""
        # Simple keyword-based extraction
        ingredient_keywords = [
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'shrimp',
            'rice', 'pasta', 'noodles', 'bread', 'eggs',
            'tomato', 'onion', 'garlic', 'pepper', 'mushroom',
            'cheese', 'milk', 'butter', 'oil', 'flour'
        ]
        
        found_ingredients = []
        query_lower = query.lower()
        
        for ingredient in ingredient_keywords:
            if ingredient in query_lower:
                found_ingredients.append(ingredient)
                
        return ', '.join(found_ingredients[:5])  # Limit to 5 ingredients
    
    @staticmethod
    def _extract_constraints(query: str) -> list:
        """Extract dietary and cooking constraints from query."""
        constraints = [
            'vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'low-carb',
            'keto', 'paleo', 'diabetic', 'low-sodium', 'healthy', 'quick',
            'budget', 'cheap', 'easy', 'low-fat', 'high-protein', 'meal prep'
        ]
        
        found_constraints = []
        query_lower = query.lower()
        
        for constraint in constraints:
            if constraint in query_lower:
                found_constraints.append(constraint)
                
        return found_constraints

# Convenience function for easy integration
def process_cooking_query(query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Process a cooking query using meta-prompting system.
    
    Args:
        query: User's cooking question
        context: Optional conversation context
        
    Returns:
        Response with strategy and metadata
    """
    system = MetaPromptingSystem()
    return system.process_query(query, context)

# Example usage and testing
if __name__ == "__main__":
    # Test Week 2 scenarios
    test_scenarios = [
        "What temperature for chicken?",  # Simple → Zero-shot
        "How do I make pasta carbonara?",  # Moderate → Few-shot
        "Plan healthy meals for diabetic with 30-min cooking limit"  # Complex → Chain-of-thought
    ]
    
    system = MetaPromptingSystem()
    
    for query in test_scenarios:
        print(f"Query: '{query}'")
        result = system.process_query(query)
        print(f"Strategy: {result['strategy']} (complexity: {result['complexity']})")
        print(f"Reasoning: {result['reasoning']}")
        print(f"Response preview: {result['response'][:100]}...")
        print("-" * 60)