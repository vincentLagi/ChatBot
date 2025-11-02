import sys
import os
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unified_system.interface.unified_chat import UnifiedChatSystem

load_dotenv()

def main():
    """Main entry point for Unified Academic Assistant"""
    
    print("🚀 Starting Unified Academic Assistant...")
    print("=" * 55)
    
    import argparse
    parser = argparse.ArgumentParser(description='Unified Academic Assistant')
    parser.add_argument('--info', action='store_true', help='Show system information')
    parser.add_argument('--legacy-router', action='store_true', help='Use legacy keyword-based router instead of AI agent')
    parser.add_argument('--direct', type=str, help='Process single query directly')
    
    args = parser.parse_args()
    
    if args.info:
        show_system_info()
        return
    
    try:
        use_agent_router = not args.legacy_router  # Default to agent router
        if use_agent_router:
            print("🧠 Initializing with AI-powered Router Agent...")
        else:
            print("📊 Initializing with legacy keyword-based router...")
            
        chat_system = UnifiedChatSystem(use_agent_router=use_agent_router)
        
        if args.direct:
            # Direct query mode
            print(f"\n🔍 Processing direct query: {args.direct}")
            response = chat_system.process_direct_query(args.direct)
            print(f"\n📝 Response:\n{response}")
        else:
            # Interactive mode
            chat_system.run_interactive()
            
    except KeyboardInterrupt:
        print("\n\n👋 Program terminated by user")
    except Exception as e:
        print(f"\n💥 Fatal error: {str(e)}")
        print("Please check your configuration and try again")

if __name__ == "__main__":
    main() 