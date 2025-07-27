"""
Intelligent Cooking Assistant
Conversational interface for intelligent cooking assistance.
"""

from src.core import CookingAssistant
from src.exceptions import CookingAssistantError
from src.config import get_ui_config, setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

def main():
    """Interactive conversation mode with intelligent prompting and memory."""
    print("🧑‍🍳 Welcome to AI Cooking Assistant!")
    print("I use intelligent prompting strategies and remember our conversation.")
    print("Commands: 'help', 'memory', 'reset', 'quit'")
    
    logger.info("Starting AI Cooking Assistant interactive session")
    assistant = CookingAssistant()
    
    while True:
        config = get_ui_config()
        print("\n" + "=" * config.SEPARATOR_LENGTH)
        query = input("💬 What can I help you cook today? ")
        
        if query.lower() == 'quit':
            summary = assistant.get_memory_status()
            logger.info(f"Session ended - Duration: {summary['duration_minutes']:.1f}min, Questions: {summary['turns_count']}, Strategies: {summary['strategies_used']}")
            print(f"\n📊 Session Summary:")
            print(f"Duration: {summary['duration_minutes']:.1f} minutes")
            print(f"Questions: {summary['turns_count']}")
            print(f"Strategies: {', '.join(summary['strategies_used'])}")
            print("👋 Happy cooking!")
            break
            
        elif query.lower() == 'help':
            show_help()
            continue
            
        elif query.lower() == 'memory':
            show_memory_status(assistant)
            continue
            
        elif query.lower() == 'reset':
            assistant.reset_memory()
            logger.info("User reset conversation memory")
            print("🔄 Memory reset. Starting fresh conversation.")
            continue
        
        try:
            # Process query
            logger.debug(f"Processing user query: {query[:50]}...")
            print("\n🤔 Analyzing your question...")
            result = assistant.ask(query)
            
            # Log strategy selection
            logger.info(f"Query classified as {result['complexity']}, using {result['strategy']} strategy")
            
            # Show strategy and response
            print(f"📋 Strategy: {result['strategy']} (complexity: {result['complexity']})")
            if 'reasoning' in result:
                print(f"💡 Reasoning: {result['reasoning']}")
            
            print(f"\n🧑‍🍳 Chef's Response:")
            print("-" * config.SHORT_SEPARATOR_LENGTH)
            print(result['response'])
            
        except CookingAssistantError as e:
            logger.error(f"Cooking assistant error: {e}")
            print(f"❌ Cooking Error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
            print(f"❌ Unexpected Error: {e}")

def show_help():
    """Show help information."""
    config = get_ui_config()
    print("\n🆘 Cooking Assistant Help")
    print("=" * config.SHORT_SEPARATOR_LENGTH)
    print("💬 Commands in conversation:")
    print("  • Ask any cooking question naturally")
    print("  • 'help' - Show this help")
    print("  • 'memory' - See what I remember")
    print("  • 'reset' - Start fresh conversation")
    print("  • 'quit' - Exit with summary")
    print("\n🤖 I automatically:")
    print("  • Classify questions by complexity")
    print("  • Choose the best prompting strategy")
    print("  • Remember your preferences")
    print("  • Provide context-aware responses")

def show_memory_status(assistant: CookingAssistant):
    """Show current memory status."""
    config = get_ui_config()
    print("\n🧠 Memory Status")
    print("=" * config.MEMORY_SEPARATOR_LENGTH)
    
    prefs = assistant.get_preferences()
    
    if prefs['dietary_restrictions']:
        print(f"🥗 Dietary: {', '.join(prefs['dietary_restrictions'])}")
    
    if prefs['cuisine_preferences']:
        print(f"🌍 Cuisines: {', '.join(prefs['cuisine_preferences'])}")
    
    if prefs['skill_level']:
        print(f"👨‍🍳 Skill: {prefs['skill_level']}")
    
    if prefs['cooking_time_preference']:
        print(f"⏱️ Time: {prefs['cooking_time_preference']}")
    
    if prefs['family_size']:
        print(f"👨‍👩‍👧‍👦 Family: {prefs['family_size']} people")
    
    if prefs['equipment_available']:
        print(f"🔧 Equipment: {', '.join(prefs['equipment_available'])}")
    
    if prefs['budget_conscious']:
        print("💰 Budget conscious: Yes")
    
    summary = assistant.get_memory_status()
    print(f"💬 Questions asked: {summary['turns_count']}")

if __name__ == "__main__":
    main()