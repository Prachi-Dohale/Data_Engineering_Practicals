import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = BASE_DIR / "database" / "supply_chain.db"
OUTPUT_DIR = BASE_DIR / "powerbi_data"

OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# TABLES TO EXPORT
# ============================================================

tables = [
    "fact_sales",
    "dim_date",
    "dim_customer",
    "dim_product",
    "dim_location",
    "dim_shipping"
]


# ============================================================
# CONNECT TO DATABASE
# ============================================================

print("=" * 60)
print("POWER BI DATA EXPORT")
print("=" * 60)

print("\nConnecting to SQLite database...")

connection = sqlite3.connect(DB_FILE)


# ============================================================
# EXPORT TABLES
# ============================================================

total_tables = 0

for table in tables:

    print(f"\nExporting {table}...")

    try:

        query = f"SELECT * FROM {table}"

        df = pd.read_sql_query(
            query,
            connection
        )

        output_file = OUTPUT_DIR / f"{table}.csv"

        df.to_csv(
            output_file,
            index=False
        )

        print(f"Rows    : {len(df):,}")
        print(f"Columns : {len(df.columns)}")
        print(f"Saved   : {output_file}")

        total_tables += 1

    except Exception as error:

        print(f"ERROR exporting {table}")
        print(error)


# ============================================================
# CLOSE CONNECTION
# ============================================================

connection.close()


# ============================================================
# FINAL REPORT
# ============================================================

print("\n" + "=" * 60)
print("POWER BI EXPORT COMPLETED")
print("=" * 60)

print(
    f"Tables exported : "
    f"{total_tables}/{len(tables)}"
)

print(
    f"Output folder   : "
    f"{OUTPUT_DIR}"
)

print("=" * 60)