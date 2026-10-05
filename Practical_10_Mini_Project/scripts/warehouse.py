import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = BASE_DIR / "database" / "supply_chain.db"

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "transformed_supply_chain.csv"
)


# ============================================================
# 2. LOAD TRANSFORMED DATA
# ============================================================

print("=" * 60)
print("DATA WAREHOUSE CREATION")
print("=" * 60)

print("\nLoading transformed dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Rows loaded    : {len(df):,}")
print(f"Columns loaded : {len(df.columns)}")


# ============================================================
# 3. PARSE DATES
# ============================================================

print("\nParsing dates...")

df["order_datetime"] = pd.to_datetime(
    df["order date (DateOrders)"],
    errors="coerce"
)

df["shipping_datetime"] = pd.to_datetime(
    df["shipping date (DateOrders)"],
    errors="coerce"
)

invalid_order_dates = df["order_datetime"].isna().sum()
invalid_shipping_dates = df["shipping_datetime"].isna().sum()

print(
    f"Invalid order dates    : {invalid_order_dates:,}"
)

print(
    f"Invalid shipping dates : {invalid_shipping_dates:,}"
)

if invalid_order_dates > 0 or invalid_shipping_dates > 0:
    raise ValueError(
        "Invalid dates detected. Warehouse creation stopped."
    )


# ============================================================
# 4. CREATE DIM_DATE
# ============================================================

print("\nCreating dim_date...")

# Get unique order dates
order_dates = (
    df["order_datetime"]
    .dt.normalize()
)

# Get unique shipping dates
shipping_dates = (
    df["shipping_datetime"]
    .dt.normalize()
)

# Combine both
all_dates = pd.concat(
    [order_dates, shipping_dates],
    ignore_index=True
)

all_dates = (
    all_dates
    .dropna()
    .drop_duplicates()
    .sort_values()
    .reset_index(drop=True)
)

dim_date = pd.DataFrame()

dim_date["date_key"] = (
    all_dates
    .dt.strftime("%Y%m%d")
    .astype(int)
)

dim_date["full_date"] = (
    all_dates
    .dt.strftime("%Y-%m-%d")
)

dim_date["year"] = (
    all_dates.dt.year
)

dim_date["month"] = (
    all_dates.dt.month
)

dim_date["month_name"] = (
    all_dates.dt.month_name()
)

dim_date["quarter"] = (
    "Q" + all_dates.dt.quarter.astype(str)
)

dim_date["day"] = (
    all_dates.dt.day
)

dim_date["day_name"] = (
    all_dates.dt.day_name()
)


# ============================================================
# 5. CREATE DIM_CUSTOMER
# ============================================================

print("Creating dim_customer...")

dim_customer = (
    df[
        [
            "Customer Id",
            "Customer City",
            "Customer State",
            "Customer Country",
            "Customer Segment"
        ]
    ]
    .drop_duplicates(
        subset=["Customer Id"]
    )
    .reset_index(drop=True)
    .copy()
)

# Create surrogate key
dim_customer.insert(
    0,
    "customer_key",
    range(1, len(dim_customer) + 1)
)

dim_customer.columns = [
    "customer_key",
    "customer_id",
    "customer_city",
    "customer_state",
    "customer_country",
    "customer_segment"
]


# ============================================================
# 6. CREATE DIM_PRODUCT
# ============================================================

print("Creating dim_product...")

dim_product = (
    df[
        [
            "Product Card Id",
            "Product Name",
            "Product Category Id",
            "Category Name",
            "Department Id",
            "Department Name",
            "Product Price"
        ]
    ]
    .drop_duplicates(
        subset=["Product Card Id"]
    )
    .reset_index(drop=True)
    .copy()
)

dim_product.insert(
    0,
    "product_key",
    range(1, len(dim_product) + 1)
)

dim_product.columns = [
    "product_key",
    "product_id",
    "product_name",
    "category_id",
    "category_name",
    "department_id",
    "department_name",
    "product_price"
]


# ============================================================
# 7. CREATE DIM_LOCATION
# ============================================================

print("Creating dim_location...")

location_columns = [
    "Market",
    "Order City",
    "Order State",
    "Order Country",
    "Order Region",
    "Latitude",
    "Longitude"
]

dim_location = (
    df[location_columns]
    .drop_duplicates()
    .reset_index(drop=True)
    .copy()
)

dim_location.insert(
    0,
    "location_key",
    range(1, len(dim_location) + 1)
)

dim_location.columns = [
    "location_key",
    "market",
    "order_city",
    "order_state",
    "order_country",
    "order_region",
    "latitude",
    "longitude"
]


# ============================================================
# 8. CREATE DIM_SHIPPING
# ============================================================

print("Creating dim_shipping...")

dim_shipping = (
    df[
        [
            "Shipping Mode",
            "Days for shipment (scheduled)"
        ]
    ]
    .drop_duplicates()
    .reset_index(drop=True)
    .copy()
)

dim_shipping.insert(
    0,
    "shipping_key",
    range(1, len(dim_shipping) + 1)
)

dim_shipping.columns = [
    "shipping_key",
    "shipping_mode",
    "scheduled_days"
]


# ============================================================
# 9. CREATE LOOKUP DICTIONARIES
# ============================================================

print("\nCreating dimension lookup keys...")


# ----------------------------
# Customer lookup
# ----------------------------

customer_map = dict(
    zip(
        dim_customer["customer_id"],
        dim_customer["customer_key"]
    )
)


# ----------------------------
# Product lookup
# ----------------------------

product_map = dict(
    zip(
        dim_product["product_id"],
        dim_product["product_key"]
    )
)


# ----------------------------
# Shipping lookup
# ----------------------------

shipping_map = {
    (
        row.shipping_mode,
        row.scheduled_days
    ): row.shipping_key

    for row in dim_shipping.itertuples()
}


# ----------------------------
# Location lookup
# ----------------------------

location_map = {
    (
        row.market,
        row.order_city,
        row.order_state,
        row.order_country,
        row.order_region,
        row.latitude,
        row.longitude
    ): row.location_key

    for row in dim_location.itertuples()
}


# ============================================================
# 10. GENERATE FACT TABLE
# ============================================================

print("Generating fact table keys...")

fact_sales = pd.DataFrame()


# ----------------------------
# Basic identifiers
# ----------------------------

fact_sales["order_id"] = (
    df["Order Id"]
)

fact_sales["order_item_id"] = (
    df["Order Item Id"]
)


# ----------------------------
# Customer key
# ----------------------------

fact_sales["customer_key"] = (
    df["Customer Id"].map(customer_map)
)


# ----------------------------
# Product key
# ----------------------------

fact_sales["product_key"] = (
    df["Product Card Id"].map(product_map)
)


# ----------------------------
# Order date key
# ----------------------------

fact_sales["order_date_key"] = (
    df["order_datetime"]
    .dt.strftime("%Y%m%d")
    .astype(int)
)


# ----------------------------
# Shipping date key
# ----------------------------

fact_sales["shipping_date_key"] = (
    df["shipping_datetime"]
    .dt.strftime("%Y%m%d")
    .astype(int)
)


# ----------------------------
# Shipping key
# ----------------------------

fact_sales["shipping_key"] = [
    shipping_map.get(
        (
            mode,
            scheduled_days
        )
    )

    for mode, scheduled_days

    in zip(
        df["Shipping Mode"],
        df["Days for shipment (scheduled)"]
    )
]


# ----------------------------
# Location key
# ----------------------------

fact_sales["location_key"] = [
    location_map.get(
        (
            market,
            city,
            state,
            country,
            region,
            latitude,
            longitude
        )
    )

    for market,
        city,
        state,
        country,
        region,
        latitude,
        longitude

    in zip(
        df["Market"],
        df["Order City"],
        df["Order State"],
        df["Order Country"],
        df["Order Region"],
        df["Latitude"],
        df["Longitude"]
    )
]


# ============================================================
# 11. ADD FACT MEASURES
# ============================================================

print("Adding sales measures...")


fact_sales["quantity"] = (
    df["Order Item Quantity"]
)

fact_sales["sales"] = (
    df["Sales"]
)

fact_sales["discount_amount"] = (
    df["Discount_Amount"]
)

fact_sales["revenue"] = (
    df["Revenue"]
)

fact_sales["profit"] = (
    df["Order Profit Per Order"]
)

fact_sales["profit_margin"] = (
    df["Profit_Margin"]
)

fact_sales["shipping_delay_days"] = (
    df["Shipping_Delay_Days"]
)


# ============================================================
# 12. CREATE SALES SURROGATE KEY
# ============================================================

fact_sales.insert(
    0,
    "sales_key",
    range(
        1,
        len(fact_sales) + 1
    )
)


# ============================================================
# 13. VALIDATE FACT TABLE KEYS
# ============================================================

print("\nValidating dimension keys...")

key_columns = [
    "customer_key",
    "product_key",
    "order_date_key",
    "shipping_date_key",
    "location_key",
    "shipping_key"
]

missing_keys = {}

for column in key_columns:

    missing_keys[column] = int(
        fact_sales[column].isna().sum()
    )


print("\nMissing dimension keys")
print("-" * 60)

for column, count in missing_keys.items():

    print(
        f"{column:<25}: {count:,}"
    )


total_missing = sum(
    missing_keys.values()
)


# ============================================================
# 14. STOP IF ANY KEY IS MISSING
# ============================================================

if total_missing > 0:

    print("\nERROR: Missing dimension keys detected.")

    print(
        "Warehouse creation stopped."
    )

    raise ValueError(
        "Fact table contains missing dimension keys."
    )


print(
    "\nAll dimension keys validated successfully."
)


# ============================================================
# 15. CONNECT TO SQLITE
# ============================================================

print("\nConnecting to SQLite...")

connection = sqlite3.connect(
    DB_FILE
)

cursor = connection.cursor()

cursor.execute(
    "PRAGMA foreign_keys = ON"
)


# ============================================================
# 16. DROP PREVIOUS WAREHOUSE TABLES
# ============================================================

print("Removing previous warehouse tables...")

warehouse_tables = [
    "fact_sales",
    "dim_shipping",
    "dim_location",
    "dim_product",
    "dim_customer",
    "dim_date"
]

for table in warehouse_tables:

    cursor.execute(
        f"DROP TABLE IF EXISTS {table}"
    )


# ============================================================
# 17. CREATE DIM_DATE TABLE
# ============================================================

print("Creating dim_date...")

cursor.execute("""
CREATE TABLE dim_date (

    date_key INTEGER PRIMARY KEY,

    full_date TEXT NOT NULL,

    year INTEGER,

    month INTEGER,

    month_name TEXT,

    quarter TEXT,

    day INTEGER,

    day_name TEXT

)
""")


# ============================================================
# 18. CREATE DIM_CUSTOMER TABLE
# ============================================================

print("Creating dim_customer...")

cursor.execute("""
CREATE TABLE dim_customer (

    customer_key INTEGER PRIMARY KEY,

    customer_id INTEGER UNIQUE NOT NULL,

    customer_city TEXT,

    customer_state TEXT,

    customer_country TEXT,

    customer_segment TEXT

)
""")


# ============================================================
# 19. CREATE DIM_PRODUCT TABLE
# ============================================================

print("Creating dim_product...")

cursor.execute("""
CREATE TABLE dim_product (

    product_key INTEGER PRIMARY KEY,

    product_id INTEGER UNIQUE NOT NULL,

    product_name TEXT,

    category_id INTEGER,

    category_name TEXT,

    department_id INTEGER,

    department_name TEXT,

    product_price REAL

)
""")


# ============================================================
# 20. CREATE DIM_LOCATION TABLE
# ============================================================

print("Creating dim_location...")

cursor.execute("""
CREATE TABLE dim_location (

    location_key INTEGER PRIMARY KEY,

    market TEXT,

    order_city TEXT,

    order_state TEXT,

    order_country TEXT,

    order_region TEXT,

    latitude REAL,

    longitude REAL

)
""")


# ============================================================
# 21. CREATE DIM_SHIPPING TABLE
# ============================================================

print("Creating dim_shipping...")

cursor.execute("""
CREATE TABLE dim_shipping (

    shipping_key INTEGER PRIMARY KEY,

    shipping_mode TEXT,

    scheduled_days INTEGER

)
""")


# ============================================================
# 22. CREATE FACT_SALES TABLE
# ============================================================

print("Creating fact_sales...")

cursor.execute("""
CREATE TABLE fact_sales (

    sales_key INTEGER PRIMARY KEY,

    order_id INTEGER,

    order_item_id INTEGER,

    customer_key INTEGER NOT NULL,

    product_key INTEGER NOT NULL,

    order_date_key INTEGER NOT NULL,

    shipping_date_key INTEGER NOT NULL,

    location_key INTEGER NOT NULL,

    shipping_key INTEGER NOT NULL,

    quantity INTEGER,

    sales REAL,

    discount_amount REAL,

    revenue REAL,

    profit REAL,

    profit_margin REAL,

    shipping_delay_days INTEGER,

    FOREIGN KEY (customer_key)
        REFERENCES dim_customer(customer_key),

    FOREIGN KEY (product_key)
        REFERENCES dim_product(product_key),

    FOREIGN KEY (order_date_key)
        REFERENCES dim_date(date_key),

    FOREIGN KEY (shipping_date_key)
        REFERENCES dim_date(date_key),

    FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key),

    FOREIGN KEY (shipping_key)
        REFERENCES dim_shipping(shipping_key)

)
""")


# ============================================================
# 23. LOAD DIMENSION TABLES
# ============================================================

print("\nLoading dimension tables...")


dim_date.to_sql(
    "dim_date",
    connection,
    if_exists="append",
    index=False
)


dim_customer.to_sql(
    "dim_customer",
    connection,
    if_exists="append",
    index=False
)


dim_product.to_sql(
    "dim_product",
    connection,
    if_exists="append",
    index=False
)


dim_location.to_sql(
    "dim_location",
    connection,
    if_exists="append",
    index=False
)


dim_shipping.to_sql(
    "dim_shipping",
    connection,
    if_exists="append",
    index=False
)


# ============================================================
# 24. LOAD FACT TABLE
# ============================================================

print("Loading fact_sales...")

fact_sales.to_sql(
    "fact_sales",
    connection,
    if_exists="append",
    index=False,
    chunksize=10000
)


# ============================================================
# 25. CREATE INDEXES
# ============================================================

print("Creating indexes...")


cursor.execute("""
CREATE INDEX idx_fact_customer
ON fact_sales(customer_key)
""")


cursor.execute("""
CREATE INDEX idx_fact_product
ON fact_sales(product_key)
""")


cursor.execute("""
CREATE INDEX idx_fact_order_date
ON fact_sales(order_date_key)
""")


cursor.execute("""
CREATE INDEX idx_fact_shipping_date
ON fact_sales(shipping_date_key)
""")


cursor.execute("""
CREATE INDEX idx_fact_location
ON fact_sales(location_key)
""")


cursor.execute("""
CREATE INDEX idx_fact_shipping
ON fact_sales(shipping_key)
""")


# ============================================================
# 26. COMMIT
# ============================================================

connection.commit()


# ============================================================
# 27. DATA WAREHOUSE REPORT
# ============================================================

print("\n" + "=" * 60)
print("DATA WAREHOUSE REPORT")
print("=" * 60)


for table in warehouse_tables:

    cursor.execute(
        f"SELECT COUNT(*) FROM {table}"
    )

    count = cursor.fetchone()[0]

    print(
        f"{table:<20}: {count:,} rows"
    )


# ============================================================
# 28. FOREIGN KEY VALIDATION
# ============================================================

cursor.execute("""
SELECT COUNT(*)

FROM fact_sales

WHERE customer_key IS NULL

   OR product_key IS NULL

   OR order_date_key IS NULL

   OR shipping_date_key IS NULL

   OR location_key IS NULL

   OR shipping_key IS NULL
""")

invalid_records = cursor.fetchone()[0]


print(
    "\nFact records with missing dimension keys:",
    invalid_records
)


# ============================================================
# 29. ROW COUNT VALIDATION
# ============================================================

cursor.execute("""
SELECT COUNT(*)
FROM staging_supply_chain
""")

staging_count = cursor.fetchone()[0]


cursor.execute("""
SELECT COUNT(*)
FROM fact_sales
""")

fact_count = cursor.fetchone()[0]


print("\nRow Count Validation")
print("-" * 60)

print(
    f"Staging records : {staging_count:,}"
)

print(
    f"Fact records    : {fact_count:,}"
)


if staging_count == fact_count:

    print(
        "Status          : PASSED"
    )

else:

    print(
        "Status          : WARNING - row counts differ"
    )


# ============================================================
# 30. CLOSE DATABASE
# ============================================================

connection.close()


# ============================================================
# 31. SUCCESS MESSAGE
# ============================================================

print("\n" + "=" * 60)
print("STAR SCHEMA CREATED SUCCESSFULLY")
print("=" * 60)