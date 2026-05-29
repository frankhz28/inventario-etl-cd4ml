import os
import pandas as pd
from sqlalchemy import create_engine
from src.load import cargar_a_base_datos

class TestCargaBaseDatos:
    """Pruebas de Integración: Tocan el disco y el motor de SQLite real."""

    def test_cargar_a_base_datos_escribe_y_lee_correctamente(self, df_prueba_carga):
        # 1. ARRANGE
        df_prueba = df_prueba_carga
        nombre_tabla = "demanda_test_integracion"

        # 2. ACT
        cargar_a_base_datos(df_prueba, nombre_tabla)

        # 3. ASSERT: Actuamos como un auditor externo
        url_test = os.getenv("DATABASE_URL")
        engine_test = create_engine(url_test)
        # Leemos los datos directamente usando SQL nativo
        df_leido = pd.read_sql(f"SELECT * FROM {nombre_tabla}", con=engine_test)
        assert len(df_leido) == 1, "La tabla no se creó o no tiene registros."
        assert df_leido["id_producto"].iloc[0] == "PROD-INTEGRACION", "Los datos de texto se corrompieron al viajar a SQL."
        assert df_leido["demanda_no_restringida"].iloc[0] == 500, "Los datos numéricos perdieron precisión."

    def test_cargar_a_base_datos_es_idempotente(self, df_prueba_carga):
        """
        Prueba la idempotencia: Si corremos el ETL dos veces, 
        ¿falla por tabla duplicada o la reemplaza limpiamente?
        """
        df_prueba = df_prueba_carga
        nombre_tabla = "demanda_test_idempotencia"
        # ACT: Ejecutamos la carga dos veces seguidas
        cargar_a_base_datos(df_prueba, nombre_tabla)
        cargar_a_base_datos(df_prueba, nombre_tabla)

        # ASSERT
        engine_test = create_engine(os.getenv("DATABASE_URL"))
        df_leido = pd.read_sql(f"SELECT * FROM {nombre_tabla}", con=engine_test)
        assert len(df_leido) == 1, "La función no está reemplazando la tabla, está duplicando datos."