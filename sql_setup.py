import pandas as pd
import sqlite3
import os

# ===== STEP 1: Set paths to your CSV files =====
csv_files = {
    "AcademicStaff": "AcademicStaff.csv",
    "Faculty": "Faculty.csv",
    "Module": "Module.csv",
    "Major": "Major.csv",
    "FullTimeLearningFees": "FullTimeLearningFees.csv",
    "OpenLearningFees": "OpenLearningFees.csv",
    "FoundationProgramFees": "FoundationProgramFees.csv",
    "NonRefundableEnrollmentFees": "NonRefundableEnrollmentFees.csv",
    "PassTutor": "PassTutor.csv",
}

# ===== STEP 2: Load CSV files into DataFrames =====
dataframes = {name: pd.read_csv("./csv/"+path) for name, path in csv_files.items()}

# ===== STEP 3: Create SQLite DB (in memory or on disk) =====
conn = sqlite3.connect("aou_rag.db")  # or ":memory:" for RAM-based
cursor = conn.cursor()

# ===== STEP 4: Function to auto-create tables and insert data =====
def create_table_from_df(table_name, df):
    columns = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            col_type = "REAL"
        else:
            col_type = "TEXT"
        columns.append(f'"{col}" {col_type}')
    columns_clause = ", ".join(columns)
    create_stmt = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_clause});'
    cursor.execute(create_stmt)

    df = df.where(pd.notnull(df), None)  # replace NaN with None
    insert_stmt = f'INSERT INTO "{table_name}" VALUES ({", ".join(["?"] * len(df.columns))})'
    cursor.executemany(insert_stmt, df.values.tolist())

# ===== STEP 5: Create and populate all tables =====
for table_name, df in dataframes.items():
    create_table_from_df(table_name, df)

conn.commit()

# ===== STEP 6: Sample Queries (optional testing) =====
sample_queries = [
    ("All AI-specialized tutors:", "SELECT name, specialization FROM AcademicStaff WHERE specialization LIKE '%AI%' OR specialization LIKE '%Artificial Intelligence%' OR biography LIKE '%Artificial Intelligence%';"),
    ("Email of Dr. Sherimon:", "SELECT name, email FROM AcademicStaff WHERE name LIKE '%Sherimon%';"),
    ("Open Learning Fees by Major:", "SELECT * FROM OpenLearningFees;")
]

for label, query in sample_queries:
    print(f"\n{label}")
    for row in cursor.execute(query):
        print(row)

# ===== Optional: Close the DB =====
# conn.close()
