from sqlalchemy import create_engine
from config import DB_URI

engine = create_engine(DB_URI)

def cargar_tabla(df, nombre_tabla):
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).apply(lambda x: x.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore"))
    df.to_sql(nombre_tabla, con=engine, if_exists="replace", index=False)


def limpiar_dataframe(df):
    df = df.copy()  # para evitar SettingWithCopyWarning
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = (
                df[col]
                .astype(str)
                .apply(lambda x: x.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore"))
            )
    return df