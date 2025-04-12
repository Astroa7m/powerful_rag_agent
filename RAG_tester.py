from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq

# === Step 1: Load the vectorstore ===
embedding_model = HuggingFaceEmbeddings(model_name="thenlper/gte-small")
vectorstore = FAISS.load_local("vector_store_faq_and_general_info/aou_faq_vectorstore", embedding_model, allow_dangerous_deserialization=True)

# === Step 2: Initialize the retriever ===
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# === Step 3: Initialize ChatGroq LLM ===
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key="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"
)

# === Step 4: Combine into RetrievalQA chain ===
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",  # Sends full context to LLM
    return_source_documents=True  # Optional, for debugging
)

# === Step 5: Ask your question ===
query = input("Q: ")

while query != "-1":
    response = qa_chain(query)

    # === Step 6: Print answer and (optional) sources ===
    print("\n🤖 Answer:")
    print(response["result"])

    print("\n📄 Retrieved Chunks (for transparency):")
    for doc in response["source_documents"]:
        print("---")
        print(doc.page_content)
    query = input("Q: ")

