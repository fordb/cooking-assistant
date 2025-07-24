import os
from pathlib import Path
from dotenv import load_dotenv
from src.exceptions import ConfigurationError

# Load environment variables from .env file
load_dotenv()

def get_openai_api_key() -> str:
    """Get OpenAI API key with validation."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ConfigurationError(
            "OPENAI_API_KEY not found in environment variables. "
            "Please set it in your .env file or environment."
        )
    if not api_key.startswith("sk-"):
        raise ConfigurationError(
            "Invalid OPENAI_API_KEY format. API key should start with 'sk-'"
        )
    return api_key

def get_data_path() -> Path:
    """Get the path to the data directory."""
    return Path(__file__).parent / "data"

def get_example_recipes_path() -> Path:
    """Get the path to example recipes file."""
    path = get_data_path() / "example_recipes.json"
    if not path.exists():
        raise ConfigurationError(f"Example recipes file not found at: {path}")
    return path

# Initialize configuration
OPENAI_API_KEY = get_openai_api_key()
DATA_PATH = get_data_path()
EXAMPLE_RECIPES_PATH = get_example_recipes_path()