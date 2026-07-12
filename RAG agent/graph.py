from langgraph.graph import StateGraph, START, END
from state import AgentState
from nodes import retrieve_node, generate_node, load_resume_node

def use_resume_condition(state: AgentState) -> str:
    return "load_resume" if state.get("use_resume") else "retrieve"

def rag_graph():
    """
    Creates a state graph for the RAG agent, defining the flow of states and transitions.
    """
    workflow = StateGraph(AgentState)

    # Nodes
    workflow.add_node("load_resume", load_resume_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate", generate_node)

    # Transitions
    workflow.add_conditional_edges(
        START,
        use_resume_condition,
        {
            "load_resume": "load_resume",
            "retrieve": "retrieve"
        }
    )
    workflow.add_edge("load_resume", "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()
