import sqlite3

conn = sqlite3.connect("../university.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = OFF;")

# Step 1: Rename old table
cursor.execute("ALTER TABLE Teaches RENAME TO Teaches_old;")

# Step 2: Create new Teaches table with proper FK to Module(code)
cursor.execute("""
CREATE TABLE Teaches (
    staff_id TEXT,
    module_code TEXT,
    FOREIGN KEY (staff_id) REFERENCES AcademicStaff(id),
    FOREIGN KEY (module_code) REFERENCES Module(code)
);
""")

# Step 3: Copy data
cursor.execute("""
INSERT INTO Teaches (staff_id, module_code)
SELECT staff_id, module_code FROM Teaches_old;
""")

# Step 4: Drop old table
cursor.execute("DROP TABLE Teaches_old;")

conn.commit()
conn.close()

print("Teaches table updated with foreign key to Module(code).")
