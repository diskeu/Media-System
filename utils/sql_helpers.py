from utils.sentinel import DEFAULT

def format_value(value):
    """Formats value to correspond the sql syntax"""
    # if isinstance(value, (datetime, date, str)): return f"{value}" could possible add extra querys
    if type(value) == bool: return value
    if value == DEFAULT: return "DEFAULT"
    elif value == None: return None
    return str(value)