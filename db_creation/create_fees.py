"""
This file creates and normalizes fee-related CSVs:
- FoundationProgramFees.csv
- FullTimeLearningFees.csv
- OpenLearningFees.csv
- NonRefundableEnrollmentFees.csv

It does the following:
1- Creates a unified Fee table with fields for type, major, delivery method, and amount.
2- Loads and maps each CSV into the unified format.
3- Validates 'major_id' against the Major table where applicable.
4- Inserts clean, validated fee data into the database.
"""
import sqlite3
import pandas as pd
import uuid

# Connect to SQLite database
conn = sqlite3.connect("../university.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# --------------------------------------------
# Step 1: Create unified Fee table
# --------------------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS Fee (
    id TEXT PRIMARY KEY,
    feeType TEXT,
    deliveryMethod TEXT,
    major_id TEXT,
    feeName TEXT,
    amount REAL,
    language TEXT,
    FOREIGN KEY (major_id) REFERENCES Major(id)
);
""")

# --------------------------------------------
# Step 2: Get valid Major IDs for validation
# --------------------------------------------
cursor.execute("SELECT id FROM Major")
valid_majors = {row[0] for row in cursor.fetchall()}

# --------------------------------------------
# Step 3: Helper function to insert any list of fee rows
# --------------------------------------------
def insert_fee_rows(rows):
    df = pd.DataFrame(rows, columns=["id", "feeType", "deliveryMethod", "major_id", "feeName", "amount", "language"])
    df.to_sql("Fee", conn, if_exists="append", index=False)

# --------------------------------------------
# Step 4: Process FoundationProgramFees.csv
# --------------------------------------------
foundation = pd.read_csv("../data/csv/FoundationProgramFees.csv")
foundation_rows = [
    (
        str(uuid.uuid4()),            # id
        "Foundation",                 # feeType
        row[1],                       # deliveryMethod
        None,                         # major_id
        None,                         # feeName
        row[3],                       # amount
        "English"                     # language
    )
    for row in foundation.itertuples(index=False)
]
insert_fee_rows(foundation_rows)

# --------------------------------------------
# Step 5: Process FullTimeLearningFees.csv
# --------------------------------------------
fulltime = pd.read_csv("../data/csv/FullTimeLearningFees.csv")
fulltime_rows = []
for row in fulltime.itertuples(index=False):
    major_id = str(row[1]).strip()
    if major_id in valid_majors:
        fulltime_rows.append((
            str(uuid.uuid4()),
            "FullTime",
            None,
            major_id,
            None,
            row[4],  # Amount (R.O)
            "English"
        ))
    else:
        print(f"⚠️ Skipping invalid MajorID in FullTime: {major_id}")
insert_fee_rows(fulltime_rows)

# --------------------------------------------
# Step 6: Process OpenLearningFees.csv
# --------------------------------------------
openlearn = pd.read_csv("../data/csv/OpenLearningFees.csv")
openlearn_rows = []
for row in openlearn.itertuples(index=False):
    major_id = str(row[1]).strip()
    if major_id in valid_majors:
        openlearn_rows.append((
            str(uuid.uuid4()),
            "OpenLearning",
            None,
            major_id,
            None,
            row[4],  # Amount (R.O)
            "English"
        ))
    else:
        print(f"⚠️ Skipping invalid MajorID in OpenLearning: {major_id}")
insert_fee_rows(openlearn_rows)

# --------------------------------------------
# Step 7: Process NonRefundableEnrollmentFees.csv
# --------------------------------------------
enroll = pd.read_csv("../data/csv/NonRefundableEnrollmentFees.csv")
enrollment_rows = [
    (
        str(uuid.uuid4()),
        "Enrollment",
        None,
        None,
        row[1],     # feeName
        row[3],     # amount
        "English"
    )
    for row in enroll.itertuples(index=False)
]
insert_fee_rows(enrollment_rows)

# --------------------------------------------
# Finalize
# --------------------------------------------
conn.commit()
conn.close()
print("✅ Fee table created and populated successfully from all sources.")
