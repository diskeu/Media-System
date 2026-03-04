from typing import get_args

def check_type(obj: object) -> tuple[type]:
    """Check the type of an object and return a tuple with the one or more types if the object is an union"""
    typ = get_args(obj)
    if typ: return typ
    
    # checking if obj is a type itself
    if type(obj) == type: return (obj, )
    else: return (type(obj), )

def same_type(*objcts: object) -> bool:
    """Checks if two or more objects have the same type"""
    type_set: set = {type_o for o in objcts for type_o in check_type(o)}
    print(type_set)
    return True if len(type_set) == 1 else False

def convert_to_string(val: any):
    if isinstance(val, str): return val
    return str(val)