import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "data" / "raw" / "DataCoSupplyChainDataset.csv"

PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = PROCESSED_DIR / "cleaned_supply_chain.csv"


# --------------------------------------------------
# 2. Load raw data
# --------------------------------------------------

print("Loading raw dataset...")

df = pd.read_csv(
    RAW_FILE,
    encoding="latin1"
)

print(f"Original rows    : {df.shape[0]}")
print(f"Original columns : {df.shape[1]}")


# --------------------------------------------------
# 3. Remove unnecessary / sensitive columns
# --------------------------------------------------

columns_to_remove = [
    "Product Description",
    "Order Zipcode",
    "Customer Zipcode",
    "Customer Email",
    "Customer Password",
    "Customer Street",
    "Customer Fname",
    "Customer Lname"
]

# Remove only columns that actually exist
columns_to_remove = [
    col for col in columns_to_remove
    if col in df.columns
]

df.drop(columns=columns_to_remove, inplace=True)


print("\nRemoved columns:")
for col in columns_to_remove:
    print("-", col)


# --------------------------------------------------
# 4. Convert date columns
# --------------------------------------------------

date_columns = [
    "order date (DateOrders)",
    "shipping date (DateOrders)"
]

for col in date_columns:
    df[col] = pd.to_datetime(
        df[col],
        errors="coerce"
    )


# --------------------------------------------------
# 5. Clean text columns
# --------------------------------------------------

text_columns = df.select_dtypes(
    include=["object", "string"]
).columns

for col in text_columns:
    df[col] = df[col].str.strip()


# --------------------------------------------------
# 6. Check missing values
# --------------------------------------------------

print("\nMissing values after cleaning:")

missing = df.isnull().sum()
missing = missing[missing > 0]

if len(missing) == 0:
    print("No missing values found.")
else:
    print(missing)


# --------------------------------------------------
# 7. Check duplicates
# --------------------------------------------------

duplicate_count = df.duplicated().sum()

print(f"\nDuplicate records: {duplicate_count}")


# --------------------------------------------------
# 8. Check invalid dates
# --------------------------------------------------

print("\nDate validation:")

for col in date_columns:
    invalid_dates = df[col].isna().sum()
    print(f"{col}: {invalid_dates} invalid/missing dates")


# --------------------------------------------------
# 9. Save cleaned dataset
# --------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# 10. Final report
# --------------------------------------------------

print("\n" + "=" * 60)
print("DATA CLEANING REPORT")
print("=" * 60)

print(f"Rows after cleaning    : {df.shape[0]}")
print(f"Columns after cleaning : {df.shape[1]}")

print(f"\nCleaned dataset saved to:")
print(OUTPUT_FILE)

print("\nDATA CLEANING COMPLETED SUCCESSFULLY")