from langchain.chains import RetrievalQA
from src.vectorstore.pgvector_store import vector_store
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True
)

def answer(query: str):
    return qa_chain.invoke({"query": query})
