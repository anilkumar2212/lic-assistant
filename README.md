
# Enterprise GenAI Knowledge Assistant for Life Insurance (LIC)

## Project Overview

This project implements an **Enterprise GenAI Knowledge Assistant** for Life Insurance (LIC) documents.
The system enables internal users to query policy documents and receive
**accurate, grounded, and source-backed answers** using a **Retrieval-Augmented Generation (RAG)** architecture.

In addition to question answering, the project includes a **rigorous evaluation framework**, including:
- Custom evaluation dataset generation
- Automated RAG evaluation
- LLM-as-Evaluator scoring
- Quantitative and qualitative analysis

---

## Objectives

- Build an internal ChatGPT-like assistant for LIC documents
- Ensure answers are **factually correct, concise, and grounded**
- Provide **citations and explainability**
- Design an **enterprise-grade evaluation methodology**
- Measure correctness, groundedness, hallucinations, and citation accuracy

---

## Documents in Scope

Official LIC documents and pages, including:
- Endowment Plans
- Whole Life Plans
- Money Back Plans
- Term Assurance Plans
- Unit Linked Plans
- Pension Plans
- Claims Settlement Requirements

---

## System Architecture

**High-Level Flow**

Documents → Chunking → Embeddings → Vector Store  
User Query → Retrieval → Context → LLM → Answer + Sources  
Evaluation → LLM-as-Evaluator → Scores & Metrics

---

## Core Functional Components

### 1️⃣ Document Ingestion
- PDF ingestion and parsing
- Table and paragraph handling
- Metadata enrichment (document name, page number)

### 2️⃣ Retrieval-Augmented Generation (RAG)
- Vector similarity search
- Top-K relevant chunk retrieval
- Context-grounded prompting
- Hallucination control via strict prompts

### 3️⃣ Question Answering
- Natural language questions
- Domain-aware insurance terminology
- Clear and concise responses
- Source citations

### 4️⃣ Evaluation Dataset Creation
- 30 questions generated from documents
- Mix of:
  - Direct factual
  - Eligibility & constraints
  - Multi-condition
  - Comparative
  - Unanswerable questions
- Each item includes:
  - Question
  - Expected answer (ground truth)
  - Source document and page number

### 5️⃣ Evaluation Methodology
- Hybrid evaluation:
  - Rule-based checks
  - LLM-as-Evaluator
- Metrics:
  - Answer correctness
  - Groundedness score
  - Hallucination rate
  - Citation accuracy
  - Overall quality score

---

## 📊 Evaluation Results (Summary)

- Total evaluation questions: 30
- Correct + Partial: ~73%
- Exact correctness: ~53%
- Average groundedness score: ~0.69
- Hallucination rate: ~20%
- Citation accuracy (when present): ~67%

---

## API Interface (FastAPI)

### Endpoints

**POST /ingest**
```json
{ "path": "C:/path/to/documents" }
```

**POST /query**
```json
{ "question": "What is the minimum age at entry for LIC’s New Endowment Plan?" }
```

**POST /generate-evaluation-dataset**
```json
{
  "base_path": "C:/path/to/documents",
  "output_file": "evaluation/evaluation_dataset.xlsx",
  "num_questions": 30
}
```

**POST /run-evaluation**
```json
{
  "evaluation_dataset_path": "C:/path/to/evaluation_dataset.xlsx"
}
```

---

## Project Structure

```
ASSIGN2/
├── app.py
├── config/
├── documents/
├── evaluation/
├── src/
├── logs/
├── jupyter_notebooks/
├── README.md
├── requirements.txt
├── .env
└── .gitignore
```

## Tech Stack & Models Used

### Large Language Models
- **Answer Generation LLM:** OpenAI GPT model (e.g., `gpt-4o`)
  - Used for RAG-based answer generation
- **Evaluation & Dataset Generation LLM:** OpenAI GPT model
  - Used for evaluation dataset creation
  - Used as LLM-as-Evaluator for scoring answers

### Embedding Model
- **OpenAI Embedding Model:** `text-embedding-3-small`
  - Used to convert document chunks and user queries into vector embeddings
  - Enables semantic similarity search during retrieval

### Vector Database
- **Supabase (PostgreSQL + pgvector extension)**
  - Used as the vector database for storing document and query embeddings
  - Supports semantic similarity search using the pgvector extension
  - Enables metadata-based filtering and enterprise-grade persistence

### Frameworks & Libraries
- **FastAPI** – API layer for ingestion, querying, and evaluation
- **LangChain** – RAG orchestration
- **Pandas** – Dataset creation and evaluation analysis
- **BeautifulSoup** – Web scraping and document extraction

---

## Setup & Run

```bash
pip install -r requirements.txt or uv add -r requirements.txt
python app.py
```

Access API docs at:
```
http://localhost:8000/docs
```

---

## Security & Enterprise Readiness

- Environment-variable based secrets
- No hardcoded credentials
- Logging and error handling
- Modular and scalable design

---

## Future Improvements

- Data processing enhancements
- Chunk size and overlap tuning based on retrieval evaluation results
- Dynamic top_k retrieval optimization driven by evaluation metrics
- Role-based document retrieval using metadata and hybrid search
- Enhanced prompt design

---

## Conclusion

This project demonstrates an end-to-end **enterprise GenAI system**, covering
RAG architecture, explainability, evaluation rigor, and production readiness.
