-- 1. Помесячная выручка, количество заказов и средний чек
SELECT strftime('%Y-%m-01', order_purchase_timestamp) AS month,
    COUNT(DISTINCT order_id) AS orders_cnt,
    SUM(payment_value) AS revenue,
    SUM(payment_value) / NULLIF(COUNT(DISTINCT order_id), 0) AS avg_order_value
FROM valid_sales_orders
WHERE order_purchase_timestamp >= '2017-01-01'
    AND order_purchase_timestamp < '2018-08-01'
GROUP BY 1
ORDER BY 1;
-- 2. Топ категорий по выручке
SELECT product_category_name_english,
    SUM(price) AS revenue,
    COUNT(DISTINCT order_id) AS orders_cnt,
    COUNT(*) AS items_cnt
FROM order_items_enriched
WHERE order_id IN (
        SELECT order_id
        FROM valid_sales_orders
        WHERE order_purchase_timestamp >= '2017-01-01'
            AND order_purchase_timestamp < '2018-08-01'
    )
GROUP BY 1
ORDER BY revenue DESC
LIMIT 20;
-- 3. Новые и повторные клиенты
WITH customer_orders AS (
    SELECT order_id,
        customer_unique_id,
        order_purchase_timestamp,
        payment_value,
        ROW_NUMBER() OVER (
            PARTITION BY customer_unique_id
            ORDER BY order_purchase_timestamp
        ) AS order_number
    FROM valid_sales_orders
)
SELECT CASE
        WHEN order_number = 1 THEN 'Новые'
        ELSE 'Повторные'
    END AS customer_type,
    COUNT(DISTINCT order_id) AS orders_cnt,
    COUNT(DISTINCT customer_unique_id) AS customers_cnt,
    SUM(payment_value) AS revenue,
    SUM(payment_value) / NULLIF(COUNT(DISTINCT order_id), 0) AS avg_order_value
FROM customer_orders
WHERE order_purchase_timestamp >= '2017-01-01'
    AND order_purchase_timestamp < '2018-08-01'
GROUP BY 1
ORDER BY revenue DESC;
-- 4. Клиентские сегменты
SELECT v.customer_segment,
    COUNT(DISTINCT v.customer_unique_id) AS customers_cnt,
    COUNT(DISTINCT v.order_id) AS orders_cnt,
    SUM(v.payment_value) AS revenue,
    SUM(v.payment_value) / NULLIF(COUNT(DISTINCT v.customer_unique_id), 0) AS avg_revenue_per_customer,
    SUM(v.payment_value) / NULLIF(COUNT(DISTINCT v.order_id), 0) AS avg_order_value
FROM valid_sales_orders AS v
WHERE v.order_purchase_timestamp >= '2017-01-01'
    AND v.order_purchase_timestamp < '2018-08-01'
GROUP BY 1
ORDER BY revenue DESC;
-- 5. Доля заказов с задержкой доставки
SELECT ROUND(
        AVG(
            CASE
                WHEN delivery_delay_days > 0 THEN 1.0
                ELSE 0.0
            END
        ),
        4
    ) AS late_delivery_rate
FROM delivery_reviews_base
WHERE order_id IN (
        SELECT order_id
        FROM valid_sales_orders
        WHERE order_purchase_timestamp >= '2017-01-01'
            AND order_purchase_timestamp < '2018-08-01'
    );
-- 6. Оценка заказа в зависимости от доставки
SELECT CASE
        WHEN delivery_delay_days > 0 THEN 'С задержкой'
        ELSE 'В срок'
    END AS delivery_group,
    AVG(review_score) AS avg_review_score,
    AVG(delivery_days) AS avg_delivery_days,
    AVG(delivery_delay_days) AS avg_delay_days,
    COUNT(DISTINCT order_id) AS orders_cnt
FROM delivery_reviews_base
WHERE order_id IN (
        SELECT order_id
        FROM valid_sales_orders
        WHERE order_purchase_timestamp >= '2017-01-01'
            AND order_purchase_timestamp < '2018-08-01'
    )
GROUP BY 1
ORDER BY 1;
-- 7. Клиенты с наибольшей ценностью
SELECT customer_unique_id,
    customer_segment,
    COUNT(DISTINCT order_id) AS orders_cnt,
    SUM(payment_value) AS monetary,
    SUM(payment_value) / NULLIF(COUNT(DISTINCT order_id), 0) AS avg_order_value
FROM valid_sales_orders
WHERE order_purchase_timestamp >= '2017-01-01'
    AND order_purchase_timestamp < '2018-08-01'
GROUP BY customer_unique_id,
    customer_segment
ORDER BY monetary DESC
LIMIT 20;