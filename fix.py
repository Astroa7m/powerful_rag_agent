import sqlite3

db_path = "university.db"

with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()

    print("🔁 Backing up existing Faculty and Teaches data...")

    # Step 1: Backup
    cursor.execute("CREATE TABLE IF NOT EXISTS Faculty_backup AS SELECT * FROM Faculty;")
    cursor.execute("CREATE TABLE IF NOT EXISTS Teaches_backup AS SELECT * FROM Teaches;")

    print("🧹 Dropping original Faculty and Teaches tables...")
    cursor.execute("DROP TABLE IF EXISTS Faculty;")
    cursor.execute("DROP TABLE IF EXISTS Teaches;")

    print("🛠️ Recreating Faculty and Teaches tables with correct foreign keys...")

    # Step 2: Recreate Faculty
    cursor.execute("""
        CREATE TABLE Faculty (
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

    # Step 3: Recreate Teaches
    cursor.execute("""
        CREATE TABLE Teaches (
            staff_id TEXT,
            module_code TEXT,
            FOREIGN KEY (staff_id) REFERENCES AcademicStaff(id),
            FOREIGN KEY (module_code) REFERENCES Module(code)
        );
    """)

    print("⬆️ Restoring data from backups...")
    cursor.execute("INSERT INTO Faculty SELECT * FROM Faculty_backup;")
    cursor.execute("INSERT INTO Teaches SELECT * FROM Teaches_backup;")

    print("🧽 Cleaning up backup tables...")
    cursor.execute("DROP TABLE Faculty_backup;")
    cursor.execute("DROP TABLE Teaches_backup;")

    conn.commit()

print("✅ Foreign key fix completed successfully.")
