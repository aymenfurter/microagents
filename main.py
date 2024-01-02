import threading
import time
from dotenv import load_dotenv
from colorama import Fore, Style

from agents.microagent_manager import MicroAgentManager
from utils.utility import get_env_variable, time_function
from ui.basic_ui import clear_console, display_agent_info, display_agent_info, print_final_output, format_text

# Constants
QUESTION_SET = [
    "What is 5+9?",
    "What is the population of Thailand?",
    "What is the population of Sweden?",
    "What is the population of Sweden and Thailand combined?"
]

def initialize_manager(api_key):
    """
    Initialize and return the MicroAgentManager with the given API key.
    """
    manager = MicroAgentManager(api_key)
    manager.create_agents()
    return manager

@time_function
def process_user_input(manager, user_input):
    """
    Processes a single user input and generates a response.
    """
    agent = manager.get_or_create_agent("Bootstrap Agent", depth=1, sample_input=user_input)
    return agent.respond(user_input)

def process_questions(manager, outputs):
    """
    Process each question in the QUESTION_SET and append outputs.
    """
    for question_number, user_input in enumerate(QUESTION_SET, start=1):
        response = process_user_input(manager, user_input)
        output_text = format_text(question_number, user_input, response)
        outputs.append(output_text)

def main():
    load_dotenv()
    api_key = get_env_variable("OPENAI_KEY")

    if not api_key:
        print(f"{Fore.RED}🚫 Error: OPENAI_KEY environment variable is not set.{Style.RESET_ALL}")
        return

    manager = initialize_manager(api_key)

    outputs = []
    stop_event = threading.Event()
    display_thread = threading.Thread(target=display_agent_info, args=(manager, stop_event, outputs))
    display_thread.start()

    try:
        process_questions(manager, outputs)
    finally:
        time.sleep(5)
        stop_event.set()
        print_final_output(outputs, manager)
        display_thread.join()

if __name__ == "__main__":
    main()
