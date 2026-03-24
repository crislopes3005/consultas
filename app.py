import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# CONFIG
# =========================
COR_PRINCIPAL = "#002E73"

st.set_page_config(layout="wide")

# =========================
# UPLOAD
# =========================
st.sidebar.header("📂 Base de dados")

arquivo_upload = st.sidebar.file_uploader(
    "Envie um arquivo Excel",
    type=["xlsx"]
)

if arquivo_upload:
    df_comentarios = pd.read_excel(arquivo_upload, sheet_name='comentarios')
    df_paragrafos = pd.read_excel(arquivo_upload, sheet_name='paragrafos')
    df_pordia = pd.read_excel(arquivo_upload, sheet_name='pordia')
    df_paisestado = pd.read_excel(arquivo_upload, sheet_name='paisestado')
    df_dispositivo = pd.read_excel(arquivo_upload, sheet_name='dispositivo')
else:
    st.warning("Envie um arquivo para continuar")
    st.stop()

# =========================
# TRATAMENTO DE DATAS
# =========================
df_pordia['Date'] = pd.to_datetime(df_pordia['Date'], dayfirst=True)

# =========================
# KPIs (mantidos)
# =========================
st.divider()

col1, col2 = st.columns(2)

col1.metric("Visitantes únicos", df_pordia['Users'].sum())
col2.metric("Visualizações", df_pordia['Views'].sum())

st.divider()

# =========================
# 🔥 GRÁFICO CORRIGIDO
# =========================
st.subheader("Visitantes e visualizações por dia")

# 🔹 Agregar por dia (garante consistência)
df_agg = df_pordia.groupby('Date', as_index=False)[['Users', 'Views']].sum()

# 🔹 Ordenar corretamente
df_agg = df_agg.sort_values('Date')

# 🔹 Transformar formato
df_long = df_agg.melt(
    id_vars='Date',
    value_vars=['Users', 'Views'],
    var_name='Métrica',
    value_name='Valor'
)

# 🔹 Traduzir nomes
df_long['Métrica'] = df_long['Métrica'].replace({
    'Users': 'Visitantes',
    'Views': 'Visualizações'
})

# 🔹 Criar gráfico limpo
fig = px.line(
    df_long,
    x='Date',
    y='Valor',
    color='Métrica',
    markers=True,
    color_discrete_sequence=[COR_PRINCIPAL, "#5A7BBF"]
)

# 🔹 Melhorar layout
fig.update_layout(
    xaxis_title="Data",
    yaxis_title="Quantidade",
    legend_title="Métrica",
    hovermode="x unified"
)

# 🔹 Remover poluição de rótulos (importante!)
fig.update_traces(mode='lines+markers')

st.plotly_chart(fig, use_container_width=True)
