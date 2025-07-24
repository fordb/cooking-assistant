from pydantic import BaseModel, Field
from typing import List

class Recipe(BaseModel):
    title: str = Field(..., description="Recipe name")
    prep_time: int = Field(..., description="Prep time in minutes")
    cook_time: int = Field(..., description="Cook time in minutes") 
    servings: int = Field(..., description="Number of servings")
    difficulty: str = Field(..., description="Beginner/Intermediate/Advanced")
    ingredients: List[str] = Field(..., description="List of ingredients with amounts")
    instructions: List[str] = Field(..., description="Step-by-step instructions")