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
# TRATAMENTOS
# =========================

# Datas
df_comentarios['data_publicacao'] = pd.to_datetime(
    df_comentarios['data_publicacao'],
    format='%d/%m/%Y %H:%M',
    errors='coerce'
)

df_comentarios['data'] = df_comentarios['data_publicacao'].dt.date
df_pordia['Date'] = pd.to_datetime(df_pordia['Date'], dayfirst=True)

# Descrição curta
df_paragrafos['descricao_curta'] = df_paragrafos['descricao'].apply(
    lambda x: x[:30] + "..." if isinstance(x, str) and len(x) > 30 else x
)

# Estados
df_paisestado['Region'] = df_paisestado['Region'].str.title()

# Duração (limpeza)
df_pordia['Avg Session Duration (Sec)'] = pd.to_numeric(
    df_pordia['Avg Session Duration (Sec)'],
    errors='coerce'
)

df_duracao = df_pordia[
    (df_pordia['Avg Session Duration (Sec)'] > 0) &
    (df_pordia['Avg Session Duration (Sec)'] < 3600)
]

# =========================
# KPIs
# =========================
st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("Comentários", df_comentarios['id'].count())
col2.metric("Proponentes distintos", df_comentarios['autor/id'].nunique())
col3.metric("Parágrafos", df_paragrafos['id_proposta'].nunique())

st.divider()

col4, col5, col6, col7, col8 = st.columns(5)

col4.metric("Visitantes únicos", df_pordia['Users'].sum())
col5.metric("Visualizações", df_pordia['Views'].sum())
col6.metric("Taxa de rejeição", f"{df_pordia['Bounce Rate'].mean():.2%}")

avg_sec = df_duracao['Avg Session Duration (Sec)'].median()
col7.metric("Duração média", f"{int(avg_sec//60)}m {int(avg_sec%60)}s")

col8.metric("Países distintos", df_paisestado['Country'].nunique())

st.divider()

# =========================
# GRÁFICOS
# =========================

# 🔹 Comentários por parágrafo
st.subheader("Comentários por parágrafo")

fig1 = px.bar(
    df_paragrafos.sort_values('quantidade_comentarios'),
    y="descricao_curta",
    x="quantidade_comentarios",
    orientation="h",
    text="quantidade_comentarios",
    color_discrete_sequence=[COR_PRINCIPAL]
)

fig1.update_traces(textposition="outside")
st.plotly_chart(fig1, use_container_width=True)

# 🔹 Comentários por dia
st.subheader("Comentários por dia")

comentarios_dia = df_comentarios.groupby('data')['id'].count().reset_index()

fig2 = px.line(
    comentarios_dia.sort_values('data'),
    x='data',
    y='id',
    markers=True,
    text='id',
    labels={"data": "Data", "id": "Comentários"},
    color_discrete_sequence=[COR_PRINCIPAL]
)

fig2.update_traces(textposition="top center")
st.plotly_chart(fig2, use_container_width=True)

# 🔹 Visitantes e visualizações (CORRIGIDO)
st.subheader("Visitantes e visualizações por dia")

df_agg = df_pordia.groupby('Date', as_index=False)[['Users', 'Views']].sum()
df_agg = df_agg.sort_values('Date')

df_long = df_agg.melt(
    id_vars='Date',
    value_vars=['Users', 'Views'],
    var_name='Métrica',
    value_name='Valor'
)

df_long['Métrica'] = df_long['Métrica'].replace({
    'Users': 'Visitantes',
    'Views': 'Visualizações'
})

fig3 = px.line(
    df_long,
    x='Date',
    y='Valor',
    color='Métrica',
    markers=True,
    color_discrete_sequence=[COR_PRINCIPAL, "#5A7BBF"]
)

fig3.update_layout(
    xaxis_title="Data",
    yaxis_title="Quantidade",
    legend_title="Métrica",
    hovermode="x unified"
)
fig3.update_traces(textposition="outside")

st.plotly_chart(fig3, use_container_width=True)

# 🔹 Top 10 estados
st.subheader("Top 10 estados com mais visitas")

df_estados = df_paisestado[df_paisestado['Country'].str.lower() == 'brazil']
df_estados = df_estados.groupby('Region')['Sessions'].sum().reset_index()
df_estados = df_estados.sort_values('Sessions', ascending=True).tail(10)

fig4 = px.bar(
    df_estados,
    x='Sessions',
    y='Region',
    orientation='h',
    text='Sessions',
    color_discrete_sequence=[COR_PRINCIPAL]
)

fig4.update_traces(textposition="outside")
st.plotly_chart(fig4, use_container_width=True)

# 🔹 Dispositivos
st.subheader("Acesso por dispositivo")

fig5 = px.pie(
    df_dispositivo,
    names='Device Type',
    values='Sessions',
    color_discrete_sequence=[COR_PRINCIPAL, "#5A7BBF", "#A5B8E1"]
)

fig5.update_traces(textinfo='percent+label')
st.plotly_chart(fig5, use_container_width=True)
