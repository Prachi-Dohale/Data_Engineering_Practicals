import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = BASE_DIR / "database" / "supply_chain.db"

REPORT_DIR = BASE_DIR / "reports"

REPORT_DIR.mkdir(
    exist_ok=True
)


# ============================================================
# CONNECT TO DATABASE
# ============================================================

print("=" * 60)
print("SUPPLY CHAIN SQL ANALYTICS")
print("=" * 60)

print("\nConnecting to database...")

connection = sqlite3.connect(DB_FILE)


# ============================================================
# ANALYTICAL QUERIES
# ============================================================

queries = {

    "overall_performance": """
        SELECT
            COUNT(DISTINCT order_id) AS total_orders,
            COUNT(*) AS total_order_items,
            SUM(quantity) AS total_quantity,
            ROUND(SUM(sales), 2) AS total_sales,
            ROUND(SUM(revenue), 2) AS total_revenue,
            ROUND(SUM(profit), 2) AS total_profit,
            ROUND(AVG(profit_margin), 2)
                AS average_profit_margin
        FROM fact_sales;
    """,

    "yearly_sales": """
        SELECT
            d.year,
            COUNT(DISTINCT f.order_id) AS total_orders,
            ROUND(SUM(f.sales), 2) AS total_sales,
            ROUND(SUM(f.profit), 2) AS total_profit
        FROM fact_sales f
        JOIN dim_date d
            ON f.order_date_key = d.date_key
        GROUP BY d.year
        ORDER BY d.year;
    """,

    "monthly_sales": """
        SELECT
            d.year,
            d.month,
            d.month_name,
            ROUND(SUM(f.sales), 2) AS total_sales,
            ROUND(SUM(f.profit), 2) AS total_profit
        FROM fact_sales f
        JOIN dim_date d
            ON f.order_date_key = d.date_key
        GROUP BY
            d.year,
            d.month,
            d.month_name
        ORDER BY
            d.year,
            d.month;
    """,

    "market_sales": """
        SELECT
            l.market,
            COUNT(DISTINCT f.order_id) AS total_orders,
            ROUND(SUM(f.sales), 2) AS total_sales,
            ROUND(SUM(f.profit), 2) AS total_profit
        FROM fact_sales f
        JOIN dim_location l
            ON f.location_key = l.location_key
        GROUP BY l.market
        ORDER BY total_sales DESC;
    """,

    "region_sales": """
        SELECT
            l.order_region,
            COUNT(DISTINCT f.order_id) AS total_orders,
            ROUND(SUM(f.sales), 2) AS total_sales,
            ROUND(SUM(f.profit), 2) AS total_profit
        FROM fact_sales f
        JOIN dim_location l
            ON f.location_key = l.location_key
        GROUP BY l.order_region
        ORDER BY total_sales DESC;
    """,

    "top_products": """
        SELECT
            p.product_name,
            p.category_name,
            COUNT(DISTINCT f.order_id) AS total_orders,
            SUM(f.quantity) AS quantity_sold,
            ROUND(SUM(f.sales), 2) AS total_sales,
            ROUND(SUM(f.profit), 2) AS total_profit
        FROM fact_sales f
        JOIN dim_product p
            ON f.product_key = p.product_key
        GROUP BY
            p.product_key,
            p.product_name,
            p.category_name
        ORDER BY total_sales DESC
        LIMIT 10;
    """,

    "category_sales": """
        SELECT
            p.category_name,
            COUNT(DISTINCT f.order_id) AS total_orders,
            SUM(f.quantity) AS quantity_sold,
            ROUND(SUM(f.sales), 2) AS total_sales,
            ROUND(SUM(f.profit), 2) AS total_profit
        FROM fact_sales f
        JOIN dim_product p
            ON f.product_key = p.product_key
        GROUP BY p.category_name
        ORDER BY total_sales DESC;
    """,

    "customer_segments": """
        SELECT
            c.customer_segment,
            COUNT(DISTINCT f.order_id) AS total_orders,
            COUNT(DISTINCT f.customer_key)
                AS unique_customers,
            ROUND(SUM(f.sales), 2) AS total_sales,
            ROUND(SUM(f.profit), 2) AS total_profit
        FROM fact_sales f
        JOIN dim_customer c
            ON f.customer_key = c.customer_key
        GROUP BY c.customer_segment
        ORDER BY total_sales DESC;
    """,

    "shipping_performance": """
        SELECT
            s.shipping_mode,
            COUNT(DISTINCT f.order_id) AS total_orders,
            ROUND(
                AVG(f.shipping_delay_days),
                2
            ) AS average_shipping_delay,

            SUM(
                CASE
                    WHEN f.shipping_delay_days > 0
                    THEN 1
                    ELSE 0
                END
            ) AS delayed_items,

            ROUND(
                100.0 *
                SUM(
                    CASE
                        WHEN f.shipping_delay_days > 0
                        THEN 1
                        ELSE 0
                    END
                ) / COUNT(*),
                2
            ) AS delay_percentage

        FROM fact_sales f

        JOIN dim_shipping s
            ON f.shipping_key = s.shipping_key

        GROUP BY s.shipping_mode

        ORDER BY delay_percentage DESC;
    """,

    "profitable_products": """
        SELECT
            p.product_name,
            p.category_name,
            ROUND(SUM(f.sales), 2) AS total_sales,
            ROUND(SUM(f.profit), 2) AS total_profit,
            ROUND(
                AVG(f.profit_margin),
                2
            ) AS average_profit_margin
        FROM fact_sales f
        JOIN dim_product p
            ON f.product_key = p.product_key
        GROUP BY
            p.product_key,
            p.product_name,
            p.category_name
        ORDER BY total_profit DESC
        LIMIT 10;
    """,

    "loss_products": """
        SELECT
            p.product_name,
            p.category_name,
            ROUND(SUM(f.sales), 2) AS total_sales,
            ROUND(SUM(f.profit), 2) AS total_profit,
            ROUND(
                AVG(f.profit_margin),
                2
            ) AS average_profit_margin
        FROM fact_sales f
        JOIN dim_product p
            ON f.product_key = p.product_key
        GROUP BY
            p.product_key,
            p.product_name,
            p.category_name
        ORDER BY total_profit ASC
        LIMIT 10;
    """,

    "top_cities": """
        SELECT
            l.order_city,
            l.order_state,
            l.order_country,
            COUNT(DISTINCT f.order_id)
                AS total_orders,
            ROUND(SUM(f.sales), 2)
                AS total_sales,
            ROUND(SUM(f.profit), 2)
                AS total_profit
        FROM fact_sales f
        JOIN dim_location l
            ON f.location_key = l.location_key
        GROUP BY
            l.order_city,
            l.order_state,
            l.order_country
        ORDER BY total_sales DESC
        LIMIT 10;
    """,

    "discount_analysis": """
        SELECT
            p.category_name,
            ROUND(
                AVG(f.discount_amount),
                2
            ) AS average_discount,
            ROUND(
                SUM(f.sales),
                2
            ) AS total_sales,
            ROUND(
                SUM(f.profit),
                2
            ) AS total_profit
        FROM fact_sales f
        JOIN dim_product p
            ON f.product_key = p.product_key
        GROUP BY p.category_name
        ORDER BY average_discount DESC;
    """,

    "shipping_delay": """
        SELECT
            f.shipping_delay_days,
            COUNT(*) AS order_items,
            ROUND(
                SUM(f.sales),
                2
            ) AS total_sales,
            ROUND(
                SUM(f.profit),
                2
            ) AS total_profit
        FROM fact_sales f
        GROUP BY f.shipping_delay_days
        ORDER BY f.shipping_delay_days;
    """
}


# ============================================================
# EXECUTE QUERIES
# ============================================================

print("\nRunning analytical queries...")

successful = 0

for name, query in queries.items():

    try:

        result = pd.read_sql_query(
            query,
            connection
        )

        output_file = (
            REPORT_DIR / f"{name}.csv"
        )

        result.to_csv(
            output_file,
            index=False
        )

        print(
            f"✓ {name:<25} "
            f"{len(result):>6} rows"
        )

        successful += 1

    except Exception as error:

        print(
            f"✗ {name:<25} ERROR"
        )

        print(
            f"  {error}"
        )


# ============================================================
# CLOSE DATABASE
# ============================================================

connection.close()


# ============================================================
# FINAL REPORT
# ============================================================

print("\n" + "=" * 60)
print("SQL ANALYTICS COMPLETED")
print("=" * 60)

print(
    f"Queries executed successfully : "
    f"{successful}/{len(queries)}"
)

print(
    f"Reports saved in              : "
    f"{REPORT_DIR}"
)

print("=" * 60)