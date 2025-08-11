import streamlit as st
import csv
import json
from collections import defaultdict
import math

# Importações para gráficos interativos (Plotly)
try:
    import plotly.express as px
    import plotly.graph_objects as go
    import plotly.subplots as sp
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ Plotly não está disponível. Usando gráficos nativos do Streamlit.")

# Configuração da página
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar dados CSV sem pandas
def load_csv_data(filename):
    """Carrega dados CSV usando apenas bibliotecas padrão"""
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                data.append(row)
    except UnicodeDecodeError:
        with open(filename, 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                data.append(row)
    return data

# Função para formatar moeda
def format_currency(value):
    """Formata valores em moeda brasileira"""
    try:
        value = float(value)
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return "R$ 0,00"

# Função para converter string para float
def safe_float(value):
    """Converte string para float de forma segura"""
    try:
        return float(str(value).replace(',', '.'))
    except:
        return 0.0

# Função para criar gráfico simples usando Streamlit
def criar_grafico_simples(labels, values, title):
    """Cria um gráfico simples usando Streamlit"""
    if title:
        st.subheader(title)
    
    # Criar dados para o gráfico
    chart_data = {}
    for i, label in enumerate(labels):
        chart_data[label] = values[i]
    
    # Adicionar tooltip com informações
    st.markdown(f"""
    <div class="tooltip" style="margin-bottom: 1rem;">
        <span class="badge" style="cursor: pointer;">ℹ️ Informações do Gráfico</span>
        <span class="tooltiptext">
            Total de categorias: {len(labels)}<br>
            Valor máximo: {format_currency(max(values))}<br>
            Valor mínimo: {format_currency(min(values))}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    st.bar_chart(chart_data)

# Função para criar gráfico de linha simples
def criar_grafico_linha_simples(x, y, title):
    """Cria um gráfico de linha simples"""
    st.subheader(title)
    
    # Criar dados para o gráfico
    chart_data = {}
    for i, valor in enumerate(y):
        chart_data[f"Item {i+1}"] = valor
    
    st.line_chart(chart_data)

# Funções para gráficos interativos com Plotly
def criar_grafico_pizza_interativo(labels, values, title, colors=None):
    """Cria um gráfico de pizza interativo com Plotly"""
    if not PLOTLY_AVAILABLE:
        return criar_grafico_simples(labels, values, title)
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors or px.colors.qualitative.Set3,
        textinfo='label+percent+value',
        textposition='inside',
        insidetextorientation='radial'
    )])
    
    fig.update_layout(
        title=title,
        title_x=0.5,
        title_font_size=16,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    fig.update_traces(
        textfont_size=12,
        textinfo='label+percent',
        hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percent}<extra></extra>"
    )
    
    return fig

def criar_grafico_barras_interativo(labels, values, title, colors=None, orientation='v'):
    """Cria um gráfico de barras interativo com Plotly"""
    if not PLOTLY_AVAILABLE:
        return criar_grafico_simples(labels, values, title)
    
    if orientation == 'h':
        fig = go.Figure(data=[go.Bar(
            y=labels,
            x=values,
            orientation='h',
            marker_color=colors or px.colors.qualitative.Set3,
            text=[format_currency(v) for v in values],
            textposition='auto'
        )])
    else:
        fig = go.Figure(data=[go.Bar(
            x=labels,
            y=values,
            marker_color=colors or px.colors.qualitative.Set3,
            text=[format_currency(v) for v in values],
            textposition='auto'
        )])
    
    fig.update_layout(
        title=title,
        title_x=0.5,
        title_font_size=16,
        height=500,
        margin=dict(t=50, b=50, l=50, r=50),
        xaxis_title="Categorias" if orientation == 'v' else "Valores (R$)",
        yaxis_title="Valores (R$)" if orientation == 'v' else "Categorias"
    )
    
    fig.update_traces(
        hovertemplate="<b>%{x if orientation == 'v' else y}</b><br>Valor: R$ %{y if orientation == 'v' else x:,.2f}<extra></extra>"
    )
    
    return fig

def criar_grafico_linha_interativo(x, y, title, colors=None):
    """Cria um gráfico de linha interativo com Plotly"""
    if not PLOTLY_AVAILABLE:
        return criar_grafico_linha_simples(x, y, title)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='lines+markers',
        name='Valores',
        line=dict(color=colors or '#667eea', width=3),
        marker=dict(size=8, color=colors or '#667eea'),
        fill='tonexty',
        fillcolor='rgba(102, 126, 234, 0.1)'
    ))
    
    fig.update_layout(
        title=title,
        title_x=0.5,
        title_font_size=16,
        height=400,
        margin=dict(t=50, b=50, l=50, r=50),
        xaxis_title="Categorias",
        yaxis_title="Valores (R$)",
        hovermode='x unified'
    )
    
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>"
    )
    
    return fig

def criar_grafico_area_interativo(x, y, title, colors=None):
    """Cria um gráfico de área interativo com Plotly"""
    if not PLOTLY_AVAILABLE:
        return criar_grafico_linha_simples(x, y, title)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='lines',
        name='Valores',
        line=dict(color=colors or '#667eea', width=3),
        fill='tonexty',
        fillcolor='rgba(102, 126, 234, 0.3)'
    ))
    
    fig.update_layout(
        title=title,
        title_x=0.5,
        title_font_size=16,
        height=400,
        margin=dict(t=50, b=50, l=50, r=50),
        xaxis_title="Categorias",
        yaxis_title="Valores (R$)",
        hovermode='x unified'
    )
    
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>"
    )
    
    return fig

def criar_grafico_funnel_interativo(labels, values, title, colors=None):
    """Cria um gráfico funil interativo com Plotly"""
    if not PLOTLY_AVAILABLE:
        return criar_grafico_simples(labels, values, title)
    
    fig = go.Figure(go.Funnel(
        y=labels,
        x=values,
        textinfo="value+percent initial",
        marker=dict(color=colors or px.colors.qualitative.Set3),
        connector={"line": {"color": "royalblue", "width": 1}}
    ))
    
    fig.update_layout(
        title=title,
        title_x=0.5,
        title_font_size=16,
        height=500,
        margin=dict(t=50, b=50, l=50, r=50),
        showlegend=False
    )
    
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Valor: R$ %{x:,.2f}<extra></extra>"
    )
    
    return fig

def criar_grafico_gauge_interativo(value, max_value, title, colors=None):
    """Cria um gráfico gauge interativo com Plotly"""
    if not PLOTLY_AVAILABLE:
        return st.metric(title, format_currency(value))
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        delta={'reference': max_value * 0.5},
        gauge={
            'axis': {'range': [None, max_value]},
            'bar': {'color': colors or "#667eea"},
            'steps': [
                {'range': [0, max_value * 0.3], 'color': "lightgray"},
                {'range': [max_value * 0.3, max_value * 0.7], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.8
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig

def criar_grafico_treemap_interativo(labels, parents, values, title, colors=None):
    """Cria um gráfico treemap interativo com Plotly"""
    if not PLOTLY_AVAILABLE:
        return criar_grafico_simples(labels, values, title)
    
    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        marker_colors=colors or px.colors.qualitative.Set3,
        textinfo="label+value+percent parent+percent root"
    ))
    
    fig.update_layout(
        title=title,
        title_x=0.5,
        title_font_size=16,
        height=500,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percentParent:.1f}%<extra></extra>"
    )
    
    return fig

def criar_grafico_sunburst_interativo(labels, parents, values, title, colors=None):
    """Cria um gráfico sunburst interativo com Plotly"""
    if not PLOTLY_AVAILABLE:
        return criar_grafico_simples(labels, values, title)
    
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        marker_colors=colors or px.colors.qualitative.Set3,
        textinfo="label+value+percent parent"
    ))
    
    fig.update_layout(
        title=title,
        title_x=0.5,
        title_font_size=16,
        height=500,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percentParent:.1f}%<extra></extra>"
    )
    
    return fig

# Função para carregar dados dinamicamente
@st.cache_data(ttl=60)  # Cache por 60 segundos para permitir atualizações
def carregar_dados_dinamicos():
    """Carrega dados dos arquivos CSV com cache de 60 segundos"""
    import os
    from datetime import datetime
    
    try:
        receitas_orcadas = load_csv_data("download-123842.557.csv")
        estrutura_receitas = load_csv_data("download-123701.452.csv")
        
        if not receitas_orcadas or not estrutura_receitas:
            st.error("Erro ao carregar os dados. Verifique os arquivos CSV.")
            st.stop()
        
        # Verificar quando os arquivos foram modificados pela última vez
        try:
            stat_receitas = os.stat("download-123842.557.csv")
            stat_estrutura = os.stat("download-123701.452.csv")
            ultima_modificacao = max(stat_receitas.st_mtime, stat_estrutura.st_mtime)
            data_modificacao = datetime.fromtimestamp(ultima_modificacao).strftime("%d/%m/%Y %H:%M:%S")
        except:
            data_modificacao = "Não disponível"
            
        return receitas_orcadas, estrutura_receitas, data_modificacao
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        st.stop()

# Carregar dados com indicador animado
st.markdown("""
<div style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    text-align: center;
    color: white;
    animation: pulse 2s infinite;
">
    <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">🔄</div>
    <div style="font-weight: 600;">Carregando dados da LOA...</div>
</div>
""", unsafe_allow_html=True)

with st.spinner(""):
    receitas_orcadas, estrutura_receitas, data_modificacao = carregar_dados_dinamicos()

# Indicador de sucesso
st.markdown("""
<div style="
    background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
    padding: 1rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    text-align: center;
    color: white;
    animation: fadeIn 0.6s ease-out;
">
    <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">✅</div>
    <div style="font-weight: 600;">Dados carregados com sucesso!</div>
</div>
""", unsafe_allow_html=True)



# Função para detectar códigos dinamicamente
def detectar_codigos_dinamicos():
    """Detecta automaticamente todos os códigos de receita nas planilhas"""
    codigos_encontrados = set()
    for row in receitas_orcadas:
        codigo = row.get('CODRE', '')
        if codigo:
            codigos_encontrados.add(codigo[:4])  # Primeiros 4 dígitos
    return sorted(list(codigos_encontrados))

# Função para calcular dados dinamicamente
def calcular_dados_dinamicos():
    """Calcula todos os dados dinamicamente baseado nos arquivos CSV"""
    # Total do orçamento
    total_orcamento = sum(safe_float(row.get('TOTOR', 0)) for row in receitas_orcadas)
    
    # Detectar códigos dinamicamente
    codigos_tributarios = ['1112', '1113', '1114', '1121', '1122']
    codigos_transferencias = ['1711', '1712', '1713', '1714', '1716', '1721', '1722', '1723', '1724', '1751']
    
    # Calcular categorias principais dinamicamente
    receitas_tributarias = sum(
        safe_float(row.get('TOTOR', 0)) 
        for row in receitas_orcadas 
        if row.get('CODRE', '').startswith(tuple(codigos_tributarios))
    )
    
    transferencias = sum(
        safe_float(row.get('TOTOR', 0)) 
        for row in receitas_orcadas 
        if row.get('CODRE', '').startswith(tuple(codigos_transferencias))
    )
    
    outras_receitas = total_orcamento - receitas_tributarias - transferencias
    
    return {
        'total_orcamento': total_orcamento,
        'receitas_tributarias': receitas_tributarias,
        'transferencias': transferencias,
        'outras_receitas': outras_receitas,
        'codigos_detectados': detectar_codigos_dinamicos()
    }

# Calcular dados dinamicamente
dados = calcular_dados_dinamicos()
total_orcamento = dados['total_orcamento']
receitas_tributarias = dados['receitas_tributarias']
transferencias = dados['transferencias']
outras_receitas = dados['outras_receitas']

# Sidebar moderna
st.sidebar.markdown("""
<div style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    text-align: center;
    color: white;
">
    <h2 style="color: white; margin: 0; font-size: 1.5rem;">📊 Dashboard LOA</h2>
    <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">Município de Rifaina</p>
</div>
""", unsafe_allow_html=True)

# Botão para forçar atualização dos dados
if st.sidebar.button("🔄 Atualizar Dados", help="Força a atualização dos dados das planilhas"):
    st.cache_data.clear()
    st.rerun()

# Informações sobre os dados com cards modernos
st.sidebar.markdown("""
<div style="margin: 1rem 0;">
    <h3 style="color: #2c3e50; margin-bottom: 1rem;">📋 Informações Gerais</h3>
</div>
""", unsafe_allow_html=True)

# Métricas da sidebar
col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("📊 Receitas", len(receitas_orcadas))
with col2:
    st.metric("📋 Categorias", len(estrutura_receitas))

st.sidebar.metric("💰 Orçamento Total", format_currency(total_orcamento))

# Mostrar quando os dados foram carregados
st.sidebar.markdown(f"""
<div class="info-box" style="margin: 1rem 0;">
    <div style="font-weight: 600; margin-bottom: 0.5rem;">📅 Dados Carregados</div>
    <div style="font-size: 0.9rem;">{len(receitas_orcadas)} receitas orçadas</div>
    <div style="font-size: 0.9rem;">{len(estrutura_receitas)} categorias</div>
</div>
""", unsafe_allow_html=True)

# Mostrar quando os dados foram modificados pela última vez
st.sidebar.markdown(f"""
<div class="info-box" style="margin: 1rem 0;">
    <div style="font-weight: 600; margin-bottom: 0.5rem;">🕒 Última Atualização</div>
    <div style="font-size: 0.9rem;">{data_modificacao}</div>
</div>
""", unsafe_allow_html=True)

# Mostrar códigos detectados dinamicamente
dados_atualizados = calcular_dados_dinamicos()
st.sidebar.markdown(f"""
<div class="info-box" style="margin: 1rem 0;">
    <div style="font-weight: 600; margin-bottom: 0.5rem;">🔍 Códigos Detectados</div>
    <div style="font-size: 0.9rem;">{len(dados_atualizados['codigos_detectados'])} categorias únicas</div>
</div>
""", unsafe_allow_html=True)

# Menu de navegação
opcao = st.sidebar.selectbox(
    "📊 Escolha a análise:",
    ["Visão Geral", "Análise por Categoria", "Receitas Tributárias", "Transferências", "Detalhamento", "Estrutura de Receitas", "Códigos Detectados", "Documentação"]
)

# CSS personalizado moderno
st.markdown("""
<style>
/* Tema geral */
.main {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Cabeçalhos */
h1, h2, h3 {
    color: #2c3e50 !important;
    font-weight: 700 !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}

/* Cards de métricas */
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    backdrop-filter: blur(10px);
    transition: transform 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-5px);
}

/* Sidebar moderna */
.sidebar .sidebar-content {
    background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    color: white;
}

/* Botões personalizados */
.stButton > button {
    background: linear-gradient(45deg, #667eea, #764ba2);
    color: white;
    border: none;
    border-radius: 25px;
    padding: 0.5rem 2rem;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}

/* Caixas de informação */
.info-box {
    background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    margin: 1rem 0;
}

/* Gráficos */
.stPlotlyChart {
    border-radius: 15px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    overflow: hidden;
}

/* Tabelas */
.dataframe {
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

/* Animações */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.7; }
    100% { opacity: 1; }
}

@keyframes slideIn {
    from { transform: translateX(-100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

.fade-in {
    animation: fadeIn 0.6s ease-out;
}

.pulse {
    animation: pulse 2s infinite;
}

.slide-in {
    animation: slideIn 0.8s ease-out;
}

/* Scrollbar personalizada */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(45deg, #667eea, #764ba2);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(45deg, #764ba2, #667eea);
}

/* Cards de dados */
.data-card {
    background: white;
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    border: 1px solid rgba(0,0,0,0.05);
    margin: 1rem 0;
    transition: transform 0.3s ease;
}

.data-card:hover {
    transform: translateY(-3px);
}

/* Badges */
.badge {
    background: linear-gradient(45deg, #667eea, #764ba2);
    color: white;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
    margin: 0.2rem;
}

/* Progress bars */
.progress-bar {
    background: linear-gradient(90deg, #667eea, #764ba2);
    height: 8px;
    border-radius: 4px;
    transition: width 0.3s ease;
}

/* Tooltips */
.tooltip {
    position: relative;
    display: inline-block;
}

.tooltip .tooltiptext {
    visibility: hidden;
    width: 200px;
    background-color: #2c3e50;
    color: white;
    text-align: center;
    border-radius: 6px;
    padding: 5px;
    position: absolute;
    z-index: 1;
    bottom: 125%;
    left: 50%;
    margin-left: -100px;
    opacity: 0;
    transition: opacity 0.3s;
}

.tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# VISÃO GERAL
# ==============================================================================
if opcao == "Visão Geral":
    # Cabeçalho moderno com gradiente
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    ">
        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 700;">
            📈 Dashboard Orçamentário
        </h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Análise Completa da Lei Orçamentária Anual - Município de Rifaina
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Recalcular dados dinamicamente
    dados_atualizados = calcular_dados_dinamicos()
    
    # Métricas principais com cards modernos
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h2 style="text-align: center; color: #2c3e50; margin-bottom: 2rem;">
            📊 Métricas Principais
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">💰</div>
            <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">Orçamento Total</div>
            <div style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">{format_currency(dados_atualizados['total_orcamento'])}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Valor total previsto</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        percent_trib = (dados_atualizados['receitas_tributarias']/dados_atualizados['total_orcamento']*100) if dados_atualizados['total_orcamento'] > 0 else 0
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🏛️</div>
            <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">Receitas Tributárias</div>
            <div style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">{format_currency(dados_atualizados['receitas_tributarias'])}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">{percent_trib:.1f}% do total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        percent_transf = (dados_atualizados['transferencias']/dados_atualizados['total_orcamento']*100) if dados_atualizados['total_orcamento'] > 0 else 0
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔄</div>
            <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">Transferências</div>
            <div style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">{format_currency(dados_atualizados['transferencias'])}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">{percent_transf:.1f}% do total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        percent_outras = (dados_atualizados['outras_receitas']/dados_atualizados['total_orcamento']*100) if dados_atualizados['total_orcamento'] > 0 else 0
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📋</div>
            <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">Outras Receitas</div>
            <div style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">{format_currency(dados_atualizados['outras_receitas'])}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">{percent_outras:.1f}% do total</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Gráficos da visão geral com cards modernos
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h2 style="text-align: center; color: #2c3e50; margin-bottom: 2rem;">
            📊 Visualizações Interativas
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Card para composição do orçamento
        st.markdown("""
        <div class="data-card">
            <h3 style="color: #2c3e50; margin-bottom: 1rem; text-align: center;">
                🍰 Composição do Orçamento
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Criar dados para o gráfico
        labels = ['Receitas Tributárias', 'Transferências', 'Outras Receitas']
        values = [dados_atualizados['receitas_tributarias'], dados_atualizados['transferencias'], dados_atualizados['outras_receitas']]
        
        # Gráfico de pizza interativo
        fig_pizza = criar_grafico_pizza_interativo(
            labels, values, 
            "🍰 Composição do Orçamento por Categoria",
            colors=['#667eea', '#764ba2', '#f093fb']
        )
        st.plotly_chart(fig_pizza, use_container_width=True)
        
        # Mostrar dados em formato de tabela com badges
        st.markdown("""
        <div class="data-card">
            <h4 style="color: #2c3e50; margin-bottom: 1rem;">📋 Distribuição Detalhada</h4>
        </div>
        """, unsafe_allow_html=True)
        
        for i, (label, value) in enumerate(zip(labels, values)):
            percent = (value / dados_atualizados['total_orcamento'] * 100) if dados_atualizados['total_orcamento'] > 0 else 0
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                padding: 1rem;
                border-radius: 10px;
                margin: 0.5rem 0;
                border-left: 4px solid #667eea;
            ">
                <div style="font-weight: 600; color: #2c3e50; margin-bottom: 0.5rem;">{label}</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #667eea; margin-bottom: 0.5rem;">{format_currency(value)}</div>
                <span class="badge">{percent:.1f}% do total</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Card para gráfico de barras
        st.markdown("""
        <div class="data-card">
            <h3 style="color: #2c3e50; margin-bottom: 1rem; text-align: center;">
                📊 Comparação por Categoria
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Gráfico de barras interativo
        fig_barras = criar_grafico_barras_interativo(
            labels, values, 
            "📊 Comparação por Categoria",
            colors=['#667eea', '#764ba2', '#f093fb']
        )
        st.plotly_chart(fig_barras, use_container_width=True)
    
    # Gráfico de área cumulativa com card moderno
    st.markdown("""
    <div class="data-card" style="margin: 2rem 0;">
        <h3 style="color: #2c3e50; margin-bottom: 1rem; text-align: center;">
            📊 Composição Cumulativa do Orçamento
        </h3>
        <p style="color: #6c757d; text-align: center; margin-bottom: 1.5rem;">
            Visualização da distribuição acumulativa dos recursos orçamentários
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Criar dados para gráfico de área
    categorias_area = ['Receitas Tributárias', 'Transferências', 'Outras Receitas']
    valores_area = [dados_atualizados['receitas_tributarias'], dados_atualizados['transferencias'], dados_atualizados['outras_receitas']]
    
    # Gráfico de área interativo
    fig_area = criar_grafico_area_interativo(
        categorias_area, valores_area, 
        "📊 Composição Cumulativa do Orçamento",
        colors='#667eea'
    )
    st.plotly_chart(fig_area, use_container_width=True)
    
    # Medidores de composição com progress bars modernos
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h2 style="text-align: center; color: #2c3e50; margin-bottom: 2rem;">
            📊 Medidores de Composição
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        percent_tributarias = (dados_atualizados['receitas_tributarias'] / dados_atualizados['total_orcamento'] * 100) if dados_atualizados['total_orcamento'] > 0 else 0
        
        # Gráfico gauge interativo
        fig_gauge_trib = criar_grafico_gauge_interativo(
            percent_tributarias, 100, 
            "🏛️ Receitas Tributárias",
            colors='#667eea'
        )
        st.plotly_chart(fig_gauge_trib, use_container_width=True)
        
        st.markdown(f"""
        <div style="text-align: center; margin-top: 1rem;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #667eea;">{format_currency(dados_atualizados['receitas_tributarias'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        percent_transf = (dados_atualizados['transferencias'] / dados_atualizados['total_orcamento'] * 100) if dados_atualizados['total_orcamento'] > 0 else 0
        
        # Gráfico gauge interativo
        fig_gauge_transf = criar_grafico_gauge_interativo(
            percent_transf, 100, 
            "🔄 Transferências",
            colors='#764ba2'
        )
        st.plotly_chart(fig_gauge_transf, use_container_width=True)
        
        st.markdown(f"""
        <div style="text-align: center; margin-top: 1rem;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #764ba2;">{format_currency(dados_atualizados['transferencias'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        percent_outras = (dados_atualizados['outras_receitas'] / dados_atualizados['total_orcamento'] * 100) if dados_atualizados['total_orcamento'] > 0 else 0
        
        # Gráfico gauge interativo
        fig_gauge_outras = criar_grafico_gauge_interativo(
            percent_outras, 100, 
            "📋 Outras Receitas",
            colors='#f093fb'
        )
        st.plotly_chart(fig_gauge_outras, use_container_width=True)
        
        st.markdown(f"""
        <div style="text-align: center; margin-top: 1rem;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #f093fb;">{format_currency(dados_atualizados['outras_receitas'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Seção Top 10 com design moderno
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h2 style="text-align: center; color: #2c3e50; margin-bottom: 2rem;">
            🔝 Top 10 Maiores Receitas
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Gráfico funil interativo para fluxo de receitas
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h3 style="text-align: center; color: #2c3e50; margin-bottom: 1rem;">
            🗜️ Fluxo de Receitas (Funil)
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Criar dados para o funil
    labels_funil = ['Total Orçamento', 'Receitas Tributárias', 'Transferências', 'Outras Receitas']
    values_funil = [
        dados_atualizados['total_orcamento'],
        dados_atualizados['receitas_tributarias'],
        dados_atualizados['transferencias'],
        dados_atualizados['outras_receitas']
    ]
    
    fig_funil = criar_grafico_funnel_interativo(
        labels_funil, values_funil,
        "🗜️ Fluxo de Receitas Orçamentárias",
        colors=['#667eea', '#764ba2', '#f093fb', '#4facfe']
    )
    st.plotly_chart(fig_funil, use_container_width=True)
    
    # Ordenar receitas por valor
    sorted_receitas = sorted(
        receitas_orcadas, 
        key=lambda x: safe_float(x.get('TOTOR', 0)), 
        reverse=True
    )[:10]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Criar gráfico de barras para Top 10 usando Streamlit
        if sorted_receitas:
            nomes_top10 = [receita.get('NOME', 'Sem descrição')[:20] + '...' if len(receita.get('NOME', 'Sem descrição')) > 20 else receita.get('NOME', 'Sem descrição') for receita in sorted_receitas]
            valores_top10 = [safe_float(receita.get('TOTOR', 0)) for receita in sorted_receitas]
            
            # Gráfico de barras usando Streamlit
            chart_data_top10 = {}
            for i, nome in enumerate(nomes_top10):
                chart_data_top10[nome] = valores_top10[i]
            
            # Gráfico de barras horizontal interativo para Top 10
            fig_top10 = criar_grafico_barras_interativo(
                nomes_top10, valores_top10, 
                "🔝 Top 10 Maiores Receitas",
                colors=px.colors.qualitative.Set3,
                orientation='h'
            )
            st.plotly_chart(fig_top10, use_container_width=True)
    
    with col2:
        # Lista detalhada com cards modernos
        st.markdown("""
        <div class="data-card">
            <h3 style="color: #2c3e50; margin-bottom: 1rem; text-align: center;">
                📋 Ranking Detalhado
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        for i, receita in enumerate(sorted_receitas, 1):
            nome = receita.get('NOME', 'Sem descrição')
            valor = safe_float(receita.get('TOTOR', 0))
            percent = (valor / dados_atualizados['total_orcamento'] * 100) if dados_atualizados['total_orcamento'] > 0 else 0
            
            # Cor baseada na posição
            if i == 1:
                color = "#FFD700"  # Ouro
                emoji = "🥇"
            elif i == 2:
                color = "#C0C0C0"  # Prata
                emoji = "🥈"
            elif i == 3:
                color = "#CD7F32"  # Bronze
                emoji = "🥉"
            else:
                color = "#667eea"
                emoji = f"#{i}"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {color}20 0%, {color}10 100%);
                padding: 1rem;
                border-radius: 10px;
                margin: 0.5rem 0;
                border-left: 4px solid {color};
            ">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.2rem; margin-right: 0.5rem;">{emoji}</span>
                    <span style="font-weight: 600; color: #2c3e50;">{nome[:30]}{'...' if len(nome) > 30 else ''}</span>
                </div>
                <div style="font-size: 1.1rem; font-weight: 700; color: {color}; margin-bottom: 0.5rem;">{format_currency(valor)}</div>
                <span class="badge">{percent:.1f}% do total</span>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# ANÁLISE POR CATEGORIA
# ==============================================================================
elif opcao == "Análise por Categoria":
    st.header("📊 Análise por Categoria de Receita")
    
    # Agrupar receitas por nível hierárquico
    nivel1_data = defaultdict(float)
    
    for row in receitas_orcadas:
        codigo = row.get('CODRE', '')
        valor = safe_float(row.get('TOTOR', 0))
        if codigo:
            nivel1 = codigo[:4]
            nivel1_data[nivel1] += valor
    
    # Mapear códigos para nomes mais legíveis
    codigo_nomes = {
        '1112': 'Impostos sobre Patrimônio',
        '1113': 'Impostos sobre Renda',
        '1114': 'Impostos sobre Serviços',
        '1121': 'Taxas pelo Poder de Polícia',
        '1122': 'Taxas pelos Serviços',
        '1241': 'Contribuições de Melhoria',
        '1311': 'Exploração do Patrimônio',
        '1321': 'Remuneração de Depósitos',
        '1611': 'Serviços Administrativos',
        '1699': 'Outros Serviços',
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
    
    # Mostrar distribuição hierárquica
    st.subheader("🌳 Distribuição Hierárquica das Receitas")
    
    # Recalcular dados dinamicamente
    dados_atualizados = calcular_dados_dinamicos()
    
    # Ordenar por valor
    sorted_nivel1 = sorted(nivel1_data.items(), key=lambda x: x[1], reverse=True)
    
    # Criar dados para o treemap
    treemap_labels = []
    treemap_parents = []
    treemap_values = []
    
    for codigo, valor in sorted_nivel1:
        nome = codigo_nomes.get(codigo, f"Código {codigo}")
        treemap_labels.append(nome)
        treemap_parents.append("Orçamento Total")
        treemap_values.append(valor)
    
    # Gráfico treemap interativo para distribuição hierárquica
    if treemap_values:
        st.markdown("""
        <div style="margin: 2rem 0;">
            <h3 style="text-align: center; color: #2c3e50; margin-bottom: 1rem;">
                🌳 Distribuição Hierárquica das Receitas
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Criar gráfico treemap interativo
        fig_treemap = criar_grafico_treemap_interativo(
            treemap_labels, treemap_parents, treemap_values,
            "🌳 Distribuição Hierárquica das Receitas",
            colors=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_treemap, use_container_width=True)
        
        # Gráfico sunburst interativo
        st.markdown("""
        <div style="margin: 2rem 0;">
            <h3 style="text-align: center; color: #2c3e50; margin-bottom: 1rem;">
                ☀️ Visualização Sunburst das Receitas
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        fig_sunburst = criar_grafico_sunburst_interativo(
            treemap_labels, treemap_parents, treemap_values,
            "☀️ Visualização Hierárquica Sunburst",
            colors=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_sunburst, use_container_width=True)
    
    # Lista detalhada
    st.subheader("📋 Detalhamento por Categoria")
    for codigo, valor in sorted_nivel1:
        nome = codigo_nomes.get(codigo, f"Código {codigo}")
        percent = (valor / dados_atualizados['total_orcamento'] * 100) if dados_atualizados['total_orcamento'] > 0 else 0
        st.write(f"• **{nome}**: {format_currency(valor)} ({percent:.1f}%)")
    
    # Tabela detalhada
    st.subheader("📋 Detalhamento por Categoria")
    
    categoria_detalhes = []
    for codigo, valor in sorted_nivel1:
        nome = codigo_nomes.get(codigo, f"Código {codigo}")
        participacao = (valor / dados_atualizados['total_orcamento']) * 100
        categoria_detalhes.append({
            'Código': codigo,
            'Categoria': nome,
            'Valor (R$)': format_currency(valor),
            'Participação (%)': f"{participacao:.2f}%"
        })
    
    # Mostrar como tabela
    if categoria_detalhes:
        st.write("| Código | Categoria | Valor (R$) | Participação (%) |")
        st.write("|--------|-----------|------------|------------------|")
        for item in categoria_detalhes:
            st.write(f"| {item['Código']} | {item['Categoria']} | {item['Valor (R$)']} | {item['Participação (%)']} |")

# ==============================================================================
# RECEITAS TRIBUTÁRIAS
# ==============================================================================
elif opcao == "Receitas Tributárias":
    st.header("🏛️ Análise das Receitas Tributárias")
    
    # Filtrar apenas receitas tributárias
    tributarias = [
        row for row in receitas_orcadas
        if row.get('CODRE', '').startswith(('1112', '1113', '1114', '1121', '1122'))
    ]
    
    if tributarias:
        col1, col2 = st.columns(2)
        
        with col1:
            # Análise por tipo de tributo
            tributos_tipo = {
                'IPTU': sum(safe_float(row.get('TOTOR', 0)) for row in tributarias if row.get('CODRE', '').startswith('1112.5')),
                'ITBI': sum(safe_float(row.get('TOTOR', 0)) for row in tributarias if row.get('CODRE', '').startswith('1112.53')),
                'IRRF': sum(safe_float(row.get('TOTOR', 0)) for row in tributarias if row.get('CODRE', '').startswith('1113')),
                'ISSQN': sum(safe_float(row.get('TOTOR', 0)) for row in tributarias if row.get('CODRE', '').startswith('1114')),
                'Taxas': sum(safe_float(row.get('TOTOR', 0)) for row in tributarias if row.get('CODRE', '').startswith(('1121', '1122')))
            }
            
            # Recalcular dados dinamicamente
            dados_atualizados = calcular_dados_dinamicos()
            
            st.subheader("📊 Receitas por Tipo de Tributo")
            
            # Criar gráfico de pizza interativo para tributos
            if tributos_tipo:
                labels_tributos = list(tributos_tipo.keys())
                values_tributos = list(tributos_tipo.values())
                
                # Gráfico de pizza interativo
                fig_tributos = criar_grafico_pizza_interativo(
                    labels_tributos, values_tributos,
                    "🏛️ Distribuição por Tipo de Tributo",
                    colors=['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b']
                )
                st.plotly_chart(fig_tributos, use_container_width=True)
            
            # Lista detalhada
            for tipo, valor in tributos_tipo.items():
                percent = (valor / dados_atualizados['receitas_tributarias'] * 100) if dados_atualizados['receitas_tributarias'] > 0 else 0
                st.write(f"• **{tipo}**: {format_currency(valor)} ({percent:.1f}%)")
        
        with col2:
            # Distribuição IPTU
            iptu_detalhes = [row for row in tributarias if row.get('CODRE', '').startswith('1112.5')]
            
            if iptu_detalhes:
                st.subheader("🏠 Detalhamento do IPTU")
                for receita in iptu_detalhes:
                    nome = receita.get('NOME', 'Sem descrição')
                    valor = safe_float(receita.get('TOTOR', 0))
                    st.write(f"• **{nome}**: {format_currency(valor)}")
        
        # Tabela de tributárias
        st.subheader("📋 Detalhamento das Receitas Tributárias")
        
        for receita in tributarias:
            nome = receita.get('NOME', 'Sem descrição')
            valor = safe_float(receita.get('TOTOR', 0))
            st.write(f"• **{nome}**: {format_currency(valor)}")
    else:
        st.warning("Nenhuma receita tributária encontrada nos dados.")

# ==============================================================================
# TRANSFERÊNCIAS
# ==============================================================================
elif opcao == "Transferências":
    st.header("🔄 Análise das Transferências")
    
    # Filtrar transferências
    transf = [
        row for row in receitas_orcadas
        if row.get('CODRE', '').startswith(('1711', '1712', '1713', '1714', '1716', '1721', '1722', '1723', '1724', '1751'))
    ]
    
    if transf:
        # Separar por origem
        transf_uniao = sum(
            safe_float(row.get('TOTOR', 0)) 
            for row in transf 
            if row.get('CODRE', '').startswith(('1711', '1712', '1713', '1714', '1716', '1719'))
        )
        transf_estado = sum(
            safe_float(row.get('TOTOR', 0)) 
            for row in transf 
            if row.get('CODRE', '').startswith(('1721', '1722', '1723', '1724', '1729'))
        )
        fundeb = sum(
            safe_float(row.get('TOTOR', 0)) 
            for row in transf 
            if row.get('CODRE', '').startswith('1751')
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🏛️ União", format_currency(transf_uniao))
        with col2:
            st.metric("🏛️ Estado", format_currency(transf_estado))
        with col3:
            st.metric("🎓 FUNDEB", format_currency(fundeb))
        
        # Gráficos interativos para transferências
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de pizza interativo para transferências
            labels_transf = ['União', 'Estado', 'FUNDEB']
            values_transf = [transf_uniao, transf_estado, fundeb]
            
            fig_pizza_transf = criar_grafico_pizza_interativo(
                labels_transf, values_transf,
                "🔄 Transferências por Origem",
                colors=['#667eea', '#764ba2', '#f093fb']
            )
            st.plotly_chart(fig_pizza_transf, use_container_width=True)
        
        with col2:
            # Gráfico de barras interativo para transferências
            fig_barras_transf = criar_grafico_barras_interativo(
                labels_transf, values_transf,
                "📊 Comparação de Transferências",
                colors=['#667eea', '#764ba2', '#f093fb']
            )
            st.plotly_chart(fig_barras_transf, use_container_width=True)
        
        # Lista detalhada
        st.write(f"• **União**: {format_currency(transf_uniao)}")
        st.write(f"• **Estado**: {format_currency(transf_estado)}")
        st.write(f"• **FUNDEB**: {format_currency(fundeb)}")
        
        # Principais transferências
        st.subheader("🔝 Principais Transferências")
        
        # Ordenar por valor
        sorted_transf = sorted(transf, key=lambda x: safe_float(x.get('TOTOR', 0)), reverse=True)[:15]
        
        # Gráfico interativo para principais transferências
        if sorted_transf:
            nomes_transf = [receita.get('NOME', 'Sem descrição')[:30] + '...' if len(receita.get('NOME', 'Sem descrição')) > 30 else receita.get('NOME', 'Sem descrição') for receita in sorted_transf]
            valores_transf = [safe_float(receita.get('TOTOR', 0)) for receita in sorted_transf]
            
            # Gráfico de barras horizontal interativo
            fig_transf_principais = criar_grafico_barras_interativo(
                nomes_transf, valores_transf,
                "🔝 Top 15 Principais Transferências",
                colors=px.colors.qualitative.Set3,
                orientation='h'
            )
            st.plotly_chart(fig_transf_principais, use_container_width=True)
        
        # Lista detalhada
        for i, receita in enumerate(sorted_transf, 1):
            nome = receita.get('NOME', 'Sem descrição')
            valor = safe_float(receita.get('TOTOR', 0))
            st.write(f"{i}. **{nome}**: {format_currency(valor)}")
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
        dados_filtrados = [
            row for row in dados_filtrados 
            if safe_float(row.get('TOTOR', 0)) >= valor_min
        ]
    
    if busca:
        dados_filtrados = [
            row for row in dados_filtrados
            if busca.lower() in row.get('NOME', '').lower()
        ]
    
    # Mostrar resultados
    st.subheader(f"📊 Resultados ({len(dados_filtrados)} registros)")
    
    if dados_filtrados:
        # Ordenar por valor
        dados_filtrados.sort(key=lambda x: safe_float(x.get('TOTOR', 0)), reverse=True)
        
        # Gráfico interativo para dados filtrados (top 20)
        if len(dados_filtrados) > 0:
            top_20 = dados_filtrados[:20]
            nomes_filtrados = [receita.get('NOME', 'Sem descrição')[:25] + '...' if len(receita.get('NOME', 'Sem descrição')) > 25 else receita.get('NOME', 'Sem descrição') for receita in top_20]
            valores_filtrados = [safe_float(receita.get('TOTOR', 0)) for receita in top_20]
            
            # Gráfico de barras horizontal interativo
            fig_filtrados = criar_grafico_barras_interativo(
                nomes_filtrados, valores_filtrados,
                f"📊 Top 20 Maiores Valores ({len(dados_filtrados)} registros filtrados)",
                colors=px.colors.qualitative.Set3,
                orientation='h'
            )
            st.plotly_chart(fig_filtrados, use_container_width=True)
        
        # Mostrar dados em formato de tabela
        st.subheader("📋 Lista Detalhada")
        for receita in dados_filtrados:
            codigo = receita.get('CODRE', '')
            nome = receita.get('NOME', 'Sem descrição')
            valor = safe_float(receita.get('TOTOR', 0))
            st.write(f"• **{codigo} - {nome}**: {format_currency(valor)}")
        
        # Estatísticas dos dados filtrados
        total_filtrado = sum(safe_float(row.get('TOTOR', 0)) for row in dados_filtrados)
        valores = [safe_float(row.get('TOTOR', 0)) for row in dados_filtrados if safe_float(row.get('TOTOR', 0)) > 0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Filtrado", format_currency(total_filtrado))
        with col2:
            if valores:
                st.metric("Maior Valor", format_currency(max(valores)))
        with col3:
            if valores:
                st.metric("Menor Valor", format_currency(min(valores)))
        
        # Gráfico de linha interativo para distribuição dos valores
        if valores and len(valores) > 1:
            st.markdown("""
            <div style="margin: 2rem 0;">
                <h3 style="text-align: center; color: #2c3e50; margin-bottom: 1rem;">
                    📈 Distribuição dos Valores
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Criar gráfico de linha interativo
            x_values = [f"Item {i+1}" for i in range(len(valores))]
            fig_distribuicao = criar_grafico_linha_interativo(
                x_values, valores,
                "📈 Distribuição dos Valores Filtrados",
                colors='#667eea'
            )
            st.plotly_chart(fig_distribuicao, use_container_width=True)
    else:
        st.warning("Nenhum registro encontrado com os filtros aplicados.")

# ==============================================================================
# ESTRUTURA DE RECEITAS
# ==============================================================================
elif opcao == "Estrutura de Receitas":
    st.header("📋 Estrutura de Receitas")
    
    st.info("Este arquivo contém a estrutura hierárquica das receitas com códigos e descrições.")
    
    # Mostrar primeiros registros da estrutura
    st.subheader("Primeiros 20 registros da estrutura:")
    
    for i, row in enumerate(estrutura_receitas[:20], 1):
        codigo = row.get('CODRE', '')
        nome = row.get('NOMRE', '')
        nivel = row.get('NIVEL', '')
        st.write(f"{i}. **{codigo}** - {nome} (Nível: {nivel})")
    
    # Estatísticas da estrutura
    st.subheader("📊 Estatísticas da Estrutura")
    
    # Contar por nível
    niveis = defaultdict(int)
    for row in estrutura_receitas:
        nivel = row.get('NIVEL', '')
        if nivel:
            niveis[nivel] += 1
    
    # Criar gráfico de barras para distribuição por nível
    if niveis:
        niveis_labels = [f"Nível {nivel}" for nivel in sorted(niveis.keys())]
        niveis_values = [niveis[nivel] for nivel in sorted(niveis.keys())]
        
        # Gráfico de barras usando Streamlit
        chart_data_niveis = {}
        for i, nivel in enumerate(niveis_labels):
            chart_data_niveis[nivel] = niveis_values[i]
        
        st.subheader("📊 Distribuição por Nível Hierárquico")
        st.bar_chart(chart_data_niveis)
    
    st.write("**Distribuição por Nível:**")
    for nivel in sorted(niveis.keys()):
        st.write(f"• Nível {nivel}: {niveis[nivel]} registros")
    
    # Mostrar códigos únicos
    codigos_unicos = set()
    for row in estrutura_receitas:
        codigo = row.get('CODRE', '')
        if codigo:
            codigos_unicos.add(codigo[:4])  # Primeiros 4 dígitos
    
    st.write(f"**Códigos únicos (primeiros 4 dígitos):** {len(codigos_unicos)}")
    
    # Mostrar alguns códigos principais
    st.write("**Principais códigos:**")
    for codigo in sorted(list(codigos_unicos))[:10]:
        st.write(f"• {codigo}")

# ==============================================================================
# CÓDIGOS DETECTADOS
# ==============================================================================
elif opcao == "Códigos Detectados":
    st.header("🔍 Códigos Detectados Dinamicamente")
    
    # Recalcular dados dinamicamente
    dados_atualizados = calcular_dados_dinamicos()
    codigos_detectados = dados_atualizados['codigos_detectados']
    
    st.info(f"📊 **Total de códigos únicos detectados:** {len(codigos_detectados)}")
    
    # Mostrar todos os códigos detectados
    st.subheader("📋 Todos os Códigos Encontrados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Códigos Tributários:**")
        for codigo in codigos_detectados:
            if codigo.startswith(('1112', '1113', '1114', '1121', '1122')):
                st.write(f"• **{codigo}** - {codigo_nomes.get(codigo, 'Código tributário')}")
    
    with col2:
        st.write("**Códigos de Transferências:**")
        for codigo in codigos_detectados:
            if codigo.startswith(('1711', '1712', '1713', '1714', '1716', '1721', '1722', '1723', '1724', '1751')):
                st.write(f"• **{codigo}** - {codigo_nomes.get(codigo, 'Código de transferência')}")
    
    # Outros códigos
    outros_codigos = [codigo for codigo in codigos_detectados 
                     if not codigo.startswith(('1112', '1113', '1114', '1121', '1122', '1711', '1712', '1713', '1714', '1716', '1721', '1722', '1723', '1724', '1751'))]
    
    if outros_codigos:
        st.subheader("🔍 Outros Códigos Detectados")
        for codigo in outros_codigos:
            st.write(f"• **{codigo}** - {codigo_nomes.get(codigo, 'Código não categorizado')}")
    
    # Estatísticas
    st.subheader("📊 Estatísticas dos Códigos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tributarios = len([c for c in codigos_detectados if c.startswith(('1112', '1113', '1114', '1121', '1122'))])
        st.metric("Códigos Tributários", tributarios)
    
    with col2:
        transferencias = len([c for c in codigos_detectados if c.startswith(('1711', '1712', '1713', '1714', '1716', '1721', '1722', '1723', '1724', '1751'))])
        st.metric("Códigos de Transferências", transferencias)
    
    with col3:
        outros = len(outros_codigos)
        st.metric("Outros Códigos", outros)
    
    # Gráfico de barras para distribuição dos códigos
    if codigos_detectados:
        labels_codigos = ['Tributários', 'Transferências', 'Outros']
        values_codigos = [tributarios, transferencias, outros]
        
        # Gráfico de barras usando Streamlit
        chart_data_codigos = {}
        for i, categoria in enumerate(labels_codigos):
            chart_data_codigos[categoria] = values_codigos[i]
        
        st.subheader("📊 Distribuição dos Códigos por Categoria")
        st.bar_chart(chart_data_codigos)

# ==============================================================================
# DOCUMENTAÇÃO
# ==============================================================================
elif opcao == "Documentação":
    st.header("📚 Documentação do Dashboard")
    
    st.markdown("""
    ## 📊 Análise da Lei Orçamentária Anual
    
    Este dashboard interativo fornece uma análise completa da Lei Orçamentária Anual (LOA) do Município de Rifaina, 
    desenvolvido em Python com Streamlit.
    
    ## 🚀 Funcionalidades
    
    ### 📈 Visão Geral
    - **Métricas principais** do orçamento total
    - **Composição por categorias** (Receitas Tributárias, Transferências, Outras)
    - **Gráfico de pizza** com distribuição proporcional
    - **Top 10 maiores receitas** previstas
    
    ### 📊 Análise por Categoria
    - **Treemap hierárquico** das receitas
    - **Tabela detalhada** com códigos e participação percentual
    - **Agrupamento por nível** hierárquico da classificação orçamentária
    
    ### 🏛️ Receitas Tributárias
    - **Análise por tipo de tributo** (IPTU, ITBI, IRRF, ISSQN, Taxas)
    - **Gráficos específicos** para cada categoria
    - **Detalhamento completo** das receitas tributárias
    
    ### 🔄 Transferências
    - **Separação por origem** (União, Estado, FUNDEB)
    - **Principais transferências** em ranking
    - **Métricas por fonte** de transferência
    
    ### 🔍 Detalhamento
    - **Filtros interativos** por valor mínimo e descrição
    - **Busca textual** nas descrições
    - **Estatísticas dinâmicas** dos dados filtrados
    """)
    
    st.markdown("""
    ## 📁 Estrutura dos Dados
    
    ### Arquivo 1: `download-123842.557.csv`
    Receitas orçadas com as seguintes colunas principais:
    - `NOME`: Descrição da receita
    - `FICHA`: Número da ficha
    - `CODRE`: Código da receita
    - `TOTOR`: Valor orçado
    - `NIVEL`: Nível hierárquico
    - `FONTE`: Fonte de recursos
    
    ### Arquivo 2: `download-123701.452.csv`
    Estrutura hierárquica das receitas:
    - `CODRE`: Código da receita
    - `NOMRE`: Nome da receita
    - `NIVEL`: Nível na hierarquia
    - `COD_TCE`: Código do Tribunal de Contas
    """)
    
    st.markdown("""
    ## 🛠️ Como Executar
    
    ### Pré-requisitos
    ```bash
    pip install streamlit
    ```
    
    ### Execução
    ```bash
    streamlit run app_simple.py
    ```
    
    A aplicação estará disponível em `http://localhost:8501`
    """)
    
    st.markdown("""
    ## 📋 Categorias de Receita
    
    ### Códigos de Classificação
    - **1112**: Impostos sobre Patrimônio (IPTU, ITBI)
    - **1113**: Impostos sobre Renda (IRRF)
    - **1114**: Impostos sobre Serviços (ISSQN)
    - **1121**: Taxas pelo Poder de Polícia
    - **1122**: Taxas pelos Serviços
    - **1711-1719**: Transferências da União
    - **1721-1729**: Transferências do Estado
    - **1751**: FUNDEB
    """)
    
    st.markdown("""
    ## 📊 Principais Insights
    
    ### Composição Orçamentária
    O orçamento de Rifaina é composto principalmente por:
    1. **Transferências constitucionais** (FPM, ICMS, IPVA)
    2. **Receitas tributárias próprias** (IPTU, ISSQN, Taxas)
    3. **Transferências específicas** (SUS, Educação, Assistência Social)
    
    ### Principais Fontes de Receita
    - **FPM** (Fundo de Participação dos Municípios)
    - **ICMS** (Cota-parte do Estado)
    - **FUNDEB** (Educação)
    - **SUS** (Transferências da saúde)
    - **ISSQN** (Imposto sobre serviços)
    """)
    
    st.markdown("""
    ## 🎯 Funcionalidades Técnicas
    
    ### Cache de Dados
    - Processamento eficiente de grandes volumes de dados
    - Carregamento otimizado dos arquivos CSV
    
    ### Visualizações Interativas
    - **Streamlit** para interface web
    - **Gráficos** para visualização de dados
    - **Métricas** com comparações percentuais
    
    ### Interface Responsiva
    - Layout adaptável para diferentes telas
    - Sidebar com navegação intuitiva
    - Filtros dinâmicos e busca textual
    """)
    
    st.markdown("""
    ## 🔧 Tecnologias Utilizadas
    
    - **Python 3.8+**
    - **Streamlit** - Framework web
    - **CSV** - Manipulação de dados
    - **Collections** - Estruturas de dados otimizadas
    
    ## 📈 Possíveis Melhorias
    
    1. **Análise temporal** - Comparação entre exercícios
    2. **Indicadores financeiros** - Índices de autonomia fiscal
    3. **Projeções** - Estimativas de arrecadação
    4. **Alertas** - Monitoramento de metas
    5. **Exportação** - Download de relatórios em PDF/Excel
    
    ## 📞 Suporte
    
    Para dúvidas ou sugestões sobre o dashboard, consulte a documentação do Streamlit.
    """)

# Footer moderno
st.markdown("""
<div style="
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    padding: 2rem;
    border-radius: 20px;
    margin-top: 3rem;
    text-align: center;
    color: white;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
">
    <div style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">
        📊 Dashboard LOA - Município de Rifaina
    </div>
    <div style="font-size: 1rem; margin-bottom: 1rem; opacity: 0.9;">
        Análise Completa da Lei Orçamentária Anual
    </div>
    <div style="display: flex; justify-content: center; gap: 2rem; margin-bottom: 1rem;">
        <div style="text-align: center;">
            <div style="font-size: 2rem;">💰</div>
            <div style="font-size: 0.9rem;">Orçamento Total</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 2rem;">📊</div>
            <div style="font-size: 0.9rem;">Análise Dinâmica</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 2rem;">🔄</div>
            <div style="font-size: 0.9rem;">Atualização Automática</div>
        </div>
    </div>
    <div style="font-size: 0.8rem; opacity: 0.7; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 1rem;">
        Desenvolvido com ❤️ para análise orçamentária municipal | Streamlit + Python
    </div>
</div>
""", unsafe_allow_html=True)



 