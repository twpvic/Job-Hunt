from typing import List, TypedDict

class AgentState(TypedDict):
    """
    Represents the state of the agent, including the current document
    """
    query: str
    context: str
    answer: str
