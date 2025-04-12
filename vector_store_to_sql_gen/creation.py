import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Creating query-sql pairs and chunking then embedding them into vector store

# Load your query-SQL pairs
with open("query_pairs.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert to LangChain documents
docs = [Document(page_content=item["query"], metadata={"sql": item["sql"]}) for item in data]

# Embed and store in FAISS
embedder = HuggingFaceEmbeddings(model_name="thenlper/gte-small")
vectorstore = FAISS.from_documents(docs, embedder)
vectorstore.save_local("query_vector_index")