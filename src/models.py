from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List
from src.exceptions import RecipeValidationError

class Recipe(BaseModel):
    title: str = Field(..., description="Recipe name")
    prep_time: int = Field(..., description="Prep time in minutes")
    cook_time: int = Field(..., description="Cook time in minutes") 
    servings: int = Field(..., description="Number of servings")
    difficulty: str = Field(..., description="Beginner/Intermediate/Advanced")
    ingredients: List[str] = Field(..., description="List of ingredients with amounts")
    instructions: List[str] = Field(..., description="Step-by-step instructions")
    
    @field_validator('prep_time', 'cook_time')
    @classmethod
    def validate_times(cls, v):
        if v < 0:
            raise RecipeValidationError("Time cannot be negative")
        return v
    
    @field_validator('servings')
    @classmethod
    def validate_servings(cls, v):
        if v < 1 or v > 50:  # Allow for batch recipes like cookies
            raise RecipeValidationError("Servings must be between 1-50")
        return v
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        valid_difficulties = ["Beginner", "Intermediate", "Advanced"]
        if v not in valid_difficulties:
            raise RecipeValidationError(f"Difficulty must be one of: {valid_difficulties}")
        return v
    
    @field_validator('ingredients')
    @classmethod
    def validate_ingredients(cls, v):
        if len(v) < 2:
            raise RecipeValidationError("Recipe must have at least 2 ingredients")
        return v
    
    @field_validator('instructions')
    @classmethod
    def validate_instructions(cls, v):
        if len(v) < 3:
            raise RecipeValidationError("Recipe must have at least 3 instruction steps")
        return v
    
    @model_validator(mode='after')
    def validate_measurements(self):
        """Check ingredients have realistic measurements."""
        measurement_words = ['cup', 'tablespoon', 'teaspoon', 'pound', 'ounce', 'gram', 'piece', 'clove']
        warnings = []
        
        for ingredient in self.ingredients:
            has_measurement = any(word in ingredient.lower() for word in measurement_words)
            has_number = any(char.isdigit() for char in ingredient)
            
            if not (has_measurement or has_number):
                warnings.append(f"Ingredient missing measurement: {ingredient}")
        
        if warnings:
            import warnings as warn_module
            warn_module.warn(f"Measurement warnings: {warnings}")
        
        return self
    
    @property
    def total_time(self) -> int:
        return self.prep_time + self.cook_time

class SafetyValidation(BaseModel):
    safe: bool
    warnings: List[str] = []