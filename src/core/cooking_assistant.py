"""
Core cooking assistant interface.
Provides unified access to all cooking assistant functionality.
"""

from typing import Dict, Any, Optional
from .conversation_memory import ConversationMemory
from .query_classifier import classify_cooking_query

class CookingAssistant:
    """
    Main cooking assistant interface.
    Handles conversations, memory, and intelligent prompting.
    """
    
    def __init__(self):
        """Initialize the cooking assistant with memory and meta-prompting."""
        self.memory = ConversationMemory()
        self._meta_prompting = None
    
    def ask(self, query: str) -> Dict[str, Any]:
        """
        Process a cooking query using intelligent strategy selection.
        
        Args:
            query: User's cooking question or request
            
        Returns:
            Dictionary with response, strategy, and metadata
        """
        try:
            # Lazy import to avoid circular dependencies
            from src.prompting import process_cooking_query
            
            # Get context from conversation memory
            context = self.memory.get_context_for_query(query)
            
            # Process query using meta-prompting system
            result = process_cooking_query(query, context)
            
            # Add to conversation memory
            self.memory.add_turn(
                query, 
                result['response'], 
                result['strategy'], 
                result['complexity']
            )
            
            return result
            
        except Exception as e:
            error_result = {
                'response': f"I encountered an error processing your question: {str(e)}",
                'strategy': 'error',
                'complexity': 'unknown',
                'success': False,
                'error': str(e)
            }
            return error_result
    
    def classify_query(self, query: str) -> Dict[str, Any]:
        """
        Classify a query's complexity without processing it.
        
        Args:
            query: User's cooking question
            
        Returns:
            Dictionary with complexity, confidence, and reasoning
        """
        complexity, confidence, reasoning = classify_cooking_query(query)
        return {
            'complexity': complexity.value,
            'confidence': confidence,
            'reasoning': reasoning
        }
    
    def get_memory_status(self) -> Dict[str, Any]:
        """Get current conversation memory status."""
        return self.memory.get_session_summary()
    
    def get_preferences(self) -> Dict[str, Any]:
        """Get user preferences from memory."""
        return {
            'dietary_restrictions': self.memory.preferences.dietary_restrictions,
            'cuisine_preferences': self.memory.preferences.cuisine_preferences,
            'skill_level': self.memory.preferences.skill_level,
            'cooking_time_preference': self.memory.preferences.cooking_time_preference,
            'family_size': self.memory.preferences.family_size,
            'budget_conscious': self.memory.preferences.budget_conscious,
            'equipment_available': self.memory.preferences.equipment_available
        }
    
    def reset_memory(self) -> None:
        """Reset conversation memory for a new session."""
        self.memory = ConversationMemory()
    
    def get_conversation_history(self) -> list:
        """Get conversation history for this session."""
        return [
            {
                'query': turn.user_query,
                'response': turn.assistant_response[:200] + "..." if len(turn.assistant_response) > 200 else turn.assistant_response,
                'strategy': turn.strategy_used,
                'complexity': turn.complexity,
                'timestamp': turn.timestamp.isoformat()
            }
            for turn in self.memory.conversation_history
        ]

# Convenience functions for backward compatibility
def ask_cooking_question(query: str, assistant: Optional[CookingAssistant] = None) -> Dict[str, Any]:
    """
    Convenience function to ask a cooking question.
    
    Args:
        query: User's cooking question
        assistant: Optional existing assistant instance
        
    Returns:
        Response dictionary
    """
    if assistant is None:
        assistant = CookingAssistant()
    return assistant.ask(query)

def create_cooking_assistant() -> CookingAssistant:
    """Create a new cooking assistant instance."""
    return CookingAssistant()