import os 
import glob
import pandas as pd
import numpy as np
from llama_cpp import Llama

Embedding_model_path = "models/embeddinggemma-300M-Q8_0.gguf"

embedding_model = Llama(
    model_path=Embedding_model_path,
    embedding=True,
    verbose=False,
    n_ctx=20480
)


def load_data_from_csv():
    # Load data from CSV files in the 'Data' directory
    csv_files = glob.glob(os.path.join('Data', '*.csv'))
    if not csv_files:
            print("No CSV files found in directory.")
            return [], np.array([])

    documents = []

    for file in csv_files:
        df = pd.read_csv(file)
        df = df.fillna("")

        for _, row in df.iterrows():
            # Convert each row into a text block (e.g., "Role: Developer | Salary: $100k")
            row_data = " | ".join([f"{col}: {val}" for col, val in row.items() if val])
            
            # Prepend the source file name
            doc_text = f"[Source: {os.path.basename(file)}] {row_data}"
            documents.append(doc_text)
        
    print(f"Loaded {len(documents)} documents from CSV files.")

    doc_embeddings = []
    batch_size = 100  # Adjust batch size as needed
    
    print("Generating embeddings for documents...")
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        response = embedding_model.create_embedding(batch)

        for item in response["data"]:
            vector = item["embedding"]
            doc_embeddings.append(vector)

    return documents, np.array(doc_embeddings)

DOCUMENTS, DOC_EMBEDDINGS = load_data_from_csv()

def get_closest_postings(query: str, top_k: int = 5) -> str:
    """Embeds the query and returns the top_k most relevant job postings."""
    if len(DOCUMENTS) == 0:
        return "No job posting data available."
        
    res = embedding_model.create_embedding(query)
    query_vector = np.array(res["data"][0]["embedding"])
    
    # Calculate Cosine Similarity
    dot_products = np.dot(DOC_EMBEDDINGS, query_vector)
    norms = (np.linalg.norm(DOC_EMBEDDINGS, axis=1) * np.linalg.norm(query_vector)) + 1e-9
    similarities = dot_products / norms
    
    # Get indices of the highest scoring documents
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    # Combine the top results into a single context string
    retrieved_docs = [DOCUMENTS[i] for i in top_indices]
    return "\n\n".join(retrieved_docs)