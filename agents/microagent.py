import logging
from integrations.openaiwrapper import OpenAIAPIWrapper
from agents.agent_evaluation import AgentEvaluator
from agents.agent_response import AgentResponse
from agents.agent_similarity import AgentSimilarity
from runtime.code_execution import CodeExecution
from prompt_management.prompt_evolution import PromptEvolution
from agents.response_extraction import ResponseExtraction
from utils.utility import get_env_variable, time_function, log_exception

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class MicroAgent:
    """
    The MicroAgent class encapsulates the behavior of a small, purpose-driven agent
    that interacts with the OpenAI API.
    """
    
    def __init__(self, initial_prompt, purpose, depth, agent_creator, openai_wrapper, max_depth=3, bootstrap_agent=False):
        self.dynamic_prompt = initial_prompt
        self.purpose = purpose
        self.depth = depth
        self.max_depth = max_depth
        self.usage_count = 0
        self.working_agent = bootstrap_agent
        self.agent_creator = agent_creator
        self.openai_wrapper = openai_wrapper
        self.evolve_count = 0  # Track how often the agent has evolved
        self.current_status = None  # Track the current status of the agent
        self.active_agents = {}  # Track active agents in a tree view

        # Initialize components used by the agent
        self.agent_evaluator = AgentEvaluator(self.openai_wrapper)
        self.code_executor = CodeExecution()
        self.agent_responder = AgentResponse(self.openai_wrapper, self.agent_creator, self.code_executor, self, agent_creator, depth)
        self.agent_similarity = AgentSimilarity(self.openai_wrapper, self.agent_creator.agents)
        self.prompt_evolver = PromptEvolution(self.openai_wrapper, self.agent_creator)
        self.response_extractor = ResponseExtraction(self.openai_wrapper)

    def update_status(self, status):
        """Update the agent's current status."""
        self.current_status = status
        logging.info(f"Agent {self.purpose} status updated to: {status}")

    def update_active_agents(self, calling_agent, called_agent=None):
        """Update the tree view of active agents."""
        if called_agent:
            self.active_agents[calling_agent] = called_agent
        else:
            self.active_agents.pop(calling_agent, None)
        logging.info(f"Active agents updated: {self.active_agents}")

    @time_function
    def respond(self, input_text):
        """
        Generate a response to the given input text.
        """
        try:
            self.update_status('Planning')
            response, conversation, solution, iterations = self.agent_responder.generate_response(
                input_text, self.dynamic_prompt, self.max_depth
            )

            if not self.working_agent:
                if iterations > 2:
                    self.evolve_count += 1
                    self.update_status('Evolving prompt')
                    self.dynamic_prompt = self.prompt_evolver.evolve_prompt(
                        input_text, self.dynamic_prompt, response, conversation, solution, self.depth
                    )
                elif solution: 
                    self.working_agent = True

            self.update_status('Idle')
            self.update_active_agents(self.purpose)
            return response
        except Exception as e:
            log_exception(e)
            self.update_status('Error')
            self.update_active_agents(self.purpose)
            return "An error occurred while generating the response."
