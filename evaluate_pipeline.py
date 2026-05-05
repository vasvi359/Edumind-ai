import os
import json
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from langchain_groq import ChatGroq
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

# Import EduMind components
from backend import EduMindOrchestrator, EduMindMemory
from rag import get_embedding, create_vectorstore, retrieve_context

def main():
    print("Initializing LLM and Embeddings...")
    llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0)
    embeddings = get_embedding()
    
    print("Reading sample notes...")
    with open("sample_notes.txt", "r", encoding="utf-8") as f:
        text_content = f.read()

    print("Creating temporary Vectorstore...")
    vectorstore, chunk_count = create_vectorstore(text_content)
    print(f"Created vectorstore with {chunk_count} chunks.")

    print("Loading evaluation dataset...")
    with open("eval_dataset.json", "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    # Data lists for Ragas
    questions = []
    answers = []
    contexts_list = []
    ground_truths = []

    print("Running queries through EduMind pipeline...")
    # Process each question
    for item in eval_data[:2]:
        question = item["question"]
        ground_truth = item["ground_truth"]
        
        # 1. Retrieve Context
        # Similarity search raw output for Ragas 'contexts' field
        raw_docs = vectorstore.similarity_search(question, k=4)
        contexts = [doc.page_content for doc in raw_docs]
        
        # Context string for EduMind
        context_str = "\n".join(contexts)
        
        # 2. Generate Answer using Orchestrator (simulating backend)
        memory = EduMindMemory()
        orchestrator = EduMindOrchestrator(memory)
        result = orchestrator.route(question, context_str, llm)
        answer = result["answer"]
        
        # Collect data
        questions.append(question)
        answers.append(answer)
        contexts_list.append(contexts)
        ground_truths.append(ground_truth)
        
        print(f"Processed question: {question[:50]}...")

    # Prepare HuggingFace Dataset
    data_dict = {
        "question": questions,
        "answer": answers,
        "contexts": contexts_list,
        "ground_truth": ground_truths
    }
    dataset = Dataset.from_dict(data_dict)

    print("Running Ragas Evaluation (this may take a minute)...")
    
    # Run evaluation
    result = evaluate(
        dataset,
        metrics=[
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy,
        ],
        llm=llm,
        embeddings=embeddings,
        raise_exceptions=False,
    )

    print("\n--- Evaluation Complete ---")
    print(result)

    # Save to CSV
    df = result.to_pandas()
    df.to_csv("evaluation_results.csv", index=False)
    print("\nDetailed results saved to 'evaluation_results.csv'")

if __name__ == "__main__":
    main()
