import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
from scipy.stats import entropy

# Configuração da página
st.set_page_config(
    page_title="Portal Transparência Rifaina - Execução Orçamentária", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar e processar dados
@st.cache_data
def load_data():
    """Carrega e processa os dados de execução orçamentária e LOA"""
    
    # Carregar dados de receitas executadas
    try:
        receitas_executadas = pd.read_csv("Portal Transparencia Receitas Acumuladas - Exercício 2025 (1).csv", 
                                        sep=';', encoding='utf-8')
    except:
        receitas_executadas = pd.read_csv("Portal Transparencia Receitas Acumuladas - Exercício 2025 (1).csv", 
                                        sep=';', encoding='latin-1')
    
    # Carregar dados de despesas executadas
    try:
        despesas_executadas = pd.read_csv("Portal Transparencia Despesas Gerais - Exercício 2025.csv", 
                                        sep=';', encoding='utf-8')
    except:
        despesas_executadas = pd.read_csv("Portal Transparencia Despesas Gerais - Exercício 2025.csv", 
                                        sep=';', encoding='latin-1')
    
    # Carregar dados da LOA (receitas orçadas)
    try:
        receitas_orcadas = pd.read_csv("download-123842.557.csv", sep=';', encoding='utf-8')
    except:
        receitas_orcadas = pd.read_csv("download-123842.557.csv", sep=';', encoding='latin-1')
    
    # Carregar estrutura de receitas da LOA
    try:
        estrutura_receitas = pd.read_csv("download-123701.452.csv", sep=';', encoding='utf-8')
    except:
        estrutura_receitas = pd.read_csv("download-123701.452.csv", sep=';', encoding='latin-1')
    
    return receitas_executadas, despesas_executadas, receitas_orcadas, estrutura_receitas

def format_currency(value):
    """Formata valores em moeda brasileira"""
    if pd.isna(value) or value == 0:
        return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def parse_currency(value_str):
    """Converte string de moeda brasileira para float"""
    if pd.isna(value_str) or value_str == '' or value_str == 0:
        return 0.0
    
    # Se já for um número, retorna como está
    if isinstance(value_str, (int, float)):
        return float(value_str)
    
    # Remove pontos de milhares e substitui vírgula por ponto decimal
    try:
        cleaned = str(value_str).replace('.', '').replace(',', '.')
        return float(cleaned)
    except:
        return 0.0

def process_receitas_data(df):
    """Processa dados de receitas"""
    df = df.copy()
    
    # Converter valores monetários
    for col in ['Prev. Inicial', 'Prev. Atualizada', 'Arrec. Período', 'Arrec. Total']:
        if col in df.columns:
            df[col] = df[col].apply(parse_currency)
    
    return df

def process_despesas_data(df):
    """Processa dados de despesas"""
    df = df.copy()
    
    # Converter valores monetários
    for col in ['Dotação', 'Alteração Dotação', 'Dotação Atual', 'Valor Anulado', 
                'Reforço', 'Valor Empenhado', 'Valor Liquidado', 'Valor Pago',
                'Empenhado até Hoje', 'Liquidado até Hoje', 'Pago até Hoje']:
        if col in df.columns:
            df[col] = df[col].apply(parse_currency)
    
    # Converter data
    if 'Data' in df.columns:
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
    
    return df

def process_loa_data(df):
    """Processa dados da LOA"""
    df = df.copy()
    
    # Converter valores monetários da LOA
    if 'TOTOR' in df.columns:
        df['TOTOR'] = pd.to_numeric(df['TOTOR'], errors='coerce').fillna(0)
    
    return df

# Carregar dados
st.title("🏛️ Portal Transparência - Município de Rifaina")
st.markdown("**Análise Completa: LOA vs Execução Orçamentária 2025**")

with st.spinner("Carregando dados de execução orçamentária e LOA..."):
    receitas_raw, despesas_raw, receitas_loa_raw, estrutura_loa_raw = load_data()

# Processar dados
receitas_df = process_receitas_data(receitas_raw)
despesas_df = process_despesas_data(despesas_raw)
receitas_loa_df = process_loa_data(receitas_loa_raw)
estrutura_loa_df = process_loa_data(estrutura_loa_raw)

# Verificar se os dados foram carregados corretamente
if receitas_df.empty or despesas_df.empty or receitas_loa_df.empty:
    st.error("Erro ao carregar os dados. Verifique os arquivos CSV.")
    st.stop()

# Calcular totais das receitas (execução)
total_previsto_receitas = receitas_df['Prev. Atualizada'].sum()
total_arrecadado_receitas = receitas_df['Arrec. Total'].sum()
percentual_execucao_receitas = (total_arrecadado_receitas / total_previsto_receitas * 100) if total_previsto_receitas > 0 else 0

# Calcular totais da LOA (orçamento original)
total_loa_receitas = receitas_loa_df['TOTOR'].sum()

# Calcular totais das despesas
total_dotacao_despesas = despesas_df['Dotação Atual'].sum()
total_empenhado_despesas = despesas_df['Empenhado até Hoje'].sum()
total_liquidado_despesas = despesas_df['Liquidado até Hoje'].sum()
total_pago_despesas = despesas_df['Pago até Hoje'].sum()

# Sidebar com informações gerais
st.sidebar.header("📊 Resumo Executivo")

# Comparação LOA vs Execução
st.sidebar.subheader("💰 Receitas")
st.sidebar.metric("🎯 LOA Original", format_currency(total_loa_receitas))
st.sidebar.metric("📈 Arrecadado", format_currency(total_arrecadado_receitas))
execucao_vs_loa = (total_arrecadado_receitas / total_loa_receitas * 100) if total_loa_receitas > 0 else 0
st.sidebar.metric("📊 Execução vs LOA", f"{execucao_vs_loa:.1f}%")

st.sidebar.subheader("💳 Despesas") 
st.sidebar.metric("📉 Empenhado", format_currency(total_empenhado_despesas))
st.sidebar.metric("✅ Liquidado", format_currency(total_liquidado_despesas))
st.sidebar.metric("💸 Pago", format_currency(total_pago_despesas))

st.sidebar.subheader("🔍 Resultado")
resultado_orcamentario = total_arrecadado_receitas - total_empenhado_despesas
cor_resultado = "normal" if resultado_orcamentario >= 0 else "inverse"
st.sidebar.metric("💰 Saldo Orçamentário", format_currency(resultado_orcamentario), 
                 delta_color=cor_resultado)

# Menu de navegação
opcao = st.sidebar.selectbox(
    "📊 Escolha a análise:",
    ["Visão Geral", "🎯 Métricas Completas", "LOA vs Execução", "Receitas Executadas", "Despesas Executadas", 
     "Comparação Previsto vs Realizado", "Análise por Função", "Detalhamento"]
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
.positive-result {
    color: #2E8B57;
    font-weight: bold;
}
.negative-result {
    color: #DC143C;
    font-weight: bold;
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
    st.header("📈 Visão Geral da Execução Orçamentária")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Total Arrecadado",
            format_currency(total_arrecadado_receitas),
            f"{percentual_execucao_receitas:.1f}% do previsto"
        )
    
    with col2:
        st.metric(
            "📊 Total Empenhado",
            format_currency(total_empenhado_despesas),
            f"{(total_empenhado_despesas/total_dotacao_despesas*100):.1f}% da dotação"
        )
    
    with col3:
        st.metric(
            "✅ Total Liquidado",
            format_currency(total_liquidado_despesas),
            f"{(total_liquidado_despesas/total_empenhado_despesas*100):.1f}% do empenhado"
        )
    
    with col4:
        st.metric(
            "💳 Total Pago",
            format_currency(total_pago_despesas),
            f"{(total_pago_despesas/total_liquidado_despesas*100):.1f}% do liquidado"
        )
    
    st.divider()
    
    # Gráficos da visão geral
    col1, col2 = st.columns(2)
    
    with col1:
        # Comparação Receitas vs Despesas
        fig_comparacao = go.Figure(data=[
            go.Bar(name='Receitas', x=['Previsto', 'Realizado'], 
                  y=[total_previsto_receitas, total_arrecadado_receitas], 
                  marker_color='#2E8B57'),
            go.Bar(name='Despesas', x=['Dotado', 'Empenhado'], 
                  y=[total_dotacao_despesas, total_empenhado_despesas], 
                  marker_color='#DC143C')
        ])
        
        fig_comparacao.update_layout(
            title="Receitas vs Despesas - Previsto vs Realizado",
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig_comparacao, use_container_width=True)
    
    with col2:
        # Execução das Despesas (Funil)
        fases_despesas = ['Dotado', 'Empenhado', 'Liquidado', 'Pago']
        valores_despesas = [total_dotacao_despesas, total_empenhado_despesas, 
                          total_liquidado_despesas, total_pago_despesas]
        
        fig_funil = go.Figure(go.Funnel(
            y=fases_despesas,
            x=valores_despesas,
            textinfo="value+percent previous",
            marker={"color": ["deepskyblue", "lightsalmon", "lightgreen", "gold"]}
        ))
        
        fig_funil.update_layout(
            title="Funil de Execução das Despesas",
            height=400
        )
        
        st.plotly_chart(fig_funil, use_container_width=True)

# ==============================================================================
# MÉTRICAS COMPLETAS
# ==============================================================================
elif opcao == "🎯 Métricas Completas":
    st.header("🎯 Métricas Completas de Gestão Orçamentária")
    st.markdown("**Todos os indicadores financeiros, fiscais e de performance do município**")
    
    # Calcular métricas adicionais
    pop_estimada = 5000  # População estimada de Rifaina
    
    # Métricas básicas
    receita_per_capita = total_arrecadado_receitas / pop_estimada
    despesa_per_capita = total_empenhado_despesas / pop_estimada
    
    # Métricas de execução
    execucao_financeira = (total_pago_despesas / total_empenhado_despesas * 100) if total_empenhado_despesas > 0 else 0
    execucao_orcamentaria = (total_empenhado_despesas / total_dotacao_despesas * 100) if total_dotacao_despesas > 0 else 0
    
    # Métricas de liquidez
    liquidez_geral = (total_arrecadado_receitas / total_empenhado_despesas) if total_empenhado_despesas > 0 else 0
    resto_a_pagar = total_liquidado_despesas - total_pago_despesas
    
    # Métricas de autonomia fiscal
    receitas_tributarias = receitas_df[receitas_df['Código'].str.startswith(('1112', '1113', '1114', '1121', '1122'))]['Arrec. Total'].sum()
    transferencias = receitas_df[receitas_df['Código'].str.startswith(('1711', '1712', '1713', '1714', '1716', '1721', '1722', '1723', '1724', '1751'))]['Arrec. Total'].sum()
    
    autonomia_fiscal = (receitas_tributarias / total_arrecadado_receitas * 100) if total_arrecadado_receitas > 0 else 0
    dependencia_transferencias = (transferencias / total_arrecadado_receitas * 100) if total_arrecadado_receitas > 0 else 0
    
    # Métricas por área (Saúde, Educação, etc.)
    saude_despesas = despesas_df[despesas_df['Função'] == '10']['Empenhado até Hoje'].sum()
    educacao_despesas = despesas_df[despesas_df['Função'] == '12']['Empenhado até Hoje'].sum()
    assistencia_despesas = despesas_df[despesas_df['Função'] == '08']['Empenhado até Hoje'].sum()
    
    saude_percentual = (saude_despesas / total_empenhado_despesas * 100) if total_empenhado_despesas > 0 else 0
    educacao_percentual = (educacao_despesas / total_empenhado_despesas * 100) if total_empenhado_despesas > 0 else 0
    
    # ==============================================================================
    # SEÇÃO 1: MÉTRICAS FINANCEIRAS BÁSICAS
    # ==============================================================================
    st.subheader("💰 1. Métricas Financeiras Básicas")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "💵 Receita Total",
            format_currency(total_arrecadado_receitas),
            help="Total de receitas arrecadadas no período"
        )
    
    with col2:
        st.metric(
            "💸 Despesa Total",
            format_currency(total_empenhado_despesas),
            help="Total de despesas empenhadas no período"
        )
    
    with col3:
        st.metric(
            "⚖️ Saldo Orçamentário",
            format_currency(resultado_orcamentario),
            f"{((resultado_orcamentario/total_arrecadado_receitas)*100):.1f}% da receita" if total_arrecadado_receitas > 0 else "0%"
        )
    
    with col4:
        st.metric(
            "👥 Receita per Capita",
            format_currency(receita_per_capita),
            help=f"Receita por habitante (pop. estimada: {pop_estimada:,})"
        )
    
    with col5:
        st.metric(
            "👥 Despesa per Capita",
            format_currency(despesa_per_capita),
            help=f"Despesa por habitante (pop. estimada: {pop_estimada:,})"
        )
    
    # ==============================================================================
    # SEÇÃO 2: MÉTRICAS DE EXECUÇÃO ORÇAMENTÁRIA
    # ==============================================================================
    st.subheader("📊 2. Métricas de Execução Orçamentária")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "🎯 Execução LOA",
            f"{execucao_vs_loa:.1f}%",
            "Arrecadado vs LOA Original",
            help="Percentual da LOA efetivamente arrecadado"
        )
    
    with col2:
        st.metric(
            "📈 Execução Portal",
            f"{percentual_execucao_receitas:.1f}%",
            "Arrecadado vs Previsto Atualizado",
            help="Execução conforme Portal de Transparência"
        )
    
    with col3:
        st.metric(
            "💼 Execução Orçamentária",
            f"{execucao_orcamentaria:.1f}%",
            "Empenhado vs Dotado",
            help="Percentual da dotação orçamentária executada"
        )
    
    with col4:
        st.metric(
            "💳 Execução Financeira",
            f"{execucao_financeira:.1f}%",
            "Pago vs Empenhado",
            help="Percentual dos empenhos efetivamente pagos"
        )
    
    with col5:
        st.metric(
            "📋 Liquidação",
            f"{(total_liquidado_despesas/total_empenhado_despesas*100):.1f}%" if total_empenhado_despesas > 0 else "0%",
            "Liquidado vs Empenhado",
            help="Percentual dos empenhos liquidados"
        )
    
    # ==============================================================================
    # SEÇÃO 3: MÉTRICAS DE AUTONOMIA FISCAL
    # ==============================================================================
    st.subheader("🏛️ 3. Métricas de Autonomia Fiscal")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cor_autonomia = "normal" if autonomia_fiscal > 20 else "inverse"
        st.metric(
            "🎯 Autonomia Fiscal",
            f"{autonomia_fiscal:.1f}%",
            "Receitas Próprias / Total",
            delta_color=cor_autonomia,
            help="Percentual de receitas próprias (impostos e taxas)"
        )
    
    with col2:
        cor_dependencia = "inverse" if dependencia_transferencias > 70 else "normal"
        st.metric(
            "🔄 Dependência Transferências",
            f"{dependencia_transferencias:.1f}%",
            "Transferências / Total",
            delta_color=cor_dependencia,
            help="Dependência de transferências intergovernamentais"
        )
    
    with col3:
        outras_receitas = total_arrecadado_receitas - receitas_tributarias - transferencias
        outras_percentual = (outras_receitas / total_arrecadado_receitas * 100) if total_arrecadado_receitas > 0 else 0
        st.metric(
            "📊 Outras Receitas",
            f"{outras_percentual:.1f}%",
            format_currency(outras_receitas),
            help="Patrimoniais, serviços e outras receitas"
        )
    
    with col4:
        equilibrio_score = 100 - abs(50 - autonomia_fiscal) - abs(dependencia_transferencias - 60)
        equilibrio_score = max(0, equilibrio_score)
        st.metric(
            "⚖️ Equilíbrio Fiscal",
            f"{equilibrio_score:.0f}/100",
            "Score de Sustentabilidade",
            help="Índice de equilíbrio entre receitas próprias e transferências"
        )
    
    # ==============================================================================
    # SEÇÃO 4: MÉTRICAS POR ÁREA DE GOVERNO
    # ==============================================================================
    st.subheader("🏛️ 4. Métricas por Área de Governo")
    
    # Calcular métricas constitucionais
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        cor_saude = "normal" if saude_percentual >= 15 else "inverse"
        st.metric(
            "🏥 Saúde",
            f"{saude_percentual:.1f}%",
            format_currency(saude_despesas),
            delta_color=cor_saude,
            help="Mínimo constitucional: 15% (municípios)"
        )
    
    with col2:
        cor_educacao = "normal" if educacao_percentual >= 25 else "inverse"
        st.metric(
            "🎓 Educação",
            f"{educacao_percentual:.1f}%",
            format_currency(educacao_despesas),
            delta_color=cor_educacao,
            help="Mínimo constitucional: 25% (municípios)"
        )
    
    with col3:
        assistencia_percentual = (assistencia_despesas / total_empenhado_despesas * 100) if total_empenhado_despesas > 0 else 0
        st.metric(
            "🤝 Assistência Social",
            f"{assistencia_percentual:.1f}%",
            format_currency(assistencia_despesas),
            help="Gastos com assistência social"
        )
    
    with col4:
        # Calcular investimentos (natureza 4.4)
        investimentos = despesas_df[despesas_df['Natureza'].str.startswith('4.4', na=False)]['Empenhado até Hoje'].sum()
        investimentos_percentual = (investimentos / total_empenhado_despesas * 100) if total_empenhado_despesas > 0 else 0
        st.metric(
            "🏗️ Investimentos",
            f"{investimentos_percentual:.1f}%",
            format_currency(investimentos),
            help="Despesas de capital - investimentos"
        )
    
    with col5:
        # Calcular custeio (natureza 3.3)
        custeio = despesas_df[despesas_df['Natureza'].str.startswith('3.3', na=False)]['Empenhado até Hoje'].sum()
        custeio_percentual = (custeio / total_empenhado_despesas * 100) if total_empenhado_despesas > 0 else 0
        st.metric(
            "🔧 Custeio",
            f"{custeio_percentual:.1f}%",
            format_currency(custeio),
            help="Outras despesas correntes"
        )
    
    # ==============================================================================
    # SEÇÃO 5: MÉTRICAS DE LIQUIDEZ E FLUXO
    # ==============================================================================
    st.subheader("💧 5. Métricas de Liquidez e Fluxo Financeiro")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cor_liquidez = "normal" if liquidez_geral >= 1.0 else "inverse"
        st.metric(
            "💧 Liquidez Geral",
            f"{liquidez_geral:.2f}",
            "Receita / Despesa",
            delta_color=cor_liquidez,
            help="Capacidade de honrar compromissos (ideal ≥ 1.0)"
        )
    
    with col2:
        st.metric(
            "⏳ Resto a Pagar",
            format_currency(resto_a_pagar),
            f"{(resto_a_pagar/total_liquidado_despesas*100):.1f}% do liquidado" if total_liquidado_despesas > 0 else "0%",
            help="Valor liquidado mas ainda não pago"
        )
    
    with col3:
        disponibilidade_caixa = total_arrecadado_receitas - total_pago_despesas
        st.metric(
            "💰 Disponibilidade",
            format_currency(disponibilidade_caixa),
            f"{(disponibilidade_caixa/total_arrecadado_receitas*100):.1f}% da receita" if total_arrecadado_receitas > 0 else "0%",
            help="Saldo disponível (receita - pago)"
        )
    
    with col4:
        rotatividade = (total_pago_despesas / total_empenhado_despesas * 100) if total_empenhado_despesas > 0 else 0
        st.metric(
            "🔄 Rotatividade",
            f"{rotatividade:.1f}%",
            "Velocidade de Pagamento",
            help="Eficiência no pagamento de compromissos"
        )
    
    # ==============================================================================
    # SEÇÃO 6: MÉTRICAS DE EFICIÊNCIA E PRODUTIVIDADE
    # ==============================================================================
    st.subheader("⚡ 6. Métricas de Eficiência e Produtividade")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Eficiência arrecadatória
        eficiencia_arrecadacao = (total_arrecadado_receitas / total_loa_receitas * 100) if total_loa_receitas > 0 else 0
        cor_eficiencia = "normal" if eficiencia_arrecadacao >= 90 else "inverse"
        st.metric(
            "📈 Eficiência Arrecadação",
            f"{eficiencia_arrecadacao:.1f}%",
            "Real vs Planejado (LOA)",
            delta_color=cor_eficiencia,
            help="Capacidade de cumprir metas de receita"
        )
    
    with col2:
        # Concentração de fornecedores
        total_fornecedores = despesas_df['Nome Fornecedor'].nunique()
        fornecedor_concentracao = despesas_df.groupby('Nome Fornecedor')['Empenhado até Hoje'].sum()
        top5_fornecedores = fornecedor_concentracao.nlargest(5).sum()
        concentracao_pct = (top5_fornecedores / total_empenhado_despesas * 100) if total_empenhado_despesas > 0 else 0
        
        st.metric(
            "🏢 Concentração Fornecedores",
            f"{concentracao_pct:.1f}%",
            f"Top 5 de {total_fornecedores} fornecedores",
            help="Percentual gasto com os 5 maiores fornecedores"
        )
    
    with col3:
        # Diversificação de receitas
        receitas_por_categoria = receitas_df.groupby(receitas_df['Código'].str[:4])['Arrec. Total'].sum()
        
        # Calcular índice de diversificação (entropia normalizada)
        if len(receitas_por_categoria) > 0:
            valores_norm = receitas_por_categoria.values / receitas_por_categoria.sum()
            # Evitar log(0) adicionando pequeno valor
            valores_norm = valores_norm + 1e-10
            diversificacao = entropy(valores_norm) / np.log(len(valores_norm)) * 100
        else:
            diversificacao = 0
        
        st.metric(
            "🎯 Diversificação Receitas",
            f"{diversificacao:.1f}%",
            "Índice de Diversificação",
            help="Diversificação das fontes de receita (0-100%)"
        )
    
    with col4:
        # Tempo médio de pagamento (aproximado)
        if 'Data' in despesas_df.columns:
            despesas_com_data = despesas_df.dropna(subset=['Data'])
            if not despesas_com_data.empty:
                tempo_medio = (datetime.now() - despesas_com_data['Data'].min()).days
                st.metric(
                    "⏱️ Tempo Médio Ciclo",
                    f"{tempo_medio} dias",
                    "Empenho até hoje",
                    help="Tempo médio do ciclo orçamentário"
                )
            else:
                st.metric("⏱️ Tempo Médio Ciclo", "N/A", "Dados indisponíveis")
        else:
            st.metric("⏱️ Tempo Médio Ciclo", "N/A", "Dados indisponíveis")
    
    # ==============================================================================
    # SEÇÃO 7: MÉTRICAS COMPARATIVAS E BENCHMARKS
    # ==============================================================================
    st.subheader("📊 7. Métricas Comparativas e Benchmarks")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Índice de Qualidade Fiscal (IQF) - criado
        iqf = (autonomia_fiscal * 0.3 + execucao_vs_loa * 0.3 + 
               (100 - dependencia_transferencias) * 0.2 + liquidez_geral * 20 * 0.2)
        iqf = min(100, max(0, iqf))
        
        cor_iqf = "normal" if iqf >= 70 else ("inverse" if iqf < 50 else "off")
        st.metric(
            "🏆 Índice Qualidade Fiscal",
            f"{iqf:.0f}/100",
            "IQF Composto",
            delta_color=cor_iqf,
            help="Índice composto: autonomia + execução + liquidez"
        )
    
    with col2:
        # Sustentabilidade fiscal
        sustentabilidade = ((saude_percentual >= 15) * 25 + 
                          (educacao_percentual >= 25) * 25 + 
                          (autonomia_fiscal >= 20) * 25 + 
                          (execucao_vs_loa >= 80) * 25)
        
        st.metric(
            "🌱 Sustentabilidade",
            f"{sustentabilidade:.0f}/100",
            "Score Constitucional",
            help="Cumprimento de limites constitucionais"
        )
    
    with col3:
        # Transparência e controle
        total_empenhos = len(despesas_df)
        empenhos_por_habitante = total_empenhos / pop_estimada
        
        st.metric(
            "🔍 Transparência",
            f"{total_empenhos:,}",
            f"{empenhos_por_habitante:.1f} empenhos/hab",
            help="Número total de empenhos registrados"
        )
    
    with col4:
        # Efetividade do gasto público
        gasto_social = saude_despesas + educacao_despesas + assistencia_despesas
        efetividade = (gasto_social / total_empenhado_despesas * 100) if total_empenhado_despesas > 0 else 0
        
        cor_efetividade = "normal" if efetividade >= 50 else "inverse"
        st.metric(
            "🎯 Efetividade Social",
            f"{efetividade:.1f}%",
            "Gasto Social / Total",
            delta_color=cor_efetividade,
            help="Percentual gasto em áreas sociais prioritárias"
        )
    
    # ==============================================================================
    # SEÇÃO 8: DASHBOARD DE ALERTAS E RECOMENDAÇÕES
    # ==============================================================================
    st.subheader("⚠️ 8. Alertas e Recomendações")
    
    alertas = []
    recomendacoes = []
    
    # Verificar limites constitucionais
    if saude_percentual < 15:
        alertas.append(f"🚨 **SAÚDE**: {saude_percentual:.1f}% - Abaixo do mínimo constitucional (15%)")
        recomendacoes.append("📌 Aumentar investimentos em saúde para cumprir limite constitucional")
    
    if educacao_percentual < 25:
        alertas.append(f"🚨 **EDUCAÇÃO**: {educacao_percentual:.1f}% - Abaixo do mínimo constitucional (25%)")
        recomendacoes.append("📌 Ampliar gastos com educação conforme determinação constitucional")
    
    # Verificar autonomia fiscal
    if autonomia_fiscal < 20:
        alertas.append(f"⚠️ **AUTONOMIA FISCAL**: {autonomia_fiscal:.1f}% - Muito dependente de transferências")
        recomendacoes.append("📌 Fortalecer arrecadação própria (IPTU, ISS, taxas)")
    
    # Verificar execução orçamentária
    if execucao_vs_loa < 70:
        alertas.append(f"⚠️ **EXECUÇÃO LOA**: {execucao_vs_loa:.1f}% - Baixa execução do orçamento")
        recomendacoes.append("📌 Revisar projeções orçamentárias e melhorar arrecadação")
    
    # Verificar liquidez
    if liquidez_geral < 1.0:
        alertas.append(f"🚨 **LIQUIDEZ**: {liquidez_geral:.2f} - Insuficiente para cobrir gastos")
        recomendacoes.append("📌 Urgente: equilibrar receitas e despesas")
    
    # Verificar resto a pagar
    if resto_a_pagar > total_arrecadado_receitas * 0.1:  # > 10% da receita
        alertas.append(f"⚠️ **RESTO A PAGAR**: {format_currency(resto_a_pagar)} - Alto valor não pago")
        recomendacoes.append("📌 Priorizar quitação de compromissos liquidados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if alertas:
            st.error("🚨 **ALERTAS CRÍTICOS**")
            for alerta in alertas:
                st.write(alerta)
        else:
            st.success("✅ **SITUAÇÃO FISCAL REGULAR** - Sem alertas críticos")
    
    with col2:
        if recomendacoes:
            st.info("💡 **RECOMENDAÇÕES**")
            for rec in recomendacoes:
                st.write(rec)
        else:
            st.success("🎯 **GESTÃO ADEQUADA** - Continue monitorando os indicadores")

# ==============================================================================
# LOA vs EXECUÇÃO
# ==============================================================================
elif opcao == "LOA vs Execução":
    st.header("📊 Comparação: LOA (Orçamento) vs Execução Real")
    
    # Métricas principais de comparação
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 LOA - Receitas",
            format_currency(total_loa_receitas),
            "Orçamento Original"
        )
    
    with col2:
        st.metric(
            "📈 Receitas Arrecadadas",
            format_currency(total_arrecadado_receitas),
            f"{execucao_vs_loa:.1f}% da LOA"
        )
    
    with col3:
        diferenca_loa_execucao = total_arrecadado_receitas - total_loa_receitas
        st.metric(
            "🔄 Diferença",
            format_currency(diferenca_loa_execucao),
            "Arrecadado vs LOA"
        )
    
    with col4:
        st.metric(
            "📊 Performance",
            f"{execucao_vs_loa:.1f}%",
            "Execução da LOA"
        )
    
    st.divider()
    
    # Análise por categoria LOA vs Execução
    st.subheader("📈 Análise Detalhada por Categoria")
    
    # Agrupar receitas da LOA por categoria principal
    receitas_loa_df['categoria_loa'] = receitas_loa_df['CODRE'].str[:4]
    loa_por_categoria = receitas_loa_df.groupby('categoria_loa')['TOTOR'].sum().reset_index()
    
    # Agrupar receitas executadas por categoria
    receitas_df['categoria_exec'] = receitas_df['Código'].str[:4]
    exec_por_categoria = receitas_df.groupby('categoria_exec')['Arrec. Total'].sum().reset_index()
    
    # Merge das categorias
    comparacao_categorias = pd.merge(
        loa_por_categoria, 
        exec_por_categoria, 
        left_on='categoria_loa', 
        right_on='categoria_exec', 
        how='outer'
    ).fillna(0)
    
    comparacao_categorias['execucao_pct'] = (
        comparacao_categorias['Arrec. Total'] / comparacao_categorias['TOTOR'] * 100
    ).fillna(0)
    
    # Mapear nomes das categorias
    categoria_nomes = {
        '1112': 'Impostos s/ Patrimônio', '1113': 'Impostos s/ Renda', '1114': 'Impostos s/ Serviços',
        '1121': 'Taxas Poder Polícia', '1122': 'Taxas por Serviços', '1321': 'Rendimentos Financeiros',
        '1335': 'Concessões', '1399': 'Outras Patrimoniais', '1699': 'Outros Serviços',
        '1711': 'Transferências União', '1712': 'Compensações Financeiras', '1713': 'SUS - União',
        '1714': 'FNDE', '1715': 'FUNDEB - União', '1716': 'FNAS', '1719': 'Outras - União',
        '1721': 'Transferências Estado', '1722': 'Royalties Estado', '1723': 'SUS - Estado',
        '1724': 'Convênios Estado', '1729': 'Outras - Estado', '1751': 'FUNDEB',
        '1911': 'Multas', '1922': 'Restituições', '1999': 'Outras Correntes', '2422': 'Transferências Capital'
    }
    
    comparacao_categorias['nome_categoria'] = comparacao_categorias['categoria_loa'].map(categoria_nomes)
    comparacao_categorias = comparacao_categorias.dropna(subset=['nome_categoria'])
    comparacao_categorias = comparacao_categorias[comparacao_categorias['TOTOR'] > 0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico comparativo LOA vs Execução
        fig_comparacao_loa = go.Figure()
        
        fig_comparacao_loa.add_trace(go.Bar(
            name='LOA (Previsto)',
            x=comparacao_categorias['nome_categoria'],
            y=comparacao_categorias['TOTOR'],
            marker_color='lightcoral',
            opacity=0.7
        ))
        
        fig_comparacao_loa.add_trace(go.Bar(
            name='Executado',
            x=comparacao_categorias['nome_categoria'],
            y=comparacao_categorias['Arrec. Total'],
            marker_color='steelblue'
        ))
        
        fig_comparacao_loa.update_layout(
            title="LOA vs Execução por Categoria",
            barmode='group',
            height=500,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig_comparacao_loa, use_container_width=True)
    
    with col2:
        # Percentual de execução por categoria
        top_execucao = comparacao_categorias.nlargest(10, 'execucao_pct')
        
        fig_exec_pct = px.bar(
            top_execucao,
            x='execucao_pct',
            y='nome_categoria',
            orientation='h',
            title="% Execução da LOA por Categoria",
            labels={'execucao_pct': 'Execução (%)', 'nome_categoria': 'Categoria'},
            color='execucao_pct',
            color_continuous_scale='RdYlGn'
        )
        
        fig_exec_pct.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_exec_pct, use_container_width=True)
    
    # Tabela detalhada de comparação
    st.subheader("📋 Tabela Comparativa: LOA vs Execução")
    
    tabela_comparacao = comparacao_categorias[['nome_categoria', 'TOTOR', 'Arrec. Total', 'execucao_pct']].copy()
    tabela_comparacao['diferenca'] = tabela_comparacao['Arrec. Total'] - tabela_comparacao['TOTOR']
    
    # Ordenar por valor da LOA
    tabela_comparacao = tabela_comparacao.sort_values('TOTOR', ascending=False)
    
    # Formatar valores
    tabela_comparacao['TOTOR'] = tabela_comparacao['TOTOR'].apply(format_currency)
    tabela_comparacao['Arrec. Total'] = tabela_comparacao['Arrec. Total'].apply(format_currency)
    tabela_comparacao['diferenca'] = tabela_comparacao['diferenca'].apply(format_currency)
    tabela_comparacao['execucao_pct'] = tabela_comparacao['execucao_pct'].round(1).astype(str) + '%'
    
    tabela_comparacao.columns = ['Categoria', 'LOA (Previsto)', 'Executado', '% Execução', 'Diferença']
    st.dataframe(tabela_comparacao, use_container_width=True)
    
    # Insights da comparação
    st.subheader("💡 Insights LOA vs Execução")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Categorias com melhor execução
        melhor_execucao = comparacao_categorias[comparacao_categorias['execucao_pct'] > 100]
        if not melhor_execucao.empty:
            categoria_destaque = melhor_execucao.loc[melhor_execucao['execucao_pct'].idxmax()]
            st.success(f"🎯 **Melhor Performance**: {categoria_destaque['nome_categoria']} - {categoria_destaque['execucao_pct']:.1f}%")
        else:
            st.info("ℹ️ Nenhuma categoria superou 100% da previsão LOA")
    
    with col2:
        # Categorias com pior execução
        pior_execucao = comparacao_categorias[comparacao_categorias['execucao_pct'] < 50]
        if not pior_execucao.empty:
            categoria_atencao = pior_execucao.loc[pior_execucao['execucao_pct'].idxmin()]
            st.warning(f"⚠️ **Atenção**: {categoria_atencao['nome_categoria']} - {categoria_atencao['execucao_pct']:.1f}%")
        else:
            st.success("✅ Todas as categorias com execução > 50%")
    
    with col3:
        # Execução geral
        if execucao_vs_loa > 90:
            st.success(f"🟢 **Execução Geral**: {execucao_vs_loa:.1f}% - Excelente")
        elif execucao_vs_loa > 70:
            st.info(f"🟡 **Execução Geral**: {execucao_vs_loa:.1f}% - Boa")
        else:
            st.error(f"🔴 **Execução Geral**: {execucao_vs_loa:.1f}% - Baixa")

# ==============================================================================
# RECEITAS EXECUTADAS
# ==============================================================================
elif opcao == "Receitas Executadas":
    st.header("💰 Análise das Receitas Executadas")
    
    # Filtrar receitas com arrecadação > 0
    receitas_com_valor = receitas_df[receitas_df['Arrec. Total'] > 0].copy()
    
    # Principais categorias de receitas
    receitas_com_valor['categoria'] = receitas_com_valor['Código'].str[:4]
    receitas_por_categoria = receitas_com_valor.groupby('categoria').agg({
        'Prev. Atualizada': 'sum',
        'Arrec. Total': 'sum'
    }).reset_index()
    
    receitas_por_categoria['execucao_pct'] = (receitas_por_categoria['Arrec. Total'] / 
                                            receitas_por_categoria['Prev. Atualizada'] * 100)
    
    # Mapear códigos para nomes
    categoria_nomes = {
        '1112': 'Impostos s/ Patrimônio',
        '1113': 'Impostos s/ Renda',
        '1114': 'Impostos s/ Serviços',
        '1121': 'Taxas Poder Polícia',
        '1122': 'Taxas por Serviços',
        '1321': 'Rendimentos Financeiros',
        '1335': 'Concessões',
        '1399': 'Outras Patrimoniais',
        '1699': 'Outros Serviços',
        '1711': 'Transferências União',
        '1712': 'Compensações Financeiras',
        '1713': 'SUS - União',
        '1714': 'FNDE',
        '1715': 'FUNDEB - União',
        '1716': 'FNAS',
        '1719': 'Outras - União',
        '1721': 'Transferências Estado',
        '1722': 'Royalties Estado',
        '1723': 'SUS - Estado',
        '1724': 'Convênios Estado',
        '1729': 'Outras - Estado',
        '1751': 'FUNDEB',
        '1911': 'Multas',
        '1922': 'Restituições',
        '1999': 'Outras Correntes',
        '2422': 'Transferências Capital'
    }
    
    receitas_por_categoria['nome_categoria'] = receitas_por_categoria['categoria'].map(categoria_nomes)
    receitas_por_categoria['nome_categoria'] = receitas_por_categoria['nome_categoria'].fillna(
        'Outras - ' + receitas_por_categoria['categoria'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 receitas por arrecadação
        top_receitas = receitas_por_categoria.nlargest(10, 'Arrec. Total')
        
        fig_bar = px.bar(
            top_receitas,
            x='Arrec. Total',
            y='nome_categoria',
            orientation='h',
            title="Top 10 Categorias - Arrecadação Realizada",
            labels={'Arrec. Total': 'Arrecadado (R$)', 'nome_categoria': 'Categoria'}
        )
        
        fig_bar.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Percentual de execução por categoria
        receitas_execucao = receitas_por_categoria[receitas_por_categoria['execucao_pct'] > 0]
        
        fig_execucao = px.bar(
            receitas_execucao.nlargest(10, 'execucao_pct'),
            x='execucao_pct',
            y='nome_categoria',
            orientation='h',
            title="Top 10 - Percentual de Execução das Receitas",
            labels={'execucao_pct': 'Execução (%)', 'nome_categoria': 'Categoria'},
            color='execucao_pct',
            color_continuous_scale='RdYlGn'
        )
        
        fig_execucao.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_execucao, use_container_width=True)
    
    # Tabela detalhada das principais receitas
    st.subheader("📋 Detalhamento das Principais Receitas Arrecadadas")
    
    principais_receitas = receitas_com_valor.nlargest(20, 'Arrec. Total')[
        ['Especificação', 'Prev. Atualizada', 'Arrec. Total']
    ].copy()
    
    principais_receitas['Execução (%)'] = (principais_receitas['Arrec. Total'] / 
                                         principais_receitas['Prev. Atualizada'] * 100)
    
    principais_receitas['Prev. Atualizada'] = principais_receitas['Prev. Atualizada'].apply(format_currency)
    principais_receitas['Arrec. Total'] = principais_receitas['Arrec. Total'].apply(format_currency)
    principais_receitas['Execução (%)'] = principais_receitas['Execução (%)'].round(1).astype(str) + '%'
    
    principais_receitas.columns = ['Descrição', 'Previsto', 'Arrecadado', 'Execução (%)']
    st.dataframe(principais_receitas, use_container_width=True)

# ==============================================================================
# DESPESAS EXECUTADAS
# ==============================================================================
elif opcao == "Despesas Executadas":
    st.header("💳 Análise das Despesas Executadas")
    
    # Análise por função
    despesas_por_funcao = despesas_df.groupby(['Função', 'Nome da Função']).agg({
        'Dotação Atual': 'sum',
        'Empenhado até Hoje': 'sum',
        'Liquidado até Hoje': 'sum',
        'Pago até Hoje': 'sum'
    }).reset_index()
    
    despesas_por_funcao['execucao_pct'] = (despesas_por_funcao['Empenhado até Hoje'] / 
                                         despesas_por_funcao['Dotação Atual'] * 100)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 funções por valor empenhado
        top_funcoes = despesas_por_funcao.nlargest(10, 'Empenhado até Hoje')
        
        fig_funcoes = px.bar(
            top_funcoes,
            x='Empenhado até Hoje',
            y='Nome da Função',
            orientation='h',
            title="Top 10 Funções - Valor Empenhado",
            labels={'Empenhado até Hoje': 'Empenhado (R$)', 'Nome da Função': 'Função'}
        )
        
        fig_funcoes.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_funcoes, use_container_width=True)
    
    with col2:
        # Análise por natureza da despesa
        despesas_por_natureza = despesas_df.groupby('Nome Natureza').agg({
            'Empenhado até Hoje': 'sum'
        }).reset_index()
        
        top_natureza = despesas_por_natureza.nlargest(8, 'Empenhado até Hoje')
        
        fig_natureza = px.pie(
            top_natureza,
            values='Empenhado até Hoje',
            names='Nome Natureza',
            title="Distribuição por Natureza da Despesa"
        )
        
        st.plotly_chart(fig_natureza, use_container_width=True)
    
    # Evolução temporal das despesas
    st.subheader("📈 Evolução Temporal das Despesas")
    
    if 'Data' in despesas_df.columns:
        despesas_df['mes_ano'] = despesas_df['Data'].dt.to_period('M')
        evolucao_mensal = despesas_df.groupby('mes_ano')['Valor Empenhado'].sum().reset_index()
        evolucao_mensal['mes_ano_str'] = evolucao_mensal['mes_ano'].astype(str)
        
        fig_evolucao = px.line(
            evolucao_mensal,
            x='mes_ano_str',
            y='Valor Empenhado',
            title="Evolução Mensal dos Empenhos",
            labels={'mes_ano_str': 'Mês/Ano', 'Valor Empenhado': 'Valor (R$)'}
        )
        
        st.plotly_chart(fig_evolucao, use_container_width=True)
    
    # Tabela dos maiores fornecedores
    st.subheader("🏢 Maiores Fornecedores")
    
    fornecedores = despesas_df.groupby('Nome Fornecedor').agg({
        'Empenhado até Hoje': 'sum',
        'Liquidado até Hoje': 'sum',
        'Pago até Hoje': 'sum'
    }).reset_index()
    
    top_fornecedores = fornecedores.nlargest(15, 'Empenhado até Hoje')
    
    top_fornecedores['Empenhado até Hoje'] = top_fornecedores['Empenhado até Hoje'].apply(format_currency)
    top_fornecedores['Liquidado até Hoje'] = top_fornecedores['Liquidado até Hoje'].apply(format_currency)
    top_fornecedores['Pago até Hoje'] = top_fornecedores['Pago até Hoje'].apply(format_currency)
    
    top_fornecedores.columns = ['Fornecedor', 'Empenhado', 'Liquidado', 'Pago']
    st.dataframe(top_fornecedores, use_container_width=True)

# ==============================================================================
# COMPARAÇÃO PREVISTO VS REALIZADO
# ==============================================================================
elif opcao == "Comparação Previsto vs Realizado":
    st.header("📊 Comparação: Previsto vs Realizado")
    
    # Análise de receitas
    st.subheader("💰 Receitas: Previsão vs Arrecadação")
    
    # Principais categorias de receitas
    receitas_categoria = receitas_df.groupby(receitas_df['Código'].str[:4]).agg({
        'Prev. Atualizada': 'sum',
        'Arrec. Total': 'sum'
    }).reset_index()
    
    receitas_categoria['diferenca'] = receitas_categoria['Arrec. Total'] - receitas_categoria['Prev. Atualizada']
    receitas_categoria['execucao_pct'] = (receitas_categoria['Arrec. Total'] / 
                                        receitas_categoria['Prev. Atualizada'] * 100)
    
    # Mapear nomes das categorias
    categoria_nomes = {
        '1112': 'Impostos s/ Patrimônio', '1113': 'Impostos s/ Renda', '1114': 'Impostos s/ Serviços',
        '1121': 'Taxas Poder Polícia', '1122': 'Taxas por Serviços', '1321': 'Rendimentos Financeiros',
        '1335': 'Concessões', '1399': 'Outras Patrimoniais', '1699': 'Outros Serviços',
        '1711': 'Transferências União', '1712': 'Compensações Financeiras', '1713': 'SUS - União',
        '1714': 'FNDE', '1715': 'FUNDEB - União', '1716': 'FNAS', '1719': 'Outras - União',
        '1721': 'Transferências Estado', '1722': 'Royalties Estado', '1723': 'SUS - Estado',
        '1724': 'Convênios Estado', '1729': 'Outras - Estado', '1751': 'FUNDEB',
        '1911': 'Multas', '1922': 'Restituições', '1999': 'Outras Correntes', '2422': 'Transferências Capital'
    }
    
    receitas_categoria['nome'] = receitas_categoria['Código'].map(categoria_nomes)
    receitas_categoria = receitas_categoria.dropna(subset=['nome'])
    
    # Gráfico de comparação
    fig_comparacao_receitas = go.Figure()
    
    fig_comparacao_receitas.add_trace(go.Bar(
        name='Previsto',
        x=receitas_categoria['nome'],
        y=receitas_categoria['Prev. Atualizada'],
        marker_color='lightblue'
    ))
    
    fig_comparacao_receitas.add_trace(go.Bar(
        name='Arrecadado',
        x=receitas_categoria['nome'],
        y=receitas_categoria['Arrec. Total'],
        marker_color='darkblue'
    ))
    
    fig_comparacao_receitas.update_layout(
        title="Receitas: Previsto vs Arrecadado por Categoria",
        barmode='group',
        height=500,
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig_comparacao_receitas, use_container_width=True)
    
    # Tabela de comparação
    st.subheader("📋 Análise Detalhada por Categoria")
    
    comparacao_receitas = receitas_categoria[['nome', 'Prev. Atualizada', 'Arrec. Total', 'diferenca', 'execucao_pct']].copy()
    comparacao_receitas = comparacao_receitas.sort_values('execucao_pct', ascending=False)
    
    comparacao_receitas['Prev. Atualizada'] = comparacao_receitas['Prev. Atualizada'].apply(format_currency)
    comparacao_receitas['Arrec. Total'] = comparacao_receitas['Arrec. Total'].apply(format_currency)
    comparacao_receitas['diferenca'] = comparacao_receitas['diferenca'].apply(format_currency)
    comparacao_receitas['execucao_pct'] = comparacao_receitas['execucao_pct'].round(1).astype(str) + '%'
    
    comparacao_receitas.columns = ['Categoria', 'Previsto', 'Arrecadado', 'Diferença', 'Execução (%)']
    st.dataframe(comparacao_receitas, use_container_width=True)

# ==============================================================================
# ANÁLISE POR FUNÇÃO
# ==============================================================================
elif opcao == "Análise por Função":
    st.header("🏛️ Análise das Despesas por Função de Governo")
    
    # Análise detalhada por função
    funcoes_detalhadas = despesas_df.groupby(['Função', 'Nome da Função']).agg({
        'Dotação Atual': 'sum',
        'Empenhado até Hoje': 'sum',
        'Liquidado até Hoje': 'sum',
        'Pago até Hoje': 'sum'
    }).reset_index()
    
    funcoes_detalhadas['execucao_orcamentaria'] = (funcoes_detalhadas['Empenhado até Hoje'] / 
                                                 funcoes_detalhadas['Dotação Atual'] * 100)
    funcoes_detalhadas['execucao_financeira'] = (funcoes_detalhadas['Pago até Hoje'] / 
                                               funcoes_detalhadas['Empenhado até Hoje'] * 100)
    
    # Filtrar funções com valores significativos
    funcoes_principais = funcoes_detalhadas[funcoes_detalhadas['Empenhado até Hoje'] > 10000].copy()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Execução orçamentária por função
        fig_exec_orc = px.bar(
            funcoes_principais.sort_values('execucao_orcamentaria', ascending=True).tail(10),
            x='execucao_orcamentaria',
            y='Nome da Função',
            orientation='h',
            title="Execução Orçamentária por Função (%)",
            labels={'execucao_orcamentaria': 'Execução (%)', 'Nome da Função': 'Função'},
            color='execucao_orcamentaria',
            color_continuous_scale='RdYlGn'
        )
        
        st.plotly_chart(fig_exec_orc, use_container_width=True)
    
    with col2:
        # Execução financeira por função
        fig_exec_fin = px.bar(
            funcoes_principais.sort_values('execucao_financeira', ascending=True).tail(10),
            x='execucao_financeira',
            y='Nome da Função',
            orientation='h',
            title="Execução Financeira por Função (%)",
            labels={'execucao_financeira': 'Pagamento (%)', 'Nome da Função': 'Função'},
            color='execucao_financeira',
            color_continuous_scale='Blues'
        )
        
        st.plotly_chart(fig_exec_fin, use_container_width=True)
    
    # Análise dos principais gastos por função
    st.subheader("💰 Maiores Gastos por Área")
    
    # Selecionar função para análise detalhada
    funcao_selecionada = st.selectbox(
        "Selecione uma função para análise detalhada:",
        options=funcoes_principais.sort_values('Empenhado até Hoje', ascending=False)['Nome da Função'].tolist()
    )
    
    if funcao_selecionada:
        # Filtrar despesas da função selecionada
        despesas_funcao = despesas_df[despesas_df['Nome da Função'] == funcao_selecionada]
        
        # Análise por subfunção
        subfuncoes = despesas_funcao.groupby(['Subfunção', 'Nome da Subfunção']).agg({
            'Empenhado até Hoje': 'sum',
            'Liquidado até Hoje': 'sum',
            'Pago até Hoje': 'sum'
        }).reset_index()
        
        if not subfuncoes.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Distribuição por subfunção
                fig_subfuncao = px.pie(
                    subfuncoes,
                    values='Empenhado até Hoje',
                    names='Nome da Subfunção',
                    title=f"Distribuição de Gastos - {funcao_selecionada}"
                )
                st.plotly_chart(fig_subfuncao, use_container_width=True)
            
            with col2:
                # Principais fornecedores da função
                fornecedores_funcao = despesas_funcao.groupby('Nome Fornecedor')['Empenhado até Hoje'].sum().reset_index()
                top_fornecedores = fornecedores_funcao.nlargest(8, 'Empenhado até Hoje')
                
                fig_fornecedores = px.bar(
                    top_fornecedores,
                    x='Empenhado até Hoje',
                    y='Nome Fornecedor',
                    orientation='h',
                    title=f"Principais Fornecedores - {funcao_selecionada}",
                    labels={'Empenhado até Hoje': 'Valor (R$)', 'Nome Fornecedor': 'Fornecedor'}
                )
                
                fig_fornecedores.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_fornecedores, use_container_width=True)
    
    # Tabela resumo de todas as funções
    st.subheader("📊 Resumo por Função de Governo")
    
    resumo_funcoes = funcoes_detalhadas.copy()
    resumo_funcoes['Dotação Atual'] = resumo_funcoes['Dotação Atual'].apply(format_currency)
    resumo_funcoes['Empenhado até Hoje'] = resumo_funcoes['Empenhado até Hoje'].apply(format_currency)
    resumo_funcoes['Liquidado até Hoje'] = resumo_funcoes['Liquidado até Hoje'].apply(format_currency)
    resumo_funcoes['Pago até Hoje'] = resumo_funcoes['Pago até Hoje'].apply(format_currency)
    resumo_funcoes['execucao_orcamentaria'] = resumo_funcoes['execucao_orcamentaria'].round(1).astype(str) + '%'
    resumo_funcoes['execucao_financeira'] = resumo_funcoes['execucao_financeira'].round(1).astype(str) + '%'
    
    resumo_funcoes.columns = ['Código', 'Função', 'Dotação', 'Empenhado', 'Liquidado', 'Pago', 'Exec. Orç. (%)', 'Exec. Fin. (%)']
    st.dataframe(resumo_funcoes, use_container_width=True)

# ==============================================================================
# DETALHAMENTO
# ==============================================================================
elif opcao == "Detalhamento":
    st.header("🔍 Detalhamento Completo")
    
    # Tabs para receitas e despesas
    tab1, tab2 = st.tabs(["📈 Receitas Detalhadas", "📉 Despesas Detalhadas"])
    
    with tab1:
        st.subheader("Receitas - Busca e Filtros")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            valor_min_rec = st.number_input("Arrecadação mínima (R$)", min_value=0.0, value=0.0, key="rec_min")
        
        with col2:
            busca_rec = st.text_input("Buscar por descrição", key="busca_rec")
        
        with col3:
            apenas_com_arrecadacao = st.checkbox("Apenas com arrecadação", value=True)
        
        # Aplicar filtros às receitas
        receitas_filtradas = receitas_df.copy()
        
        if valor_min_rec > 0:
            receitas_filtradas = receitas_filtradas[receitas_filtradas['Arrec. Total'] >= valor_min_rec]
        
        if busca_rec:
            receitas_filtradas = receitas_filtradas[
                receitas_filtradas['Especificação'].str.contains(busca_rec, case=False, na=False)
            ]
        
        if apenas_com_arrecadacao:
            receitas_filtradas = receitas_filtradas[receitas_filtradas['Arrec. Total'] > 0]
        
        # Mostrar resultados das receitas
        st.write(f"**📊 Resultados: {len(receitas_filtradas)} receitas encontradas**")
        
        if not receitas_filtradas.empty:
            display_receitas = receitas_filtradas[['Código', 'Especificação', 'Prev. Atualizada', 'Arrec. Total']].copy()
            display_receitas['Execução (%)'] = (display_receitas['Arrec. Total'] / 
                                              display_receitas['Prev. Atualizada'] * 100).round(1)
            
            display_receitas['Prev. Atualizada'] = display_receitas['Prev. Atualizada'].apply(format_currency)
            display_receitas['Arrec. Total'] = display_receitas['Arrec. Total'].apply(format_currency)
            display_receitas['Execução (%)'] = display_receitas['Execução (%)'].astype(str) + '%'
            
            display_receitas.columns = ['Código', 'Descrição', 'Previsto', 'Arrecadado', 'Execução (%)']
            st.dataframe(display_receitas, use_container_width=True)
            
            # Estatísticas das receitas filtradas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Filtrado", format_currency(receitas_filtradas['Arrec. Total'].sum()))
            with col2:
                st.metric("Maior Arrecadação", format_currency(receitas_filtradas['Arrec. Total'].max()))
            with col3:
                execucao_media = (receitas_filtradas['Arrec. Total'].sum() / 
                                receitas_filtradas['Prev. Atualizada'].sum() * 100)
                st.metric("Execução Média", f"{execucao_media:.1f}%")
    
    with tab2:
        st.subheader("Despesas - Busca e Filtros")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            valor_min_desp = st.number_input("Valor mínimo (R$)", min_value=0.0, value=0.0, key="desp_min")
        
        with col2:
            funcao_filtro = st.selectbox(
                "Filtrar por função",
                options=['Todas'] + sorted(despesas_df['Nome da Função'].dropna().unique().tolist()),
                key="funcao_filtro"
            )
        
        with col3:
            fornecedor_filtro = st.text_input("Buscar fornecedor", key="fornecedor_filtro")
        
        with col4:
            periodo_inicio = st.date_input("Data início", value=None, key="data_inicio")
        
        # Aplicar filtros às despesas
        despesas_filtradas = despesas_df.copy()
        
        if valor_min_desp > 0:
            despesas_filtradas = despesas_filtradas[despesas_filtradas['Empenhado até Hoje'] >= valor_min_desp]
        
        if funcao_filtro and funcao_filtro != 'Todas':
            despesas_filtradas = despesas_filtradas[despesas_filtradas['Nome da Função'] == funcao_filtro]
        
        if fornecedor_filtro:
            despesas_filtradas = despesas_filtradas[
                despesas_filtradas['Nome Fornecedor'].str.contains(fornecedor_filtro, case=False, na=False)
            ]
        
        if periodo_inicio:
            despesas_filtradas = despesas_filtradas[despesas_filtradas['Data'] >= pd.Timestamp(periodo_inicio)]
        
        # Mostrar resultados das despesas
        st.write(f"**📊 Resultados: {len(despesas_filtradas)} empenhos encontrados**")
        
        if not despesas_filtradas.empty:
            display_despesas = despesas_filtradas[[
                'Empenho', 'Data', 'Nome Fornecedor', 'Nome da Função', 
                'Empenhado até Hoje', 'Liquidado até Hoje', 'Pago até Hoje'
            ]].copy()
            
            display_despesas['Empenhado até Hoje'] = display_despesas['Empenhado até Hoje'].apply(format_currency)
            display_despesas['Liquidado até Hoje'] = display_despesas['Liquidado até Hoje'].apply(format_currency)
            display_despesas['Pago até Hoje'] = display_despesas['Pago até Hoje'].apply(format_currency)
            
            display_despesas.columns = ['Empenho', 'Data', 'Fornecedor', 'Função', 'Empenhado', 'Liquidado', 'Pago']
            st.dataframe(display_despesas, use_container_width=True)
            
            # Estatísticas das despesas filtradas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Empenhado", format_currency(despesas_filtradas['Empenhado até Hoje'].sum()))
            with col2:
                st.metric("Total Pago", format_currency(despesas_filtradas['Pago até Hoje'].sum()))
            with col3:
                execucao_pagamento = (despesas_filtradas['Pago até Hoje'].sum() / 
                                    despesas_filtradas['Empenhado até Hoje'].sum() * 100)
                st.metric("% Pago", f"{execucao_pagamento:.1f}%")

# Insights finais
st.divider()
st.header("💡 Insights da Execução Orçamentária")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Indicadores Principais")
    
    # Comparação LOA vs Execução
    if execucao_vs_loa > 90:
        status_loa = "🟢 Excelente execução da LOA"
    elif execucao_vs_loa > 70:
        status_loa = "🟡 Boa execução da LOA"
    else:
        status_loa = "🔴 Execução baixa da LOA"
    
    st.write(f"**LOA vs Execução**: {execucao_vs_loa:.1f}% - {status_loa}")
    
    # Status da execução de receitas (portal transparência)
    if percentual_execucao_receitas > 90:
        status_rec = "🟢 Excelente execução"
    elif percentual_execucao_receitas > 70:
        status_rec = "🟡 Boa execução"
    else:
        status_rec = "🔴 Execução baixa"
    
    st.write(f"**Receitas (Portal)**: {percentual_execucao_receitas:.1f}% - {status_rec}")
    
    # Status do resultado orçamentário
    if resultado_orcamentario > 0:
        status_resultado = "🟢 Superávit orçamentário"
    else:
        status_resultado = "🔴 Déficit orçamentário"
    
    st.write(f"**Resultado**: {format_currency(resultado_orcamentario)} - {status_resultado}")
    
    # Liquidez dos empenhos
    liquidez = (total_pago_despesas / total_empenhado_despesas * 100) if total_empenhado_despesas > 0 else 0
    if liquidez > 80:
        status_liquidez = "🟢 Alta liquidez"
    elif liquidez > 60:
        status_liquidez = "🟡 Liquidez moderada"
    else:
        status_liquidez = "🔴 Baixa liquidez"
    
    st.write(f"**Liquidez**: {liquidez:.1f}% - {status_liquidez}")

with col2:
    st.subheader("📈 Principais Achados")
    
    # Comparação LOA vs Portal
    diferenca_loa_portal = total_arrecadado_receitas - total_loa_receitas
    if abs(diferenca_loa_portal) > total_loa_receitas * 0.1:  # Diferença > 10%
        if diferenca_loa_portal > 0:
            st.success(f"📈 **Arrecadação superou LOA** em {format_currency(diferenca_loa_portal)}")
        else:
            st.warning(f"📉 **Arrecadação abaixo da LOA** em {format_currency(abs(diferenca_loa_portal))}")
    else:
        st.info(f"⚖️ **Arrecadação próxima da LOA** - Diferença: {format_currency(diferenca_loa_portal)}")
    
    # Maior receita individual
    maior_receita = receitas_df.loc[receitas_df['Arrec. Total'].idxmax()]
    st.write(f"💰 **Maior receita**: {maior_receita['Especificação'][:40]}... - {format_currency(maior_receita['Arrec. Total'])}")
    
    # Função com maior gasto
    funcao_maior_gasto = despesas_df.groupby('Nome da Função')['Empenhado até Hoje'].sum().idxmax()
    valor_maior_gasto = despesas_df.groupby('Nome da Função')['Empenhado até Hoje'].sum().max()
    st.write(f"🏛️ **Função com maior gasto**: {funcao_maior_gasto} - {format_currency(valor_maior_gasto)}")
    
    # Maior fornecedor
    maior_fornecedor = despesas_df.groupby('Nome Fornecedor')['Empenhado até Hoje'].sum().idxmax()
    valor_maior_fornecedor = despesas_df.groupby('Nome Fornecedor')['Empenhado até Hoje'].sum().max()
    st.write(f"🏢 **Maior fornecedor**: {maior_fornecedor[:25]}... - {format_currency(valor_maior_fornecedor)}")

# Rodapé
st.divider()
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <p><strong>🏛️ Portal Transparência - Município de Rifaina</strong></p>
    <p>Análise Completa: LOA vs Execução Orçamentária 2025 | Dados atualizados em: {datetime.now().strftime('%d/%m/%Y')}</p>
    <p><em>Este dashboard apresenta análise comparativa entre o orçamento planejado (LOA) e a execução real das receitas e despesas.</em></p>
    <p><strong>Fontes:</strong> Lei Orçamentária Anual (LOA) + Portal de Transparência + Dados de Execução</p>
</div>
""", unsafe_allow_html=True)
