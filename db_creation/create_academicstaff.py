"""
This file creates and normalizes csv/AcademicStaff.csv file

it does the following:
1- Loads the CSV.

2- Normalizes the teaches column into a separate Teaches table.

3- Creates the AcademicStaff and Teaches tables in an SQLite database.

4- Inserts all data accordingly.
"""
import sqlite3
import pandas as pd

# Load the AcademicStaff CSV
df = pd.read_csv("../csv/AcademicStaff.csv")

# Normalize the teaches column into a new dataframe
teaches_data = []
for _, row in df.iterrows():
    staff_id = row["id"]
    teaches = row["teaches"]
    if pd.notna(teaches):
        for module_code in str(teaches).split(","):
            teaches_data.append((staff_id, module_code.strip()))

teaches_df = pd.DataFrame(teaches_data, columns=["staff_id", "module_code"])

# Remove the teaches column from AcademicStaff table
df = df.drop(columns=["teaches"])

# Create SQLite connection
conn = sqlite3.connect("../university.db")
cursor = conn.cursor()

# Create AcademicStaff table
cursor.execute("""
CREATE TABLE IF NOT EXISTS AcademicStaff (
    id TEXT PRIMARY KEY,
    name TEXT,
    nameArabic TEXT,
    title TEXT,
    titleArabic TEXT,
    email TEXT,
    biography TEXT,
    biographyArabic TEXT,
    office_hours TEXT,
    specialization TEXT,
    specializationArabic TEXT,
    position TEXT,
    positionArabic TEXT,
    link TEXT
);
""")

# Create Teaches table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Teaches (
    staff_id TEXT,
    module_code TEXT,
    FOREIGN KEY (staff_id) REFERENCES AcademicStaff(id)
);
""")

# Insert AcademicStaff data
df.to_sql("AcademicStaff", conn, if_exists="append", index=False)

# Insert Teaches data
teaches_df.to_sql("Teaches", conn, if_exists="append", index=False)

# Commit and close
conn.commit()
conn.close()

print("AcademicStaff and Teaches tables created and populated.")
