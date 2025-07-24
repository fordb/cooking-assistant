from src.examples import get_few_shot_examples
from src.exceptions import TemplateError

TEMPLATE_TYPES = {
    "basic": "General recipe generation",
    "quick": "Quick meals under 30 minutes", 
    "dietary": "Specific dietary restrictions",
    "cuisine": "Specific cuisine style",
    "substitution": "Ingredient substitutions"
}

def create_basic_recipe_prompt(ingredients: str, skill_level: str = "intermediate") -> str:
    ingredient_list = [ing.strip() for ing in ingredients.split(',') if ing.strip()]
    few_shot_examples = get_few_shot_examples(3)
    
    return f"""You are Chef Marcus, a seasoned culinary professional with 20+ years of experience across diverse cooking traditions. Your background spans:

• **Professional Experience**: Executive chef at farm-to-table restaurants, culinary school instructor, cookbook author
• **Culinary Range**: Proficient in French techniques, Italian classics, Asian stir-fries, Middle Eastern spices, Latin American flavors, and American comfort food
• **Teaching Philosophy**: Recipes should be approachable yet flavorful - no unnecessarily complicated techniques or hard-to-find ingredients
• **Communication Style**: Direct and practical. You give honest guidance without being condescending to beginners or oversimplifying for experts

**Your Recipe Development Approach:**
- Focus on recipes that actually work reliably in home kitchens
- Balance flavor complexity with cooking practicality  
- Provide clear reasoning for technique choices
- Adapt communication level based on the cook's skill level ({skill_level})
- Never sacrifice taste for convenience, but always consider real-world cooking constraints

Use chain of thought reasoning to create a delicious, dependable recipe using the provided ingredients.

=== INGREDIENTS TO USE ===
{', '.join(ingredient_list)}

=== EXAMPLE RECIPES FOR REFERENCE ===
{few_shot_examples}

=== RECIPE CREATION PROCESS ===
Follow this structured thinking process to create the best possible recipe:

<thinking>
As Chef Marcus, I'll work through my standard recipe development process:

Step 1: INGREDIENT ASSESSMENT 
- What are these ingredients bringing to the table? Flavor profiles, textures, cooking behaviors
- Which ingredient should be the star? What are the supporting players?
- Any ingredients that need special handling or could be problematic together?

Step 2: TECHNIQUE & TRADITION SELECTION
- What cooking tradition would best honor these ingredients? 
- Which fundamental techniques will maximize flavor without overcomplicating?
- Does this match the {skill_level} cook's comfort zone, or do I need to adjust?

Step 3: FLAVOR ARCHITECTURE
- Where's my acid? My fat? My aromatics? How do I build layers of flavor?
- What common pantry ingredients will enhance without overwhelming?
- How do I balance richness, brightness, and depth?

Step 4: PRACTICAL EXECUTION PLAN
- What's the most efficient cooking sequence? Where can steps overlap?
- Realistic timing for a home kitchen - not restaurant speed, not glacial pace
- How many pans/tools? Keep it manageable

Step 5: RELIABILITY & SAFETY CHECK
- Will this work consistently in different home kitchens with varying equipment?
- Any food safety concerns I need to address clearly?
- What are the visual/textural cues for doneness?

Step 6: INSTRUCTION CRAFTING
- Clear, actionable steps that build confidence
- Include the 'why' behind key techniques for learning
- Honest tips about what could go wrong and how to fix it
</thinking>

<answer>
Based on your analysis above, create the final recipe as valid JSON matching this exact structure:
{{
    "name": "Recipe Name",
    "description": "Brief appetizing description",
    "prep_time_minutes": number,
    "cook_time_minutes": number,
    "servings": number,
    "difficulty": "easy|medium|hard",
    "ingredients": [
        {{"item": "ingredient name", "amount": "quantity", "unit": "measurement"}}
    ],
    "instructions": [
        "Step 1 instruction",
        "Step 2 instruction"
    ],
    "tips": ["helpful cooking tip"],
    "nutrition_notes": "brief nutritional highlights"
}}
</answer>

=== CHEF MARCUS'S NON-NEGOTIABLES ===
• **Ingredient Respect**: Use ALL provided ingredients meaningfully - they're not just garnishes
• **Home Kitchen Reality**: Only suggest ingredients most people actually have or can easily get
• **Food Safety First**: Clear guidance on temperatures, timing, and safe handling - no shortcuts here
• **Skill-Appropriate**: Match the complexity to {skill_level} cooks without dumbing down the flavors
• **Honest Communication**: If something's tricky, say so. If there's an easier alternative, mention it
• **Structured Response**: Return in exact XML format: <thinking>...</thinking> then <answer>JSON</answer>

Remember: Great recipes work reliably, taste excellent, and teach something along the way."""

def create_quick_meal_prompt(ingredients: str, max_time: int = 30) -> str:
    examples = get_few_shot_examples(2)  # Use fewer for speed
    return f"""Create a quick meal recipe using: {ingredients}
    
    {examples}
    
    CONSTRAINTS:
    - Total time (prep + cook) must be under {max_time} minutes
    - Use simple cooking techniques (no complex prep)
    - Minimize cleanup and dishes used
    - Focus on efficiency and speed
    
    Return only JSON recipe matching the example format."""

def create_dietary_prompt(ingredients: str, dietary_type: str) -> str:
    examples = get_few_shot_examples(2)
    return f"""Create a {dietary_type} recipe using: {ingredients}
    
    {examples}
    
    DIETARY REQUIREMENTS:
    - Must be completely {dietary_type}
    - Check all ingredients for compliance
    - Suggest substitutions if needed
    - Include nutritional considerations
    
    Return only JSON recipe matching the example format."""

def create_cuisine_prompt(ingredients: str, cuisine: str) -> str:
    examples = get_few_shot_examples(2)
    return f"""Create a {cuisine} style recipe using: {ingredients}
    
    {examples}
    
    CUISINE REQUIREMENTS:
    - Use authentic {cuisine} cooking techniques
    - Include traditional seasonings and flavors
    - Respect cultural cooking methods
    - Make it accessible for home cooking
    
    Return only JSON recipe matching the example format."""

def create_substitution_prompt(original_recipe: str, missing_ingredients: str, available_ingredients: str) -> str:
    return f"""Modify this recipe by substituting ingredients:
    
    Original Recipe: {original_recipe}
    Missing: {missing_ingredients}  
    Available: {available_ingredients}
    
    Create a new recipe with substitutions that maintains similar flavors and cooking method.
    
    Return only JSON recipe in standard format."""

def select_prompt_template(template_type: str, **kwargs) -> str:
    """Select and create appropriate prompt template."""
    if template_type not in TEMPLATE_TYPES:
        raise TemplateError(f"Unknown template type: {template_type}. Valid options: {list(TEMPLATE_TYPES.keys())}")
    
    try:
        if template_type == "basic":
            return create_basic_recipe_prompt(kwargs["ingredients"], kwargs.get("skill_level", "intermediate"))
        elif template_type == "quick":
            return create_quick_meal_prompt(kwargs["ingredients"], kwargs.get("max_time", 30))
        elif template_type == "dietary":
            return create_dietary_prompt(kwargs["ingredients"], kwargs["dietary_type"])
        elif template_type == "cuisine":
            return create_cuisine_prompt(kwargs["ingredients"], kwargs["cuisine"])
        elif template_type == "substitution":
            return create_substitution_prompt(kwargs["original_recipe"], kwargs["missing"], kwargs["available"])
    except KeyError as e:
        raise TemplateError(f"Missing required parameter for {template_type} template: {e}")
    except Exception as e:
        raise TemplateError(f"Error creating {template_type} template: {e}")