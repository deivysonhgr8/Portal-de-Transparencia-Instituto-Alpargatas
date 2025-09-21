import pandas as pd
# Assumindo que todas as suas funções de extração estão em um único 'extract.py'
import extract 

def criar_base_municipios_atuacao():
    """
    Cria a base de dados mestre com os municípios de atuação do Instituto,
    cruzando os dados do IA com a base oficial de municípios do IBGE (DTB).
    Esta função é baseada no seu script 'transform.py' original.

    Returns:
        pd.DataFrame: DataFrame com a lista única de municípios de atuação.
    """
    print("--- ETAPA 1: Criando a base de municípios de atuação do Instituto ---")
    df_ia = extract.ler_ia()
    df_dtb = extract.ler_dtb()

    if df_ia.empty or df_dtb.empty:
        print("ERRO: DataFrame do IA ou DTB está vazio. Não é possível continuar.")
        return pd.DataFrame()

    # Função interna para replicar a formatação do seu script
    def formatar_nome(df, coluna, novo_nome="ds_formatada"):
        df[novo_nome] = (df[coluna].str.upper()
                           .str.replace("[-.!?'`()]", "", regex=True)
                           .str.replace("- MIXING CENTER", "")
                           .str.strip()
                           .str.replace(" ", ""))
        return df

    df_ia = formatar_nome(df=df_ia, coluna='ds_mun')
    df_ia['ds_uf'] = df_ia['sg_uf'].map({"PB": "Paraíba", "PE": "Pernambuco",
                                       "MG": "Minas Gerais", "SP": "São Paulo"})
    print("-> Dados do Instituto (IA) formatados.")

    data_m = pd.merge(df_ia, df_dtb, how='inner', on=['ds_formatada', 'ds_uf'],
                      suffixes=['_ia', '_dtb'])
    print(f"-> Merge entre IA e DTB concluído. {len(data_m)} registros de atuação encontrados.")
    
    # ##################################################################
    # CORREÇÃO APLICADA AQUI 
    # Renomeia 'id_mundv' (que veio do dtb) diretamente para 'cod_municipio'
    # e 'ds_mun_dtb' para 'nome_municipio', pois não há sufixo no 'id_mundv'.
    data_m.rename(columns={
        'id_mundv': 'cod_municipio', 
        'ds_mun_dtb': 'nome_municipio'
    }, inplace=True)
    # ##################################################################
    
    municipios_unicos = data_m[['cod_municipio', 'nome_municipio', 'ds_uf']].drop_duplicates().reset_index(drop=True)
    print(f"-> Base final com {len(municipios_unicos)} municípios de atuação únicos.")
    
    return municipios_unicos

def criar_base_de_analise_completa():
    """
    Orquestra todo o processo de transformação:
    1. Cria a base de municípios de atuação.
    2. Consolida as 5 variáveis para a análise fatorial.
    3. Une as duas bases com prioridade para os municípios de atuação (left merge).
    
    Returns:
        pd.DataFrame: O DataFrame final, pronto para a análise.
    """
    # --- ETAPA 1: Obter a lista de municípios prioritários ---
    df_municipios_atuacao = criar_base_municipios_atuacao()
    if df_municipios_atuacao.empty:
        return pd.DataFrame() # Retorna DF vazio se a base prioritária falhar

    # --- ETAPA 2: Consolidar as 5 variáveis de análise ---
    print("\n--- ETAPA 2: Consolidando as 5 variáveis para análise fatorial ---")
    
    # Extração
    df_saeb = extract.pt_mt_saeb()
    df_aprovacao = extract.aprov_ideb()
    df_infra = extract.gerar_indice_infraestrutura_municipal()
    df_nse = extract.processar_inse()
    df_formacao = extract.extrair_afd()

    # Padronização de colunas
    df_saeb.rename(columns={'Codigo_Municipio': 'cod_municipio', 'Nota_Media_SAEB': 'nota_saeb'}, inplace=True)
    df_aprovacao.rename(columns={'cod_municipio': 'cod_municipio', 'taxa_aprovacao': 'taxa_aprovacao'}, inplace=True)
    df_infra.rename(columns={'Código do Município': 'cod_municipio', 'IQIE': 'iqie_infraestrutura'}, inplace=True)
    if df_nse is not None:
        df_nse.rename(columns={'CO_MUNICIPIO': 'cod_municipio', 'MEDIA_INSE': 'inse_socioeconomico'}, inplace=True)
    else:
        print("ERRO: O DataFrame retornado por extract.processar_inse() está vazio ou é None.")
        return pd.DataFrame()
    if df_formacao is not None:
        df_formacao.rename(columns={'cod_municipio': 'cod_municipio', 'media_percentual_formacao_adequada': 'formacao_docente'}, inplace=True)
    else:
        print("ERRO: O DataFrame retornado por extract.extrair_afd() está vazio ou é None.")
        return pd.DataFrame()

    # Consolidação (Merge) das variáveis
    dfs_padronizados = [
        df_saeb[['cod_municipio', 'nota_saeb']],
        df_aprovacao[['cod_municipio', 'taxa_aprovacao']],
        df_infra[['cod_municipio', 'iqie_infraestrutura']],
        df_nse[['cod_municipio', 'inse_socioeconomico']],
        df_formacao[['cod_municipio', 'formacao_docente']]
    ]
    
    df_variaveis_analise = dfs_padronizados[0]
    for df_a_juntar in dfs_padronizados[1:]:
        df_variaveis_analise = pd.merge(df_variaveis_analise, df_a_juntar, on='cod_municipio', how='inner')
    
    print(f"-> Consolidação das 5 variáveis concluída. {len(df_variaveis_analise)} municípios com dados completos.")

    # --- ETAPA 3: UNIÃO FINAL COM PRIORIDADE (LEFT MERGE) ---
    print("\n--- ETAPA 3: Unindo a base de atuação com as variáveis de análise ---")
    
    df_final_para_analise = pd.merge(
        df_municipios_atuacao,
        df_variaveis_analise,
        on='cod_municipio',
        how='left'
    )
    
    print("-> Merge final com prioridade concluído.")
    
    return df_final_para_analise

# =========================================================================
# Bloco de Execução Principal
# =========================================================================
if __name__ == "__main__":
    # Agora, apenas uma chamada de função é necessária
    df_final = criar_base_de_analise_completa()
    
    if not df_final.empty:
        print("\n--- ANÁLISE FINAL CONCLUÍDA ---")
        print(f"O DataFrame final contém {len(df_final)} municípios.")
        
        print("\nAmostra do DataFrame final:")
        print(df_final.head())
        
        print("\nVerificação de valores nulos (NaN) no DataFrame final:")
        print(df_final.isnull().sum())