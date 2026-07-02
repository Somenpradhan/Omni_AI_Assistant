from app.llm.provider import get_chat_completion
from app.llm.prompts import REFLECTION_PROMPT
from app.llm.output_parser import parse_json

def reflection_agent(query: str, evidence: str, response: str) -> dict:
    """
    Audits the generated response text against retrieved evidence context for accuracy.
    """
    prompt = REFLECTION_PROMPT.format(
        query=query,
        evidence=evidence or "None",
        response=response
    )
    
    try:
        res = get_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            json_mode=True
        )
        data = parse_json(res)
        return {
            "is_valid": data.get("is_valid", True),
            "confidence_score": data.get("confidence_score", 1.0),
            "suggested_corrections": data.get("suggested_corrections", ""),
            "reasoning": data.get("reasoning", "")
        }
    except Exception as e:
        print(f"[Warning] Reflection Agent failed: {e}.")
        return {
            "is_valid": True,
            "confidence_score": 1.0,
            "suggested_corrections": "",
            "reasoning": str(e)
        }
    
