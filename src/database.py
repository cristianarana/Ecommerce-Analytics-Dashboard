from sqlalchemy import create_engine

def get_engine():
    return create_engine(
        "postgresql+psycopg2://admin:admin123@localhost:5432/ecommerce-analytics-dashboard"
    )