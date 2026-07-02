import os
import sys
from dotenv import load_dotenv

# Ensure the local path is registered for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.orchestrator.graph import run_orchestrator

load_dotenv()

def main():
    print("=" * 65)
    print("    Aether Enterprise Multi-Agent AI Assistant (LangGraph CLI)")
    print("=" * 65)
    print("Type 'exit' to quit. Conversation history is persistent (session: cli_session).\n")
    
    thread_id = "cli_session"
    
    while True:
        try:
            user_input = input("\nYou: ")
            if not user_input.strip():
                continue
                
            if user_input.lower() == "exit":
                print("\nExiting. Goodbye!")
                break
                
            print("\n[Thinking...]")
            result = run_orchestrator(user_input, thread_id=thread_id)
            
            print(f"\n[Pipeline Route: {result['route'].upper()}]")
            if result.get("tools_used"):
                print(f"[Tools Executed: {', '.join(result['tools_used'])}]")
                
            print("\nAssistant:")
            print(result["final_response"])
            print("-" * 65)
            
        except KeyboardInterrupt:
            print("\nExiting. Goodbye!")
            break
        except Exception as e:
            print(f"\n[System Error]: {e}")

if __name__ == "__main__":
    main()
