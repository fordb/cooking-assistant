"""
Conversation memory management for cooking assistant.
Maintains session-level context and user preferences during conversations.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from src.common.config import get_memory_config, get_logger
import re

logger = get_logger(__name__)

@dataclass
class UserPreferences:
    """Stores user cooking preferences and constraints."""
    dietary_restrictions: List[str] = field(default_factory=list)
    cuisine_preferences: List[str] = field(default_factory=list)
    skill_level: Optional[str] = None
    cooking_time_preference: Optional[str] = None  # "quick", "moderate", "no_limit"
    equipment_available: List[str] = field(default_factory=list)
    family_size: Optional[int] = None
    budget_conscious: bool = False
    
    def update_from_query(self, query: str) -> List[str]:
        """Extract and update preferences from user query. Returns list of updates made."""
        updates = []
        query_lower = query.lower()
        
        # Dietary restrictions
        dietary_terms = {
            'vegetarian': 'vegetarian',
            'vegan': 'vegan', 
            'gluten-free': 'gluten-free',
            'dairy-free': 'dairy-free',
            'low-carb': 'low-carb',
            'keto': 'keto',
            'paleo': 'paleo',
            'diabetic': 'diabetic',
            'low-sodium': 'low-sodium'
        }
        
        for term, restriction in dietary_terms.items():
            if term in query_lower and restriction not in self.dietary_restrictions:
                self.dietary_restrictions.append(restriction)
                updates.append(f"Added dietary restriction: {restriction}")
        
        # Cuisine preferences
        cuisine_terms = ['italian', 'mexican', 'asian', 'chinese', 'indian', 'french', 'greek', 'thai']
        for cuisine in cuisine_terms:
            if cuisine in query_lower and cuisine not in self.cuisine_preferences:
                self.cuisine_preferences.append(cuisine)
                updates.append(f"Added cuisine preference: {cuisine}")
        
        # Skill level
        if 'beginner' in query_lower or 'easy' in query_lower:
            if self.skill_level != 'beginner':
                self.skill_level = 'beginner'
                updates.append("Set skill level: beginner")
        elif 'advanced' in query_lower or 'expert' in query_lower:
            if self.skill_level != 'advanced':
                self.skill_level = 'advanced'
                updates.append("Set skill level: advanced")
        elif 'intermediate' in query_lower:
            if self.skill_level != 'intermediate':
                self.skill_level = 'intermediate'
                updates.append("Set skill level: intermediate")
        
        # Cooking time preferences
        if any(term in query_lower for term in ['quick', 'fast', '30 min', 'minutes']):
            if self.cooking_time_preference != 'quick':
                self.cooking_time_preference = 'quick'
                updates.append("Set time preference: quick meals")
        
        # Family size
        family_match = re.search(r'family of (\d+)|(\d+) people|serves (\d+)', query_lower)
        if family_match:
            size = int(family_match.group(1) or family_match.group(2) or family_match.group(3))
            if self.family_size != size:
                self.family_size = size
                updates.append(f"Set family size: {size} people")
        
        # Budget consciousness
        if any(term in query_lower for term in ['budget', 'cheap', 'affordable', 'save money']):
            if not self.budget_conscious:
                self.budget_conscious = True
                updates.append("Noted budget consciousness")
        
        # Equipment
        equipment_terms = {
            'slow cooker': 'slow cooker',
            'instant pot': 'instant pot', 
            'air fryer': 'air fryer',
            'grill': 'grill',
            'oven': 'oven',
            'stovetop': 'stovetop'
        }
        
        for term, equipment in equipment_terms.items():
            if term in query_lower and equipment not in self.equipment_available:
                self.equipment_available.append(equipment)
                updates.append(f"Added available equipment: {equipment}")
        
        return updates

@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation."""
    timestamp: datetime
    user_query: str
    assistant_response: str
    strategy_used: str
    complexity: str
    topics: List[str] = field(default_factory=list)

class ConversationMemory:
    """Manages conversation context and memory for a cooking assistant session."""
    
    def __init__(self):
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now()
        self.preferences = UserPreferences()
        self.conversation_history: List[ConversationTurn] = []
        self.current_context: Dict[str, Any] = {}
        
    def add_turn(self, user_query: str, assistant_response: str, strategy_used: str, complexity: str) -> None:
        """Add a conversation turn and update memory."""
        
        # Extract topics from the query
        topics = self._extract_topics(user_query)
        
        # Create conversation turn
        turn = ConversationTurn(
            timestamp=datetime.now(),
            user_query=user_query,
            assistant_response=assistant_response,
            strategy_used=strategy_used,
            complexity=complexity,
            topics=topics
        )
        
        self.conversation_history.append(turn)
        
        # Update preferences based on query
        preference_updates = self.preferences.update_from_query(user_query)
        
        # Update current context
        self._update_context(user_query, topics)
        
        # Log preference updates if any
        if preference_updates:
            logger.info(f"Updated user preferences: {', '.join(preference_updates)}")
    
    def get_context_for_query(self, current_query: str) -> Dict[str, Any]:
        """Get relevant context for the current query."""
        context = {
            'preferences': self.preferences,
            'recent_topics': self._get_recent_topics(5),
            'session_length': len(self.conversation_history),
            'current_context': self.current_context.copy()
        }
        
        # Add relevant history if this appears to be a follow-up question
        if self._is_followup_question(current_query):
            context['recent_conversation'] = self._get_recent_turns(3)
        
        return context
    
    def _extract_topics(self, query: str) -> List[str]:
        """Extract cooking topics from user query."""
        topics = []
        query_lower = query.lower()
        
        # Cooking methods
        methods = ['bake', 'fry', 'grill', 'steam', 'boil', 'roast', 'sauté', 'stir-fry']
        for method in methods:
            if method in query_lower:
                topics.append(f"cooking_method:{method}")
        
        # Meal types
        meals = ['breakfast', 'lunch', 'dinner', 'snack', 'dessert', 'appetizer']
        for meal in meals:
            if meal in query_lower:
                topics.append(f"meal_type:{meal}")
        
        # Ingredients (simple detection)
        ingredients = ['chicken', 'beef', 'fish', 'vegetables', 'pasta', 'rice', 'eggs']
        for ingredient in ingredients:
            if ingredient in query_lower:
                topics.append(f"ingredient:{ingredient}")
        
        return topics
    
    def _update_context(self, query: str, topics: List[str]) -> None:
        """Update current conversation context."""
        # Track current recipe focus if any
        if any('ingredient:' in topic for topic in topics):
            ingredients = [topic.split(':')[1] for topic in topics if topic.startswith('ingredient:')]
            self.current_context['current_ingredients'] = ingredients
        
        # Track current meal planning if mentioned
        if 'meal plan' in query.lower() or 'weekly' in query.lower():
            self.current_context['planning_mode'] = True
        
        # Track current dietary focus
        dietary_in_query = [pref for pref in self.preferences.dietary_restrictions 
                           if pref.lower() in query.lower()]
        if dietary_in_query:
            self.current_context['current_dietary_focus'] = dietary_in_query
    
    def _get_recent_topics(self, count: int) -> List[str]:
        """Get topics from recent conversation turns."""
        recent_topics = []
        for turn in self.conversation_history[-count:]:
            recent_topics.extend(turn.topics)
        return list(set(recent_topics))  # Remove duplicates
    
    def _get_recent_turns(self, count: int) -> List[Dict[str, str]]:
        """Get recent conversation turns for context."""
        recent_turns = []
        for turn in self.conversation_history[-count:]:
            recent_turns.append({
                'user_query': turn.user_query,
                'assistant_response': turn.assistant_response[:200] + "..." if len(turn.assistant_response) > 200 else turn.assistant_response,
                'strategy': turn.strategy_used
            })
        return recent_turns
    
    def _is_followup_question(self, query: str) -> bool:
        """Determine if current query is a follow-up to previous conversation."""
        followup_indicators = [
            'what about', 'how about', 'can you also', 'what if', 'instead',
            'alternatively', 'but what', 'however', 'also', 'too'
        ]
        
        query_lower = query.lower()
        # Check for exact phrase matches and word boundary matches
        for indicator in followup_indicators:
            if indicator in query_lower:
                return True
        
        # Additional checks for common follow-up patterns
        if query_lower.startswith(('and ', 'or ', 'but ')):
            return True
            
        return False
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session."""
        return {
            'session_id': self.session_id,
            'duration_minutes': (datetime.now() - self.start_time).total_seconds() / 60,
            'turns_count': len(self.conversation_history),
            'preferences': self.preferences,
            'topics_discussed': self._get_recent_topics(len(self.conversation_history)),
            'strategies_used': list(set([turn.strategy_used for turn in self.conversation_history]))
        }

# Deprecated global functions - maintained for backward compatibility
# New code should create ConversationMemory instances directly

def get_conversation_memory() -> ConversationMemory:
    """
    DEPRECATED: Get or create conversation memory instance.
    Use ConversationMemory() directly instead.
    """
    return ConversationMemory()

def reset_conversation_memory() -> ConversationMemory:
    """
    DEPRECATED: Reset conversation memory (start new session).
    Use ConversationMemory() directly instead.
    """
    return ConversationMemory()

# Example usage
if __name__ == "__main__":
    # Test conversation memory
    memory = ConversationMemory()
    
    # Simulate conversation
    test_queries = [
        "I'm vegetarian and need quick dinner ideas",
        "What about something with pasta?", 
        "Can you make it gluten-free too?"
    ]
    
    for query in test_queries:
        context = memory.get_context_for_query(query)
        logger.debug(f"Demo query: {query}")
        logger.debug(f"Demo context: {context}")
        
        # Simulate response
        memory.add_turn(query, "Sample response", "test_strategy", "moderate")
        logger.debug("Demo turn added")
    
    logger.info("Demo session summary:")
    logger.info(memory.get_session_summary())