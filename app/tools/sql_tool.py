from sqlalchemy import text
from app.database.database import engine

def execute_sql_query(query: str) -> str:
    """
    Executes a raw SQL statement against the local database engine and returns the formatted results.
    Restricts write operations to prevent unintended modifications.
    """
    query_clean = query.strip()
    
    # Simple check to enforce read-only SELECT operations
    if not query_clean.lower().startswith("select") and not query_clean.lower().startswith("pragma") and not query_clean.lower().startswith("explain"):
         return "Security Error: Only read-only queries (e.g. SELECT) are permitted."
         
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query_clean))
            
            # If no rows are returned (e.g., SELECT statements that return no results)
            if not result.returns_rows:
                return "Query executed successfully. No records returned."
                
            keys = result.keys()
            rows = result.all()
            
            if not rows:
                return f"Query returned empty table (Columns: {', '.join(keys)})."
                
            # Format as markdown table
            headers = " | ".join(str(k) for k in keys)
            separator = " | ".join("---" for _ in keys)
            markdown_rows = []
            
            for row in rows:
                markdown_rows.append(" | ".join(str(val) for val in row))
                
            table = f"| {headers} |\n| {separator} |\n"
            table += "\n".join(f"| {r} |" for r in markdown_rows)
            return table
            
    except Exception as e:
        return f"Database Error: {e}"
