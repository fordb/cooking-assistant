"""
Recipe filtering utilities for vector search operations.
"""

from typing import List, Optional
from dataclasses import dataclass

from src.common.config import get_vector_config
from src.common.exceptions import CookingAssistantError
from .types import SearchResult

class FilterValidationError(CookingAssistantError):
    """Exception raised for filter validation errors."""
    pass

@dataclass
class RecipeFilter:
    """Recipe filter for search operations."""
    difficulty: Optional[str] = None
    prep_time_min: Optional[int] = None
    prep_time_max: Optional[int] = None
    cook_time_min: Optional[int] = None
    cook_time_max: Optional[int] = None
    servings_min: Optional[int] = None
    servings_max: Optional[int] = None
    dietary_restrictions: Optional[List[str]] = None
    max_total_time: Optional[int] = None
    
    def __post_init__(self):
        """Validate filter parameters."""
        config = get_vector_config()
        
        # Validate difficulty
        if self.difficulty and self.difficulty not in config.SUPPORTED_DIFFICULTIES:
            raise FilterValidationError(f"Invalid difficulty '{self.difficulty}'")
        
        # Validate ranges
        if self.prep_time_min is not None and self.prep_time_max is not None and self.prep_time_min > self.prep_time_max:
            raise FilterValidationError("prep_time_min cannot be greater than prep_time_max")
        if self.cook_time_min is not None and self.cook_time_max is not None and self.cook_time_min > self.cook_time_max:
            raise FilterValidationError("cook_time_min cannot be greater than cook_time_max")
        if self.servings_min is not None and self.servings_max is not None and self.servings_min > self.servings_max:
            raise FilterValidationError("servings_min cannot be greater than servings_max")
        
        # Validate dietary restrictions
        if self.dietary_restrictions:
            for restriction in self.dietary_restrictions:
                if restriction.lower() not in [r.lower() for r in config.SUPPORTED_DIETARY_RESTRICTIONS]:
                    raise FilterValidationError(f"Invalid dietary restriction '{restriction}'")
    
    def has_filters(self) -> bool:
        """Check if any filters are set."""
        return any([
            self.difficulty is not None,
            self.prep_time_min is not None, self.prep_time_max is not None,
            self.cook_time_min is not None, self.cook_time_max is not None,
            self.servings_min is not None, self.servings_max is not None,
            self.dietary_restrictions is not None,
            self.max_total_time is not None
        ])


def apply_metadata_filters(search_results: List[SearchResult], 
                          filters: RecipeFilter) -> List[SearchResult]:
    """Apply metadata filters to search results."""
    if not filters or not filters.has_filters():
        return search_results
    
    filtered_results = []
    
    for result in search_results:
        # Extract metadata - handle both sparse and dense result formats
        metadata = result.get('metadata') or result.get('recipe', {})
        if not metadata:
            continue
        
        # Apply difficulty filter
        if filters.difficulty and metadata.get('difficulty') != filters.difficulty:
            continue
        
        # Apply time range filters
        prep_time = metadata.get('prep_time')
        if prep_time is not None:
            try:
                prep_time = int(prep_time)
                if filters.prep_time_min is not None and prep_time < filters.prep_time_min:
                    continue
                if filters.prep_time_max is not None and prep_time > filters.prep_time_max:
                    continue
            except (ValueError, TypeError):
                continue
        
        cook_time = metadata.get('cook_time')  
        if cook_time is not None:
            try:
                cook_time = int(cook_time)
                if filters.cook_time_min is not None and cook_time < filters.cook_time_min:
                    continue
                if filters.cook_time_max is not None and cook_time > filters.cook_time_max:
                    continue
            except (ValueError, TypeError):
                continue
        
        # Apply servings filter
        servings = metadata.get('servings')
        if servings is not None:
            try:
                servings = int(servings)
                if filters.servings_min is not None and servings < filters.servings_min:
                    continue
                if filters.servings_max is not None and servings > filters.servings_max:
                    continue
            except (ValueError, TypeError):
                continue
        
        # Apply dietary restrictions filter
        if filters.dietary_restrictions:
            recipe_text = " ".join([
                metadata.get('title', '').lower(),
                " ".join(metadata.get('ingredients', [])).lower()
            ])
            
            dietary_match = False
            for restriction in filters.dietary_restrictions:
                restriction_lower = restriction.lower()
                if restriction_lower in recipe_text:
                    dietary_match = True
                    break
                # Simple heuristics for common dietary restrictions
                if restriction_lower == 'vegetarian' and not any(meat in recipe_text for meat in ['meat', 'chicken', 'beef']):
                    dietary_match = True
                    break
            
            if not dietary_match:
                continue
        
        # Apply max total time filter
        if filters.max_total_time is not None:
            try:
                total_time = int(metadata.get('prep_time', 0)) + int(metadata.get('cook_time', 0))
                if total_time > filters.max_total_time:
                    continue
            except (ValueError, TypeError):
                continue
        
        filtered_results.append(result)
    
    return filtered_results


