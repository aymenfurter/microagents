import os
from agents.microagent import MicroAgent
from agents.microagent_manager import MicroAgentManager
from utils.utility import get_env_variable, time_function
from prompt_management.prompts import USER_INPUTS
from colorama import Fore, Style
from terminaltables import AsciiTable

def main():
    api_key = get_env_variable("OPENAI_KEY", raise_error=False)
    if not api_key:
        print(Fore.RED + "🚫 Error: OPENAI_KEY environment variable is not set." + Style.RESET_ALL)
        return

    manager = MicroAgentManager(api_key)
    manager.create_agents()  # Initialize agents

    for user_input in USER_INPUTS:
        process_user_input(manager, user_input)

@time_function
def process_user_input(manager, user_input):
    """
    Processes a single user input and generates a response.
    """
    agent = manager.get_or_create_agent("General", depth=1, sample_input=user_input)
    response = agent.respond(user_input)
    print(Fore.YELLOW + "🔍 Question:" + Style.RESET_ALL, user_input)
    print(Fore.GREEN + "💡 Response:" + Style.RESET_ALL, response)

    agents_data = [["Agent", "Depth", "Max Depth", "Usage Count", "Working Agent", "Agent Creator"]]
    agents = manager.get_agents()
    for agent in agents:
        agents_data.append([
            f"{agent.purpose}", 
            f"{agent.depth}", 
            f"{agent.max_depth}",
            f"{agent.usage_count}",
            f"{agent.working_agent}",
            f"{agent.agent_creator}"
        ])

    table = AsciiTable(agents_data)
    print(Fore.CYAN + "🤖 Agents Overview:" + Style.RESET_ALL)
    print(table.table)

    print(Fore.BLUE + "📝 Dynamic Prompts:" + Style.RESET_ALL)
    for agent in agents:
        print(Fore.MAGENTA + f"Prompt for {agent.purpose}:" + Style.RESET_ALL)
        print(agent.dynamic_prompt + "\n")

def microagent_factory(initial_prompt, purpose, api_key, depth, max_depth, bootstrap_agent):
    return MicroAgent(initial_prompt, purpose, api_key, depth, max_depth, bootstrap_agent)

if __name__ == "__main__":
    main()
