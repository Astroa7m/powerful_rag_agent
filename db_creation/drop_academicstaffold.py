import sqlite3

# Connect to your database
conn = sqlite3.connect("../university.db")
cursor = conn.cursor()

# Step 1: Disable foreign key checks temporarily
cursor.execute("PRAGMA foreign_keys = OFF;")

# Step 2: Drop the old table
cursor.execute("DROP TABLE IF EXISTS AcademicStaff_old;")

# Step 3: Re-enable foreign key checks
cursor.execute("PRAGMA foreign_keys = ON;")

# Commit and close connection
conn.commit()
conn.close()

print("✅ AcademicStaff_old has been successfully deleted.")
