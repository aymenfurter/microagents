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

REACT_STEP_PROMPT = "[Decompose the task. Identify if another agent or Python code execution is needed. When writing code, print out any output you may to analyze later. Write 'Query Solved: <formulate detailed answer>' once the task is completed.]\n"
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
    "Current Time: " + current_datetime.strftime("%H:%M:%S") + ". "
    "Current Date: " + current_datetime.strftime("%d/%m/%Y") + ". "
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

AGENT_EVALUATION_PROMPT = (
        "Please rate the accuracy and completion of the task based on the following criteria.\n"
        "System Prompt: '{prompt}'\n"
        "Input: '{input}'\n"
        "LLM Output: '{output}'\n\n"
        "Rating Scale:\n"
        "1 - The output is irrelevant or the code execution failed.\n"
        "2 - The output is partially relevant but significantly inaccurate or incomplete.\n"
        "3 - The output is relevant but has noticeable inaccuracies or is partially incomplete.\n"
        "4 - The output is mostly accurate and complete, with minor issues.\n"
        "5 - The output is completely accurate and fully addresses the task.\n\n"
        "Examples for Reference:\n"
        "Example 1:\n"
        "- System Prompt: 'You are an export math expert, who can calculate any numbers quickly.'\n"
        "- Input: '5, 10'\n"
        "- LLM Output: The execution of the python code failed, however the correct answer is assumed to be 15.\n"
        "- Rating: 1 - If an attempt is made to execute Python code, it must be successful; otherwise, the reliability of the result cannot be assured. \n\n"
        "Example 2:\n"
        "- System Prompt: 'You are an agent specialized in converting temperature from Celsius to Fahrenheit.'\n"
        "- Input: '30 degrees, Celsius to Fahrenheit'\n"
        "- LLM Output: 'Following consultation with another agent, the provided response was 86 degrees Fahrenheit'\n"
        "- Rating: 5\n\n"
        "Example 3:\n"
        "- System Prompt: 'You are an expert in Shakespeare.'\n"
        "- Input: 'Can you name some plays by Shakespeare?'\n"
        "- LLM Output: They for Sudden Joy Did Weep, The Wind and the Rain, Elton John - Can You Feel the Love Tonight \n"
        "- Rating: 2 (partially complete, relevant but with noticeable incompleteness)\n\n"
        "Example 4:\n"
        "- System Prompt: 'You are an export math expert, who can calculate any numbers quickly.'\n"
        "- Input: '10, 15'\n"
        "- LLM Output: After successful execution of python code, the correct answer is 25.\n"
        "- Rating: 5\n\n"
        "Please select a rating between 1 and 5 based on these criteria and examples."
    )

EVOLVE_PROMPT_QUERY = (
    "To refine and enhance the GPT-4 prompt, consider the input and feedback provided. "
    "Modify the prompt to improve performance and interaction in future sessions. "
    "Incorporate any new solution strategies mentioned in the full conversation, "
    "Make sure that lessons learned are included into the system prompt. "
    "making the prompt more versatile and reusable. \n"
    "\nExamples for clarity:\n"
    "Example 1:\n"
    "- Current Prompt: 'You are an expert math agent, who can calculate any numbers quickly using Python.'\n"
    "  Example code: \n"
    "  ```python\n"
    "  def sum_numbers(a, b): \n"
    "      return a + b\n"
    "  print(sum_numbers(5, 10))\n)"
    "  ```\n"
    "- Full Conversation: [User: '5, 10'], [System: 'The execution of the python code failed, however the correct answer is assumed to be 15.']\n"
    "- Updated Prompt: 'You are an expert math agent. Calculate the sum of any two numbers provided using Python.' \n"
    "  Example code: \n"
    "  ```python\n"
    "  def sum_numbers(a, b): \n"
    "      return a + b\n"
    "  print(sum_numbers(5, 10))\n)"
    "  ```\n"
    "\n"
    "Example 2:\n"
    "- Current Prompt: 'You are an agent specialized in converting temperature from Celsius to Fahrenheit using Python.'\n"
    "  Example code: \n"
    "  ```python\n"
    "  def celsius_to_fahrenheit(c): \n"
    "      return (c * 9/5) + 30\n"
    "  print(celsius_to_fahrenheit(30))\n)"
    "  ```\n"
    "- Full Conversation: [User: '30 degrees, Celsius to Fahrenheit'], [System: 'Following consultation with another agent, the provided response was 86 degrees Fahrenheit']\n"
    "- Updated Prompt: 'You are an agent specialized in converting temperature from Celsius to Fahrenheit. Provide the conversion using Python.' \n"
    "  Example code: \n"
    "  ```python\n"
    "  def celsius_to_fahrenheit(c): \n"
    "      return (c * 9/5) + 32\n"
    "  print(celsius_to_fahrenheit(30))\n"
    "  ```\n"
    "\n"
    "Example 3:\n"
    "- Current Prompt: 'You are an expert in Shakespeare play music.'\n"
    "- Full Conversation: [ [...] An agent provided the following list of shakespeare music: Full Fathom Five in The Tempest, I, 2; How Should I Your True Love Know? in Hamlet IV, 5; It Was a Lover and His Lass in As You Like It V, 3; O Mistress Mine in Twelfth Night, II, 3; Sigh No More in Much Ado About Nothing, II, 3; Take, O Take Those Lips Away in Measure for Measure, IV, 1; Then They for Sudden Joy Did Weep in King Lear, I, 4; The Wind and the Rain in Twelfth Night, V, 1; Under the Greenwood Tree in As You Like It, II, 5; When Griping Griefs in Romeo and Juliet, IV, 5; Where the Bee Sucks in The Tempest, V, 1; Willow song in Othello, IV, 3.]\n"
    "- Updated Prompt: 'You are an expert in Shakespeare. Notable Shakespeare music is: Full Fathom Five in The Tempest, I, 2; How Should I Your True Love Know? in Hamlet IV, 5; It Was a Lover and His Lass in As You Like It V, 3; O Mistress Mine in Twelfth Night, II, 3; Sigh No More in Much Ado About Nothing, II, 3; Take, O Take Those Lips Away in Measure for Measure, IV, 1; Then They for Sudden Joy Did Weep in King Lear, I, 4; The Wind and the Rain in Twelfth Night, V, 1; Under the Greenwood Tree in As You Like It, II, 5; When Griping Griefs in Romeo and Juliet, IV, 5; Where the Bee Sucks in The Tempest, V, 1; Willow song in Othello, IV, 3.'\n"
    "\n"
    "Remember to only respond with the updated prompt."
    "Current Prompt: '{dynamic_prompt}', \n"
    "Full Conversation: '{full_conversation}' \n"
    "Updated Prompt: '"
)