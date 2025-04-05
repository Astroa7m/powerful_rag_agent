from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(model_name="thenlper/gte-small")

retriever = FAISS.load_local("aou_faiss_index", embedding_model, allow_dangerous_deserialization=True)
results = retriever.similarity_search("Who teaches machine learning?")
for doc in results:
    print(doc.page_content)