import re

def calculate(expression: str) -> str:
    """
    Safely evaluates simple mathematical expressions.
    Supports numbers, spaces, operators (+, -, *, /, **, (, )).
    """
    # Sanitize input: allow only digits, operators, spaces, parentheses, decimal points
    sanitized = re.sub(r"[^0-9\+\-\*\/\(\)\.\s]", "", expression)
    sanitized = sanitized.strip()
    
    if not sanitized:
        return "Error: Empty expression."
        
    try:
        # Safe eval using limited globals/locals
        result = eval(sanitized, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression '{expression}': {e}"
