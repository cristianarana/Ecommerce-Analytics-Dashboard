SELECT 
DATE_TRUNC('month', o.order_delivered_customer_date::TIMESTAMP) as month,
ROUND((COUNT(CASE WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 1 END)::NUMERIC / COUNT(o.order_id)::NUMERIC, 2)) as on_time_delivery_rate
FROM orders o
WHERE o.order_status = 'delivered'
GROUP BY month
ORDER BY month DESC;