"""
Utility functions for the cooking assistant application.
Shared utilities that don't belong to specific modules.
"""

import os
from src.config import get_logger

logger = get_logger(__name__)

def check_openai_api_key() -> bool:
    """
    Check if OpenAI API key is available.
    
    Returns:
        True if API key is found
    """
    import openai
    
    # Check if API key is set in environment or openai module
    api_key = getattr(openai, 'api_key', None) or os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        logger.warning("No OpenAI API key found. Set OPENAI_API_KEY environment variable.")
        return False
    
    logger.info("OpenAI API key found")
    return True