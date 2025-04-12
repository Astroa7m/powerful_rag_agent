"""
This file creates and normalizes csv/Faculty.csv

It does the following:
1- Loads the Faculty CSV.
2- Maps the 'HeadOfFaculty' field to AcademicStaff via foreign key.
3- Creates the Faculty table in the SQLite database.
4- Inserts all faculty data accordingly.
"""
import sqlite3
import pandas as pd

# Load Faculty CSV
df = pd.read_csv("../data/csv/Faculty.csv")

# Optional cleanup
df["id"] = df["id"].astype(str).str.strip()
df["HeadOfFaculty"] = df["HeadOfFaculty"].astype(str).str.strip()

# Create DB connection
conn = sqlite3.connect("../university.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# Create Faculty table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Faculty (
    id TEXT PRIMARY KEY,
    name TEXT,
    nameArabic TEXT,
    description TEXT,
    descriptionArabic TEXT,
    HeadOfFaculty TEXT,
    phoneNumber TEXT,
    email TEXT,
    link TEXT,
    FOREIGN KEY (HeadOfFaculty) REFERENCES AcademicStaff(id)
);
""")

# Insert data
df.to_sql("Faculty", conn, if_exists="append", index=False)

conn.commit()
conn.close()

print("Faculty table created and populated successfully.")
