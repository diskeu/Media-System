from typing import Callable, Any, Type
from inspect import iscoroutinefunction
def return_when_error(error_type: Type[BaseException]):
    def decorator(func: Callable[..., Callable]) -> Callable[..., Any]:
        async def wrapper(*args, **kwargs):
            """The first arg indicates the error type to look for"""
            if iscoroutinefunction(func):
                return isinstance(await func(*args, **kwargs), error_type)
            return isinstance(func(*args, **kwargs), error_type)
        return wrapper
    return decorator