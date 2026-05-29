from src.load import cargar_a_base_datos
from src.transform import PipelineDemandaBuilder
from src.extract import sanitizar_cv, extraer_df

def run_etl():
    sanitizar_cv('data/ventas_diarias.csv', 5)
    sanitizar_cv('data/fotografia_inventario_diario.csv', 4)
    
    df_ventas = extraer_df('data/ventas_diarias_sanitizado.csv')
    df_inventario = extraer_df('data/fotografia_inventario_diario_sanitizado.csv')
    
    df_final = (PipelineDemandaBuilder(df_ventas=df_ventas, df_inventario=df_inventario)
                    .limpiar_datos()
                    .cruzar_datos()
                    .aplicar_reglas_negocio()
                    .build())
    
    print(df_final.head(20))

    cargar_a_base_datos(df_final, 'demanda_no_restringida')

    
if __name__ == "__main__":
    run_etl()