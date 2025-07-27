"""
Cooking Assistant - Week 2 Advanced Prompting System
Simple, unified interface for intelligent cooking assistance.
"""

import argparse
from src.core import CookingAssistant
from src.exceptions import CookingAssistantError

def conversation_mode():
    """Interactive conversation mode with intelligent prompting and memory."""
    print("🧑‍🍳 Welcome to AI Cooking Assistant!")
    print("I use intelligent prompting strategies and remember our conversation.")
    print("Commands: 'help', 'memory', 'reset', 'quit'")
    
    assistant = CookingAssistant()
    
    while True:
        print("\n" + "=" * 60)
        query = input("💬 What can I help you cook today? ")
        
        if query.lower() == 'quit':
            summary = assistant.get_memory_status()
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
            print("🔄 Memory reset. Starting fresh conversation.")
            continue
        
        try:
            # Process query
            print("\n🤔 Analyzing your question...")
            result = assistant.ask(query)
            
            # Show strategy and response
            print(f"📋 Strategy: {result['strategy']} (complexity: {result['complexity']})")
            if 'reasoning' in result:
                print(f"💡 Reasoning: {result['reasoning']}")
            
            print(f"\n🧑‍🍳 Chef's Response:")
            print("-" * 40)
            print(result['response'])
            
        except CookingAssistantError as e:
            print(f"❌ Cooking Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")

def quick_question_mode():
    """Quick question mode for single queries."""
    print("🧑‍🍳 Quick Question Mode")
    print("Ask a single cooking question for immediate answer.")
    
    query = input("\n💬 Your cooking question: ")
    
    try:
        assistant = CookingAssistant()
        result = assistant.ask(query)
        
        print(f"\n📋 Strategy: {result['strategy']} (complexity: {result['complexity']})")
        print(f"\n🧑‍🍳 Answer:")
        print("-" * 40)
        print(result['response'])
        
    except Exception as e:
        print(f"❌ Error: {e}")

def classify_mode():
    """Query classification mode for testing."""
    print("🔍 Query Classification Mode")
    print("Test how queries are classified by complexity.")
    
    while True:
        query = input("\n💬 Enter query to classify (or 'quit'): ")
        if query.lower() == 'quit':
            break
            
        assistant = CookingAssistant()
        classification = assistant.classify_query(query)
        
        print(f"📊 Complexity: {classification['complexity']}")
        print(f"🎯 Confidence: {classification['confidence']:.2f}")
        print(f"💭 Reasoning: {classification['reasoning']}")

def show_help():
    """Show help information."""
    print("\n🆘 Cooking Assistant Help")
    print("=" * 40)
    print("💬 Commands in conversation mode:")
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
    print("\n🧠 Memory Status")
    print("=" * 30)
    
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

def main():
    """Main entry point with simplified command-line interface."""
    parser = argparse.ArgumentParser(
        description="AI Cooking Assistant with Advanced Prompting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Interactive conversation mode
  python main.py --quick           # Single question mode
  python main.py --classify        # Test query classification
  python main.py --demos           # Run demos and examples
        """
    )
    
    parser.add_argument("--quick", action="store_true", 
                       help="Quick question mode for single queries")
    parser.add_argument("--classify", action="store_true", 
                       help="Query classification testing mode")
    parser.add_argument("--demos", action="store_true", 
                       help="Run demos and examples")
    
    args = parser.parse_args()
    
    if args.quick:
        quick_question_mode()
    elif args.classify:
        classify_mode()
    elif args.demos:
        # Import and run demos
        try:
            import demos
            demos.demo_conversation()
        except ImportError:
            print("❌ Demos module not available")
    else:
        # Default to conversation mode
        conversation_mode()

if __name__ == "__main__":
    main()