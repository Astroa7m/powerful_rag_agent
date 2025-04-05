import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.utilities import SQLDatabase
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from langchain.agents.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType

# === CONFIG ===
DB_PATH = "sqlite:///aou_rag.db"
FAISS_PATH = "aou_faiss_index"
GROQ_API_KEY = "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"
MODEL_NAME = "llama-3.3-70b-versatile"

# === STEP 1: Initialize ChatGroq LLM ===
llm = ChatGroq(
    model_name=MODEL_NAME,
    temperature=0,
    groq_api_key=GROQ_API_KEY
)

# === STEP 2: Create SQL Agent ===
db = SQLDatabase.from_uri(DB_PATH)
sql_agent = create_sql_agent(
    llm=llm,
    db=db,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
)

# === STEP 3: Create RAG Chain with FAISS ===
embedding_model = HuggingFaceEmbeddings(model_name="thenlper/gte-small")
vectorstore = FAISS.load_local(FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

rag_qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",
    return_source_documents=True
)

# === STEP 4: Combine SQL + RAG Results with LLM ===
def combine_sql_rag(llm, query, sql_result, rag_result):
    prompt = f"""
You are a helpful assistant. A user asked this question:

"{query}"

You were given two responses:

🧮 From SQL (structured data):
{sql_result}

🔍 From RAG (semantic search):
{rag_result}

Please write a clear and complete answer by combining or choosing the best parts of both responses. Be concise, helpful, and remove any duplication.
"""
    response = llm.invoke(prompt)
    return response.content.strip()

# === STEP 5: Hybrid Query Handler ===
def hybrid_agent(query):
    print("📌 User Query:", query)

    try:
        sql_result = sql_agent.invoke(query)
    except Exception as e:
        sql_result = f"⚠️ SQL failed: {str(e)}"

    try:
        rag_result = rag_qa_chain.invoke(query)
    except Exception as e:
        rag_result = f"⚠️ RAG failed: {str(e)}"

    print("\n🔍 RAG Result:")
    print(rag_result)

    print("\n🧮 SQL Result:")
    print(sql_result)

    final = combine_sql_rag(llm, query, sql_result, rag_result)

    print("\n🤖 Final Combined Answer:")
    print(final)

    return final

# === Run Example ===
if __name__ == "__main__":
    question = "List all the faculty members who are in IT"
    hybrid_agent(question)
