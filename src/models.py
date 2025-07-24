from pydantic import BaseModel, Field, field_validator
from typing import List

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
            raise ValueError("Time cannot be negative")
        return v
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        valid_difficulties = ["Beginner", "Intermediate", "Advanced"]
        if v not in valid_difficulties:
            raise ValueError(f"Difficulty must be one of: {valid_difficulties}")
        return v
    
    @field_validator('ingredients')
    @classmethod
    def validate_ingredients(cls, v):
        if len(v) == 0:
            raise ValueError("Recipe must have at least one ingredient")
        return v
    
    @field_validator('instructions')
    @classmethod
    def validate_instructions(cls, v):
        if len(v) == 0:
            raise ValueError("Recipe must have at least one instruction")
        return v
    
    @property
    def total_time(self) -> int:
        return self.prep_time + self.cook_time

class SafetyValidation(BaseModel):
    safe: bool
    warnings: List[str] = []