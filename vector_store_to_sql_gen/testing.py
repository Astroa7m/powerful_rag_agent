import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

embedder = HuggingFaceEmbeddings(model_name="thenlper/gte-small")


retriever = FAISS.load_local("query_vector_index", embedder, allow_dangerous_deserialization=True)
query = "List all the teacher of it faculty"
results = retriever.similarity_search(query, k=5)

for r in results:
    print("Query match:", r.page_content)
    print("SQL:", r.metadata["sql"])