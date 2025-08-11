import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="LOA Rifaina - Análise Orçamentária", 
    layout="wide",
    initial_sidebar_state="expanded"
)
hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Função para carregar e processar dados
@st.cache_data
def load_data():
    """Carrega e processa os dados da LOA"""
    
    # Carregar dados de receitas orçadas (file1)
    try:
        receitas_orcadas = pd.read_csv("download-123842.557.csv", sep=';', encoding='utf-8')
    except:
        receitas_orcadas = pd.read_csv("download-123842.557.csv", sep=';', encoding='latin-1')
    
    # Carregar dados de estrutura de receitas (file2)  
    try:
        estrutura_receitas = pd.read_csv("download-123701.452.csv", sep=';', encoding='utf-8')
    except:
        estrutura_receitas = pd.read_csv("download-123701.452.csv", sep=';', encoding='latin-1')
    
    return receitas_orcadas, estrutura_receitas

def format_currency(value):
    """Formata valores em moeda brasileira"""
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def create_treemap_data(df, codigo_col, nome_col, valor_col, nivel_max=4):
    """Cria dados para treemap hierárquico"""
    treemap_data = []
    
    # Agrupar por diferentes níveis hierárquicos
    for nivel in range(1, nivel_max + 1):
        df_nivel = df.copy()
        df_nivel['codigo_truncado'] = df_nivel[codigo_col].str[:4 + (nivel-1)*3]
        df_nivel['nome_truncado'] = df_nivel[nome_col]
        
        grouped = df_nivel.groupby(['codigo_truncado', 'nome_truncado'])[valor_col].sum().reset_index()
        grouped['nivel'] = nivel
        treemap_data.append(grouped)
    
    return pd.concat(treemap_data, ignore_index=True)

# Carregar dados
st.title("📊 Análise da LOA - Município de Rifaina")
st.markdown("**Lei Orçamentária Anual - Dashboard Interativo**")

with st.spinner("Carregando dados da LOA..."):
    receitas_orcadas, estrutura_receitas = load_data()

# Verificar se os dados foram carregados corretamente
if receitas_orcadas.empty or estrutura_receitas.empty:
    st.error("Erro ao carregar os dados. Verifique os arquivos CSV.")
    st.stop()

# Sidebar com informações gerais
st.sidebar.header("📋 Informações Gerais")
st.sidebar.metric("Total de Receitas Previstas", len(receitas_orcadas))
st.sidebar.metric("Categorias de Receita", len(estrutura_receitas))

# Processamento de dados para análise
receitas_orcadas['TOTOR'] = pd.to_numeric(receitas_orcadas['TOTOR'], errors='coerce').fillna(0)
total_orcamento = receitas_orcadas['TOTOR'].sum()

# Calcular categorias principais globalmente
receitas_tributarias = receitas_orcadas[
    receitas_orcadas['CODRE'].str.startswith(('1112', '1113', '1114', '1121', '1122'))
]['TOTOR'].sum()

transferencias = receitas_orcadas[
    receitas_orcadas['CODRE'].str.startswith(('1711', '1712', '1713', '1714', '1716', '1721', '1722', '1723', '1724', '1751'))
]['TOTOR'].sum()

outras_receitas = total_orcamento - receitas_tributarias - transferencias

st.sidebar.metric("Orçamento Total", format_currency(total_orcamento))

# Menu de navegação
opcao = st.sidebar.selectbox(
    "📊 Escolha a análise:",
    ["Visão Geral", "Análise por Categoria", "Receitas Tributárias", "Transferências", "Detalhamento"]
)

# CSS personalizado
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
}
.big-font {
    font-size: 20px !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# VISÃO GERAL
# ==============================================================================
if opcao == "Visão Geral":
    st.header("📈 Visão Geral do Orçamento")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Orçamento Total",
            format_currency(total_orcamento),
            help="Valor total previsto para todas as receitas"
        )
    
    with col2:
        st.metric(
            "🏛️ Receitas Tributárias",
            format_currency(receitas_tributarias),
            f"{(receitas_tributarias/total_orcamento*100):.1f}% do total"
        )
    
    with col3:
        st.metric(
            "🔄 Transferências",
            format_currency(transferencias),
            f"{(transferencias/total_orcamento*100):.1f}% do total"
        )
    
    with col4:
        st.metric(
            "📋 Outras Receitas",
            format_currency(outras_receitas),
            f"{(outras_receitas/total_orcamento*100):.1f}% do total"
        )
    
    st.divider()
    
    # Gráficos da visão geral
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de pizza - Composição do orçamento
        fig_pizza = go.Figure(data=[go.Pie(
            labels=['Receitas Tributárias', 'Transferências', 'Outras Receitas'],
            values=[receitas_tributarias, transferencias, outras_receitas],
            hole=0.4,
            marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c']
        )])
        
        fig_pizza.update_layout(
            title="Composição do Orçamento por Categoria",
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig_pizza, use_container_width=True)
    
    with col2:
        # Top 10 maiores receitas
        top_receitas = receitas_orcadas.nlargest(10, 'TOTOR')
        
        fig_bar = px.bar(
            top_receitas,
            x='TOTOR',
            y='NOME',
            orientation='h',
            title="Top 10 Maiores Receitas Previstas",
            labels={'TOTOR': 'Valor (R$)', 'NOME': 'Receita'}
        )
        
        fig_bar.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

# ==============================================================================
# ANÁLISE POR CATEGORIA
# ==============================================================================
elif opcao == "Análise por Categoria":
    st.header("📊 Análise por Categoria de Receita")
    
    # Agrupar receitas por nível hierárquico
    receitas_orcadas['nivel_1'] = receitas_orcadas['CODRE'].str[:4]
    receitas_orcadas['nivel_2'] = receitas_orcadas['CODRE'].str[:7]
    
    # Análise por nível 1
    nivel1_agrupado = receitas_orcadas.groupby('nivel_1')['TOTOR'].sum().sort_values(ascending=False)
    
    # Mapear códigos para nomes mais legíveis
    codigo_nomes = {
        '1112': 'Impostos sobre Patrimônio',
        '1113': 'Impostos sobre Renda',
        '1114': 'Impostos sobre Serviços',
        '1121': 'Taxas pelo Poder de Polícia',
        '1122': 'Taxas pelos Serviços',
        '1311': 'Exploração do Patrimônio',
        '1321': 'Remuneração de Depósitos',
        '1611': 'Serviços Administrativos',
        '1711': 'Transferências da União',
        '1712': 'Transferências da União - Outras',
        '1713': 'Transferências da União - SUS',
        '1714': 'Transferências da União - Educação',
        '1716': 'Transferências da União - Assistência',
        '1719': 'Outras Transferências da União',
        '1721': 'Transferências do Estado',
        '1722': 'Transferências do Estado - Outras',
        '1723': 'Transferências do Estado - SUS',
        '1724': 'Transferências do Estado - Educação',
        '1729': 'Outras Transferências do Estado',
        '1751': 'FUNDEB',
        '1911': 'Multas Administrativas',
        '1922': 'Restituições',
        '1999': 'Outras Receitas Correntes',
        '2213': 'Alienação de Bens'
    }
    
    # Treemap hierárquico
    fig_treemap = go.Figure(go.Treemap(
        labels=[codigo_nomes.get(codigo, f"Código {codigo}") for codigo in nivel1_agrupado.index],
        values=nivel1_agrupado.values,
        parents=[""] * len(nivel1_agrupado),
        textinfo="label+value+percent parent",
        hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Participação: %{percentParent}<extra></extra>'
    ))
    
    fig_treemap.update_layout(
        title="Distribuição Hierárquica das Receitas",
        height=500
    )
    
    st.plotly_chart(fig_treemap, use_container_width=True)
    
    # Tabela detalhada
    st.subheader("📋 Detalhamento por Categoria")
    
    categoria_detalhes = []
    for codigo, valor in nivel1_agrupado.items():
        nome = codigo_nomes.get(codigo, f"Código {codigo}")
        participacao = (valor / total_orcamento) * 100
        categoria_detalhes.append({
            'Código': codigo,
            'Categoria': nome,
            'Valor (R$)': format_currency(valor),
            'Participação (%)': f"{participacao:.2f}%"
        })
    
    df_categorias = pd.DataFrame(categoria_detalhes)
    st.dataframe(df_categorias, use_container_width=True)

# ==============================================================================
# RECEITAS TRIBUTÁRIAS
# ==============================================================================
elif opcao == "Receitas Tributárias":
    st.header("🏛️ Análise das Receitas Tributárias")
    
    # Filtrar apenas receitas tributárias
    tributarias = receitas_orcadas[
        receitas_orcadas['CODRE'].str.startswith(('1112', '1113', '1114', '1121', '1122'))
    ].copy()
    
    if not tributarias.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Análise por tipo de tributo
            tributos_tipo = {
                'IPTU': tributarias[tributarias['CODRE'].str.startswith('1112.5')]['TOTOR'].sum(),
                'ITBI': tributarias[tributarias['CODRE'].str.startswith('1112.53')]['TOTOR'].sum(),
                'IRRF': tributarias[tributarias['CODRE'].str.startswith('1113')]['TOTOR'].sum(),
                'ISSQN': tributarias[tributarias['CODRE'].str.startswith('1114')]['TOTOR'].sum(),
                'Taxas': tributarias[tributarias['CODRE'].str.startswith(('1121', '1122'))]['TOTOR'].sum()
            }
            
            fig_tributos = px.bar(
                x=list(tributos_tipo.keys()),
                y=list(tributos_tipo.values()),
                title="Receitas por Tipo de Tributo",
                labels={'x': 'Tipo de Tributo', 'y': 'Valor (R$)'}
            )
            
            st.plotly_chart(fig_tributos, use_container_width=True)
        
        with col2:
            # Distribuição IPTU
            iptu_detalhes = tributarias[tributarias['CODRE'].str.startswith('1112.5')]
            
            if not iptu_detalhes.empty:
                fig_iptu = px.pie(
                    iptu_detalhes,
                    values='TOTOR',
                    names='NOME',
                    title="Detalhamento do IPTU"
                )
                st.plotly_chart(fig_iptu, use_container_width=True)
        
        # Tabela de tributárias
        st.subheader("📋 Detalhamento das Receitas Tributárias")
        tributarias_display = tributarias[['NOME', 'TOTOR']].copy()
        tributarias_display['TOTOR'] = tributarias_display['TOTOR'].apply(format_currency)
        tributarias_display.columns = ['Descrição', 'Valor Previsto']
        
        st.dataframe(tributarias_display, use_container_width=True)
    else:
        st.warning("Nenhuma receita tributária encontrada nos dados.")

# ==============================================================================
# TRANSFERÊNCIAS
# ==============================================================================
elif opcao == "Transferências":
    st.header("🔄 Análise das Transferências")
    
    # Filtrar transferências
    transf = receitas_orcadas[
        receitas_orcadas['CODRE'].str.startswith(('1711', '1712', '1713', '1714', '1716', '1721', '1722', '1723', '1724', '1751'))
    ].copy()
    
    if not transf.empty:
        # Separar por origem
        transf_uniao = transf[transf['CODRE'].str.startswith(('1711', '1712', '1713', '1714', '1716', '1719'))]['TOTOR'].sum()
        transf_estado = transf[transf['CODRE'].str.startswith(('1721', '1722', '1723', '1724', '1729'))]['TOTOR'].sum()
        fundeb = transf[transf['CODRE'].str.startswith('1751')]['TOTOR'].sum()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("União", format_currency(transf_uniao))
        with col2:
            st.metric("Estado", format_currency(transf_estado))
        with col3:
            st.metric("FUNDEB", format_currency(fundeb))
        
        # Gráfico de transferências por origem
        fig_origem = go.Figure(data=[go.Pie(
            labels=['União', 'Estado', 'FUNDEB'],
            values=[transf_uniao, transf_estado, fundeb],
            hole=0.3
        )])
        
        fig_origem.update_layout(title="Transferências por Origem")
        st.plotly_chart(fig_origem, use_container_width=True)
        
        # Principais transferências
        st.subheader("🔝 Principais Transferências")
        top_transf = transf.nlargest(15, 'TOTOR')[['NOME', 'TOTOR']]
        top_transf['TOTOR'] = top_transf['TOTOR'].apply(format_currency)
        top_transf.columns = ['Descrição', 'Valor Previsto']
        
        st.dataframe(top_transf, use_container_width=True)
    else:
        st.warning("Nenhuma transferência encontrada nos dados.")

# ==============================================================================
# DETALHAMENTO
# ==============================================================================
elif opcao == "Detalhamento":
    st.header("🔍 Detalhamento Completo")
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        valor_min = st.number_input("Valor mínimo (R$)", min_value=0, value=0)
    
    with col2:
        busca = st.text_input("Buscar por descrição")
    
    # Aplicar filtros
    dados_filtrados = receitas_orcadas.copy()
    
    if valor_min > 0:
        dados_filtrados = dados_filtrados[dados_filtrados['TOTOR'] >= valor_min]
    
    if busca:
        dados_filtrados = dados_filtrados[
            dados_filtrados['NOME'].str.contains(busca, case=False, na=False)
        ]
    
    # Mostrar resultados
    st.subheader(f"📊 Resultados ({len(dados_filtrados)} registros)")
    
    if not dados_filtrados.empty:
        # Preparar dados para exibição
        display_data = dados_filtrados[['CODRE', 'NOME', 'TOTOR']].copy()
        display_data['TOTOR'] = display_data['TOTOR'].apply(format_currency)
        display_data.columns = ['Código', 'Descrição', 'Valor Previsto']
        
        st.dataframe(display_data, use_container_width=True)
        
        # Estatísticas dos dados filtrados
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Filtrado", format_currency(dados_filtrados['TOTOR'].sum()))
        with col2:
            st.metric("Maior Valor", format_currency(dados_filtrados['TOTOR'].max()))
        with col3:
            st.metric("Menor Valor", format_currency(dados_filtrados['TOTOR'].min()))
    else:
        st.warning("Nenhum registro encontrado com os filtros aplicados.")

# Adicionar seção de insights gerais
st.divider()
st.header("💡 Insights e Análises")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Principais Indicadores")
    
    # Dependência de transferências
    dependencia_transf = (transferencias / total_orcamento) * 100
    if dependencia_transf > 70:
        cor_dep = "🔴"
        status_dep = "Alta dependência"
    elif dependencia_transf > 50:
        cor_dep = "🟡"
        status_dep = "Dependência moderada"
    else:
        cor_dep = "🟢"
        status_dep = "Baixa dependência"
    
    st.write(f"{cor_dep} **Dependência de Transferências**: {dependencia_transf:.1f}% - {status_dep}")
    
    # Autonomia fiscal
    autonomia_fiscal = (receitas_tributarias / total_orcamento) * 100
    if autonomia_fiscal > 30:
        cor_aut = "🟢"
        status_aut = "Boa autonomia"
    elif autonomia_fiscal > 15:
        cor_aut = "🟡"
        status_aut = "Autonomia moderada"
    else:
        cor_aut = "🔴"
        status_aut = "Baixa autonomia"
    
    st.write(f"{cor_aut} **Autonomia Fiscal**: {autonomia_fiscal:.1f}% - {status_aut}")
    
    # Receita per capita estimada (assumindo população de ~5.000 hab)
    pop_estimada = 5000
    receita_per_capita = total_orcamento / pop_estimada
    st.write(f"💰 **Receita per capita estimada**: {format_currency(receita_per_capita)}")

with col2:
    st.subheader("📈 Composição Ideal vs Real")
    
    # Dados ideais baseados em boas práticas municipais
    ideal_tributaria = 25  # %
    ideal_transferencias = 60  # %
    ideal_outras = 15  # %
    
    real_tributaria = (receitas_tributarias/total_orcamento*100)
    real_transferencias = (transferencias/total_orcamento*100)
    real_outras = (outras_receitas/total_orcamento*100)
    
    comparacao_data = {
        'Categoria': ['Tributárias', 'Transferências', 'Outras'],
        'Ideal (%)': [ideal_tributaria, ideal_transferencias, ideal_outras],
        'Real (%)': [real_tributaria, real_transferencias, real_outras]
    }
    
    df_comparacao = pd.DataFrame(comparacao_data)
    
    fig_comparacao = px.bar(
        df_comparacao,
        x='Categoria',
        y=['Ideal (%)', 'Real (%)'],
        title="Composição Ideal vs Real do Orçamento",
        barmode='group',
        color_discrete_map={'Ideal (%)': '#2E8B57', 'Real (%)': '#FF6347'}
    )
    
    fig_comparacao.update_layout(height=300)
    st.plotly_chart(fig_comparacao, use_container_width=True)

# Análises adicionais
st.subheader("📊 Análises Complementares")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🏥 Recursos SUS",
        format_currency(receitas_orcadas[receitas_orcadas['CODRE'].str.startswith('1713')]['TOTOR'].sum()),
        help="Transferências do SUS para saúde"
    )

with col2:
    st.metric(
        "🎓 Recursos Educação",
        format_currency(receitas_orcadas[receitas_orcadas['CODRE'].str.startswith(('1714', '1751'))]['TOTOR'].sum()),
        help="FNDE + FUNDEB para educação"
    )

with col3:
    st.metric(
        "🤝 Assistência Social",
        format_currency(receitas_orcadas[receitas_orcadas['CODRE'].str.startswith('1716')]['TOTOR'].sum()),
        help="Transferências FNAS para assistência"
    )

# Rodapé
st.divider()
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>📊 Dashboard LOA - Município de Rifaina</strong></p>
    <p>Desenvolvido com Streamlit e Plotly | Análise Orçamentária Interativa</p>
    <p><em>Este dashboard apresenta uma análise da Lei Orçamentária Anual com base nos dados fornecidos.</em></p>
</div>
""", unsafe_allow_html=True)

