from app.llm.provider import get_chat_completion
from app.tools.calculator import calculate
from app.tools.python_executor import execute_python
from app.tools.sql_tool import execute_sql_query
from app.tools.datetime_tool import get_current_datetime
from app.tools.file_reader import read_local_file
from app.database import crud
from app.database.database import SessionLocal

def extract_tool_arguments(tool_name: str, query: str, plan: str) -> str:
    """
    Asks the LLM to isolate and format the argument input for a specific tool.
    """
    prompt = f"""You are a tool input parsing agent.
You need to extract the raw input argument for the tool '{tool_name}' given the user's query and plan.

User Query: "{query}"
Plan: "{plan}"

Format instructions:
- For 'calculator': Return only the mathematical expression (e.g. "2 + 2"). Do not wrap in print() or extra code.
- For 'python_executor': Return the full, runnable Python script block. Do not include markdown code fences (like ```python).
- For 'sql_tool': Return only the SELECT statement query string.
- For 'file_reader': Return only the absolute/relative filepath to read.

Write the tool input below:"""
    try:
        response = get_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        # Clean up any trailing/leading whitespace or markdown quotes
        clean_arg = response.strip()
        if clean_arg.startswith("```python"):
            clean_arg = clean_arg.replace("```python", "", 1)
        if clean_arg.startswith("```"):
            clean_arg = clean_arg.replace("```", "", 1)
        if clean_arg.endswith("```"):
            clean_arg = clean_arg[:-3]
        return clean_arg.strip()
    except Exception:
        return query

def executor_agent(tools: list, query: str, plan: str) -> str:
    """
    Executes a list of selected tools and aggregates the results into a markdown log string.
    Persists tool transaction logs to database.
    """
    if not tools:
        return "No tools executed."
        
    execution_results = []
    db = SessionLocal()
    
    for tool in tools:
        tool_clean = tool.strip().lower()
        arg = extract_tool_arguments(tool_clean, query, plan)
        output = ""
        
        print(f"[ExecutorAgent] Executing tool: '{tool_clean}' with input: '{arg}'")
        
        if tool_clean == "calculator":
            output = calculate(arg)
        elif tool_clean == "python_executor":
            output = execute_python(arg)
        elif tool_clean == "sql_tool":
            output = execute_sql_query(arg)
        elif tool_clean == "datetime_tool":
            output = get_current_datetime()
        elif tool_clean == "file_reader":
            output = read_local_file(arg)
        else:
            output = f"Unknown tool: '{tool}'"
            
        # Log to db
        try:
            crud.log_tool_execution(db, tool_clean, arg, output)
        except Exception as e:
            print(f"[Warning] Failed logging tool to db: {e}")
            
        execution_results.append(f"### Tool: {tool_clean}\n- **Input**: `{arg}`\n- **Output**:\n{output}\n")
        
    db.close()
    return "\n".join(execution_results)
