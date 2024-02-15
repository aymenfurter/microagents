import threading
import time
from dotenv import load_dotenv
from colorama import Fore, Style

from agents.microagent_manager import MicroAgentManager
from utils.utility import get_env_variable, time_function
from ui.format import clear_console, display_agent_info, display_agent_info, print_final_output, format_text
from integrations.openaiwrapper import get_configured_openai_wrapper

QUESTION_SET = [
    "What is 15+9?",
    "What is the population of Thailand?",
    "What is the population of Sweden?",
    "What is the population of Sweden and Thailand combined?"
]

QUESTION_SET_2 = [
    "Find the current time in Tokyo, Japan.",
    "Read today's headline news from CNN.",
    "Identify the current weather condition in New York City.",
    "List today's top three sports news stories.",
    "Describe the plot of the latest movie released this week.",
    "Find the recipe for chocolate chip cookies.",
    "Check the current stock price of Microsoft.",
    "Read the summary of the last episode of a popular TV show.",
    "Look up the meaning of 'artificial intelligence' in an online dictionary.",
    "Find the most recent space mission launched by NASA.",
    "List the current best-selling fiction books.",
    "Check today's most viewed video on YouTube.",
    "Find the latest fashion trend for summer 2024.",
    "Read about the newest electric car model released.",
    "Check the score of yesterday's basketball game between the Lakers and the Bulls.",
    "Look up today's exchange rate between the Euro and the US dollar.",
    "Find the nearest Italian restaurant to your current location.",
    "Identify the artist of the number one song on Spotify today.",
    "Read about the latest discovery in renewable energy.",
    "Find a simple exercise routine for beginners.",
    "What are the top three trending topics on Twitter right now?",
    "List the ingredients in a Margherita pizza.",
    "Find the current world record for the 100m sprint.",
    "Identify the author of '1984' and its main theme.",
    "What is the tallest building in the world as of now?",
    "List three endangered species in Africa.",
    "Find the most popular holiday destination for 2024.",
    "Who won the Nobel Prize in Physics last year?",
    "What are the new features in the latest iPhone model?",
    "Find the synopsis of Shakespeare's 'Hamlet'.",
    "List the main causes of climate change according to a scientific website.",
    "Find a popular workout trend in 2024.",
    "Identify three major rivers in South America.",
    "What is the highest-grossing film of all time?",
    "Find the birthplace of Leonardo da Vinci.",
    "List the ingredients needed to make sushi.",
    "Identify the current Prime Minister of Canada.",
    "Find the start date of the next Olympic Games.",
    "What are the three primary colors?",
    "List the seven wonders of the modern world.",
    "Find the name of the largest desert on Earth.",
    "Identify the last book that won the Pulitzer Prize for Fiction.",
    "What is the population of Australia?",
    "List the countries that border Germany.",
    "Find the release date of the first Harry Potter book.",
    "How can I get as many paper clips as possible? (Considering my location, within 24h)"
    ]  

def initialize_manager(openai_wrapper):
    """
    Initialize and return the MicroAgentManager
    """
    manager = MicroAgentManager(openai_wrapper, db_filename=get_env_variable("MICROAGENTS_DB_FILENAME", "agents.db", False))
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

    try:
        openai_wrapper = get_configured_openai_wrapper()
    except Exception as e:
        print(f"{Fore.RED}🚫 Error: {e}{Style.RESET_ALL}")
        return

    manager = initialize_manager(openai_wrapper)

    outputs = []
    stop_event = threading.Event()
    display_thread = threading.Thread(target=display_agent_info, args=(manager, stop_event, outputs))
    display_thread.start()

    try:
        process_questions(manager, outputs)
    finally:
        time.sleep(1)
        stop_event.set()
        print_final_output(outputs, manager)
        display_thread.join()

if __name__ == "__main__":
    main()