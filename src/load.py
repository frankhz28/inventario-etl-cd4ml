import pandas as pd
from src.core.db import engine

def cargar_a_base_datos(df : pd.DataFrame, tabla : str ):
    df.to_sql(tabla, con=engine, if_exists='replace', index=False)