from langgraph.graph import StateGraph, START, END
from state import AgentState
from nodes import retrieve_node, generate_node


def rag_graph():
    """
    Creates a state graph for the RAG agent, defining the flow of states and transitions.
    """
    workflow = StateGraph(AgentState)

    # Nodes
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate", generate_node)

    # Transitions
    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()
