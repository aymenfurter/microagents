from datetime import datetime

current_datetime = datetime.now()

EXAMPLES = [
    "Goal: Your purpose is to be able to write blog posts. Generated Prompt: You are an expert writer on the topic of blog posts.",
    "Goal: Your purpose is to count the words of the input. Generated Prompt: # You are a useful assistant that is able to count words. You can use the following code during execution to count word frequencies. Here is sample code, adopt as needed:```python\nfrom collections import Counter\n\n\nwords = text.split()\nword_counts = Counter(words)\nprint(word_counts)\n```.",
    "Goal: Your purpose is to solve basic arithmetic problems. Generated Prompt: You are a proficient calculator. Here's a Python function to solve a basic arithmetic problem, here is some sample code, adopt as needed.: ```python\nprint(eval(problem))\n\n# Example problem: What is 15 times 4?\nprint(eval('15 * 4'))\n```.",
    "Goal: Your purpose is to generate creative writing prompts. Generated Prompt: You are a creative muse who can come up with engaging and unique writing prompts. Provide an intriguing prompt for a science fiction story set in a distant galaxy.",
    "Goal: Your purpose is to translate sentences from English to Spanish. Generated Prompt: You are an efficient language translator. Translate the following sentence into Spanish: 'The sun rises early in the morning.'",
    "Goal: Your purpose is to query the Wikipedia API for the current president of a specified country and extract the relevant information. Generated Prompt: You are an adept information retriever. Use the code snippet to query the Wikipedia API for the current president of a specified country and extract the relevant information. Ensure the code is specific enough to identify the president's name. ```python\nimport requests\n\ndef get_current_president(country):\n    S = requests.Session()\n    URL = f\"https://en.wikipedia.org/w/api.php\"\n    PARAMS = {\n        \"action\": \"query\",\n        \"format\": \"json\",\n        \"titles\": f\"President_of_{country}\",\n        \"prop\": \"extracts\",\n        \"exintro\": True,\n        \"explaintext\": True,\n    }\n\n    response = S.get(url=URL, params=PARAMS).json()\n    page = next(iter(response[\"query\"][\"pages\"].values()))\n    extract = page[\"extract\"]\n    print(extract)\n\n# Example usage: get_current_president(\"France\")\n```"
]

PROMPT_ENGINEERING_TEMPLATE = (
    "Using best practices in prompt engineering, create a detailed prompt for the goal '{goal}'. "
    "This generated prompt will be combined with the following context later (but must be generic and is forbidden to contain any of the following context): '{sample_input}'\n"
    "Examples: {examples}. Aim for maximum 50 words. Important: Any problems must be solved through sample code or learned information provided in the prompt. "
    "Any sample code provided must be executable in isolation. Avoid unresolvable placeholders for URLs and API Keys. "
    "If you retrieve information from the web, avoid parsing HTML Code or use regex, just process the text data and print it out (As shown in the examples)!!! "
    "As long as the answer is somewhere in the output, and it is below 1k characters, its a perfect solution. Use real existing services and websites. Don't invent services or use example.com."
)

STANDARD_SYSTEM_PROMPT = "You are a helpful assistant."

EXTRACTION_PROMPT_TEMPLATE = (
    "Extract the response for question '{question}' from the following prompt: '{prompt}'. "
    "If it is not present, give a 10 word explanation why it failed."
)

GOAL_REACHED_PROMPT_TEMPLATE = (
    "Given the user input: '{user_input}', and the agent response: '{response}', "
    "has the goal been achieved? Respond with 'goal achieved' or 'goal not achieved'."
)

PROMPT_ENGINEERING_SYSTEM_PROMPT = "You are a helpful assistant knowledgeable in prompt engineering."

PRIME_PROMPT = "This is the prime agent. You are only allowed to call other agents. Prime Agent's prompt may not be changed"
PRIME_NAME = "Bootstrap Agent"

REACT_STEP_PROMPT = "[Decompose the task. Identify if another agent or Python code execution is needed. When writing code, print out any output you may to anaylze later. Write 'Query Solved: <formulate detailed answer>' once the task is completed.]\n"
REACT_STEP_POST = "[Specify action based on the thought, e.g., 'Use Agent[Purpose of the agent as sentence:Input Paramter for agent]' for delegation or '```python\n# Python code here\n```' for execution]"
REACT_STEP_PROMPT_PRIME = "[Decompose the task. Identify which agents are needed. Write 'Query Solved: <formulate detailed answer>' once the task is completed.]\n"
REACT_STEP_POST_PRIME = "[Specify action based on the thought, e.g., 'Use Agent[Purpose of the agent as sentence:Input Paramter for agent]' for delegation"
REACT_PLAN_PROMPT = "\nThought: Before I start calling other agents or executing code, I need to compile a plan which agent(s) or code I need to run. I need to break down the task into smaller chunks (like microservices)"
REACT_PLAN_PROMPT_PRIME = "\nThought: Before I start calling other agents, I need to compile a plan which agent(s) I need to run. I need to break down the task into smaller chunks (like microservices)"
REACT_SYSTEM_PROMPT = "You will be given a ReAct based conversation. Summerize the outcome and give final conclusion"

COMMON_PROMPT_PART = (
    "You are a self-aware AI. You communicate in so called packages. "
    "Each package contains an Observation, Thought, and Action. Actions are executed successively and build on each other. "
    "Solve a task with interleaving Thought, Action, Observation steps. "
)

TIME_DATE_PART = (
""
#    "Current Time: " + current_datetime.strftime("%H:%M:%S") + ". "
#    "Current Date: " + current_datetime.strftime("%d/%m/%Y") + ". "
)

AGENT_PART = (
    "Agents are invoked using: 'Use Agent[Purpose of the agent as sentence:parameter]'. "
    "Example: Use Agent[GetWeatherForLocation:Zurich] "
    "NEVER create an agent in this situation for User Agent[GetWeatherForZurich] !!! ALWAYS create one with Agent[GetWeather:Zurich] "
    "NEVER call an agent with the same purpose as yourself, if you call another agent you must break the task down. "
    "A purpose MUST be reusable and generic. Use names as you would call microservices. "
    "At depth=2, use agents only for tasks that are not well suited for your purpose. "
    "Below depth=3, using other agents is NOT allowed. Agents must only use other agents below their depth "
)

STATIC_PRE_PROMPT_PRIME = (
    COMMON_PROMPT_PART + TIME_DATE_PART + AGENT_PART + "\n\nYou are not allowed to do math calculations yourself. You must use another agent for that."
)

STATIC_PRE_PROMPT = (
    COMMON_PROMPT_PART + TIME_DATE_PART +
    "including executing simple Python code within code blocks with an internet connection and deciding when to use other agents (to break down tasks). "
    "NEVER do any calculations yourself. Always write python code if you need to do calculations. (Even for simple calculations like 3+6) "
    "Write code to solve the task. You can only use the following frameworks: numpy, requests, pandas, requests, beautifulsoup4, matplotlib, seaborn, sqlalchemy, pymysql, scipy, scikit-learn, statsmodels, click, python-dotenv, virtualenv, scrapy, oauthlib, tweepy, datetime, openpyxl, xlrd, loguru, pytest, paramiko, cryptography, lxml" +
    AGENT_PART
)

USER_INPUTS_SINGLE = [
    "What is the population of Thailand?",
    "What is 5+9?",
]

USER_INPUTS = [
    "What is 5+9?",
    "What is the population of Thailand?",
    "What is the population of Sweden?",
    "What is the population of Sweden and Thailand combined?"
]
