"""Advanced prompting system with meta-prompting and template management."""

from .meta_prompting import MetaPromptingSystem, process_cooking_query
from .prompts import select_prompt_template
from .examples import load_example_recipes, get_few_shot_examples

__all__ = [
    'MetaPromptingSystem',
    'process_cooking_query',
    'select_prompt_template',
    'load_example_recipes',
    'get_few_shot_examples'
]