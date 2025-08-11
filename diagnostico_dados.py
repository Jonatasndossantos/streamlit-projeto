import pandas as pd
import numpy as np

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

def load_data():
    """Carrega e processa os dados de execução orçamentária e LOA"""
    
    # Carregar dados de receitas executadas
    try:
        receitas_executadas = pd.read_csv("Portal Transparencia Receitas Acumuladas - Exercício 2025 (1).csv", 
                                        sep=';', encoding='utf-8')
    except:
        receitas_executadas = pd.read_csv("Portal Transparencia Receitas Acumuladas - Exercício 2025 (1).csv", 
                                        sep=';', encoding='latin-1')
    
    # Carregar dados da LOA (receitas orçadas)
    try:
        receitas_orcadas = pd.read_csv("download-123842.557.csv", sep=';', encoding='utf-8')
    except:
        receitas_orcadas = pd.read_csv("download-123842.557.csv", sep=';', encoding='latin-1')
    
    return receitas_executadas, receitas_orcadas

def process_receitas_data(df):
    """Processa dados de receitas"""
    df = df.copy()
    
    # Converter valores monetários
    for col in ['Prev. Inicial', 'Prev. Atualizada', 'Arrec. Período', 'Arrec. Total']:
        if col in df.columns:
            df[col] = df[col].apply(parse_currency)
    
    return df

def process_loa_data(df):
    """Processa dados da LOA"""
    df = df.copy()
    
    # Converter valores monetários da LOA
    if 'TOTOR' in df.columns:
        df['TOTOR'] = pd.to_numeric(df['TOTOR'], errors='coerce').fillna(0)
    
    return df

# Carregar dados
print("🔍 DIAGNÓSTICO DOS DADOS DE RECEITAS")
print("=" * 50)

receitas_raw, receitas_loa_raw = load_data()

print(f"📊 Dados de receitas executadas: {len(receitas_raw)} linhas")
print(f"📊 Dados da LOA: {len(receitas_loa_raw)} linhas")

# Verificar colunas
print("\n📋 COLUNAS DOS DADOS:")
print("Receitas executadas:", list(receitas_raw.columns))
print("LOA:", list(receitas_loa_raw.columns))

# Processar dados
receitas_df = process_receitas_data(receitas_raw)
receitas_loa_df = process_loa_data(receitas_loa_raw)

# Análise dos valores
print("\n💰 ANÁLISE DOS VALORES:")
print("=" * 30)

# Valores antes do processamento
print("\n📈 ANTES DO PROCESSAMENTO:")
print(f"Prev. Atualizada (raw): {receitas_raw['Prev. Atualizada'].sum()}")
print(f"Arrec. Total (raw): {receitas_raw['Arrec. Total'].sum()}")

# Valores após processamento
print("\n📈 APÓS PROCESSAMENTO:")
total_previsto = receitas_df['Prev. Atualizada'].sum()
total_arrecadado = receitas_df['Arrec. Total'].sum()
total_loa = receitas_loa_df['TOTOR'].sum()

print(f"Prev. Atualizada (processado): {total_previsto:,.2f}")
print(f"Arrec. Total (processado): {total_arrecadado:,.2f}")
print(f"LOA Total: {total_loa:,.2f}")

# Verificar valores problemáticos
print("\n⚠️ VERIFICAÇÃO DE VALORES PROBLEMÁTICOS:")
print("=" * 40)

# Verificar valores nulos
print(f"Valores nulos em 'Arrec. Total': {receitas_raw['Arrec. Total'].isnull().sum()}")
print(f"Valores vazios em 'Arrec. Total': {(receitas_raw['Arrec. Total'] == '').sum()}")

# Verificar valores zero
print(f"Valores zero em 'Arrec. Total': {(receitas_raw['Arrec. Total'] == 0).sum()}")

# Verificar valores negativos
valores_negativos = receitas_df[receitas_df['Arrec. Total'] < 0]
print(f"Valores negativos em 'Arrec. Total': {len(valores_negativos)}")

# Verificar valores muito altos
valores_altos = receitas_df[receitas_df['Arrec. Total'] > 1000000]
print(f"Valores > 1M em 'Arrec. Total': {len(valores_altos)}")

# Mostrar alguns exemplos de valores
print("\n📋 EXEMPLOS DE VALORES:")
print("=" * 25)

print("\nPrimeiros 10 valores de 'Arrec. Total' (raw):")
for i, valor in enumerate(receitas_raw['Arrec. Total'].head(10)):
    print(f"  {i+1}: '{valor}' (tipo: {type(valor)})")

print("\nPrimeiros 10 valores de 'Arrec. Total' (processado):")
for i, valor in enumerate(receitas_df['Arrec. Total'].head(10)):
    print(f"  {i+1}: {valor:,.2f}")

# Verificar se há duplicatas
print("\n🔍 VERIFICAÇÃO DE DUPLICATAS:")
print("=" * 30)

# Verificar se há linhas duplicadas
duplicatas = receitas_raw.duplicated().sum()
print(f"Linhas duplicadas: {duplicatas}")

# Verificar códigos duplicados
codigos_duplicados = receitas_raw['Código'].duplicated().sum()
print(f"Códigos duplicados: {codigos_duplicados}")

# Análise por categoria
print("\n📊 ANÁLISE POR CATEGORIA:")
print("=" * 30)

receitas_df['categoria'] = receitas_df['Código'].str[:4]
analise_categoria = receitas_df.groupby('categoria').agg({
    'Prev. Atualizada': 'sum',
    'Arrec. Total': 'sum'
}).reset_index()

analise_categoria['execucao_pct'] = (analise_categoria['Arrec. Total'] / 
                                    analise_categoria['Prev. Atualizada'] * 100)

print("\nTop 10 categorias por arrecadação:")
top_categorias = analise_categoria.nlargest(10, 'Arrec. Total')
for _, row in top_categorias.iterrows():
    print(f"  {row['categoria']}: R$ {row['Arrec. Total']:,.2f} ({row['execucao_pct']:.1f}%)")

# Comparação LOA vs Execução
print("\n🔄 COMPARAÇÃO LOA vs EXECUÇÃO:")
print("=" * 35)

execucao_vs_loa = (total_arrecadado / total_loa * 100) if total_loa > 0 else 0
print(f"LOA Total: R$ {total_loa:,.2f}")
print(f"Arrecadado: R$ {total_arrecadado:,.2f}")
print(f"Execução vs LOA: {execucao_vs_loa:.1f}%")

# Verificar se há diferenças significativas
diferenca = total_arrecadado - total_loa
print(f"Diferença: R$ {diferenca:,.2f}")

if abs(diferenca) > total_loa * 0.1:
    print("⚠️ ATENÇÃO: Diferença significativa (>10%) entre LOA e execução!")
else:
    print("✅ Diferença dentro do esperado")

# Verificar se há valores suspeitos
print("\n🔍 VERIFICAÇÃO DE VALORES SUSPEITOS:")
print("=" * 40)

# Verificar se há valores que são strings estranhas
valores_string = receitas_raw[receitas_raw['Arrec. Total'].apply(lambda x: isinstance(x, str) and not x.replace('.', '').replace(',', '').isdigit())]
print(f"Valores string não numéricos: {len(valores_string)}")

if len(valores_string) > 0:
    print("Exemplos de valores string problemáticos:")
    for i, valor in enumerate(valores_string['Arrec. Total'].head(5)):
        print(f"  {i+1}: '{valor}'")

print("\n✅ DIAGNÓSTICO CONCLUÍDO")
