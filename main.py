import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
from matplotlib.ticker import MaxNLocator

warnings.simplefilter(action='ignore', category=FutureWarning)

st.set_page_config(
    page_title="Dashboard de Voos no Brasil",
    page_icon="✈️",
    layout="wide"
)

# --- FUNÇÃO DE CARREGAMENTO DE DADOS (COM CACHE) ---
# O decorator @st.cache_data garante que os dados sejam carregados apenas uma vez.
@st.cache_data
def carregar_dados():
    arquivos = {
        2022: 'dataset/merge_2022.csv',
        2023: 'dataset/merge_2023.csv',
        2024: 'dataset/merge_2024.csv',
        2025: 'dataset/merge_2025.csv'
    }
    lista_de_dfs = []
    for ano, caminho in arquivos.items():
        try:
            df_temp = pd.read_csv(caminho, sep=';', encoding='utf-8', dtype={'Código Justificativa': str})
            df_temp['ano'] = ano
            lista_de_dfs.append(df_temp)
        except FileNotFoundError:
            pass
    
    if not lista_de_dfs:
        st.error("Nenhum arquivo de dados de voos (merge_*.csv) foi encontrado na pasta 'dataset/'. O dashboard não pode continuar.")
        st.stop()
        
    df_completo = pd.concat(lista_de_dfs, ignore_index=True)
    
    try:
        df_aeroportos = pd.read_csv('dataset/airport-codes.csv', sep=';', encoding='latin1')
        df_nomes_aeroportos = df_aeroportos[df_aeroportos['iso_country'] == 'BR'][['ident', 'name']].copy()
    except FileNotFoundError:
        st.warning("Arquivo 'dataset/airport-codes.csv' não encontrado. Os nomes dos aeroportos serão exibidos como códigos ICAO.")
        df_nomes_aeroportos = pd.DataFrame(columns=['ident', 'name'])
    except Exception as e:
        st.error(f"Erro ao ler o arquivo 'airport-codes.csv': {e}")
        df_nomes_aeroportos = pd.DataFrame(columns=['ident', 'name'])

    try:
        df_airlines = pd.read_csv('dataset/airlines-codes.csv', sep=';', encoding='latin1')
        df_airlines.rename(columns={'Nome': 'Nome', 'Sigla': 'Sigla'}, inplace=True)
    except FileNotFoundError:
        st.warning("Arquivo 'dataset/airlines-codes.csv' não encontrado. Nomes das companhias serão exibidos como códigos ICAO.")
        df_airlines = pd.DataFrame(columns=['Sigla', 'Nome'])
    except Exception as e:
        st.error(f"Erro ao ler o arquivo 'airlines-codes.csv': {e}")
        df_airlines = pd.DataFrame(columns=['Sigla', 'Nome'])

    df_realizados = df_completo[df_completo['Situação Voo'] == 'REALIZADO'].copy()
    
    # --- MERGE PARA ADICIONAR NOMES DOS AEROPORTOS ---
    if not df_nomes_aeroportos.empty:
        df_realizados = pd.merge(df_realizados, df_nomes_aeroportos, left_on='ICAO Aeródromo Origem', right_on='ident', how='left')
        df_realizados.rename(columns={'name': 'nome_aeroporto_origem'}, inplace=True)
        df_realizados['nome_aeroporto_origem'].fillna(df_realizados['ICAO Aeródromo Origem'], inplace=True)
    else:
        df_realizados['nome_aeroporto_origem'] = df_realizados['ICAO Aeródromo Origem']

    # --- MERGE PARA ADICIONAR NOMES DAS COMPANHIAS AÉREAS ---
    if not df_airlines.empty:
        df_realizados = pd.merge(df_realizados, df_airlines[['Sigla', 'Nome']], left_on='ICAO Empresa Aérea', right_on='Sigla', how='left')
        df_realizados['Nome'].fillna(df_realizados['ICAO Empresa Aérea'], inplace=True)
    else:
        df_realizados['Nome'] = df_realizados['ICAO Empresa Aérea']

    colunas_de_data = ['Partida Prevista', 'Partida Real', 'Chegada Prevista', 'Chegada Real']
    for coluna in colunas_de_data:
        df_realizados[coluna] = pd.to_datetime(df_realizados[coluna], format='%d/%m/%Y %H:%M', errors='coerce')
    df_realizados.dropna(subset=colunas_de_data, inplace=True)
    
    df_realizados['atraso_partida_min'] = (df_realizados['Partida Real'] - df_realizados['Partida Prevista']).dt.total_seconds() / 60
    df_realizados['voo_atrasado'] = (df_realizados['atraso_partida_min'] > 15).astype(int)
    
    df_realizados['dia_da_semana'] = df_realizados['Partida Prevista'].dt.day_name()
    bins = [-1, 6, 12, 18, 24]
    labels = ['Madrugada', 'Manhã', 'Tarde', 'Noite']
    df_realizados['periodo_dia'] = pd.cut(df_realizados['Partida Prevista'].dt.hour, bins=bins, labels=labels, right=False)
    
    return df_realizados

df_realizados = carregar_dados()

st.title("✈️ Dashboard de Atrasos de Voos no Brasil")

st.sidebar.header("Filtros")
anos_disponiveis = sorted(df_realizados['ano'].unique())
anos_selecionados = st.sidebar.multiselect(
    "Selecione o Ano", options=anos_disponiveis, default=anos_disponiveis
)
if not anos_selecionados:
    st.sidebar.warning("Por favor, selecione pelo menos um ano.")
    st.stop()
df_filtrado = df_realizados[df_realizados['ano'].isin(anos_selecionados)]

st.header("Visão Geral do Período Selecionado")
total_voos = df_filtrado.shape[0]
total_atrasos = df_filtrado['voo_atrasado'].sum()
percentual_atrasos = (total_atrasos / total_voos) * 100 if total_voos > 0 else 0
col1, col2, col3 = st.columns(3)
col1.metric("Total de Voos Realizados", f"{total_voos:,}".replace(",", "."))
col2.metric("Atrasos na Partida (>15 min)", f"{total_atrasos:,}".replace(",", "."))
col3.metric("Percentual de Atrasos", f"{percentual_atrasos:.2f}%")

st.divider()

st.header("Análises Detalhadas")

# Pergunta: Aeroporto com mais atrasos no geral?
st.subheader("🏆 Top 10 Aeroportos com Mais Atrasos na Partida")
atrasos_por_aeroporto = df_filtrado.groupby('nome_aeroporto_origem')['voo_atrasado'].sum().sort_values(ascending=False).head(10)
if not atrasos_por_aeroporto.empty:
    fig_aeroporto, ax_aeroporto = plt.subplots(figsize=(10, 6))
    colors = ['#88c7dc' if (x < max(atrasos_por_aeroporto.values)) else '#006699' for x in atrasos_por_aeroporto.values]
    sns.barplot(x=atrasos_por_aeroporto.values, y=atrasos_por_aeroporto.index, ax=ax_aeroporto, orient='h', palette=colors)
    for index, value in enumerate(atrasos_por_aeroporto.values):
        ax_aeroporto.text(value, index, f' {value:,.0f}'.replace(",", "."), color='black', ha="left", va="center", fontsize=10)
    ax_aeroporto.set_title('Top 10 Aeroportos por Volume Total de Atrasos (anos selecionados)')
    ax_aeroporto.set_xticks([])
    sns.despine(left=True, bottom=True, right=True)
    ax_aeroporto.set_xlabel('')
    ax_aeroporto.set_ylabel('Aeroporto')
    st.pyplot(fig_aeroporto)
else:
    st.warning("Não há dados de atraso de aeroportos para os filtros selecionados.")

st.subheader("✈️ Comparativo Anual de Atrasos (Top 10 Companhias)")
if len(anos_selecionados) > 1:
    top_10_nomes = df_filtrado.groupby('Nome')['voo_atrasado'].sum().nlargest(10).index
    
    df_para_plot = df_filtrado[df_filtrado['Nome'].isin(top_10_nomes)]
    atrasos_companhia_ano = df_para_plot.groupby(['ano', 'Nome'])['voo_atrasado'].sum().reset_index()
    
    if not atrasos_companhia_ano.empty:
        fig_companhia, ax_companhia = plt.subplots(figsize=(12, 7)) 
        sns.barplot(data=atrasos_companhia_ano, x='Nome', y='voo_atrasado', hue='ano', ax=ax_companhia, palette='viridis')
        
        ax_companhia.set_title('Comparativo de Atrasos na Partida por Ano (Top 10 Companhias)')
        ax_companhia.set_xlabel('Companhia Aérea')
        ax_companhia.set_ylabel('Número Total de Voos Atrasados')
        ax_companhia.grid(axis='y', linestyle='--', linewidth=0.7)
        
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        st.pyplot(fig_companhia)
    else:
        st.info("Não há dados de atrasos de companhias para os anos selecionados.")
else:
    st.info("Selecione mais de um ano no filtro para visualizar a comparação entre companhias aéreas.")

st.subheader("📅 Atrasos por Dia da Semana e Período do Dia")
col_dia, col_periodo = st.columns(2)

with col_dia:
    st.markdown("##### Por Dia da Semana")
    atrasos_por_dia = df_filtrado.groupby('dia_da_semana')['voo_atrasado'].sum()
    dias_ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    atrasos_por_dia = atrasos_por_dia.reindex(dias_ordem).fillna(0)

    if not atrasos_por_dia.empty:
        fig_dia, ax_dia = plt.subplots()
        sns.barplot(x=atrasos_por_dia.index, y=atrasos_por_dia.values, ax=ax_dia, palette='magma')
        ax_dia.set_title('Total de Atrasos por Dia da Semana')
        ax_dia.set_xlabel('Dia da Semana')
        ax_dia.set_ylabel('Número de Voos Atrasados')
        ax_dia.set_xticklabels(['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'])
        plt.xticks(rotation=45)
        st.pyplot(fig_dia)

with col_periodo:
    st.markdown("##### Por Período do Dia")
    atrasos_por_periodo = df_filtrado.groupby('periodo_dia')['voo_atrasado'].sum()
    periodos_ordem = ['Madrugada', 'Manhã', 'Tarde', 'Noite']
    atrasos_por_periodo = atrasos_por_periodo.reindex(periodos_ordem).fillna(0)

    if not atrasos_por_periodo.empty:
        fig_periodo, ax_periodo = plt.subplots()
        sns.barplot(x=atrasos_por_periodo.index, y=atrasos_por_periodo.values, ax=ax_periodo, palette='plasma')
        ax_periodo.set_title('Total de Atrasos por Período do Dia')
        ax_periodo.set_xlabel('Período')
        ax_periodo.set_ylabel('Número de Voos Atrasados')
        plt.xticks(rotation=45)
        st.pyplot(fig_periodo)

st.divider()

st.header("📈📉 Tendências de Atrasos nos Últimos 3 Anos (2022-2024)")
anos_necessarios_tendencia = [2022, 2023, 2024]
anos_presentes_no_filtro = df_filtrado['ano'].unique()
if all(ano in anos_presentes_no_filtro for ano in anos_necessarios_tendencia):
    
    df_pivot = df_filtrado.pivot_table(
        index='nome_aeroporto_origem', columns='ano', values='voo_atrasado', aggfunc='sum'
    ).fillna(0)
    for ano in anos_necessarios_tendencia:
        if ano not in df_pivot.columns:
            df_pivot[ano] = 0

    condicao_aumento = (df_pivot[2023] >= df_pivot[2022]) & (df_pivot[2024] > df_pivot[2023])
    condicao_reducao = (df_pivot[2023] <= df_pivot[2022]) & (df_pivot[2024] < df_pivot[2023])

    df_aumento = df_pivot[condicao_aumento].copy()
    df_reducao = df_pivot[condicao_reducao].copy()
    df_aumento['Variacao_Total'] = df_aumento[2024] - df_aumento[2022]
    df_reducao['Variacao_Total'] = df_reducao[2024] - df_reducao[2022]
    df_aumento.sort_values('Variacao_Total', ascending=False, inplace=True)
    df_reducao.sort_values('Variacao_Total', ascending=True, inplace=True)

    col_tend_aumento, col_tend_reducao = st.columns(2)
    with col_tend_aumento:
        st.subheader("Tendência de Aumento 📈")
        st.markdown("Aeroportos com aumento consistente de atrasos. O gráfico mostra o **aumento total** de 2022 para 2024.")
        if not df_aumento.empty:
            top_10_aumento = df_aumento.head(10)
            fig_aumento, ax_aumento = plt.subplots(figsize=(8, 5))
            sns.barplot(x=top_10_aumento['Variacao_Total'], y=top_10_aumento.index, ax=ax_aumento, palette='Reds_r', orient='h')
            ax_aumento.set_title('Top 10 Piores Tendências')
            ax_aumento.set_xlabel('Nº de Atrasos a Mais em 2024 vs 2022')
            ax_aumento.set_ylabel('Aeroporto')
            st.pyplot(fig_aumento)
            with st.expander("Ver dados detalhados da tendência de aumento"):
                st.dataframe(df_aumento)
        else:
            st.info("Nenhum aeroporto apresentou tendência consistente de aumento.")
    with col_tend_reducao:
        st.subheader("Tendência de Redução 📉")
        st.markdown("Aeroportos com redução consistente de atrasos. O gráfico mostra a **redução total** de 2022 para 2024.")
        if not df_reducao.empty:
            top_10_reducao = df_reducao.head(10).copy()
            top_10_reducao['Variacao_Absoluta'] = top_10_reducao['Variacao_Total'] * -1
            fig_reducao, ax_reducao = plt.subplots(figsize=(8, 5))
            sns.barplot(x=top_10_reducao['Variacao_Absoluta'], y=top_10_reducao.index, ax=ax_reducao, palette='Greens_r', orient='h')
            ax_reducao.set_title('Top 10 Melhores Tendências')
            ax_reducao.set_xlabel('Nº de Atrasos a Menos em 2024 vs 2022')
            ax_reducao.set_ylabel('')
            st.pyplot(fig_reducao)
            with st.expander("Ver dados detalhados da tendência de redução"):
                st.dataframe(df_reducao)
        else:
            st.info("Nenhum aeroporto apresentou tendência consistente de redução.")
else:
    st.info("Para visualizar a análise de tendência de 3 anos, os dados de 2022, 2023 e 2024 devem estar disponíveis e selecionados no filtro.")