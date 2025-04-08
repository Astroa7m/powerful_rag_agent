"""
This file creates and loads csv/FAQ.csv

It does the following:
1- Loads the FAQ CSV file.
2- Creates a simple FAQ table with multilingual question and answer fields.
3- Inserts all records directly (no normalization needed).
"""
import sqlite3
import pandas as pd

# Load FAQ CSV
df = pd.read_csv("../csv/FAQ.csv")

# Optional cleanup
df["id"] = df["id"].astype(str).str.strip()

# Connect to DB
conn = sqlite3.connect("../university.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# Create FAQ table
cursor.execute("""
CREATE TABLE IF NOT EXISTS FAQ (
    id TEXT PRIMARY KEY,
    question TEXT,
    questionArabic TEXT,
    answer TEXT,
    answerArabic TEXT
);
""")

# Insert data
df.to_sql("FAQ", conn, if_exists="append", index=False)

conn.commit()
conn.close()

print("✅ FAQ table created and populated successfully.")
