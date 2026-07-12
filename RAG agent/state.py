from typing import List, TypedDict

class AgentState(TypedDict):
    """
    Represents the state of the agent, including the current document
    """
    query: str
    use_resume: bool
    resume_path: str
    resume_text: str
    context: str
    answer: str
