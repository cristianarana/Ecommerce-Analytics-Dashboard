import pandas as pd
from src.database import get_engine


def csv_to_db(csv_path, table_name):
    df = pd.read_csv(csv_path)
    engine = get_engine()
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"Tabla {table_name} cargada")
    
    