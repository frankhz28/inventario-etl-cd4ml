import pytest
import pandas as pd
import numpy as np
from src.transform import PipelineDemandaBuilder, generar_bandera_quiebre, calcular_demanda_no_restringida, preparar_inventario, preparar_ventas

class TestReglasDeNegocio:
    """Pruebas para validar las reglas de negocio específicas del cruce de datos."""
    @pytest.mark.parametrize(
        "venta, stock, quiebre_esperado",
        [
            (500, 1000.0, 0),
            (0,   0.0,    1),
            (0,  -50.0,   1),
            (0,   np.nan, 1),
            (50,  0.0,    0),
        ]
    )
    def test_generar_bandera_quiebre_detecta_escenarios(self, venta, stock, quiebre_esperado):
        ## Arrange
        df_ventas = pd.DataFrame({
            "fecha": ["2023-10-01"], 
            "id_producto": ["PROD-A"], 
            "cantidad_vendida": [venta]
        })
        
        df_inventario = pd.DataFrame({
            "fecha": ["2023-10-01"], 
            "id_producto": ["PROD-A"], 
            "stock_cierre": [stock]
        })

        ## Act
        df_resultado = generar_bandera_quiebre(df_ventas, df_inventario)
        ## Assert
        assert df_resultado["quiebre_stock"].iloc[0] == quiebre_esperado


    def test_calcular_demanda_no_restringida_imputa_promedio_correcto(self, df_escenario_quiebre):
        # ACT
        df_resultado = calcular_demanda_no_restringida(df_escenario_quiebre)
        # ASSERT
        demanda_imputada = df_resultado["demanda_no_restringida"].iloc[1]
        assert demanda_imputada == 300, f"Se esperaba 300, pero se calculó {demanda_imputada}"
 
        
class TestLimpiezaDeDatos:
    """Pruebas para garantizar el Contrato de Datos antes de los cruces."""
    @pytest.mark.parametrize(
        "stock_cierre, valor",
        [
            (["100", "-50", "no_hay"], 100),
            (["-50","100","no hay"], 0),
            (["no_hay","-50","100"], 0)
        ]
    )
    def test_preparar_inventario_aplica_contrato_de_datos(self, stock_cierre, valor):
        # ARRANGE
        df_sucio = pd.DataFrame({
            "fecha": ["2023-10-01", "2023/10/02", "texto_invalido"],
            "id_producto": [" prod-a ", "PROD-B", None], 
            "almacen": [" ALM 1 ", "alm 2", "ALM 3"],             
            "stock_cierre": stock_cierre                
        })

        # ACT:
        df_limpio = preparar_inventario(df_sucio)

        # ASSERT
        assert len(df_limpio) == 1, "No se eliminaron correctamente las filas invalidas"
        assert pd.api.types.is_datetime64_any_dtype(df_limpio["fecha"]), "La fecha no se casteó a datetime"
        assert df_limpio["id_producto"].iloc[0] == "PROD-A", "Fallo al limpiar espacios/mayúsculas en ID"
        assert df_limpio["almacen"].iloc[0] == "ALM1", "Fallo al limpiar espacios en el almacén"
        assert df_limpio["stock_cierre"].iloc[0] == valor, "Casteo numérico fallido"


    def test_preparar_ventas_elimina_duplicados_correctamente(self):
        # ARRANGE
        df_duplicado = pd.DataFrame({
            "fecha": ["2023-10-01", "2023-10-01"],
            "id_producto": ["PROD-A", "PROD-A"],
            "cantidad_vendida": [500, 500],  
            "cliente_b2b": ["ALFA", "ALFA"],
            "estado_orden": ["COMPLETADA", "COMPLETADA"]
        })

        # ACT
        df_limpio = preparar_ventas(df_duplicado)
        # ASSERT
        assert len(df_limpio) == 1, "No se eliminaron los registros duplicados del ERP"


class TestPipelineDemandaBuilder:
    """Pruebas exclusivas para el comportamiento arquitectónico del patrón Builder."""
    def test_builder_lanza_error_al_construir_prematuramente(self):
        # ARRANGE: DFs vacíos, no nos importan los datos aquí
        df_dummy = pd.DataFrame()
        builder = PipelineDemandaBuilder(df_ventas=df_dummy, df_inventario=df_dummy)
        
        # ACT & ASSERT: Verificamos que explote controladamente usando pytest.raises
        import pytest
        with pytest.raises(ValueError, match="El pipeline no ha sido procesado aún"):
            builder.build()

    def test_builder_encadena_metodos_secuencialmente(self, df_dummy_ventas, df_dummy_inventario):
        # ARRANGE        
        builder = PipelineDemandaBuilder(df_dummy_ventas, df_dummy_inventario)
        # ACT & ASSERT
        paso_1 = builder.limpiar_datos()
        assert isinstance(paso_1, PipelineDemandaBuilder), "limpiar_datos no retornó self"
        # ACT & ASSERT
        paso_2 = builder.cruzar_datos()
        assert isinstance(paso_2, PipelineDemandaBuilder), "cruzar_datos no retornó self"
        assert builder._resultado is not None, "El cruce de datos no generó el estado interno"
        # ACT & ASSERT
        paso_3 = builder.aplicar_reglas_negocio()
        assert isinstance(paso_3, PipelineDemandaBuilder), "aplicar_reglas_negocio no retornó self"