import pandas as pd
from sqlalchemy import text
from src.database import get_engine

engine = get_engine()

def order_monthly(order_status:str)->pd.DataFrame:

    with engine.connect() as connection:
        orders_per_month = connection.execute(
            text(f"""
                 SELECT
                 DATE_TRUNC('month', order_delivered_customer_date::TIMESTAMP) as month,
                 COUNT(*) as total_orders
                 FROM orders
                 WHERE order_status = '{order_status}'
                 GROUP BY month
                 ORDER BY month DESC
            """
        )
        ).fetchall()


    return pd.DataFrame(orders_per_month)

