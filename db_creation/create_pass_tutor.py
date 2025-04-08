"""
This file creates and normalizes csv/PassedTutor.csv

It does the following:
1- Loads the PassedTutor CSV.
2- Creates the PassTutor table with foreign key to Major.
3- Normalizes 'moduleTaught' into a many-to-many relation.
4- Creates the PassTutorTeachingModule table and inserts all data.
"""

import sqlite3
import pandas as pd

# Load the CSV
df = pd.read_csv("../csv/PassTutor.csv")

# Clean up
df["id"] = df["id"].astype(str).str.strip()
df["major"] = df["major"].astype(str).str.strip()
df["moduleTaught"] = df["moduleTaught"].astype(str)

# Extract PassTutorTeachingModule relations
teaching_data = []
for _, row in df.iterrows():
    tutor_id = row["id"]
    modules = row["moduleTaught"]
    if pd.notna(modules):
        for module in str(modules).split(","):
            module_code = module.strip()
            if module_code:
                teaching_data.append((tutor_id, module_code))

teaching_df = pd.DataFrame(teaching_data, columns=["tutor_id", "module_code"])

# Remove moduleTaught from main tutor table
df = df.drop(columns=["moduleTaught"])

# Connect to DB
conn = sqlite3.connect("../university.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# Create PassTutor table
cursor.execute("""
CREATE TABLE IF NOT EXISTS PassTutor (
    id TEXT PRIMARY KEY,
    name TEXT,
    nameArabic TEXT,
    email TEXT,
    major TEXT,
    FOREIGN KEY (major) REFERENCES Major(id)
);
""")

# Create PassTutorTeachingModule table
cursor.execute("""
CREATE TABLE IF NOT EXISTS PassTutorTeachingModule (
    tutor_id TEXT,
    module_code TEXT,
    FOREIGN KEY (tutor_id) REFERENCES PassTutor(id),
    FOREIGN KEY (module_code) REFERENCES Module(code)
);
""")

# Insert data
df.to_sql("PassTutor", conn, if_exists="append", index=False)
teaching_df.to_sql("PassTutorTeachingModule", conn, if_exists="append", index=False)

conn.commit()
conn.close()

print("PassTutor and PassTutorTeachingModule tables created and populated.")
