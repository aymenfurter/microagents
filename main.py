import os
import time
import threading
from agents.microagent import MicroAgent
from agents.microagent_manager import MicroAgentManager
from utils.utility import get_env_variable, time_function
from prompt_management.prompts import USER_INPUTS, USER_INPUTS_SINGLE 
from colorama import Fore, Style
from terminaltables import AsciiTable
from itertools import cycle

def clear_console():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_agent_info(manager, stop_event, outputs):
    """
    Continuously displays comprehensive information about the agents.
    """
    animation = cycle(['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘'])
    while not stop_event.is_set():
        clear_console()

        header = [
            "👤 Agent", 
            "🔁 Evolve Count", 
            "💻 Code Executions", 
            "👥 Active Agents", 
            "📈 Usage Count", 
            "🌟 Depth", 
            "Working?", 
            "📝 Last Input", 
            "🚦 Status"
        ]

        agents_data = [header]
        agents = manager.get_agents()
        for agent in agents:
            active_agents = ", ".join(f"{k}->{v}" for k, v in agent.active_agents.items())
            agents_data.append([
                agent.purpose, 
                agent.evolve_count, 
                agent.number_of_code_executions,
                active_agents,
                agent.usage_count,
                agent.depth,
                "✅" if agent.working_agent else "❌",
                agent.last_input,
                agent.current_status 
            ])

        table = AsciiTable(agents_data)
        print(Fore.CYAN + "🤖 \033[1m Agents Status:\033[0m \n" + Style.RESET_ALL)
        print(table.table)
        for output in outputs:
            print(output)
        print(f"\nAgents are running.. {next(animation)}\n", end='\r')  # '\r' returns the cursor to the start of the line

        time.sleep(1) 

@time_function
def process_user_input(manager, user_input, outputs):
    """
    Processes a single user input and generates a response.
    """
    agent = manager.get_or_create_agent("Bootstrap Agent", depth=1, sample_input=user_input)
    return agent.respond(user_input)


def main():
    api_key = get_env_variable("OPENAI_KEY", raise_error=False)
    if not api_key:
        print(Fore.RED + "🚫 Error: OPENAI_KEY environment variable is not set." + Style.RESET_ALL)
        return

    manager = MicroAgentManager(api_key)
    manager.create_agents()  

    outputs = []
    stop_event = threading.Event()
    display_thread = threading.Thread(target=display_agent_info, args=(manager, stop_event, outputs))
    display_thread.start()
    question_number = 1
    try:
        for user_input in USER_INPUTS:
            response = process_user_input(manager, user_input, outputs)
            output_text = Fore.YELLOW + "\n\n🔍 Question " + str(question_number) +": "+ Style.RESET_ALL + f" {user_input}\n" + Fore.GREEN + "💡 Response:" + Style.RESET_ALL + f" {response}"
            outputs += [output_text]
            question_number += 1

    finally:
        time.sleep(5)
        stop_event.set()
        clear_console()
        for output in outputs:
            print(output)
        for agent in manager.get_agents():
            print("📊 Stats for " + agent.purpose + ":")
            print("🔁 Evolve Count: " + str(agent.evolve_count))
            print("💻 Code Executions: " + str(agent.number_of_code_executions))
            print("👥 Active Agents: " + str(agent.active_agents))
            print("📈 Usage Count: " + str(agent.usage_count))
            print("🏔️ Max Depth: " + str(agent.max_depth))
            print("🌟 Depth: " + str(agent.depth))
            print("🛠️ Working Agent: " + str(agent.working_agent))
            print("📝 Last Input: " + str(agent.last_input))
            print("🚦 Status: " + str(agent.current_status))
            print(Fore.MAGENTA + f"\nPrompt for {agent.purpose}:" + Style.RESET_ALL)
            print(Fore.LIGHTMAGENTA_EX + agent.dynamic_prompt + "\n" + Style.RESET_ALL)

        display_thread.join()
        display_agent_info(manager, stop_event, outputs)  

def microagent_factory(initial_prompt, purpose, api_key, depth, max_depth, bootstrap_agent):
    return MicroAgent(initial_prompt, purpose, api_key, depth, max_depth, bootstrap_agent)

if __name__ == "__main__":
    main()
