with revenue_monthly as (
    SELECT 
        DATE_TRUNC('month', o.order_delivered_customer_date::TIMESTAMP) as month,
        ROUND(SUM(op.payment_value)::NUMERIC, 2) as total_revenue
    FROM orders o 
    INNER JOIN order_payments op ON o.order_id = op.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY month
    ORDER BY month DESC
)

SELECT 
    month,
    total_revenue,
    LAG(total_revenue) OVER (ORDER BY month) AS previous_month_revenue
FROM revenue_monthly
ORDER BY month DESC;
