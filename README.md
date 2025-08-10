# Dashboard LOA - Município de Rifaina

## 📊 Análise da Lei Orçamentária Anual

Este dashboard interativo fornece uma análise completa da Lei Orçamentária Anual (LOA) do Município de Rifaina, desenvolvido em Python com Streamlit e Plotly.

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

## 🛠️ Como Executar

### Pré-requisitos
```bash
pip install streamlit pandas plotly numpy
```

### Execução
```bash
streamlit run app.py
```

A aplicação estará disponível em `http://localhost:8501`

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

## 🎯 Funcionalidades Técnicas

### Cache de Dados
- Utiliza `@st.cache_data` para otimizar carregamento
- Processamento eficiente de grandes volumes de dados

### Visualizações Interativas
- **Plotly** para gráficos dinâmicos
- **Treemap** para visualização hierárquica
- **Métricas** com comparações percentuais

### Interface Responsiva
- Layout adaptável para diferentes telas
- Sidebar com navegação intuitiva
- Filtros dinâmicos e busca textual

## 🔧 Tecnologias Utilizadas

- **Python 3.8+**
- **Streamlit** - Framework web
- **Pandas** - Manipulação de dados
- **Plotly** - Visualizações interativas
- **NumPy** - Computação numérica

## 📈 Possíveis Melhorias

1. **Análise temporal** - Comparação entre exercícios
2. **Indicadores financeiros** - Índices de autonomia fiscal
3. **Projeções** - Estimativas de arrecadação
4. **Alertas** - Monitoramento de metas
5. **Exportação** - Download de relatórios em PDF/Excel

## 📞 Suporte

Para dúvidas ou sugestões sobre o dashboard, consulte a documentação do Streamlit ou Plotly.

---
**Desenvolvido com ❤️ para análise orçamentária municipal**
