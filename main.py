import time
import os
from microagentmanager import MicroAgentManager 
from prompts import USER_INPUTS

def main():
    try:
        api_key = os.environ["OPENAI_KEY"]
    except KeyError:
        print("Error: OPENAI_KEY environment variable is not set.")
        return

    manager = MicroAgentManager(api_key)

    user_inputs = USER_INPUTS
    
    for user_input in user_inputs:
        start_time = time.time()
        response = manager.respond(user_input)
        final_response = manager.extractResponseFromPrompt(response, user_input)
        print("Question:", user_input)
        print("Response:", final_response)
        end_time = time.time() - start_time
        print("Time taken:", end_time)
        print("Number of Agents:", len(manager.agents))

if __name__ == "__main__":
    main()