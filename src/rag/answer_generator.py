from src.retrieval.retriever import retrieve_relevant_chunks
from src.prompts.system_prompt import prompt_template
from src.llm.llm_client import llm
from src.utils.logger import get_logger
import traceback

logger = get_logger("ANSWER_GENERATOR", "answer.log")


def answer_query(query: str):
    """
    Enterprise-grade RAG pipeline with robust error handling
    """

    # logger.info(f"Received query: {query}")

    try:
        # 1️⃣ Retrieve relevant chunks
        chunks = retrieve_relevant_chunks(query)
        # logger.info(f"Retrieved {len(chunks)} relevant chunks")

        # 2️⃣ No relevant info
        if not chunks:
            # logger.warning("No relevant chunks found above similarity threshold")
            return {
                "answer": "I'm sorry, I do not have information regarding this."
            }

        # 3️⃣ Build context
        context_blocks = []
        sources = []
        retrieval_details = []

        for idx, (doc, semantic_score) in enumerate(chunks, start=1):

            context_blocks.append(
                f"""
                --- Document {idx} ---
                Source: {doc.metadata.get("source")}
                Document Name: {doc.metadata.get("file_name")}
                Page Number: {doc.metadata.get("page_number")}
                Semantic Score: {round(semantic_score, 2)}

                Content:
                {doc.page_content}
                """.strip()
            )

            # Explainability (user-facing)
            sources.append({
                "document_name": doc.metadata.get("file_name"),
                "page_number": doc.metadata.get("page_number"),
                "source": doc.metadata.get("source")
            })

            # Evaluation & debugging (internal)
            retrieval_details.append({
                "rank": idx,
                "document_name": doc.metadata.get("file_name"),
                "page_number": doc.metadata.get("page_number"),
                "semantic_score": round(semantic_score, 2)
            })

        context = "\n\n".join(context_blocks)

        # 4️⃣ Prompt construction
        messages = prompt_template.format_messages(
            context=context,
            question=query
        )

        # logger.info("Invoking LLM")

        # 5️⃣ LLM invocation
        response = llm.invoke(messages)

        # logger.info("LLM response generated successfully")

        # return response.content

        return {
            "answer": response.content,
            "retrieval_context": context
        }

    except Exception as e:
        # Critical error logging
        logger.error("Error occurred during answer generation")
        logger.error(str(e))
        logger.error(traceback.format_exc())

        return "An internal error occurred while processing your request. Please try again later.",