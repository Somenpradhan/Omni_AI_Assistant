from datetime import datetime

def get_current_datetime() -> str:
    """
    Returns current date, time, and timezone information.
    """
    now = datetime.now()
    return f"Current System Date/Time: {now.strftime('%A, %B %d, %Y - %I:%M:%S %p')} (local time)"
