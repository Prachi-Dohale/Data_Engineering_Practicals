-- ============================================================
-- SUPPLY CHAIN DATA ENGINEERING MINI PROJECT
-- SQL ANALYTICS
-- ============================================================


-- ============================================================
-- 1. OVERALL BUSINESS PERFORMANCE
-- ============================================================

SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(*) AS total_order_items,
    SUM(quantity) AS total_quantity,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(profit_margin), 2) AS average_profit_margin
FROM fact_sales;


-- ============================================================
-- 2. SALES BY YEAR
-- ============================================================

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


-- ============================================================
-- 3. MONTHLY SALES TREND
-- ============================================================

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


-- ============================================================
-- 4. SALES BY MARKET
-- ============================================================

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


-- ============================================================
-- 5. SALES BY REGION
-- ============================================================

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


-- ============================================================
-- 6. TOP 10 PRODUCTS BY SALES
-- ============================================================

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


-- ============================================================
-- 7. SALES BY PRODUCT CATEGORY
-- ============================================================

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


-- ============================================================
-- 8. SALES BY CUSTOMER SEGMENT
-- ============================================================

SELECT
    c.customer_segment,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(DISTINCT f.customer_key) AS unique_customers,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_key = c.customer_key
GROUP BY c.customer_segment
ORDER BY total_sales DESC;


-- ============================================================
-- 9. SHIPPING PERFORMANCE
-- ============================================================

SELECT
    s.shipping_mode,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(AVG(f.shipping_delay_days), 2)
        AS average_shipping_delay,
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


-- ============================================================
-- 10. TOP 10 MOST PROFITABLE PRODUCTS
-- ============================================================

SELECT
    p.product_name,
    p.category_name,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND(AVG(f.profit_margin), 2) AS average_profit_margin
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY
    p.product_key,
    p.product_name,
    p.category_name
ORDER BY total_profit DESC
LIMIT 10;


-- ============================================================
-- 11. LOWEST PROFIT / LOSS-MAKING PRODUCTS
-- ============================================================

SELECT
    p.product_name,
    p.category_name,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND(AVG(f.profit_margin), 2) AS average_profit_margin
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY
    p.product_key,
    p.product_name,
    p.category_name
ORDER BY total_profit ASC
LIMIT 10;


-- ============================================================
-- 12. TOP 10 CITIES BY SALES
-- ============================================================

SELECT
    l.order_city,
    l.order_state,
    l.order_country,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit
FROM fact_sales f
JOIN dim_location l
    ON f.location_key = l.location_key
GROUP BY
    l.order_city,
    l.order_state,
    l.order_country
ORDER BY total_sales DESC
LIMIT 10;


-- ============================================================
-- 13. DISCOUNT VS PROFIT ANALYSIS
-- ============================================================

SELECT
    p.category_name,
    ROUND(AVG(f.discount_amount), 2)
        AS average_discount,
    ROUND(SUM(f.sales), 2)
        AS total_sales,
    ROUND(SUM(f.profit), 2)
        AS total_profit
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY p.category_name
ORDER BY average_discount DESC;


-- ============================================================
-- 14. ORDER STATUS ANALYSIS
-- ============================================================

SELECT
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit
FROM fact_sales f;


-- ============================================================
-- 15. SHIPPING DELAY ANALYSIS
-- ============================================================

SELECT
    f.shipping_delay_days,
    COUNT(*) AS order_items,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit
FROM fact_sales f
GROUP BY f.shipping_delay_days
ORDER BY f.shipping_delay_days;