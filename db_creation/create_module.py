"""
This file creates and normalizes csv/Module.csv

It does the following:
1- Loads the Module CSV file.
2- Uses 'code' as the primary key (not 'id').
3- Adds foreign keys for 'offeredByFaculty' and self-referencing 'prerequisite'.
4- Creates the Module table and inserts validated module data.
"""
import sqlite3
import pandas as pd

# Load the Module CSV
df = pd.read_csv("../data/csv/Module.csv")

# Optional cleanup: strip whitespace and cast
df["code"] = df["code"].astype(str).str.strip()
df["prerequisite"] = df["prerequisite"].astype(str).str.strip()
df["offeredByFaculty"] = df["offeredByFaculty"].astype(str).str.strip()
df["creditsHours"] = pd.to_numeric(df["creditsHours"], errors="coerce").fillna(0).astype(int)

# Create SQLite connection
conn = sqlite3.connect("../university.db")
cursor = conn.cursor()

# Create Module table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Module (
    code TEXT PRIMARY KEY,
    name TEXT,
    nameArabic TEXT,
    creditsHours INTEGER,
    description TEXT,
    descriptionArabic TEXT,
    objectives TEXT,
    objectivesArabic TEXT,
    outcomes TEXT,
    outcomesArabic TEXT,
    prerequisite TEXT,
    offeredByFaculty TEXT,
    FOREIGN KEY (prerequisite) REFERENCES Module(code),
    FOREIGN KEY (offeredByFaculty) REFERENCES Faculty(id)
);
""")

# Prepare and insert
df_db = df[[
    "code", "name", "nameArabic", "creditsHours",
    "description", "descriptionArabic", "objectives",
    "objectivesArabic", "outcomes", "outcomesArabic",
    "prerequisite", "offeredByFaculty"
]].copy()

df_db = df_db.astype(str)

df_db.to_sql("Module", conn, if_exists="append", index=False)

conn.commit()
conn.close()

print("Module table created and populated successfully.")
