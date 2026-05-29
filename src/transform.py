import pandas as pd
import numpy as np

class PipelineDemandaBuilder:
    def __init__(self, df_ventas : pd.DataFrame, df_inventario : pd.DataFrame):
        self.df_ventas = df_ventas
        self.df_inventario = df_inventario
        self._resultado = None

    def limpiar_datos(self) -> 'PipelineDemandaBuilder':
        self.df_ventas = preparar_ventas(self.df_ventas)
        self.df_inventario = preparar_inventario(self.df_inventario)
        return self

    def cruzar_datos(self) -> 'PipelineDemandaBuilder':
        self._resultado = generar_bandera_quiebre(self.df_ventas, self.df_inventario)
        return self
    
    def aplicar_reglas_negocio(self) -> 'PipelineDemandaBuilder':
        self._resultado = calcular_demanda_no_restringida(self._resultado)
        return self

    def build(self) -> pd.DataFrame:
        if self._resultado is None:
            raise ValueError("El pipeline no ha sido procesado aún.")
        return self._resultado

def preparar_inventario(df_inv : pd.DataFrame) -> pd.DataFrame:
    
    """Prepara el DataFrame de inventario diario para su análisis.
    Returns:
        pd.DataFrame: DataFrame limpio y preparado con las columnas adecuadas.
    """
    
    df = df_inv.copy()
    df["fecha"] = pd.to_datetime(df["fecha"], format='%Y-%m-%d', errors='coerce')
    df = df.dropna(subset=["fecha", "id_producto"], how="any")
    df = df.drop_duplicates(subset=["fecha", "id_producto"], keep="last")
    
    df['id_producto'] = (df['id_producto']
                         .astype(str)
                         .str.upper()
                         .str.replace(r'\s+', '', regex=True))
    
    df['almacen'] = (df['almacen']  
                     .str.replace(' ', '')
                     .str.strip()
                     .str.upper())
    
    df['stock_cierre'] = pd.to_numeric(df['stock_cierre'], errors='coerce')
    df['stock_cierre'] = df['stock_cierre'].fillna(0).astype(int)
    df.loc[df['stock_cierre'] < 0, 'stock_cierre'] = 0
    
    return df


def preparar_ventas(df_ven : pd.DataFrame) -> pd.DataFrame:   
    df = df_ven.copy()
    df["fecha"] = pd.to_datetime(df["fecha"], format='%Y-%m-%d', errors='coerce')
    df = df.dropna(subset=["fecha", "id_producto"], how="any")
    df = df.drop_duplicates(subset=["fecha", "id_producto", "cantidad_vendida", "cliente_b2b", "estado_orden"], keep="first")
    
    df['id_producto'] = (df['id_producto']
                         .astype(str)
                         .str.upper()
                         .str.replace(r'\s+', '', regex=True))
    
    df['cliente_b2b'] = (df['cliente_b2b']
                         .str.upper()
                         .str.replace(r'\s\s+', '', regex=True)
                         .str.strip())
    
    df['estado_orden'] = (df['estado_orden']
                          .str.upper())
    
    df['cantidad_vendida'] = pd.to_numeric(df['cantidad_vendida'], errors='coerce')
    df['cantidad_vendida'] = df['cantidad_vendida'].fillna(0).astype(int)
    df.loc[df['cantidad_vendida'] < 0, 'cantidad_vendida'] = 0

    return df

def generar_bandera_quiebre(df_ventas : pd.DataFrame, df_inventario : pd.DataFrame) -> pd.DataFrame:

    df_merge = pd.merge(df_ventas, df_inventario, on=["fecha", "id_producto"], how="left")
    condicion_ventas = df_merge["cantidad_vendida"] == 0
    condicion_stock = (df_merge["stock_cierre"] <= 0) | (df_merge["stock_cierre"].isna())
    df_merge["quiebre_stock"] = np.where(condicion_ventas & condicion_stock, 1, 0)
    
    return df_merge

def calcular_demanda_no_restringida(df : pd.DataFrame) -> pd.DataFrame:
    df_out = df.copy()
    df_out["ventas_sanas"] = np.where(
                                df_out["quiebre_stock"] == 1, 
                                np.nan, df_out["cantidad_vendida"]
                            )

    promedio_historico = (df_out.groupby("id_producto")["ventas_sanas"]
                            .transform("mean")
                            .fillna(0)
                            .round()
                            .astype(int))

    df_out["demanda_no_restringida"] = np.where(
                                        df_out["quiebre_stock"] == 1, 
                                        promedio_historico, df_out["ventas_sanas"]
                                    )
    
    df_out = df_out.drop(columns=["ventas_sanas"])
    
    return df_out
