"""
Recipe filtering utilities for vector search operations.
Provides structured filtering based on recipe metadata.
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass

from src.common.config import get_vector_config, get_logger
from src.common.exceptions import CookingAssistantError
from .types import SearchResult, FilterDict

logger = get_logger(__name__)

class FilterValidationError(CookingAssistantError):
    """Exception raised for filter validation errors."""
    pass

@dataclass
class RecipeFilter:
    """
    Structured recipe filter for search operations.
    Supports categorical, range, and list-based filtering.
    """
    # Categorical filters
    difficulty: Optional[str] = None
    
    # Range filters (inclusive)
    prep_time_min: Optional[int] = None
    prep_time_max: Optional[int] = None
    cook_time_min: Optional[int] = None
    cook_time_max: Optional[int] = None
    servings_min: Optional[int] = None
    servings_max: Optional[int] = None
    
    # List filters (any match)
    dietary_restrictions: Optional[List[str]] = None
    
    # Advanced filters
    max_total_time: Optional[int] = None  # prep_time + cook_time
    
    def __post_init__(self):
        """Validate filter parameters after initialization."""
        self._validate_filters()
    
    def _validate_filters(self) -> None:
        """Validate all filter parameters."""
        config = get_vector_config()
        
        # Validate difficulty level
        if self.difficulty and self.difficulty not in config.SUPPORTED_DIFFICULTIES:
            raise FilterValidationError(
                f"Invalid difficulty '{self.difficulty}'. Must be one of: {config.SUPPORTED_DIFFICULTIES}"
            )
        
        # Validate range filters
        self._validate_range_filter("prep_time", self.prep_time_min, self.prep_time_max, 
                                   config.MIN_PREP_TIME_FILTER, config.MAX_PREP_TIME_FILTER)
        self._validate_range_filter("cook_time", self.cook_time_min, self.cook_time_max,
                                   config.MIN_COOK_TIME_FILTER, config.MAX_COOK_TIME_FILTER)
        self._validate_range_filter("servings", self.servings_min, self.servings_max,
                                   config.MIN_SERVINGS_FILTER, config.MAX_SERVINGS_FILTER)
        
        # Validate dietary restrictions
        if self.dietary_restrictions:
            for restriction in self.dietary_restrictions:
                if restriction.lower() not in [r.lower() for r in config.SUPPORTED_DIETARY_RESTRICTIONS]:
                    raise FilterValidationError(
                        f"Invalid dietary restriction '{restriction}'. Supported: {config.SUPPORTED_DIETARY_RESTRICTIONS}"
                    )
        
        # Validate max_total_time
        if self.max_total_time is not None:
            if self.max_total_time < 0 or self.max_total_time > (config.MAX_PREP_TIME_FILTER + config.MAX_COOK_TIME_FILTER):
                raise FilterValidationError(
                    f"max_total_time must be between 0 and {config.MAX_PREP_TIME_FILTER + config.MAX_COOK_TIME_FILTER} minutes"
                )
    
    def _validate_range_filter(self, field_name: str, min_val: Optional[int], max_val: Optional[int], 
                             config_min: int, config_max: int) -> None:
        """Validate a range filter's bounds."""
        if min_val is not None:
            if min_val < config_min or min_val > config_max:
                raise FilterValidationError(
                    f"{field_name}_min must be between {config_min} and {config_max}"
                )
        
        if max_val is not None:
            if max_val < config_min or max_val > config_max:
                raise FilterValidationError(
                    f"{field_name}_max must be between {config_min} and {config_max}"
                )
        
        if min_val is not None and max_val is not None and min_val > max_val:
            raise FilterValidationError(
                f"{field_name}_min ({min_val}) cannot be greater than {field_name}_max ({max_val})"
            )
    
    def has_filters(self) -> bool:
        """Check if any filters are set."""
        return any([
            self.difficulty is not None,
            self.prep_time_min is not None,
            self.prep_time_max is not None,
            self.cook_time_min is not None,
            self.cook_time_max is not None,
            self.servings_min is not None,
            self.servings_max is not None,
            self.dietary_restrictions is not None,
            self.max_total_time is not None
        ])
    
    def to_dict(self) -> FilterDict:
        """Convert filter to dictionary for logging/debugging."""
        return {
            'difficulty': self.difficulty,
            'prep_time_range': f"{self.prep_time_min}-{self.prep_time_max}" if self.prep_time_min or self.prep_time_max else None,
            'cook_time_range': f"{self.cook_time_min}-{self.cook_time_max}" if self.cook_time_min or self.cook_time_max else None,
            'servings_range': f"{self.servings_min}-{self.servings_max}" if self.servings_min or self.servings_max else None,
            'dietary_restrictions': self.dietary_restrictions,
            'max_total_time': self.max_total_time
        }


def apply_metadata_filters(search_results: List[SearchResult], 
                          filters: RecipeFilter) -> List[SearchResult]:
    """
    Apply metadata filters to search results.
    
    Args:
        search_results: List of search results with metadata
        filters: RecipeFilter object with filter criteria
        
    Returns:
        Filtered list of search results
    """
    if not filters or not filters.has_filters():
        return search_results
    
    config = get_vector_config()
    if not config.ENABLE_FILTERING:
        logger.warning("Filtering is disabled in configuration")
        return search_results
    
    logger.info(f"Applying filters to {len(search_results)} search results: {filters.to_dict()}")
    
    filtered_results = []
    filter_stats = {
        'total_input': len(search_results),
        'difficulty_filtered': 0,
        'prep_time_filtered': 0,
        'cook_time_filtered': 0,
        'servings_filtered': 0,
        'dietary_filtered': 0,
        'total_time_filtered': 0,
        'final_count': 0
    }
    
    for result in search_results:
        # Extract metadata - handle both sparse and dense result formats
        metadata = result.get('metadata') or result.get('recipe', {})
        
        if not metadata:
            logger.debug("Skipping result with no metadata")
            continue
        
        # Apply difficulty filter
        if filters.difficulty:
            recipe_difficulty = metadata.get('difficulty')
            if recipe_difficulty != filters.difficulty:
                filter_stats['difficulty_filtered'] += 1
                continue
        
        # Apply prep time range filter
        if filters.prep_time_min is not None or filters.prep_time_max is not None:
            prep_time = metadata.get('prep_time')
            if prep_time is None:
                continue
            
            try:
                prep_time = int(prep_time)
                if filters.prep_time_min is not None and prep_time < filters.prep_time_min:
                    filter_stats['prep_time_filtered'] += 1
                    continue
                if filters.prep_time_max is not None and prep_time > filters.prep_time_max:
                    filter_stats['prep_time_filtered'] += 1
                    continue
            except (ValueError, TypeError):
                logger.debug(f"Invalid prep_time value: {prep_time}")
                continue
        
        # Apply cook time range filter
        if filters.cook_time_min is not None or filters.cook_time_max is not None:
            cook_time = metadata.get('cook_time')
            if cook_time is None:
                continue
            
            try:
                cook_time = int(cook_time)
                if filters.cook_time_min is not None and cook_time < filters.cook_time_min:
                    filter_stats['cook_time_filtered'] += 1
                    continue
                if filters.cook_time_max is not None and cook_time > filters.cook_time_max:
                    filter_stats['cook_time_filtered'] += 1
                    continue
            except (ValueError, TypeError):
                logger.debug(f"Invalid cook_time value: {cook_time}")
                continue
        
        # Apply servings range filter
        if filters.servings_min is not None or filters.servings_max is not None:
            servings = metadata.get('servings')
            if servings is None:
                continue
            
            try:
                servings = int(servings)
                if filters.servings_min is not None and servings < filters.servings_min:
                    filter_stats['servings_filtered'] += 1
                    continue
                if filters.servings_max is not None and servings > filters.servings_max:
                    filter_stats['servings_filtered'] += 1
                    continue
            except (ValueError, TypeError):
                logger.debug(f"Invalid servings value: {servings}")
                continue
        
        # Apply dietary restrictions filter
        if filters.dietary_restrictions:
            # For now, we'll implement this as a keyword search in ingredients/title
            # In a real system, you'd want structured dietary tags in metadata
            recipe_text = " ".join([
                metadata.get('title', '').lower(),
                " ".join(metadata.get('ingredients', [])).lower()
            ])
            
            dietary_match = False
            for restriction in filters.dietary_restrictions:
                restriction_lower = restriction.lower()
                # Simple keyword matching - could be enhanced with better logic
                if restriction_lower in recipe_text:
                    dietary_match = True
                    break
                
                # Check for common patterns
                if restriction_lower == 'vegetarian' and 'meat' not in recipe_text and 'chicken' not in recipe_text and 'beef' not in recipe_text:
                    dietary_match = True
                    break
                elif restriction_lower == 'vegan' and all(keyword not in recipe_text for keyword in ['meat', 'chicken', 'beef', 'cheese', 'milk', 'egg', 'butter']):
                    dietary_match = True
                    break
            
            if not dietary_match:
                filter_stats['dietary_filtered'] += 1
                continue
        
        # Apply max total time filter
        if filters.max_total_time is not None:
            prep_time = metadata.get('prep_time', 0)
            cook_time = metadata.get('cook_time', 0)
            
            try:
                total_time = int(prep_time) + int(cook_time)
                if total_time > filters.max_total_time:
                    filter_stats['total_time_filtered'] += 1
                    continue
            except (ValueError, TypeError):
                logger.debug(f"Invalid time values: prep={prep_time}, cook={cook_time}")
                continue
        
        # If we get here, the result passed all filters
        filtered_results.append(result)
    
    filter_stats['final_count'] = len(filtered_results)
    
    logger.info(f"Filter results: {filter_stats['final_count']}/{filter_stats['total_input']} results passed filters")
    logger.debug(f"Filter statistics: {filter_stats}")
    
    return filtered_results


def create_recipe_filter(difficulty: Optional[str] = None,
                        prep_time_min: Optional[int] = None,
                        prep_time_max: Optional[int] = None,
                        cook_time_min: Optional[int] = None,
                        cook_time_max: Optional[int] = None,
                        servings_min: Optional[int] = None,
                        servings_max: Optional[int] = None,
                        dietary_restrictions: Optional[List[str]] = None,
                        max_total_time: Optional[int] = None) -> RecipeFilter:
    """
    Convenience function to create a RecipeFilter with validation.
    
    Args:
        difficulty: Recipe difficulty level
        prep_time_min: Minimum prep time in minutes
        prep_time_max: Maximum prep time in minutes
        cook_time_min: Minimum cook time in minutes
        cook_time_max: Maximum cook time in minutes
        servings_min: Minimum servings
        servings_max: Maximum servings
        dietary_restrictions: List of dietary restrictions
        max_total_time: Maximum total time (prep + cook) in minutes
        
    Returns:
        Validated RecipeFilter object
        
    Raises:
        FilterValidationError: If any filter parameters are invalid
    """
    try:
        return RecipeFilter(
            difficulty=difficulty,
            prep_time_min=prep_time_min,
            prep_time_max=prep_time_max,
            cook_time_min=cook_time_min,
            cook_time_max=cook_time_max,
            servings_min=servings_min,
            servings_max=servings_max,
            dietary_restrictions=dietary_restrictions,
            max_total_time=max_total_time
        )
    except Exception as e:
        raise FilterValidationError(f"Failed to create recipe filter: {e}") from e


def validate_filter_ranges(prep_time_range: Optional[Tuple[int, int]] = None,
                          cook_time_range: Optional[Tuple[int, int]] = None,
                          servings_range: Optional[Tuple[int, int]] = None) -> bool:
    """
    Validate filter ranges before creating filters.
    
    Args:
        prep_time_range: (min, max) prep time tuple
        cook_time_range: (min, max) cook time tuple
        servings_range: (min, max) servings tuple
        
    Returns:
        True if all ranges are valid
        
    Raises:
        FilterValidationError: If any range is invalid
    """
    config = get_vector_config()
    
    if prep_time_range:
        min_val, max_val = prep_time_range
        if min_val > max_val:
            raise FilterValidationError(f"prep_time_min ({min_val}) cannot be greater than prep_time_max ({max_val})")
        if min_val < config.MIN_PREP_TIME_FILTER or max_val > config.MAX_PREP_TIME_FILTER:
            raise FilterValidationError(f"prep_time range must be within {config.MIN_PREP_TIME_FILTER}-{config.MAX_PREP_TIME_FILTER}")
    
    if cook_time_range:
        min_val, max_val = cook_time_range
        if min_val > max_val:
            raise FilterValidationError(f"cook_time_min ({min_val}) cannot be greater than cook_time_max ({max_val})")
        if min_val < config.MIN_COOK_TIME_FILTER or max_val > config.MAX_COOK_TIME_FILTER:
            raise FilterValidationError(f"cook_time range must be within {config.MIN_COOK_TIME_FILTER}-{config.MAX_COOK_TIME_FILTER}")
    
    if servings_range:
        min_val, max_val = servings_range
        if min_val > max_val:
            raise FilterValidationError(f"servings_min ({min_val}) cannot be greater than servings_max ({max_val})")
        if min_val < config.MIN_SERVINGS_FILTER or max_val > config.MAX_SERVINGS_FILTER:
            raise FilterValidationError(f"servings range must be within {config.MIN_SERVINGS_FILTER}-{config.MAX_SERVINGS_FILTER}")
    
    return True