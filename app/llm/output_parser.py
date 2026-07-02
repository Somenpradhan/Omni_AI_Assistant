import json
import re

def parse_json(text: str) -> dict:
    """
    Cleans up any markdown wrapper blocks (e.g. ```json ... ```) and parses text as JSON.
    """
    if not text:
        return {}
        
    text_clean = text.strip()
    
    # Remove markdown code fence blocks if present
    text_clean = re.sub(r"^```(?:json)?\n", "", text_clean, flags=re.IGNORECASE)
    text_clean = re.sub(r"\n```$", "", text_clean)
    text_clean = text_clean.strip()
    
    # Try parsing
    try:
        return json.loads(text_clean)
    except Exception:
        # Fallback regex extraction if parsing failed directly
        try:
            match = re.search(r"\{.*\}", text_clean, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception:
            pass
            
    print(f"[Warning] Failed parsing JSON from raw text: {text}")
    return {}
