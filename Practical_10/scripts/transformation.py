import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "cleaned_supply_chain.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "transformed_supply_chain.csv"
)


# --------------------------------------------------
# 2. Load cleaned data
# --------------------------------------------------

print("Loading cleaned dataset...")

df = pd.read_csv(
    INPUT_FILE,
    parse_dates=[
        "order date (DateOrders)",
        "shipping date (DateOrders)"
    ]
)

print(f"Rows loaded    : {df.shape[0]}")
print(f"Columns loaded : {df.shape[1]}")


# --------------------------------------------------
# 3. Date transformations
# --------------------------------------------------

order_date = df["order date (DateOrders)"]

df["Order_Year"] = order_date.dt.year
df["Order_Month"] = order_date.dt.month
df["Order_Month_Name"] = order_date.dt.month_name()
df["Order_Quarter"] = "Q" + order_date.dt.quarter.astype(str)
df["Order_Day"] = order_date.dt.day
df["Order_Day_Name"] = order_date.dt.day_name()


# --------------------------------------------------
# 4. Shipping delay
# --------------------------------------------------

df["Shipping_Delay_Days"] = (
    df["Days for shipping (real)"]
    - df["Days for shipment (scheduled)"]
)


# --------------------------------------------------
# 5. Shipping performance
# --------------------------------------------------

df["Shipping_Performance"] = df[
    "Shipping_Delay_Days"
].apply(
    lambda x: "Delayed" if x > 0 else "On Time"
)


# --------------------------------------------------
# 6. Discount amount
# --------------------------------------------------

df["Discount_Amount"] = (
    df["Order Item Product Price"]
    * df["Order Item Quantity"]
    * df["Order Item Discount Rate"]
)


# --------------------------------------------------
# 7. Revenue
# --------------------------------------------------

df["Revenue"] = (
    df["Order Item Product Price"]
    * df["Order Item Quantity"]
) - df["Discount_Amount"]


# --------------------------------------------------
# 8. Profit margin
# --------------------------------------------------

df["Profit_Margin"] = (
    df["Order Profit Per Order"]
    / df["Revenue"]
    * 100
)

# Avoid infinite values
df["Profit_Margin"] = df[
    "Profit_Margin"
].replace(
    [float("inf"), float("-inf")],
    0
)

df["Profit_Margin"] = df[
    "Profit_Margin"
].fillna(0)


# --------------------------------------------------
# 9. Validate transformations
# --------------------------------------------------

print("\nTransformed columns:")
print(
    df[
        [
            "Order_Year",
            "Order_Month",
            "Order_Quarter",
            "Shipping_Delay_Days",
            "Shipping_Performance",
            "Discount_Amount",
            "Revenue",
            "Profit_Margin"
        ]
    ].head()
)


# --------------------------------------------------
# 10. Save transformed dataset
# --------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n" + "=" * 60)
print("DATA TRANSFORMATION COMPLETED")
print("=" * 60)

print(f"Final rows    : {df.shape[0]}")
print(f"Final columns : {df.shape[1]}")

print("\nSaved to:")
print(OUTPUT_FILE)