import streamlit as st
import pandas as pd
import plotly.express as px
from transform import data_final
import base64
from pathlib import Path



st.set_page_config(layout="wide")
def get_image_as_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

logo_path = Path(__file__).parent / "IA.png"
logo_base64 = get_image_as_base64(logo_path)


COR_PRIMARIA = "#B0B0B0"  
COR_ACENTO = "#F26522"   
CORES_GRAFICO_UF = [COR_PRIMARIA, COR_ACENTO, "#00A99D", "#666666", "#99CCFF", "#FFCC99"]


def load_css():
    css = f"""
    <style>
        /* Animação de fade-in */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Habilita a rolagem suave */
        html {{
            scroll-behavior: smooth;
        }}

        /* Banner do topo com fundo branco e texto preto */
        .hero-banner {{
            padding: 5rem 2rem;
            background-image: linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.9)), url(data:image/png;base64,{logo_base64});
            background-size: cover;
            background-position: center;
            color: #333333;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 2rem;
            border: 1px solid #ddd; /* Adiciona uma borda sutil */
        }}
        
        /* Botão de rolagem (mantém o design) */
        .scroll-button {{
            display: inline-block;
            margin-top: 2rem;
            padding: 0.8rem 1.5rem;
            background-color: {COR_ACENTO};
            color: white;
            text-decoration: none;
            font-weight: bold;
            border-radius: 50px;
            transition: transform 0.3s ease, background-color 0.3s ease;
        }}
        .scroll-button:hover {{
            transform: scale(1.05);
            background-color: #e05a1a;
            color: white;
        }}

        /* Aplica animação aos cabeçalhos dos gráficos */
        .st-emotion-cache-10trblm {{
            animation: fadeIn 1s ease-out;
        }}

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

load_css()


@st.cache_data
def carregar_e_preparar_dados():
    df = data_final.copy()
    if 'ds_mun' not in df.columns:
        if 'ds_mun_ia' in df.columns:
            df = df.rename(columns={'ds_mun_ia': 'ds_mun'})
        elif 'ds_mun_dtb' in df.columns:
            df = df.rename(columns={'ds_mun_dtb': 'ds_mun'})

    ideb_cols = [col for col in df.columns if col.startswith('ideb_')]
    anos_ideb = sorted([int(col.replace('ideb_', '')) for col in ideb_cols])

    ideb_media_mun = df.groupby('ds_mun')[ideb_cols].mean().reset_index()
    ideb_long_mun = ideb_media_mun.melt(
        id_vars='ds_mun', value_vars=ideb_cols, var_name='Ano', value_name='IDEB'
    )
    ideb_long_mun['Ano'] = ideb_long_mun['Ano'].str.replace('ideb_', '').astype(int)
    ideb_long_mun = ideb_long_mun.dropna(subset=['IDEB'])

    ideb_media_uf = df.groupby('ds_uf')[ideb_cols].mean().reset_index()
    ideb_long_uf = ideb_media_uf.melt(
        id_vars='ds_uf', value_vars=ideb_cols, var_name='Ano', value_name='IDEB'
    )
    ideb_long_uf['Ano'] = ideb_long_uf['Ano'].str.replace('ideb_', '').astype(int)
    ideb_long_uf = ideb_long_uf.sort_values(by=['ds_uf', 'Ano'])
    ideb_long_uf = ideb_long_uf.dropna(subset=['IDEB'])

    return ideb_long_mun, ideb_long_uf, anos_ideb

df_mun, df_uf, anos_ideb = carregar_e_preparar_dados()


if logo_base64:
    st.markdown(
        """
        <div class="hero-banner">
            <h1>Instituto Alpargatas: Democratizando o Acesso à Informação e o Impacto Social</h1>
            <p>Este projeto tem como objetivo principal tornar o impacto social do Instituto Alpargatas mais claro e acessível a um público amplo. 
            Para isso, estamos desenvolvendo um portal web interativo que irá evidenciar visualmente os resultados das iniciativas do Instituto. 
            O coração deste projeto é a criação e o cálculo de um Índice de Igualdade de Educação. 
            O portal permitirá aos usuários visualizar e comparar o crescimento desse índice em áreas de atuação do Instituto, utilizando dados operacionais não sensíveis e promovendo a democratização do acesso à informação.
            A inovação principal do projeto reside na estratégia de democratização do acesso à informação. A ideia é integrar um QR Code em produtos da Alpargatas (como Havaianas), direcionando os consumidores diretamente para o portal.</p>
            <a href="#analises" class="scroll-button">Ver Análises ↓</a>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.error("Arquivo 'IA.png' não encontrado. Por favor, coloque a imagem na mesma pasta do aplicativo.")
    st.title("Instituto Alpargatas: Democratizando o Acesso à Informação e o Impacto Social")


st.markdown("<div id='analises'></div>", unsafe_allow_html=True)

st.header("Evolução do IDEB por Município")
lista_municipios = sorted(df_mun['ds_mun'].unique())
municipio_selecionado = st.selectbox(
    "Selecione um município para visualizar:",
    options=lista_municipios,
    index=0
)

if municipio_selecionado:
    dados_filtrados = df_mun[df_mun['ds_mun'] == municipio_selecionado]
    fig_mun = px.line(
        dados_filtrados,
        x='Ano',
        y='IDEB',
        markers=True,
        title=f'Evolução do IDEB - {municipio_selecionado}',
        labels={'Ano': 'Ano', 'IDEB': 'IDEB Médio'}
    )

    fig_mun.update_traces(line=dict(color=COR_PRIMARIA))

    fig_mun.add_vrect(
        x0="2019.5", x1=str(max(anos_ideb) + 0.5),
        fillcolor=COR_ACENTO, opacity=0.15, layer="below", line_width=0,
        annotation_text="Período de Atuação do Instituto",
        annotation_position="top left"
    )
    fig_mun.update_layout(
        xaxis=dict(tickmode='array', tickvals=anos_ideb),
        yaxis_title="IDEB Médio",
        xaxis_title="Ano",
        hovermode="x unified"
    )
    st.plotly_chart(fig_mun, use_container_width=True)


st.header("Evolução Comparativa do IDEB por UF")
lista_ufs = sorted(df_uf['ds_uf'].unique())
ufs_selecionadas = st.multiselect(
    "Selecione as UFs para comparar:",
    options=lista_ufs,
    default=lista_ufs
)

if ufs_selecionadas:
    dados_uf_filtrados = df_uf[df_uf['ds_uf'].isin(ufs_selecionadas)]
    fig_uf = px.line(
        dados_uf_filtrados,
        x='Ano',
        y='IDEB',
        color='ds_uf',
        markers=True,
        title='Evolução do IDEB Médio por UF',
        labels={'Ano': 'Ano', 'IDEB': 'IDEB Médio', 'ds_uf': 'UF'},
        color_discrete_sequence=CORES_GRAFICO_UF
    )
    fig_uf.add_vrect(
        x0="2019.5", x1=str(max(anos_ideb) + 0.5),
        fillcolor=COR_ACENTO, opacity=0.15, layer="below", line_width=0
    )
    fig_uf.update_layout(
        xaxis=dict(tickmode='array', tickvals=anos_ideb),
        yaxis_title="IDEB Médio",
        xaxis_title="Ano",
        legend_title_text='UF',
        hovermode="x unified"
    )
    st.plotly_chart(fig_uf, use_container_width=True)