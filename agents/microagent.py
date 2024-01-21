import logging
import uuid
from integrations.openaiwrapper import OpenAIAPIWrapper
from agents.agent_evaluation import AgentEvaluator
from agents.agent_response import AgentResponse
from agents.agent_similarity import AgentSimilarity
from agents.response_extraction import ResponseExtraction
from agents.agent_stopped_exception import AgentStoppedException
from agents.response_handler import ResponseHandler
from runtime.code_execution import CodeExecution
from prompt_management.prompt_evolution import PromptEvolution
from utils.utility import get_env_variable, time_function, log_exception

logger = logging.getLogger()


class MicroAgent:
    """
    The MicroAgent class encapsulates the behavior of a small, purpose-driven agent
    that interacts with the OpenAI API.
    """

    def __init__(self, initial_prompt, purpose, depth, agent_lifecycle, openai_wrapper, max_depth=3, bootstrap_agent=False, is_prime=False, purpose_embedding=None, parent=None, parent_id=None, id=None) :
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
        self.last_conversation = ""
        self.stopped = False
        self.is_prime = is_prime
        self.stop_execution = False

        if parent:
            self.parent_id = parent.id if parent else None
        else: 
            self.parent_id = None

        if parent_id:
            self.parent_id = parent_id

        if is_prime:
            self.id = "2a5e6fe9-1bb1-426c-9521-145caa2cf66b"
        else:
            if id:
                self.id = id
            else:
                self.id = str(uuid.uuid4()) 


        # Initialize components used by the agent
        self.agent_evaluator = AgentEvaluator(self.openai_wrapper)
        self.code_executor = CodeExecution()
        self.agent_responder = AgentResponse(self.openai_wrapper, self.agent_lifecycle, self.code_executor, self, agent_lifecycle, depth)
        self.agent_similarity = AgentSimilarity(self.openai_wrapper, self.agent_lifecycle.agents)
        self.prompt_evolver = PromptEvolution(self.openai_wrapper, self.agent_lifecycle)
        self.response_extractor = ResponseExtraction(self.openai_wrapper)
        self.response_handler = ResponseHandler(self)

    def update_status(self, status):
        """Update the agent's current status."""
        self.check_for_stopped()
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

    def get_children(self):
        """Get the children of the agent."""
        return [agent for agent in self.agent_lifecycle.agents if agent.parent_id == self.id]

    def is_working_agent(self):
        return self.working_agent

    def set_agent_deleted(self): 
        """Set the agent as deleted."""
        self.working_agent = False
        self.current_status = "❌ Deleted"
        self.stopped = True
        self.stop_execution = True
        self.agent_lifecycle.remove_agent(self)
        logger.info(f"Agent {self.purpose} set as deleted.")

    def check_for_stopped(self):
        """Check if the agent has been stopped."""
        if self.stop_execution:
            self.current_status = "❌ Stopped"
            if self.is_prime:
                self.agent_lifecycle.reset_all_agents()
            raise AgentStoppedException("Agent stopped.")

    def respond(self, input_text, evolve_count=0):
        """
        Generate a response to the given input text.
        """
        return self.response_handler.respond(input_text, evolve_count)
    
    def stop(self): 
        """Stop the agent."""
        self.stop_execution = True
        if not self.is_working_agent():
            self.stopped = True

    def reset(self):
        """Reset the agent's stopped status."""
        self.current_status = ""
        self.stop_execution = False

    def __eq__(self, other):
        if not isinstance(other, MicroAgent):
            return NotImplemented

        return (self.dynamic_prompt, self.purpose) == (other.dynamic_prompt, other.purpose)

    def __hash__(self):
        return hash((self.dynamic_prompt, self.purpose))
