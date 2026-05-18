SELECT 
DATE_TRUNC('month', o.order_delivered_customer_date::TIMESTAMP) as month,
ROUND((AVG(o.order_delivered_customer_date - o.order_estimated_delivery_date))) as delivery_delay_avg
FROM orders o
WHERE o.order_status = 'delivered'
GROUP BY month
ORDER BY month DESC;