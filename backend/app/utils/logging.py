# app/utils/logging.py
import logging
import json
import traceback
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

T = TypeVar('T')

def log_execution_time(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to log the execution time of a function."""
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            logging.info(f"Executed {func.__name__} in {execution_time:.4f} seconds")
    return wrapper

def log_error(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to log errors in a function."""
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}")
            logging.debug(traceback.format_exc())
            raise
    return wrapper