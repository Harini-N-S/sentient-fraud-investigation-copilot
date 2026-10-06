import sqlite3
from pathlib import Path

db_path = Path("database/synthetic_bank.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = [row["name"] for row in cursor.fetchall() if not row["name"].startswith("sqlite_")]

print(f"Database File: {db_path} ({db_path.stat().st_size:,} bytes)\n")

table_counts = {}
for t in tables:
    cursor.execute(f"SELECT COUNT(*) as c FROM \"{t}\"")
    c = cursor.fetchone()["c"]
    table_counts[t] = c
    cursor.execute(f"PRAGMA table_info(\"{t}\")")
    cols = [r["name"] for r in cursor.fetchall()]
    print(f"{t} ({c} rows): {cols}")

print("\nTotal Records Across Core Tables:", sum(table_counts.values()))
