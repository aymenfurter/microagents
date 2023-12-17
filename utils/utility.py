import os
import time
import logging

def get_env_variable(var_name, default=None, raise_error=True):
    """
    Retrieves an environment variable. If not found, returns the default
    value or raises an error based on the raise_error flag.
    """
    try:
        return os.environ[var_name]
    except KeyError:
        if raise_error:
            raise EnvironmentError(f"Error: {var_name} environment variable is not set.")
        return default

def time_function(func):
    """
    Decorator to measure the execution time of a function.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time() - start_time
        logging.info(f"Time taken by {func.__name__}: {end_time} seconds")
        return result
    return wrapper

def log_exception(e, message="An error occurred"):
    """
    Logs exceptions with a custom message.
    """
    logging.error(f"{message}: {str(e)}")
