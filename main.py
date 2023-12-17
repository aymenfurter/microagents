import os
import time
import threading
from agents.microagent import MicroAgent
from agents.microagent_manager import MicroAgentManager
from utils.utility import get_env_variable, time_function
from prompt_management.prompts import USER_INPUTS
from colorama import Fore, Style
from terminaltables import AsciiTable

def clear_console():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_agent_info(manager, stop_event):
    """
    Continuously displays comprehensive information about the agents.
    """
    while not stop_event.is_set():
        clear_console()

        header = ["Agent", "Evolve Count", "Active Agents", "Usage Count", "Max Depth", "Depth", "Working Agent", "Status"]
        agents_data = [header]
        agents = manager.get_agents()
        for agent in agents:
            active_agents = ", ".join(f"{k}->{v}" for k, v in agent.active_agents.items())
            agents_data.append([
                agent.purpose, 
                agent.evolve_count, 
                active_agents,
                agent.usage_count,
                agent.max_depth,
                agent.depth,
                "Yes" if agent.working_agent else "No",
                agent.current_status 
            ])

        table = AsciiTable(agents_data)
        print(Fore.CYAN + "🤖 Agents Comprehensive Status and Tree View:" + Style.RESET_ALL)
        print(table.table)
        time.sleep(1)  # Refresh interval

@time_function
def process_user_input(manager, user_input):
    """
    Processes a single user input and generates a response.
    """
    agent = manager.get_or_create_agent("General", depth=1, sample_input=user_input)
    response = agent.respond(user_input)
    print(Fore.YELLOW + "🔍 Question:" + Style.RESET_ALL, user_input)
    print(Fore.GREEN + "💡 Response:" + Style.RESET_ALL, response)
    print(Fore.BLUE + "📝 Dynamic Prompts:" + Style.RESET_ALL)
    for agent in manager.get_agents():
        print(Fore.MAGENTA + f"Prompt for {agent.purpose}:" + Style.RESET_ALL)
        print(agent.dynamic_prompt + "\n")


def main():
    api_key = get_env_variable("OPENAI_KEY", raise_error=False)
    if not api_key:
        print(Fore.RED + "🚫 Error: OPENAI_KEY environment variable is not set." + Style.RESET_ALL)
        return

    manager = MicroAgentManager(api_key)
    manager.create_agents()  

    stop_event = threading.Event()
    display_thread = threading.Thread(target=display_agent_info, args=(manager, stop_event))
    display_thread.start()

    try:
        for user_input in USER_INPUTS:
            process_user_input(manager, user_input)
    finally:
        stop_event.set()
        display_thread.join()
        display_agent_info(manager, stop_event)  

def microagent_factory(initial_prompt, purpose, api_key, depth, max_depth, bootstrap_agent):
    return MicroAgent(initial_prompt, purpose, api_key, depth, max_depth, bootstrap_agent)

if __name__ == "__main__":
    main()
