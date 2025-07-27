"""
Demo and testing functions for cooking assistant.
Contains example usage and testing utilities.
"""

from src.examples import load_example_recipes, get_few_shot_examples
from src.prompts import TEMPLATE_TYPES, select_prompt_template
from src.query_classifier import classify_cooking_query, QueryComplexity
from src.core import CookingAssistant
from src.exceptions import CookingAssistantError

def demo_examples():
    """Load and display example recipes."""
    print("🧑‍🍳 Example Recipes Demo")
    print("=" * 50)
    
    try:
        recipes = load_example_recipes()
        print(f"Loaded {len(recipes)} example recipes:")
        
        for i, recipe in enumerate(recipes[:5], 1):  # Show first 5
            print(f"\n{i}. {recipe.title}")
            print(f"   Difficulty: {recipe.difficulty} | Time: {recipe.total_time} min | Serves: {recipe.servings}")
            print(f"   Ingredients: {len(recipe.ingredients)} | Steps: {len(recipe.instructions)}")
            
    except Exception as e:
        print(f"❌ Error loading examples: {e}")

def demo_prompt_templates():
    """Demonstrate all prompt template types."""
    print("\n🧑‍🍳 Prompt Templates Demo")
    print("=" * 50)
    
    ingredients = "chicken, rice, vegetables"
    
    for template_type, description in TEMPLATE_TYPES.items():
        print(f"\n{template_type.upper()} Template ({description}):")
        print("-" * 40)
        
        try:
            if template_type == "dietary":
                prompt = select_prompt_template(template_type, ingredients=ingredients, dietary_type="vegetarian")
            elif template_type == "cuisine":
                prompt = select_prompt_template(template_type, ingredients=ingredients, cuisine="Italian")
            elif template_type == "substitution":
                prompt = select_prompt_template(template_type, 
                                              original_recipe="Chicken Rice Bowl",
                                              missing="chicken",
                                              available="tofu")
            else:
                prompt = select_prompt_template(template_type, ingredients=ingredients)
            
            # Show first 200 characters of prompt
            print(f"Prompt preview: {prompt[:200]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")

def demo_template_usage():
    """Show usage examples for each template type."""
    print("\n🧑‍🍳 Template Usage Guide")
    print("=" * 50)
    
    usage_examples = {
        "basic": "general recipe generation with any ingredients",
        "quick": "meals that can be prepared in under 30 minutes",
        "dietary": "recipes for specific dietary needs (vegetarian, vegan, gluten-free, etc.)",
        "cuisine": "recipes in specific cuisine styles (Italian, Mexican, Asian, etc.)",
        "substitution": "modify existing recipes by substituting unavailable ingredients"
    }
    
    for template_type, usage in usage_examples.items():
        print(f"\n{template_type.upper()}: {usage}")

def demo_query_classification():
    """Test query classification system."""
    print("🔍 Query Classification Demo")
    print("=" * 40)
    
    test_queries = [
        "What temperature for chicken?",
        "How long to cook rice?", 
        "Substitute for eggs?",
        "How to make pasta carbonara?",
        "Recipe for beef stir fry",
        "Best way to cook salmon?",
        "Plan weekly meals for family of 4",
        "Healthy meal prep ideas for diabetic",
        "Budget-friendly vegetarian dinners for busy weeknights"
    ]
    
    for query in test_queries:
        complexity, confidence, reasoning = classify_cooking_query(query)
        print(f"\nQuery: '{query}'")
        print(f"📊 {complexity.value} (confidence: {confidence:.2f})")
        print(f"💭 {reasoning}")
        print("-" * 50)

def demo_week2_scenarios():
    """Demonstrate Week 2 scenarios: zero-shot, few-shot, and chain-of-thought."""
    print("🎯 Week 2 Advanced Prompting Scenarios")
    print("=" * 50)
    
    scenarios = [
        {
            'name': 'Simple Query (Zero-shot)',
            'query': 'What temperature for chicken?',
            'expected': 'Simple factual question should use zero-shot prompting'
        },
        {
            'name': 'Moderate Query (Few-shot)', 
            'query': 'How do I make pasta carbonara?',
            'expected': 'Recipe request should use few-shot prompting with examples'
        },
        {
            'name': 'Complex Query (Chain-of-thought)',
            'query': 'Plan healthy meals for diabetic with 30-min cooking limit',
            'expected': 'Complex planning should use chain-of-thought reasoning'
        }
    ]
    
    # Create fresh assistant for demo
    assistant = CookingAssistant()
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print("-" * 40)
        print(f"Query: '{scenario['query']}'")
        print(f"Expected: {scenario['expected']}")
        
        try:
            # Classify query
            classification = assistant.classify_query(scenario['query'])
            print(f"🎯 Classification: {classification['complexity']} (confidence: {classification['confidence']:.2f})")
            
            # Process with cooking assistant
            result = assistant.ask(scenario['query'])
            
            print(f"✅ Strategy used: {result['strategy']}")
            print(f"📝 Response preview: {result['response'][:150]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue to next scenario...")

def demo_conversation():
    """Demonstrate conversation mode with memory."""
    print("🧑‍🍳 Conversation Demo")
    print("=" * 30)
    print("This demo shows how the assistant remembers preferences and context.")
    print("Commands: 'memory' to see status, 'quit' to exit")
    
    assistant = CookingAssistant()
    
    while True:
        print("\n" + "=" * 50)
        query = input("💬 Ask a cooking question: ")
        
        if query.lower() == 'quit':
            summary = assistant.get_memory_status()
            print("\n📊 Session Summary:")
            print(f"Questions asked: {summary['turns_count']}")
            print(f"Duration: {summary['duration_minutes']:.1f} minutes")
            print("👋 Demo complete!")
            break
            
        elif query.lower() == 'memory':
            prefs = assistant.get_preferences()
            print("\n🧠 Current Preferences:")
            for key, value in prefs.items():
                if value:
                    print(f"  {key}: {value}")
            continue
        
        try:
            result = assistant.ask(query)
            
            print(f"\n📋 Strategy: {result['strategy']} (complexity: {result['complexity']})")
            print(f"🧑‍🍳 Response:")
            print("-" * 40)
            print(result['response'])
            
        except Exception as e:
            print(f"❌ Error: {e}")

def run_evaluation_demo():
    """Run recipe evaluation pipeline demo."""
    try:
        from evaluations.run_eval import run_evaluation
        print("🔄 Running evaluation demo...")
        run_evaluation(category="basic", sample_size=3)  # Small demo
    except ImportError:
        print("❌ Evaluation module not available. Run: python -m evaluations.run_eval")
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")

if __name__ == "__main__":
    print("🎯 Cooking Assistant Demos")
    print("=" * 40)
    print("Available demos:")
    print("1. Examples - Show recipe examples")
    print("2. Templates - Demonstrate prompt templates") 
    print("3. Classification - Test query classification")
    print("4. Week 2 Scenarios - Advanced prompting demo")
    print("5. Conversation - Interactive conversation demo")
    print("6. Evaluation - Run evaluation demo")
    
    while True:
        choice = input("\nChoose demo (1-6) or 'quit': ").strip()
        
        if choice == 'quit':
            break
        elif choice == '1':
            demo_examples()
        elif choice == '2':
            demo_prompt_templates()
        elif choice == '3':
            demo_query_classification()
        elif choice == '4':
            demo_week2_scenarios()
        elif choice == '5':
            demo_conversation()
        elif choice == '6':
            run_evaluation_demo()
        else:
            print("❌ Invalid choice. Please enter 1-6 or 'quit'.")