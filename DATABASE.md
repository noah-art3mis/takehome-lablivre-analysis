# Banco de Dados - Projetos de Investimento

Este documento descreve o schema do banco de dados e como utilizá-lo.

## Arquivos

- **`create_schema.sql`**: Script SQL que cria todas as tabelas, índices e views
- **`load_data.py`**: Script Python para carregar dados processados no banco
- **`projeto_investimento.db`**: Arquivo SQLite gerado (não versionado)

## Estrutura do Banco de Dados

### Diagrama de Relacionamentos

```
┌─────────────────────┐
│  instituicoes       │
│  - codigo (PK)      │
│  - nome             │
│  - sigla            │
│  - tipo             │
└─────────────────────┘
         ▲ ▲ ▲
         │ │ │
    ┌────┘ │ └────┐
    │      │      │
┌───┴──┐ ┌─┴───┐ ┌┴────┐
│tomad.│ │exec.│ │repas│  (junction tables)
└──────┘ └─────┘ └─────┘
         │
         ▼
┌─────────────────────────────┐
│  projeto_investimento       │
│  - idUnico (PK)             │
│  - nome                     │
│  - descricao                │
│  - natureza                 │
│  - situacao                 │
│  - dataInicialPrevista      │
│  - dataFinalPrevista        │
│  - isModeladaPorBim         │
│  - ...                      │
└─────────────────────────────┘
    │            │
    ▼            ▼
┌─────────┐  ┌──────────────┐
│eixos    │  │fontes_recurso│
│tipos    │  │- origem      │
│subtipos │  │- valor       │
└─────────┘  └──────────────┘
(via junction tables)
```

### Tabelas Principais

#### `projeto_investimento`
Tabela central com informações dos projetos.

**Campos principais:**
- `idUnico`: Identificador único do projeto (formato: "50379.53-54")
- `nome`: Nome do projeto
- `descricao`: Descrição detalhada
- `natureza`: Tipo (Obra, Projeto, PII, Estudo, Outros)
- `situacao`: Status atual (Cadastrada, Em execução, Concluída, etc.)
- `dataInicialPrevista`, `dataFinalPrevista`: Datas de planejamento
- `dataInicialEfetiva`, `dataFinalEfetiva`: Datas de execução real
- `isModeladaPorBim`: Se usa tecnologia BIM

#### `instituicoes`
Instituições envolvidas (tomadores, executores, repassadores).

#### `eixos`, `tipos`, `subtipos`
Hierarquia de categorização dos projetos:
- Eixo (ex: Econômico, Social)
  - Tipo (ex: Rodovia, Educação)
    - Subtipo (ex: Acessos Terrestres, Escola Básica)

#### `fontes_de_recurso`
Origem e valor do investimento por projeto (um projeto pode ter múltiplas fontes).

### Tabelas de Relacionamento

- `projeto_tomadores`: Instituições que tomam o recurso
- `projeto_executores`: Instituições que executam o projeto
- `projeto_repassadores`: Instituições que repassam o recurso
- `projeto_eixos`, `projeto_tipos`, `projeto_subtipos`: Categorização dos projetos

### Views Úteis

#### `v_projetos_investimento_total`
Projetos com valor total agregado de todas as fontes de recurso.

```sql
SELECT * FROM v_projetos_investimento_total
WHERE valorTotalPrevisto > 1000000
ORDER BY valorTotalPrevisto DESC;
```

#### `v_projetos_instituicoes`
Projetos com todas as instituições concatenadas.

```sql
SELECT idUnico, nome, executores, repassadores
FROM v_projetos_instituicoes
WHERE executores LIKE '%EDUCACAO%';
```

#### `v_estatisticas_natureza`
Estatísticas agregadas por tipo de projeto.

```sql
SELECT * FROM v_estatisticas_natureza;
```

#### `v_projetos_atrasados`
Projetos com data final prevista já passou mas ainda não concluídos.

```sql
SELECT * FROM v_projetos_atrasados
WHERE dias_atraso > 365
ORDER BY dias_atraso DESC;
```

## Como Usar

### 1. Criar o banco de dados vazio

```bash
sqlite3 projeto_investimento.db < create_schema.sql
```

Ou dentro do Python:

```python
import sqlite3

conn = sqlite3.connect("projeto_investimento.db")
with open("create_schema.sql", 'r') as f:
    conn.executescript(f.read())
conn.commit()
conn.close()
```

### 2. Carregar dados a partir do notebook

No notebook Jupyter, após processar todos os dados:

```python
from load_data import load_all_data

load_all_data(
    df=df,
    instituicoes_df=instituicoes_df,
    eixos_df=eixos_df,
    tipos_df=tipos_df,
    subtipos_df=subtipos_df,
    fontes_de_recurso_df=fontes_de_recurso_df,
    projeto_tomadores_df=projeto_tomadores_df,
    projeto_executores_df=projeto_executores_df,
    projeto_repassadores_df=projeto_repassadores_df,
    projeto_eixos_df=projeto_eixos_df,
    projeto_tipos_df=projeto_tipos_df,
    projeto_subtipos_df=projeto_subtipos_df
)
```

### 3. Consultar dados

```python
import pandas as pd
import sqlite3

conn = sqlite3.connect("projeto_investimento.db")

# Projetos por natureza
df = pd.read_sql_query("""
    SELECT natureza, COUNT(*) as quantidade
    FROM projeto_investimento
    GROUP BY natureza
    ORDER BY quantidade DESC
""", conn)

# Projetos com maior investimento
df = pd.read_sql_query("""
    SELECT * FROM v_projetos_investimento_total
    WHERE valorTotalPrevisto > 0
    ORDER BY valorTotalPrevisto DESC
    LIMIT 10
""", conn)

# Projetos com BIM
df = pd.read_sql_query("""
    SELECT natureza, 
           SUM(CASE WHEN isModeladaPorBim = 1 THEN 1 ELSE 0 END) as com_bim,
           COUNT(*) as total,
           ROUND(SUM(CASE WHEN isModeladaPorBim = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pct_bim
    FROM projeto_investimento
    WHERE isModeladaPorBim IS NOT NULL
    GROUP BY natureza
""", conn)

conn.close()
```

## Queries Úteis

### Total de investimento por natureza

```sql
SELECT 
    p.natureza,
    COUNT(DISTINCT p.idUnico) as num_projetos,
    SUM(f.valorInvestimentoPrevisto) as valor_total,
    AVG(f.valorInvestimentoPrevisto) as valor_medio
FROM projeto_investimento p
LEFT JOIN fontes_de_recurso f ON p.idUnico = f.idUnico
GROUP BY p.natureza
ORDER BY valor_total DESC;
```

### Instituições mais ativas

```sql
SELECT 
    codigo,
    nome,
    COUNT(*) as num_projetos
FROM (
    SELECT codigo, nome FROM projeto_executores
    UNION ALL
    SELECT codigo, nome FROM projeto_tomadores
    UNION ALL
    SELECT codigo, nome FROM projeto_repassadores
) AS todas_participacoes
GROUP BY codigo, nome
ORDER BY num_projetos DESC
LIMIT 10;
```

### Projetos por situação e ano

```sql
SELECT 
    strftime('%Y', dataCadastro) as ano,
    situacao,
    COUNT(*) as quantidade
FROM projeto_investimento
GROUP BY ano, situacao
ORDER BY ano DESC, quantidade DESC;
```

### Distribuição temporal dos projetos

```sql
SELECT 
    strftime('%Y', dataInicialPrevista) as ano_inicio,
    COUNT(*) as num_projetos,
    SUM(populacaoBeneficiada) as pop_total_beneficiada
FROM projeto_investimento
WHERE dataInicialPrevista IS NOT NULL
GROUP BY ano_inicio
ORDER BY ano_inicio;
```

## Manutenção

### Verificar integridade

```sql
PRAGMA foreign_key_check;
PRAGMA integrity_check;
```

### Recriar índices

```sql
REINDEX;
```

### Analisar para otimização

```sql
ANALYZE;
```

### Vacuum para compactar

```bash
sqlite3 projeto_investimento.db "VACUUM;"
```

## Notas sobre Tipos de Dados

SQLite tem tipagem dinâmica, mas o schema define os tipos esperados:

- **TEXT**: Strings (IDs, nomes, descrições)
- **INTEGER**: Números inteiros (autoincrement em junction tables)
- **REAL**: Números decimais (valores, métricas)
- **DATE**: Datas armazenadas como TEXT no formato ISO 8601 (YYYY-MM-DD)
- **BOOLEAN**: Armazenado como INTEGER (0 = False, 1 = True, NULL = NULL)

## Exportar Dados

### Para CSV

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("projeto_investimento.db")
df = pd.read_sql_query("SELECT * FROM projeto_investimento", conn)
df.to_csv("projetos_export.csv", index=False, encoding='utf-8')
conn.close()
```

### Para Excel

```python
with pd.ExcelWriter('projetos_export.xlsx') as writer:
    pd.read_sql_query("SELECT * FROM projeto_investimento", conn).to_excel(writer, sheet_name='Projetos', index=False)
    pd.read_sql_query("SELECT * FROM v_estatisticas_natureza", conn).to_excel(writer, sheet_name='Estatísticas', index=False)
```

## Licença e Fonte de Dados

**Fonte**: API ObrasGov - https://api.obrasgov.gestao.gov.br/  
**Jurisdição**: Distrito Federal (DF), Brasil  
**Última atualização**: Ver `dataCadastro` mais recente no banco

