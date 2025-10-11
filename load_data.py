"""
Script para carregar dados dos projetos de investimento no banco de dados SQLite
usando o schema definido em create_schema.sql

Uso:
    python load_data.py

Pré-requisitos:
    - Arquivo create_schema.sql no mesmo diretório
    - DataFrames já processados no notebook (ou executar células de tratamento)
"""

import sqlite3
import pandas as pd
from pathlib import Path


def execute_schema(conn: sqlite3.Connection, schema_file: str = "create_schema.sql"):
    """Executa o arquivo SQL de schema para criar tabelas"""
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Executar cada statement separadamente
    conn.executescript(schema_sql)
    conn.commit()
    print(f"✓ Schema criado a partir de {schema_file}")


def load_dataframe_to_sql(
    df: pd.DataFrame, 
    table_name: str, 
    conn: sqlite3.Connection,
    if_exists: str = "append"
):
    """
    Carrega DataFrame no SQLite com conversões apropriadas de tipo
    
    Args:
        df: DataFrame a ser carregado
        table_name: Nome da tabela no banco
        conn: Conexão SQLite
        if_exists: 'append' ou 'replace'
    """
    # Criar cópia para não modificar original
    df_copy = df.copy()
    
    # Conversões de tipo para compatibilidade SQLite
    for col in df_copy.columns:
        # Converter boolean para int (SQLite não tem boolean nativo)
        if df_copy[col].dtype == 'boolean':
            df_copy[col] = df_copy[col].astype('Int64')  # Int64 permite NULL
        
        # Converter category para string
        elif df_copy[col].dtype.name == 'category':
            df_copy[col] = df_copy[col].astype(str)
        
        # Converter datetime para string ISO format
        elif pd.api.types.is_datetime64_any_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d')
    
    # Carregar no banco
    df_copy.to_sql(table_name, conn, if_exists=if_exists, index=False)
    print(f"✓ {len(df_copy)} registros carregados em '{table_name}'")


def load_all_data(
    df: pd.DataFrame,
    instituicoes_df: pd.DataFrame,
    eixos_df: pd.DataFrame,
    tipos_df: pd.DataFrame,
    subtipos_df: pd.DataFrame,
    fontes_de_recurso_df: pd.DataFrame,
    projeto_tomadores_df: pd.DataFrame,
    projeto_executores_df: pd.DataFrame,
    projeto_repassadores_df: pd.DataFrame,
    projeto_eixos_df: pd.DataFrame,
    projeto_tipos_df: pd.DataFrame,
    projeto_subtipos_df: pd.DataFrame,
    db_file: str = "projeto_investimento.db"
):
    """
    Carrega todos os DataFrames no banco de dados
    
    Args:
        df: DataFrame principal dos projetos
        *_df: DataFrames de entidades e relacionamentos
        db_file: Caminho do arquivo de banco de dados
    """
    # Criar/conectar ao banco
    conn = sqlite3.connect(db_file)
    
    try:
        # 1. Executar schema (cria tabelas)
        execute_schema(conn)
        
        print("\n=== Carregando Entidades ===")
        # 2. Carregar tabelas de entidades (sem foreign keys para outras entidades)
        load_dataframe_to_sql(instituicoes_df, "instituicoes", conn)
        load_dataframe_to_sql(eixos_df, "eixos", conn)
        load_dataframe_to_sql(tipos_df, "tipos", conn)
        load_dataframe_to_sql(subtipos_df, "subtipos", conn)
        
        print("\n=== Carregando Projetos ===")
        # 3. Carregar tabela principal
        load_dataframe_to_sql(df, "projeto_investimento", conn)
        
        print("\n=== Carregando Relacionamentos ===")
        # 4. Carregar tabelas de relacionamento
        load_dataframe_to_sql(projeto_tomadores_df, "projeto_tomadores", conn)
        load_dataframe_to_sql(projeto_executores_df, "projeto_executores", conn)
        load_dataframe_to_sql(projeto_repassadores_df, "projeto_repassadores", conn)
        load_dataframe_to_sql(projeto_eixos_df, "projeto_eixos", conn)
        load_dataframe_to_sql(projeto_tipos_df, "projeto_tipos", conn)
        load_dataframe_to_sql(projeto_subtipos_df, "projeto_subtipos", conn)
        
        print("\n=== Carregando Fontes de Recurso ===")
        # 5. Carregar fontes de recurso
        load_dataframe_to_sql(fontes_de_recurso_df, "fontes_de_recurso", conn)
        
        # Commit final
        conn.commit()
        
        print("\n" + "="*50)
        print("✓ DADOS CARREGADOS COM SUCESSO!")
        print("="*50)
        
        # Estatísticas
        print("\n=== Estatísticas do Banco ===")
        cursor = conn.cursor()
        
        tables = [
            "projeto_investimento",
            "instituicoes",
            "eixos",
            "tipos",
            "subtipos",
            "fontes_de_recurso",
            "projeto_tomadores",
            "projeto_executores",
            "projeto_repassadores",
            "projeto_eixos",
            "projeto_tipos",
            "projeto_subtipos"
        ]
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table:30s}: {count:5d} registros")
        
        print("\n=== Verificação de Integridade ===")
        # Verificar foreign keys
        cursor.execute("PRAGMA foreign_key_check")
        fk_errors = cursor.fetchall()
        if fk_errors:
            print("⚠ ATENÇÃO: Problemas de integridade referencial encontrados:")
            for error in fk_errors:
                print(f"  {error}")
        else:
            print("✓ Todas as foreign keys estão válidas")
        
    except Exception as e:
        print(f"\n✗ ERRO ao carregar dados: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()
        print(f"\n✓ Banco de dados salvo em: {db_file}")


def main():
    """
    Função principal - assumindo que os DataFrames já foram criados no notebook
    
    Para usar este script:
    1. Execute as células do notebook até a seção de normalização
    2. Exporte as variáveis ou use este código no próprio notebook
    """
    print("="*50)
    print("CARREGAMENTO DE DADOS - PROJETOS DE INVESTIMENTO")
    print("="*50)
    
    # Verificar se arquivo de schema existe
    if not Path("create_schema.sql").exists():
        print("✗ ERRO: Arquivo 'create_schema.sql' não encontrado!")
        print("  Execute este script no mesmo diretório que o arquivo de schema.")
        return
    
    print("\n⚠ IMPORTANTE:")
    print("Este script assume que os DataFrames já foram criados.")
    print("Execute as células de tratamento de dados do notebook primeiro.")
    print("\nAlternativamente, importe e use a função load_all_data() diretamente:")
    print("\n  from load_data import load_all_data")
    print("  load_all_data(df, instituicoes_df, eixos_df, ...)")
    print("\n" + "="*50)


if __name__ == "__main__":
    main()


# =============================================================================
# EXEMPLO DE USO NO NOTEBOOK
# =============================================================================

"""
# No seu notebook, após processar todos os dados, adicione esta célula:

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
    projeto_subtipos_df=projeto_subtipos_df,
    db_file="projeto_investimento.db"
)
"""

