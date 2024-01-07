from dotenv import load_dotenv
import os

def load_env_variable(var_name: str) -> str:
    """
    Load an environment variable.
    """
    load_dotenv()
    return os.getenv(var_name, "")

def format_agent_data(agent_data: dict) -> str:
    """
    Format agent data into a readable string for display in Gradio interface.
    """
    formatted_data = []
    for key, value in agent_data.items():
        formatted_data.append(f"### {key}:\n {value} \n")
    return "\n".join(formatted_data)

def format_log_message(message: str) -> str:
    """
    Format a log message for display in Gradio interface.
    """
    # Implement any specific formatting you need for log messages
    return message