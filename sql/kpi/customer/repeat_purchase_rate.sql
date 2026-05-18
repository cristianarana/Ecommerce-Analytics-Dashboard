WITH customer_monthly_purchases AS (
    SELECT 
        DATE_TRUNC('month', o.order_delivered_customer_date::TIMESTAMP) as month,
        c.customer_unique_id,
        COUNT(o.order_id) as total_orders
    FROM orders o 
    INNER JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY month, c.customer_unique_id
)
SELECT
    month,
    ROUND(COUNT(CASE WHEN total_orders > 1 THEN 1 END)::NUMERIC/COUNT(customer_unique_id)::NUMERIC, 2) as repeat_purchase_rate
    FROM customer_monthly_purchases
    GROUP BY 1
    ORDER BY 1;