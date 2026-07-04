from google import genai
from state import AgentState
from retriever import get_closest_postings
from llama_cpp import Llama

Chat_model_path = "models/gemma-4-E4B-it-UD-Q4_K_XL.gguf"

llm = Llama(
    model_path=Chat_model_path,
    n_ctx=20480,
    verbose=False
)

def retrieve_node(state: AgentState):
    print("Retrieving relevant job postings...")
    query = state["query"]

    context = get_closest_postings(query, top_k=5)

    return {"context": context}

def generate_node(state: AgentState):
    print("Generating response...")
    query = state["query"]
    context = state.get("context", "")

    prompt = f"""
    Answer the user's question about job roles based ONLY on the provided database records.
    If the answer is not in the records, state "I cannot find any matching roles in the database."
    
    Database Records:
    {context}
    
    User Query: {query}
    """

    response = llm.create_chat_completion(
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    
    answer_text = response["choices"][0]["message"]["content"]
    return {"answer": answer_text}