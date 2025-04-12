from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(model_name="thenlper/gte-small")
vectorstore = FAISS.load_local("aou_faq_vectorstore", embedding_model, allow_dangerous_deserialization=True)

query = input('Q: ')
while query != "-1":
    retrieved = vectorstore.similarity_search(query, k=10)
    for doc in retrieved:
        print(f"️️📁: {doc.metadata['source']}")
        print(f"️️🤔: {doc.page_content}")
        print("==========END==========")
    query = input('Q: ')
