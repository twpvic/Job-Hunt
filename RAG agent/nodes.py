from google import genai
from state import AgentState
from retriever import get_closest_postings
from llama_cpp import Llama
from pypdf import PdfReader

Chat_model_path = "models/gemma-4-E4B-it-UD-Q4_K_XL.gguf"

llm = Llama(
    model_path=Chat_model_path,
    n_ctx=20480,
    n_gpu_layers=-1,
    verbose=False
)

def load_resume_node(state: AgentState):
    print("Loading resume...")
    resume_path = state.get("resume_path", "")
    resume_text = ""

    if resume_path:
        try:
            if resume_path.endswith(".pdf"):
                with open(resume_path, 'rb') as file:
                    pdf_reader = PdfReader(file)
                    resume_text = ""
                    for page in pdf_reader.pages:
                        resume_text += page.extract_text()
            else:
                with open(resume_path, 'r', encoding='utf-8') as file:
                    resume_text = file.read()
        except Exception as e:
            print(f"Error reading resume file: {e}")
    return {"resume_text": resume_text}

def retrieve_node(state: AgentState):
    print("Retrieving relevant job postings...")
    query = state["query"]

    context = get_closest_postings(query, top_k=5)

    return {"context": context}

def generate_node(state: AgentState):
    query = state["query"]
    context = state.get("context", "")
    use_resume = state.get("use_resume", False)
    resume_text = state.get("resume_text", "")

    if use_resume and resume_text:
        print("Using resume for comparison")
        prompt = f"""
        Based on the provided Database Records, compare the user's resume to the available job postings.
        Highlight matching skills, identify potential gaps, and recommend the best fit based on their query.
        If no roles fit well, state "I cannot find any matching roles in the database for your specific profile."

        Database Records:
        {context}

        User Resume:
        {resume_text}

        User Query: {query}
        """
    else:
        print("No resume provided, using query only for comparison")
        prompt = f"""
        Based on the provided Database Records, recommend the best fit based on the user's query.
        Highlight key requirements from the postings and explain why they fit the query.
        If no roles fit well, state "I cannot find any matching roles in the database for your specific request."

        Database Records:
        {context}

        User Query: {query}
        """

    response = llm.create_chat_completion(
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature= 0.3
    )

    
    answer_text = response["choices"][0]["message"]["content"]
    return {"answer": answer_text}