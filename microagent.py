import logging
from openaiwrapper import OpenAIAPIWrapper
from agent_evaluation import AgentEvaluation
from agent_response import AgentResponse
from agent_similarity import AgentSimilarity
from code_execution import CodeExecution
from prompt_evolution import PromptEvolution
from response_extraction import ResponseExtraction
from utility import get_env_variable, time_function, log_exception

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MicroAgent:
    def __init__(self, initial_prompt, purpose, depth, agent_creator, openai_wrapper, max_depth=3, bootstrap_agent=False):
        self.dynamic_prompt = initial_prompt
        self.purpose = purpose
        self.depth = depth
        self.max_depth = max_depth
        self.usage_count = 0
        self.working_agent = bootstrap_agent
        self.agent_creator = agent_creator
        self.openai_wrapper = openai_wrapper

        self.agent_evaluator = AgentEvaluation(self.openai_wrapper)
        self.code_executor = CodeExecution()
        self.agent_responder = AgentResponse(self.openai_wrapper, self.agent_creator, self.code_executor, agent_creator, depth)
        self.agent_similarity = AgentSimilarity(self.openai_wrapper, self.agent_creator.agents)
        self.prompt_evolver = PromptEvolution(self.openai_wrapper, self.agent_creator)
        self.response_extractor = ResponseExtraction(self.openai_wrapper)

    @time_function
    def respond(self, input_text):
        try:
            response, full_conversation, new_solution, no_of_iterations = self.agent_responder.generate_response(input_text, self.dynamic_prompt, self.max_depth)
            if not self.working_agent:
                if (no_of_iterations > 2):
                    self.dynamic_prompt = self.prompt_evolver.evolve_prompt(input_text, self.dynamic_prompt, response, full_conversation, new_solution, self.depth)
                elif new_solution: 
                    self.working_agent = True
                # TODO Kill agent if not new_solution and no_of_iterations > 10:
            return response
        except Exception as e:
            log_exception(e)
            return "An error occurred while generating the response."