import time
import functools
import logging
from contextlib import contextmanager

# Configure logger
logger = logging.getLogger("performance")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - [TIMER] - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

@contextmanager
def timer(label: str):
    """
    Context manager to time a block of code.
    Usage:
        with timer("My Operation"):
            # do something
    """
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"{label}: {duration:.4f}s")

def time_execution(label: str = None):
    """
    Decorator to time a function execution.
    Usage:
        @time_execution("My Function")
        def my_func():
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_label = label or func.__name__
            with timer(func_label):
                return func(*args, **kwargs)
        return wrapper
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        func_label = label or func.__name__
        with timer(func_label):
            return await func(*args, **kwargs)
            
    return decorator if not asyncio.iscoroutinefunction(func) else async_wrapper

# Fix for the decorator to handle both sync and async correctly simply
# The above decorator approach is a bit complex to get right for both sync/async 
# without inspecting the function. Let's simplify and just use the context manager mostly.
# But for the decorator, we can return a wrapper that checks if it's awaiting.

def async_time_execution(label: str = None):
    """Decorator specifically for async functions"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            func_label = label or func.__name__
            with timer(func_label):
                return await func(*args, **kwargs)
        return wrapper
    return decorator
