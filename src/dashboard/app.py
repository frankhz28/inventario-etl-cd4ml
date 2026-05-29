import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

st.set_page_config(
    page_title="Dashboard Ejecutivo | Cóndor S.A.",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_resource
def init_connection():
    """Inicializa la conexión a PostgreSQL de forma segura (Singleton)."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        st.error("Variable de entorno DATABASE_URL no encontrada.")
        st.stop()
    return create_engine(db_url)

engine = init_connection()

@st.cache_data(ttl=600)
def load_data():
    """Lee la tabla de demanda desde PostgreSQL y la cachea por 10 minutos."""
    query = "SELECT * FROM demanda_no_restringida ORDER BY fecha ASC"
    try:
        df = pd.read_sql(query, con=engine)
        if not df.empty:
            df["fecha"] = pd.to_datetime(df["fecha"])
            df["Mes"] = df["fecha"].dt.to_period("M").astype(str)
        return df
    except Exception as e:
        st.error(f"Error al leer la base de datos: {e}")
        return pd.DataFrame()

with st.spinner("Conectando al Data Warehouse..."):
    df = load_data()

if df.empty:
    st.warning("No hay datos en la base de datos. Ejecuta el pipeline ETL primero.")
    st.stop()

col_titulo, col_filtros = st.columns([2, 2])

with col_titulo:
    st.title("Análisis de Demanda y Quiebres")
    st.markdown("Monitor de Inventario Corporativo - Cóndor S.A.")

with col_filtros:
    st.write("###")
    f1, f2, f3 = st.columns(3)
    producto_seleccionado = f1.selectbox("Producto", ["Todos"] + list(df["id_producto"].unique()))
    almacen_seleccionado = f2.selectbox("Almacén", ["Todos"] + list(df["almacen"].unique()))
    mes_seleccionado = f3.selectbox("Mes", ["Todos"] + list(df["Mes"].unique()))

df_filtrado = df.copy()
if producto_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["id_producto"] == producto_seleccionado]
if almacen_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["almacen"] == almacen_seleccionado]
if mes_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Mes"] == mes_seleccionado]

if df_filtrado.empty:
    st.info("No hay registros para esta combinación de filtros.")
    st.stop()

st.markdown("---")

col_izq, col_cen, col_der = st.columns([1.5, 3, 1.5])

with col_izq:
    st.subheader("Quiebres por Almacén")
    df_agrupado = df_filtrado.groupby("almacen")["quiebre_stock"].sum().reset_index()
    fig_loc = px.bar(df_agrupado, x="almacen", y="quiebre_stock", text_auto=True, color_discrete_sequence=["#1f77b4"])
    fig_loc.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=280)
    st.plotly_chart(fig_loc, use_container_width=True)

with col_cen:
    st.subheader("Ventas Reales vs Demanda Estimada")
    fig_combo = go.Figure()
    
    df_tiempo = df_filtrado.groupby("fecha")[["cantidad_vendida", "demanda_no_restringida"]].sum().reset_index()
    
    fig_combo.add_trace(go.Bar(x=df_tiempo["fecha"], y=df_tiempo["cantidad_vendida"], name="Venta Real", marker_color="#1f77b4"))
    fig_combo.add_trace(go.Scatter(x=df_tiempo["fecha"], y=df_tiempo["demanda_no_restringida"], name="Demanda Estimada", line=dict(color="#2ca02c", width=3)))
    fig_combo.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=280, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_combo, use_container_width=True)

with col_der:
    st.subheader("Estado de Órdenes")
    estado_counts = df_filtrado["estado_orden"].value_counts().reset_index()
    fig_donut = px.pie(estado_counts, names="estado_orden", values="count", hole=0.6, color_discrete_sequence=["#2ca02c", "#d62728", "#ff7f0e"])
    fig_donut.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=280, showlegend=True, legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("---")

col_bottom1, col_bottom2 = st.columns([1.5, 2.5])

with col_bottom1:
    st.subheader("Impacto por Cliente B2B")
    st.caption("Demanda perdida por falta de stock")
    df_perdidas = df_filtrado[df_filtrado["quiebre_stock"] > 0]
    if not df_perdidas.empty:
        df_b2b = df_perdidas.groupby("cliente_b2b")["demanda_no_restringida"].sum().reset_index()
        fig_hbar = px.bar(df_b2b, y="cliente_b2b", x="demanda_no_restringida", text_auto=True, orientation='h', color_discrete_sequence=["#d62728"])
        fig_hbar.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=10, b=0), height=250)
        st.plotly_chart(fig_hbar, use_container_width=True)
    else:
        st.success("¡Cero quiebres de stock en este periodo/filtro!")

with col_bottom2:
    st.subheader("Registro Detallado (Data Warehouse)")
    st.caption("Últimos movimientos procesados por el ETL")
    columnas_mostrar = ["fecha", "id_producto", "almacen", "cliente_b2b", "estado_orden", "cantidad_vendida", "demanda_no_restringida"]
    st.dataframe(df_filtrado[columnas_mostrar].sort_values("fecha", ascending=False), hide_index=True, use_container_width=True, height=250)