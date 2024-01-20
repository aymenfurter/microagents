import json
import numpy as np
from agents.microagent import MicroAgent

class AgentSerializer:
    @staticmethod
    def to_dict(agent):
        """
        Serialize the MicroAgent object to a dictionary for persistence.
        """
        purpose_embedding = agent.purpose_embedding
        if isinstance(purpose_embedding, np.ndarray):
            purpose_embedding = purpose_embedding.tolist()  # Convert ndarray to list

        return {
            "dynamic_prompt": agent.dynamic_prompt,
            "purpose": agent.purpose,
            "purpose_embedding": purpose_embedding,
            "depth": agent.depth,
            "max_depth": agent.max_depth,
            "usage_count": agent.usage_count,
            "id": agent.id,
            "parent_id": agent.parent_id,
            "working_agent": agent.working_agent,
            "is_prime": agent.is_prime,
            "evolve_count": agent.evolve_count,
            "number_of_code_executions": agent.number_of_code_executions,
            "last_input": agent.last_input,
        }

    @staticmethod
    def from_dict(data, agent_lifecycle, openai_wrapper):
        """
        Deserialize a dictionary back into a MicroAgent object.
        """
        agent = MicroAgent(
            data["dynamic_prompt"],
            data["purpose"],
            data["depth"],
            agent_lifecycle,
            openai_wrapper,
            data["max_depth"],
            data.get("working_agent", False),
            data.get("is_prime", False),
            id=data["id"],
            parent_id=data["parent_id"]
        )

        if data.get("purpose_embedding") is not None:
            agent.purpose_embedding = np.array(data["purpose_embedding"])
        else:
            agent.purpose_embedding = None

        agent.usage_count = data.get("usage_count", 0)
        agent.evolve_count = data.get("evolve_count", 0)
        agent.number_of_code_executions = data.get("number_of_code_executions", 0)
        agent.last_input = data.get("last_input", "")
        return agent