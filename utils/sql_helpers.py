from utils.sentinel import DEFAULT
from utils.type_helpers import convert_to_string
i = 0

def format_value(value):
    """Formats value to correspond the sql syntax"""
    # if isinstance(value, (datetime, date, str)): return f"{value}" could possible add extra querys
    if type(value) in (bool, bytes): return value
    if value == DEFAULT: return "DEFAULT"
    elif value == None: return None
    return convert_to_string(value)