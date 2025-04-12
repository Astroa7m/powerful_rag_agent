import pandas as pd
import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from util.funcs import detect_language

# === Load CSVs ===
faq_csv = pd.read_csv("../data/csv/FAQ.csv").fillna("")

# === Load faq.json ===
with open("../data/faq.json", "r", encoding="utf-8") as f:
    faq_json = json.load(f)

docs = []

# === FAQ CSV ===
for _, row in faq_csv.iterrows():
    if row["question"] and row["answer"]:
        docs.append(Document(
            page_content=f"Q: {row['question']}\nA: {row['answer']}",
            metadata={"source": "faq_csv", "language": "en"}
        ))
    if row["questionArabic"] and row["answerArabic"]:
        docs.append(Document(
            page_content=f"س: {row['questionArabic']}\nج: {row['answerArabic']}",
            metadata={"source": "faq_csv", "language": "ar"}
        ))

# === FAQ JSON (based on prompt & completion) ===
for entry in faq_json:
    question = entry.get("prompt", "").strip()
    answer = entry.get("completion", "").strip()
    lang = detect_language(question + answer)

    if question and answer:
        prefix = "س" if lang == "ar" else "Q"
        suffix = "ج" if lang == "ar" else "A"
        docs.append(Document(
            page_content=f"{prefix}: {question}\n{suffix}: {answer}",
            metadata={"source": "faq_json", "language": lang}
        ))

# === Smarter Chunking (preserve if <= 1500 chars, split if longer) ===
splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
chunks = []
for doc in docs:
    if len(doc.page_content) > 1500:
        chunks.extend(splitter.split_documents([doc]))
    else:
        chunks.append(doc)

# === Embed and Save FAISS Vectorstore ===
embedding_model = HuggingFaceEmbeddings(model_name="thenlper/gte-small")
vectorstore = FAISS.from_documents(chunks, embedding_model)

vectorstore.save_local("aou_faq_vectorstore")
print("✅ Vector store saved as 'aou_faq_vectorstore'")
