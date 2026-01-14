import json
import random
import re
from pathlib import Path
from typing import List

import pandas as pd
from bs4 import BeautifulSoup

from src.ingestion.pdf_blocks import extract_pdf_blocks
from src.llm.llm_client import llm
from evaluation.evaluation_dataset_prompt import EVALUATION_DATASET_PROMPT


# -------------------------------------------------
# HTML TABLE → STRING
# -------------------------------------------------

def html_table_to_dataframe_string(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    rows = []
    for tr in soup.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if cells:
            rows.append(cells)

    if not rows:
        return ""

    max_len = max(len(r) for r in rows)
    normalized_rows = [r + [""] * (max_len - len(r)) for r in rows]

    df = pd.DataFrame(normalized_rows)
    return df.to_string(index=False, header=False)


# -------------------------------------------------
# BUILD FULL DOCUMENT CONTENT
# -------------------------------------------------

def build_full_content_from_blocks(blocks: List) -> str:
    content_parts = []
    current_page = None

    for block in blocks:
        if block.page_number != current_page:
            content_parts.append(f"\n\n=== PAGE {block.page_number} ===\n")
            current_page = block.page_number

        if block.type == "paragraph":
            text = block.content.strip()
            if text:
                content_parts.append(text)

        elif block.type == "table":
            table_text = html_table_to_dataframe_string(block.content)
            if table_text:
                content_parts.append(table_text)

    return "\n".join(content_parts).strip()


# -------------------------------------------------
# LLM JSON PARSER
# -------------------------------------------------

def extract_json_from_llm(content: str) -> dict:
    content = re.sub(r"```(?:json)?", "", content, flags=re.IGNORECASE).strip()
    match = re.search(r"\{[\s\S]*\}", content)

    if not match:
        raise ValueError("No JSON found in LLM response")

    return json.loads(match.group())


# -------------------------------------------------
# MAIN PIPELINE
# -------------------------------------------------

def main(base_path: str, output_file: str, num_questions: int):
    pdfs = list(Path(base_path).rglob("*.pdf"))

    if not pdfs:
        raise ValueError("No PDF files found in the given base_path")

    random_pdfs = random.sample(
        pdfs, k=min(num_questions, len(pdfs))
    )

    records = []

    for pdf in random_pdfs:
        print(f"\nProcessing: {pdf.name}")

        page_blocks = extract_pdf_blocks(pdf)

        success = False

        for max_pages in [15, 10]:
            try:
                doc_content = build_full_content_from_blocks(
                    page_blocks[:max_pages]
                )

                prompt = EVALUATION_DATASET_PROMPT.format(
                    context=doc_content
                )

                llm_response = llm.invoke(prompt)
                parsed = extract_json_from_llm(llm_response.content)

                source = parsed.get("source_documents", [{}])[0]

                record = {
                    "question": parsed.get("question"),
                    "expected_answer": parsed.get("expected_answer"),
                    "question_type": parsed.get("question_type"),
                    "document_name": source.get("document_name"),
                    "page_number": source.get("page_number"),
                    "pdf_file": pdf.name,
                }

                records.append(record)
                print("✅ Success")
                success = True
                break

            except Exception as e:
                print(f"⚠️ Failed with {max_pages} pages → {e}")

        if not success:
            print("❌ Skipped this PDF")

    df = pd.DataFrame(records)
    df.to_excel(output_file, index=False)

    print(f"\n🎯 Evaluation dataset saved to: {output_file}")


# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------

if __name__ == "__main__":
    BASE_PATH = r"C:\Users\anilk\assign2\documents\lic-plans"
    OUTPUT_FILE = r"evaluation\evaluation_dataset.xlsx"
    NUM_QUESTIONS = 30   

    main(
        base_path=BASE_PATH,
        output_file=OUTPUT_FILE,
        num_questions=NUM_QUESTIONS
    )
