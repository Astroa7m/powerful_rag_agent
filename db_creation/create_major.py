"""
This file creates and normalizes csv/Major.csv

It does the following:
1- Loads the Major CSV.
2- Maps each major to a faculty using 'offeredByFaculty' as a foreign key.
3- Creates the Major table and inserts validated major records.
"""
import sqlite3
import pandas as pd

# Load Major CSV
df = pd.read_csv("../csv/Major.csv")

# Data cleanup
df["id"] = df["id"].astype(str).str.strip()
df["offeredByFaculty"] = df["offeredByFaculty"].astype(str).str.strip()
df["requiredCredits"] = pd.to_numeric(df["requiredCredits"], errors="coerce").fillna(0).astype(int)

# Create SQLite connection
conn = sqlite3.connect("../university.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# Create Major table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Major (
    id TEXT PRIMARY KEY,
    name TEXT,
    nameArabic TEXT,
    requiredCredits INTEGER,
    degreeLevel TEXT,
    degreeLevelArabic TEXT,
    description TEXT,
    descriptionArabic TEXT,
    studyPlan TEXT,
    offeredByFaculty TEXT,
    FOREIGN KEY (offeredByFaculty) REFERENCES Faculty(id)
);
""")

# Insert data
df.to_sql("Major", conn, if_exists="append", index=False)

conn.commit()
conn.close()

print("Major table created and populated successfully.")
