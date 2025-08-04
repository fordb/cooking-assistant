"""
Configuration settings for the Intelligent Cooking Assistant.
Centralizes all configurable constants and magic numbers.
"""

from typing import Dict, Any
import os
import logging
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class QueryClassificationConfig:
    """Configuration for query complexity classification."""
    # Word count thresholds
    SIMPLE_WORD_COUNT_THRESHOLD: int = 6
    COMPLEX_WORD_COUNT_THRESHOLD: int = 15
    
    # Question mark thresholds
    SIMPLE_QUESTION_MARKS_THRESHOLD: int = 1
    COMPLEX_QUESTION_MARKS_THRESHOLD: int = 2
    
    # Scoring weights
    SIMPLE_WORD_COUNT_SCORE: float = 0.3
    COMPLEX_WORD_COUNT_SCORE: float = 0.2
    CONSTRAINT_SCORE_WEIGHT: float = 0.4
    KEYWORD_MATCH_SCORE: float = 0.2
    MULTIPLE_MATCHES_BONUS: float = 0.1
    
    # Constraint counting
    MIN_CONSTRAINTS_FOR_COMPLEX: int = 2
    MAX_SCORE_CAP: float = 1.0


@dataclass
class ConversationMemoryConfig:
    """Configuration for conversation memory management."""
    # Context limits
    RECENT_TOPICS_LIMIT: int = 5
    RECENT_TURNS_LIMIT: int = 3
    RESPONSE_PREVIEW_LENGTH: int = 200
    
    # Time parsing patterns
    QUICK_TIME_MINUTES: int = 30
    DURATION_CONVERSION_SECONDS: int = 60


@dataclass 
class RecipeConfig:
    """Configuration for recipe validation and generation."""
    # Validation limits
    MIN_PREP_TIME: int = 0
    MIN_COOK_TIME: int = 0
    MIN_SERVINGS: int = 1
    MAX_SERVINGS: int = 50
    MIN_INGREDIENTS: int = 2
    MIN_INSTRUCTIONS: int = 3
    
    # Default values for fallback recipes
    DEFAULT_PREP_TIME: int = 15
    DEFAULT_COOK_TIME: int = 30
    DEFAULT_SERVINGS: int = 4
    DEFAULT_DIFFICULTY: str = "Intermediate"
    
    # Response processing
    RESPONSE_PREVIEW_LENGTH: int = 200
    RESPONSE_FULL_LENGTH: int = 500


@dataclass
class PromptConfig:
    """Configuration for prompt generation."""
    # Few-shot examples
    DEFAULT_EXAMPLES_COUNT: int = 3
    QUICK_EXAMPLES_COUNT: int = 2
    
    # Chef experience years
    CHEF_EXPERIENCE_YEARS: int = 20
    
    # Default time limits
    DEFAULT_QUICK_TIME_LIMIT: int = 30
    
    # Prompt formatting
    SEPARATOR_LENGTH: int = 60


@dataclass
class OpenAIConfig:
    """Configuration for OpenAI API calls."""
    # Model settings
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    SAFETY_MODEL: str = "gpt-3.5-turbo"
    
    # Temperature settings
    SIMPLE_TEMPERATURE: float = 0.3
    COMPLEX_TEMPERATURE: float = 0.7
    SAFETY_TEMPERATURE: float = 0.1
    
    # Token limits
    SIMPLE_MAX_TOKENS: int = 150
    COMPLEX_MAX_TOKENS: int = 800
    
    # API retry settings
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0


@dataclass
class UIConfig:
    """Configuration for user interface elements."""
    # Display formatting
    SEPARATOR_LENGTH: int = 60
    SHORT_SEPARATOR_LENGTH: int = 40
    MEMORY_SEPARATOR_LENGTH: int = 30
    
    # Input/output limits
    RESPONSE_PREVIEW_LENGTH: int = 100


@dataclass
class TestConfig:
    """Configuration for testing."""
    # Dataset expectations
    EXPECTED_RECIPE_COUNT: int = 15
    
    # Test limits
    TEST_EXAMPLES_COUNT: int = 2
    OVER_LIMIT_EXAMPLES_COUNT: int = 20
    ZERO_EXAMPLES_COUNT: int = 0


@dataclass
class VectorConfig:
    """Configuration for vector database (Chroma) operations."""
    # Database connection
    HOST: str = "localhost"
    PORT: int = 8000
    PERSISTENCE_DIRECTORY: str = "data/chroma_db"
    
    # Collection settings
    RECIPE_COLLECTION_NAME: str = "recipes"
    EMBEDDING_DIMENSION: int = 1536  # OpenAI text-embedding-ada-002 dimension
    
    # Search settings
    DEFAULT_SEARCH_LIMIT: int = 10
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Embedding settings
    EMBEDDING_MODEL: str = "text-embedding-ada-002"


@dataclass
class LoggingConfig:
    """Configuration for logging system."""
    # Log levels
    LOG_LEVEL: str = "INFO"
    CONSOLE_LOG_LEVEL: str = "INFO"
    FILE_LOG_LEVEL: str = "DEBUG"
    
    # Log formatting
    CONSOLE_FORMAT: str = "%(levelname)s - %(name)s - %(message)s"
    FILE_FORMAT: str = "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s"
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    
    # File logging
    LOG_FILE: str = "logs/cooking_assistant.log"
    MAX_LOG_SIZE: int = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT: int = 5
    
    # Logger names
    ROOT_LOGGER: str = "cooking_assistant"
    
    # Silence noisy loggers
    SILENCE_LOGGERS: list = None
    
    def __post_init__(self):
        if self.SILENCE_LOGGERS is None:
            self.SILENCE_LOGGERS = ["httpcore", "httpx", "openai"]


class CookingAssistantConfig:
    """Main configuration class that consolidates all config sections."""
    
    def __init__(self):
        self.query_classification = QueryClassificationConfig()
        self.conversation_memory = ConversationMemoryConfig()
        self.recipe = RecipeConfig()
        self.prompts = PromptConfig()
        self.openai = OpenAIConfig()
        self.ui = UIConfig()
        self.testing = TestConfig()
        self.vector = VectorConfig()
        self.logging = LoggingConfig()
    
    @classmethod
    def from_env(cls) -> 'CookingAssistantConfig':
        """Create configuration from environment variables."""
        config = cls()
        
        # Override with environment variables if present
        if os.getenv('OPENAI_MODEL'):
            config.openai.DEFAULT_MODEL = os.getenv('OPENAI_MODEL')
        
        if os.getenv('MAX_EXAMPLES'):
            config.prompts.DEFAULT_EXAMPLES_COUNT = int(os.getenv('MAX_EXAMPLES'))
        
        if os.getenv('SIMPLE_TEMPERATURE'):
            config.openai.SIMPLE_TEMPERATURE = float(os.getenv('SIMPLE_TEMPERATURE'))
        
        if os.getenv('COMPLEX_TEMPERATURE'):
            config.openai.COMPLEX_TEMPERATURE = float(os.getenv('COMPLEX_TEMPERATURE'))
        
        # Logging environment overrides
        if os.getenv('LOG_LEVEL'):
            config.logging.LOG_LEVEL = os.getenv('LOG_LEVEL')
        
        if os.getenv('CONSOLE_LOG_LEVEL'):
            config.logging.CONSOLE_LOG_LEVEL = os.getenv('CONSOLE_LOG_LEVEL')
        
        if os.getenv('LOG_FILE'):
            config.logging.LOG_FILE = os.getenv('LOG_FILE')
        
        # Vector database environment overrides
        if os.getenv('CHROMA_HOST'):
            config.vector.HOST = os.getenv('CHROMA_HOST')
        
        if os.getenv('CHROMA_PORT'):
            config.vector.PORT = int(os.getenv('CHROMA_PORT'))
        
        if os.getenv('CHROMA_PERSISTENCE_DIR'):
            config.vector.PERSISTENCE_DIRECTORY = os.getenv('CHROMA_PERSISTENCE_DIR')
        
        if os.getenv('EMBEDDING_MODEL'):
            config.vector.EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL')
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for inspection."""
        return {
            'query_classification': self.query_classification.__dict__,
            'conversation_memory': self.conversation_memory.__dict__,
            'recipe': self.recipe.__dict__,
            'prompts': self.prompts.__dict__,
            'openai': self.openai.__dict__,
            'ui': self.ui.__dict__,
            'testing': self.testing.__dict__,
            'vector': self.vector.__dict__,
            'logging': self.logging.__dict__
        }


# Global configuration instance
config = CookingAssistantConfig.from_env()


def get_config() -> CookingAssistantConfig:
    """Get the global configuration instance."""
    return config


def reload_config() -> CookingAssistantConfig:
    """Reload configuration from environment variables."""
    global config
    config = CookingAssistantConfig.from_env()
    return config


# Convenience functions for accessing specific config sections
def get_query_config() -> QueryClassificationConfig:
    """Get query classification configuration."""
    return config.query_classification


def get_memory_config() -> ConversationMemoryConfig:
    """Get conversation memory configuration."""
    return config.conversation_memory


def get_recipe_config() -> RecipeConfig:
    """Get recipe configuration."""
    return config.recipe


def get_prompt_config() -> PromptConfig:
    """Get prompt configuration."""
    return config.prompts


def get_openai_config() -> OpenAIConfig:
    """Get OpenAI configuration."""
    return config.openai


def get_ui_config() -> UIConfig:
    """Get UI configuration."""
    return config.ui


def get_test_config() -> TestConfig:
    """Get test configuration."""
    return config.testing


def get_vector_config() -> VectorConfig:
    """Get vector database configuration."""
    return config.vector


def get_logging_config() -> LoggingConfig:
    """Get logging configuration."""
    return config.logging


def setup_logging() -> None:
    """Setup logging configuration for the application."""
    from logging.handlers import RotatingFileHandler
    import os
    
    log_config = get_logging_config()
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_config.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create root logger
    root_logger = logging.getLogger(log_config.ROOT_LOGGER)
    root_logger.setLevel(getattr(logging, log_config.LOG_LEVEL.upper()))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_config.CONSOLE_LOG_LEVEL.upper()))
    console_formatter = logging.Formatter(
        log_config.CONSOLE_FORMAT, 
        datefmt=log_config.DATE_FORMAT
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_config.LOG_FILE:
        file_handler = RotatingFileHandler(
            log_config.LOG_FILE,
            maxBytes=log_config.MAX_LOG_SIZE,
            backupCount=log_config.BACKUP_COUNT
        )
        file_handler.setLevel(getattr(logging, log_config.FILE_LOG_LEVEL.upper()))
        file_formatter = logging.Formatter(
            log_config.FILE_FORMAT,
            datefmt=log_config.DATE_FORMAT
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Silence noisy third-party loggers
    for logger_name in log_config.SILENCE_LOGGERS:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    # Set propagation
    root_logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the application's logging configuration.
    
    Args:
        name: Logger name (typically __name__ from calling module)
    
    Returns:
        Configured logger instance
    """
    log_config = get_logging_config()
    
    # Ensure logging is setup
    if not logging.getLogger(log_config.ROOT_LOGGER).handlers:
        setup_logging()
    
    # Create hierarchical logger name
    if name.startswith(log_config.ROOT_LOGGER):
        logger_name = name
    else:
        # Convert module path to logger hierarchy
        if name.startswith('src.'):
            name = name[4:]  # Remove 'src.' prefix
        logger_name = f"{log_config.ROOT_LOGGER}.{name}"
    
    return logging.getLogger(logger_name)