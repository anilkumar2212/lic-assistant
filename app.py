from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from src.ingestion.ingest_service import ingest_folder
from src.rag.answer_generator import answer_query
from src.utils.logger import get_logger

from generate_evaluation_dataset import main as generate_eval_dataset
from run_evaluation import run_evaluation

# --------------------------------
# Logger
# --------------------------------
logger = get_logger("API", "api.log")

# --------------------------------
# FastAPI App
# --------------------------------
app = FastAPI(
    title="LIC GenAI Knowledge Assistant",
    description="Enterprise RAG-based assistant for Life Insurance documents",
    version="1.0.0"
)

# --------------------------------
# Request Models
# --------------------------------
class IngestRequest(BaseModel):
    path: str

class QueryRequest(BaseModel):
    question: str

class GenerateEvalDatasetRequest(BaseModel):
    base_path: str
    output_file: str
    num_questions: int = 30

class RunEvaluationRequest(BaseModel):
    evaluation_dataset_path: str

# --------------------------------
# Ingestion Endpoint
# --------------------------------
@app.post("/ingest")
def ingest(req: IngestRequest):
    logger.info(f"Received ingestion request for path: {req.path}")

    try:
        ingest_folder(req.path)
        logger.info("Ingestion completed successfully")

        return {
            "status": "success",
            "message": "Ingestion completed successfully"
        }

    except Exception as e:
        logger.error("Ingestion failed")
        logger.error(str(e))

        raise HTTPException(
            status_code=500,
            detail="Ingestion failed. Please check logs for details."
        )

# --------------------------------
# Query Endpoint
# --------------------------------
@app.post("/query")
def query(req: QueryRequest):
    logger.info(f"Received query request: {req.question}")

    try:
        result = answer_query(req.question)

        return {
            "answer": result['answer']
        }

    except Exception as e:
        logger.error("Query processing failed")
        logger.error(str(e))

        raise HTTPException(
            status_code=500,
            detail="Query processing failed. Please try again later."
        )
    

# --------------------------------
# Generate Evaluation Dataset
# --------------------------------
@app.post("/generate-evaluation-dataset")
def generate_evaluation_dataset(req: GenerateEvalDatasetRequest):
    logger.info("Starting evaluation dataset generation")

    try:
        generate_eval_dataset(
            base_path=req.base_path,
            output_file=req.output_file,
            num_questions=req.num_questions
        )

        return {
            "status": "success",
            "message": "Evaluation dataset generated successfully",
            "output_file": req.output_file
        }

    except Exception as e:
        logger.error("Evaluation dataset generation failed")
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Dataset generation failed")


# --------------------------------
# Run Evaluation
# --------------------------------
@app.post("/run-evaluation")
def run_evaluation_api(req: RunEvaluationRequest):
    logger.info("Starting evaluation run")

    try:
        run_evaluation(req.evaluation_dataset_path)

        return {
            "status": "success",
            "message": "Evaluation completed successfully",
            "results_file": "evaluation_dataset_results.xlsx"
        }

    except Exception as e:
        logger.error("Evaluation failed")
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Evaluation failed")



# --------------------------------
# Uvicorn Runner
# --------------------------------
if __name__ == "__main__":
    uvicorn.run("app:app",host="0.0.0.0",port=8000,reload=True)
