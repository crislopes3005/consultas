import streamlit as st
import pandas as pd
import plotly.express as px

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
    df_comentarios = pd.read_excel('consulta.xlsx', sheet_name='comentarios')
    df_paragrafos = pd.read_excel('consulta.xlsx', sheet_name='paragrafos')
    df_pordia = pd.read_excel('consulta.xlsx', sheet_name='pordia')
    df_paisestado = pd.read_excel('consulta.xlsx', sheet_name='paisestado')
    df_dispositivo = pd.read_excel('consulta.xlsx', sheet_name='dispositivo')

# =========================
# TRATAMENTOS
# =========================

# Datas (remover hora)
df_comentarios['data_publicacao'] = pd.to_datetime(
    df_comentarios['data_publicacao'],
    format='%d/%m/%Y %H:%M',
    errors='coerce'
).dt.date
df_pordia['Date'] = pd.to_datetime(df_pordia['Date']).dt.date

# Estados com primeira maiúscula
df_paisestado['Region'] = df_paisestado['Region'].str.title()

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

avg_min = df_pordia['Avg Session Duration (Sec)'].mean() / 60
col7.metric("Duração média (min)", f"{avg_min:.2f}")

col8.metric("Países distintos", df_paisestado['Country'].nunique())

st.divider()

# =========================
# GRÁFICOS
# =========================

# 🔹 Comentários por parágrafo
st.subheader("Comentários por parágrafo")

fig1 = px.bar(
    df_paragrafos.sort_values('quantidade_comentarios'),
    y="descricao",
    x="quantidade_comentarios",
    orientation="h",
    color_discrete_sequence=["#002E73"]
)

st.plotly_chart(fig1, use_container_width=True)

# 🔹 Comentários por dia
st.subheader("Comentários por dia")

comentarios_dia = df_comentarios.groupby('data_publicacao')['id'].count().reset_index()

fig2 = px.line(
    comentarios_dia,
    x='data_publicacao',
    y='id',
    labels={
        "data_publicacao": "Data",
        "id": "Comentários"
    }
)

st.plotly_chart(fig2, use_container_width=True)

# 🔹 Visitantes e visualizações por dia
st.subheader("Visitantes e visualizações por dia")

df_long = df_pordia.melt(
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
    color='Métrica'
)

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
    labels={
        "Sessions": "Sessões",
        "Region": "Estado"
    }
)

st.plotly_chart(fig4, use_container_width=True)

# 🔹 Dispositivos
st.subheader("Acesso por dispositivo")

fig5 = px.pie(
    df_dispositivo,
    names='Device Type',
    values='Sessions'
)

st.plotly_chart(fig5, use_container_width=True)
