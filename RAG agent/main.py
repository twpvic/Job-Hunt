import os
from dotenv import load_dotenv

load_dotenv()

from graph import rag_graph

if __name__ == "__main__":
    # Ensure the data directory exists
    os.makedirs("Data", exist_ok=True)
    
    # Prevent crashing if no CSVs are present
    if not os.listdir("Data"):
        print("place job posting CSV files in the 'Data/' folder and run again.")
        exit(1)
        
    print("Compiling agent...")
    app = rag_graph()
    
    # Interactive loop
    while True:
        user_query = input("\nWhat kind of role are you looking for? (or 'quit'): ")
        if user_query.lower() in ['quit', 'exit']:
            break
            
        initial_state = {
            "query": user_query,
            "context": "",
            "answer": ""
        }
        
        final_state = app.invoke(initial_state)
        
        print("\n--- Assistant ---")
        print(final_state["answer"])