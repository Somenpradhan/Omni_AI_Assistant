import sys
import io
import traceback

def execute_python(code: str) -> str:
    """
    Executes a Python code block and returns stdout or error trace.
    WARNING: Runs in-process. For production environments, utilize a secure Docker container sandbox.
    """
    # Create StringIO objects to capture stdout/stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = mystdout = io.StringIO()
    sys.stderr = mystderr = io.StringIO()
    
    local_scope = {}
    global_scope = {}
    
    try:
        # Execute code in local/global scopes
        exec(code, global_scope, local_scope)
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        
        stdout_val = mystdout.getvalue()
        stderr_val = mystderr.getvalue()
        
        output = []
        if stdout_val:
            output.append(f"STDOUT:\n{stdout_val}")
        if stderr_val:
            output.append(f"STDERR:\n{stderr_val}")
            
        if not output:
            # Check if any local variable was set, or if expression evaluates
            return "Code executed successfully. No stdout output."
            
        return "\n".join(output)
        
    except Exception as e:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        tb = traceback.format_exc()
        return f"Execution Error: {e}\nTraceback:\n{tb}"
