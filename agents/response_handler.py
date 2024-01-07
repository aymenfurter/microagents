import logging
from agents.agent_stopped_exception import AgentStoppedException
from utils.utility import time_function

logger = logging.getLogger()

MAX_EVOLVE_COUNT = 3

class ResponseHandler:
    """
    ResponseHandler is responsible for handling the response generation logic for MicroAgent.
    """

    def __init__(self, micro_agent):
        self.micro_agent = micro_agent

    @time_function
    def respond(self, input_text, evolve_count=0):
        """
        Generate a response to the given input text.
        """
        self.micro_agent.last_input = input_text
        try:
            self.micro_agent.update_status('📝 Planning.. ')
            response, conversation, solution, iterations = self.micro_agent.agent_responder.generate_response(
                input_text, self.micro_agent.dynamic_prompt, self.micro_agent.max_depth
            )
            self.micro_agent.last_output = response
            self.micro_agent.last_conversation = conversation

            if not self.micro_agent.working_agent and (solution or evolve_count == MAX_EVOLVE_COUNT):
                self.micro_agent.update_status('🕵️  Judging..')
                if self.micro_agent.agent_evaluator.evaluate(input_text, self.micro_agent.dynamic_prompt, response):
                    self.micro_agent.set_agent_as_working()
            elif not self.micro_agent.working_agent and evolve_count < MAX_EVOLVE_COUNT:
                self.micro_agent.evolve_count += 1
                self.micro_agent.update_status('🧬 Evolving..')
                self.micro_agent.dynamic_prompt = self.micro_agent.prompt_evolver.evolve_prompt(
                    input_text, self.micro_agent.dynamic_prompt, response, conversation, solution, self.micro_agent.depth
                )
                return self.respond(input_text, evolve_count + 1)

            self.micro_agent.update_status('😴 Sleeping.. ')
            self.micro_agent.update_active_agents(self.micro_agent.purpose)

            return response
        except AgentStoppedException:
            logger.info("Agent execution was stopped.")
            return "Agent execution was stopped."
        except Exception as e:
            logger.exception(f"{e}")
            self.micro_agent.update_status('💣 Error')
            self.micro_agent.update_active_agents(self.micro_agent.purpose)
            return "An error occurred while generating the response."