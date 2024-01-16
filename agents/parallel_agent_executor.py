import threading
import queue

class ParallelAgentExecutor:
    def __init__(self, agent_manager, max_parallel_agents=3):
        self.agent_manager = agent_manager
        self.max_parallel_agents = max_parallel_agents
        self.response_queue = queue.Queue()
        self.agents_and_threads = []
        self.execution_completed = threading.Event()

    def create_and_run_agents(self, purpose, depth, input_text):
        initial_agent = self.agent_manager.get_or_create_agent(purpose, depth, input_text)
        if initial_agent.is_working_agent():
            return initial_agent.respond(input_text)
        
        initial_agent.set_agent_deleted()

        for _ in range(self.max_parallel_agents):
            new_agent = self.agent_manager.get_or_create_agent(purpose, depth, input_text, force_new=True)
            new_thread = threading.Thread(target=self.run_agent, args=(new_agent, input_text))
            new_thread.start()
            self.agents_and_threads.append((new_agent, new_thread))

        while not self.execution_completed.is_set() and any(thread.is_alive() for _, thread in self.agents_and_threads):
            pass

        winning_agent, winning_response = self.determine_winning_agent()
        if winning_agent:
            self.set_other_agents_as_deleted(winning_agent)

        return winning_response

    def run_agent(self, agent, input_text):
        try:
            response = agent.respond(input_text)
            if agent.is_working_agent():
                self.response_queue.put((agent, response))
                self.execution_completed.set()
        except Exception as e:
            pass

    def determine_winning_agent(self):
        if not self.response_queue.empty():
            return self.response_queue.get()
        return None, None

    def set_other_agents_as_deleted(self, winning_agent):
        for agent, _ in self.agents_and_threads:
            if agent != winning_agent:
                agent.set_agent_deleted()

    def is_working_agent(self):
        return any(agent.is_working_agent() for agent, _ in self.agents_and_threads)
