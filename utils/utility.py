import os
import time
import logging
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger()

T = TypeVar("T", bound=Callable[..., Any])

DEFAULT_EXCEPTION_MESSAGE = "An error occurred"
ENV_VAR_NOT_SET_MESSAGE = "environment variable is not set"

def get_env_variable(var_name: str, default: Optional[str] = None, raise_error: bool = True) -> Optional[str]:
    """
    Retrieves an environment variable.

    Args:
        var_name (str): The name of the environment variable to retrieve.
        default (Optional[str]): The default value to return if the variable is not found. Defaults to None.
        raise_error (bool): Flag to indicate whether to raise an error if the variable is not found. Defaults to True.

    Returns:
        Optional[str]: The value of the environment variable or the default value.

    Raises:
        EnvironmentError: If raise_error is True and the environment variable is not set.
    """
    value = os.getenv(var_name)
    if value is None and raise_error:
        raise EnvironmentError(f"Error: {var_name} {ENV_VAR_NOT_SET_MESSAGE}.")
    return value or default

def time_function(func: T) -> T:
    """
    Decorator to measure the execution time of a function.

    Args:
        func (Callable): The function to measure.

    Returns:
        Callable: A wrapper function that adds execution time measurement to the input function.
    """
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter() - start_time
        logger.info(f"Time taken by {func.__name__}: {end_time:.6f} seconds")
        return result
    return wrapper

def log_exception(exception: Exception, message: str = DEFAULT_EXCEPTION_MESSAGE) -> None:
    """
    Logs exceptions with a custom message.

    Args:
        exception (Exception): The exception to log.
        message (str): Custom message to prepend to the exception message. Defaults to a standard error message.
    """
    logger.error(f"{message}: {exception}")
