import os
import json
from openai import OpenAI
from app.config.settings import settings

_groq_client = None

def get_groq_client():
    global _groq_client
    if _groq_client is None:
        api_key = settings.GROQ_API_KEY
        if api_key and api_key != "your_groq_api_key_here" and api_key.strip():
            _groq_client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=api_key
            )
    return _groq_client

def get_chat_completion(messages: list, temperature: float = 0.0, max_tokens: int = None, json_mode: bool = False) -> str:
    """
    Unified chat completions endpoint wrapper. Prioritizes Groq if configured.
    Provides simulation logs if no keys are found.
    """
    # 1. Attempt Groq
    groq_client = get_groq_client()
    if groq_client:
        try:
            model = settings.DEFAULT_GROQ_MODEL
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
                
            response = groq_client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            print(f"[Warning] Groq API call failed: {e}.")

    # 2. Simulation Fallback
    print("[INFO] Running in completion simulation mode (no working API keys discovered).")
    return simulate_completion(messages, json_mode)


def simulate_completion(messages: list, json_mode: bool = False) -> str:
    """
    Mock completion engine fallback when keys are absent.
    """
    last_user_msg = ""
    for m in reversed(messages):
        if m["role"] == "user":
            last_user_msg = m["content"]
            break
            
    q = last_user_msg.lower()
    
    if json_mode:
        if "route" in q or "intent" in q or "route" in messages[0]["content"]:
            # Router simulation
            route = "llm"
            if any(w in q for w in ["pdf", "document", "file", "internal", "data"]):
                route = "rag"
            elif any(w in q for w in ["plan", "roadmap", "steps", "guide", "strategy", "how to"]):
                route = "planner"
            elif any(w in q for w in ["search", "weather", "news", "latest", "current", "today"]):
                route = "web_search"
            return json.dumps({
                "route": route,
                "reasoning": f"Simulated routing classification for query containing indicators of {route}."
            })
        elif "is_valid" in q or "is_valid" in messages[0]["content"]:
            # Reflection simulation
            return json.dumps({
                "is_valid": True,
                "confidence_score": 0.95,
                "suggested_corrections": "",
                "reasoning": "Simulated reflection validated successfully."
            })
        elif "needs_tool" in q or "needs_tool" in messages[0]["content"] or "tool" in messages[0]["content"]:
            # Tool selection simulation
            needs_tool = False
            tools = []
            if any(w in q for w in ["+", "-", "*", "/", "calculate", "math"]):
                needs_tool = True
                tools.append("calculator")
            if any(w in q for w in ["python", "run code", "execute"]):
                needs_tool = True
                tools.append("python_executor")
            if any(w in q for w in ["sql", "query database", "users"]):
                needs_tool = True
                tools.append("sql_tool")
            return json.dumps({
                "needs_tool": needs_tool,
                "tools": tools,
                "reasoning": f"Simulated tool check returned {tools}."
            })
        elif "facts" in messages[0]["content"]:
            # Memory extract simulation
            facts = []
            if "my name is" in q:
                parts = last_user_msg.split("my name is")
                name = parts[1].strip().split()[0] if len(parts) > 1 else "User"
                facts.append({"key": "user_name", "value": name})
            return json.dumps({"facts": facts})
        return "{}"
        
    # Standard text completions fallback
    if "plan" in q or "roadmap" in q or "step" in q:
        return f"""### Simulated Planning Roadmap
1. **Assessment Phase**: Clarify query focus on '{last_user_msg}'.
2. **Retrieve Resources**: Ingest documentation and system database files.
3. **Draft Strategy**: Configure agent state milestones.
4. **Execution**: Invoke tools (e.g. calculator, python) and compile feedback.
5. **Review**: Self-reflection auditing for maximum grounding accuracy."""

    return f"[Simulated Response] This is a mock response for query: '{last_user_msg}'. Access to live LLM answers is restricted until GROQ_API_KEY or OPENAI_API_KEY is defined in `.env`."
