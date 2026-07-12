import os
import glob
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

        use_resume_input = input("Do you want to use your resume for comparison? y/n: ").strip().lower()
        use_resume = use_resume_input in ['yes', 'y']


        resume_path = ""
        if use_resume:
            resume_path_input = input("Place resume in Data file and provide name:").strip()
            resume_path = os.path.join("Data", resume_path_input)
            print(f"Using resume at: {resume_path}")
            if not os.path.isfile(resume_path):
                print(f"Resume file '{resume_path}' not found. Please ensure the file exists in the 'Data/' folder. Continuing without resume")
                use_resume = False
                resume_path = ""
            
        initial_state = {
            "query": user_query,
            "use_resume": use_resume,
            "resume_path": resume_path,
            "resume_text": "",
            "context": "",
            "answer": ""
        }
        
        final_state = app.invoke(initial_state)
        
        print("\n--- Assistant ---")
        print(final_state["answer"])