"""
Keyword extraction utilities for sparse search functionality.
Provides text preprocessing and tokenization for BM25 search.
"""

import re
from typing import List, Set
from src.recipes.models import Recipe
from src.common.config import get_vector_config, get_logger

logger = get_logger(__name__)

# Common English stopwords for recipe text
COOKING_STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 
    'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'will', 'with',
    'add', 'then', 'into', 'over', 'until', 'about', 'all', 'also', 'can', 'or'
}

def extract_recipe_keywords(recipe: Recipe) -> List[str]:
    """
    Extract keywords from a recipe for sparse search indexing.
    
    Args:
        recipe: Recipe object to extract keywords from
        
    Returns:
        List of keywords (tokens) for BM25 indexing
    """
    config = get_vector_config()
    
    # Combine all text content from recipe
    text_content = []
    
    # Add title (with higher weight by repeating)
    text_content.extend([recipe.title] * 2)
    
    # Add ingredients
    text_content.extend(recipe.ingredients)
    
    # Add instructions
    text_content.extend(recipe.instructions)
    
    # Join all content
    full_text = ' '.join(text_content)
    
    # Tokenize and clean
    tokens = tokenize_text(full_text)
    
    # Filter by length and stopwords
    keywords = []
    for token in tokens:
        if len(token) >= config.MIN_KEYWORD_LENGTH:
            if not config.STOPWORDS_ENABLED or token.lower() not in COOKING_STOPWORDS:
                keywords.append(token.lower())
    
    logger.debug(f"Extracted {len(keywords)} keywords from recipe: {recipe.title}")
    return keywords

def tokenize_text(text: str) -> List[str]:
    """
    Tokenize text into individual words.
    
    Args:
        text: Input text to tokenize
        
    Returns:
        List of tokens
    """
    # Convert to lowercase and remove special characters
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
    
    # Split on whitespace and filter empty strings
    tokens = [token.strip() for token in text.split() if token.strip()]
    
    return tokens

def extract_query_keywords(query: str) -> List[str]:
    """
    Extract keywords from a search query for BM25 matching.
    
    Args:
        query: Search query string
        
    Returns:
        List of query keywords
    """
    config = get_vector_config()
    
    # Tokenize query
    tokens = tokenize_text(query)
    
    # Filter keywords
    keywords = []
    for token in tokens:
        if len(token) >= config.MIN_KEYWORD_LENGTH:
            if not config.STOPWORDS_ENABLED or token.lower() not in COOKING_STOPWORDS:
                keywords.append(token.lower())
    
    logger.debug(f"Extracted {len(keywords)} keywords from query: '{query}'")
    return keywords

def build_recipe_corpus(recipes: List[Recipe]) -> List[List[str]]:
    """
    Build a tokenized corpus from a list of recipes for BM25 indexing.
    
    Args:
        recipes: List of Recipe objects
        
    Returns:
        List of tokenized documents (each recipe as list of keywords)
    """
    corpus = []
    for recipe in recipes:
        keywords = extract_recipe_keywords(recipe)
        corpus.append(keywords)
    
    logger.info(f"Built BM25 corpus from {len(recipes)} recipes")
    return corpus