import streamlit as st
import sqlite3
import pandas as pd
import altair as alt

# Conectar ao banco de dados
conn = sqlite3.connect('sensores.db')
df = pd.read_sql_query('SELECT * FROM leituras', conn)

st.title('Dashboard do Sistema de Irrigação Inteligente')

if df.empty:
    st.warning('Nenhum dado encontrado no banco. Execute o script de coleta ou insira dados de exemplo.')
else:
    st.subheader('Tabela de Leituras')
    st.dataframe(df)

    st.subheader('Gráfico de Umidade do Solo')
    chart_umidade = alt.Chart(df).mark_line(point=True).encode(
        x='id',
        y='umidade',
        tooltip=['id', 'umidade']
    ).properties(width=600)
    st.altair_chart(chart_umidade, use_container_width=True)

    st.subheader('Gráfico de pH (LDR)')
    chart_ph = alt.Chart(df).mark_line(point=True, color='orange').encode(
        x='id',
        y='ph',
        tooltip=['id', 'ph']
    ).properties(width=600)
    st.altair_chart(chart_ph, use_container_width=True)

    st.subheader('Presença de Nutrientes (Fósforo e Potássio)')
    st.bar_chart(df[['fosforo', 'potassio']])

    st.subheader('Status da Bomba de Irrigação')
    st.line_chart(df['irrigacao'])

st.info('Atualize os dados rodando o script de coleta ou inserindo novos registros no banco.') 