import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# === Load Data ===
faq_df = pd.read_csv("./csv/FAQ.csv").fillna("")
staff_df = pd.read_csv("./csv/AcademicStaff.csv").fillna("")

# === Prepare Documents ===
faq_docs = [
    Document(
        page_content=f"Q: {row['question']}\nA: {row['answer']}",
        metadata={"source": "FAQ"}
    )
    for _, row in faq_df.iterrows() if row["question"] and row["answer"]
]

staff_docs = [
    Document(
        page_content=f"Name: {row['name']}\nSpecialization: {row['specialization']}\nBio: {row['biography']}\nModules: {row.get('moduleTaught', '')}",
        metadata={"source": "AcademicStaff"}
    )
    for _, row in staff_df.iterrows() if row["name"] or row["biography"]
]

all_docs = faq_docs + staff_docs

# === Split into Chunks ===
splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
chunks = splitter.split_documents(all_docs)

# === Embed and Create FAISS Index ===
embedding_model = HuggingFaceEmbeddings(model_name="thenlper/gte-small")
vectorstore = FAISS.from_documents(chunks, embedding_model)

# === Save Index ===
vectorstore.save_local("aou_faiss_index")
