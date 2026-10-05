import pandas as pd
import sqlite3
from pathlib import Path


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "transformed_supply_chain.csv"
)

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DB_FILE = DATABASE_DIR / "supply_chain.db"


# --------------------------------------------------
# 2. Load transformed data
# --------------------------------------------------

print("Loading transformed dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Rows loaded    : {df.shape[0]}")
print(f"Columns loaded : {df.shape[1]}")


# --------------------------------------------------
# 3. Connect to SQLite
# --------------------------------------------------

print("\nConnecting to SQLite database...")

connection = sqlite3.connect(DB_FILE)


# --------------------------------------------------
# 4. Store transformed data
# --------------------------------------------------

df.to_sql(
    "staging_supply_chain",
    connection,
    if_exists="replace",
    index=False
)


# --------------------------------------------------
# 5. Verify database
# --------------------------------------------------

cursor = connection.cursor()

cursor.execute(
    "SELECT COUNT(*) FROM staging_supply_chain"
)

row_count = cursor.fetchone()[0]

cursor.execute(
    "SELECT COUNT(*) FROM pragma_table_info('staging_supply_chain')"
)

column_count = cursor.fetchone()[0]


print("\n" + "=" * 60)
print("DATABASE STORAGE REPORT")
print("=" * 60)

print(f"Database : {DB_FILE}")
print(f"Table    : staging_supply_chain")
print(f"Rows     : {row_count}")
print(f"Columns  : {column_count}")


# --------------------------------------------------
# 6. Close connection
# --------------------------------------------------

connection.close()

print("\nDatabase storage completed successfully.")