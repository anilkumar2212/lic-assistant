import json
import re
from pathlib import Path

import pandas as pd

from src.llm.llm_client import llm
from src.retrieval.retriever import retrieve_relevant_chunks
from evaluation.evaluation_prompt import EVALUATOR_PROMPT
from src.rag.answer_generator import answer_query


# -------------------------------------------------
# JSON EXTRACTION
# -------------------------------------------------

def extract_json_from_llm(content: str) -> dict:
    content = re.sub(r"```(?:json)?", "", content, flags=re.IGNORECASE).strip()
    return json.loads(content)

# -------------------------------------------------
# MAIN EVALUATION PIPELINE
# -------------------------------------------------

def run_evaluation(input_dataset_path: str):
    input_path = Path(input_dataset_path)

    output_path = input_path.with_name(
        f"{input_path.stem}_results2{input_path.suffix}"
    )

    df = pd.read_excel(input_path)

    results = []

    for _, row in df.iterrows():
        query = row["question"]
        expected_answer = row["expected_answer"]
        page_number = row["page_number"]
        pdf_file = row["pdf_file"]
        expected_answer = f"{expected_answer} \n- Document Name: {pdf_file} \n- Page Number(s): {page_number}"

        try:
            rag_result = answer_query(query)
            llm_answer = rag_result["answer"]
            retrieval_context = rag_result["retrieval_context"]

            eval_prompt = EVALUATOR_PROMPT.format(
                question=query,
                expected_answer=expected_answer,
                generated_answer=llm_answer,
                retrieved_context=retrieval_context
            )

            eval_response = llm.invoke(eval_prompt)
            eval_parsed = extract_json_from_llm(eval_response.content)

            results.append({
                "question": query,
                "expected_answer": expected_answer,
                "llm_answer": llm_answer,
                "retrieval_context": retrieval_context,
                "pdf_file": pdf_file,
                "page_number": page_number,
                "answer_correctness": eval_parsed["answer_correctness"],
                "groundedness_score": eval_parsed["groundedness_score"],
                "hallucination": eval_parsed["hallucination"],
                "citation_accuracy": eval_parsed["citation_accuracy"],
                "overall_score": eval_parsed["overall_score"],
                "explanation": eval_parsed.get("explanation")
            })
        except Exception as e:
            print(e)

    results_df = pd.DataFrame(results)
    results_df.to_excel(output_path, index=False)

    print(f"\n✅ Evaluation results saved to: {output_path}")


# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------

if __name__ == "__main__":
    INPUT_DATASET = r"C:\Users\anilk\assign2\evaluation\evaluation_dataset.xlsx"
    run_evaluation(INPUT_DATASET)
