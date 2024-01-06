import logging
from integrations.openaiwrapper import OpenAIAPIWrapper
from agents.agent_evaluation import AgentEvaluator
from agents.agent_response import AgentResponse
from agents.agent_similarity import AgentSimilarity
from runtime.code_execution import CodeExecution
from prompt_management.prompt_evolution import PromptEvolution
from agents.response_extraction import ResponseExtraction
from utils.utility import get_env_variable, time_function, log_exception

logger = logging.getLogger()

MAX_EVOLVE_COUNT = 5

class MicroAgent:
    """
    The MicroAgent class encapsulates the behavior of a small, purpose-driven agent
    that interacts with the OpenAI API.
    """

    def __init__(self, initial_prompt, purpose, depth, agent_lifecycle, openai_wrapper, max_depth=3, bootstrap_agent=False, is_prime=False, purpose_embedding=None) :
        self.dynamic_prompt = initial_prompt
        self.purpose = purpose
        self.purpose_embedding = purpose_embedding 
        self.depth = depth
        self.max_depth = max_depth
        self.usage_count = 0
        self.working_agent = bootstrap_agent
        self.agent_lifecycle = agent_lifecycle
        self.openai_wrapper = openai_wrapper
        self.evolve_count = 0
        self.number_of_code_executions = 0 
        self.current_status = None
        self.active_agents = {} 
        self.last_input = ""
        self.last_output = ""
        self.is_prime = is_prime

        # Initialize components used by the agent
        self.agent_evaluator = AgentEvaluator(self.openai_wrapper)
        self.code_executor = CodeExecution()
        self.agent_responder = AgentResponse(self.openai_wrapper, self.agent_lifecycle, self.code_executor, self, agent_lifecycle, depth)
        self.agent_similarity = AgentSimilarity(self.openai_wrapper, self.agent_lifecycle.agents)
        self.prompt_evolver = PromptEvolution(self.openai_wrapper, self.agent_lifecycle)
        self.response_extractor = ResponseExtraction(self.openai_wrapper)

    def update_status(self, status):
        """Update the agent's current status."""
        self.current_status = status
        logger.info(f"Agent {self.purpose} status updated to: {status}")

    def update_active_agents(self, calling_agent, called_agent=None):
        """Update the tree view of active agents."""
        if called_agent:
            self.active_agents[calling_agent] = called_agent
        else:
            self.active_agents.pop(calling_agent, None)
        logger.info(f"Active agents updated: {self.active_agents}")

    def set_agent_as_working(self):
        """Set the agent as a working agent."""
        self.working_agent = True
        self.agent_lifecycle.save_agent(self)
        logger.info(f"Agent {self.purpose} set as working agent.")

    @time_function
    def respond(self, input_text, evolve_count=0):
        """
        Generate a response to the given input text.
        """
        self.last_input = input_text
        try:
            self.update_status('📝 Planning.. ')
            response, conversation, solution, iterations = self.agent_responder.generate_response(
                input_text, self.dynamic_prompt, self.max_depth
            )
            self.last_output = response[:150]

            if not self.working_agent and solution or not self.working_agent and iterations == MAX_EVOLVE_COUNT:
                self.update_status('🕵️  Judging..')
                if self.agent_evaluator.evaluate(input_text, self.dynamic_prompt, response):
                    self.set_agent_as_working()
            elif not self.working_agent and evolve_count < MAX_EVOLVE_COUNT:
                self.evolve_count += 1
                self.update_status('🧬 Evolving..')
                self.dynamic_prompt = self.prompt_evolver.evolve_prompt(
                    input_text, self.dynamic_prompt, response, conversation, solution, self.depth
                )
                return self.respond(input_text, evolve_count + 1)

            self.update_status('😴 Sleeping.. ')
            self.update_active_agents(self.purpose)

            return response
        except Exception as e:
            logger.exception(f"{e}")
            self.update_status('💣 Error')
            self.update_active_agents(self.purpose)
            return "An error occurred while generating the response."
