import requests
import zipfile
import io
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import numpy as np
import time
from pathlib import Path


#Dados do Instituto Alpargatas (IA)
def ler_ia():
    data_dir = Path(__file__).parent.parent / 'data'
    file_path = data_dir / 'Projetos_de_Atuac807a771o_-_IA_-_2020_a_2025.xlsx'
    
    anos_atuacao = ['2020', '2021', '2022', '2023', '2024']
    lista_dataframes = []

    for ano in anos_atuacao:
        print(f"\nProcessando dados do ano: {ano}...")
        try:
            df = pd.read_excel(file_path, sheet_name=ano, skiprows=5)
        except ValueError:
            print(f"AVISO: A planilha para o ano '{ano}' não foi encontrada. Pulando...")
            continue # Pula para o próximo ano se a aba não existir

        # Mapeamento dinâmico das colunas
        col_map = {}
        for col in df.columns:
            col_norm = str(col).strip().lower().replace("\n", " ").replace("  ", " ")
            if "cidade" in col_norm: col_map["ds_mun"] = col
            elif col_norm in ["uf", "estado"]: col_map["sg_uf"] = col
            elif "projeto" in col_norm and "nº" in col_norm: col_map["nprojetos"] = col
            elif "institui" in col_norm: col_map["ninstituicoes"] = col
            elif "beneficiado" in col_norm: col_map["nbeneficiados"] = col

        # Lógica de fallback otimizada para colunas não encontradas
        # (Caso os nomes não batam exatamente com o esperado)
        fallback_map = {
            "nprojetos": "projeto",
            "ninstituicoes": "institui",
            "nbeneficiados": "beneficiado"
        }
        for key, keyword in fallback_map.items():
            if key not in col_map:
                cols_encontradas = [c for c in df.columns if keyword in str(c).lower()]
                if cols_encontradas:
                    col_map[key] = cols_encontradas[-1] # Pega a última coluna correspondente

        # Verifica se as colunas essenciais foram mapeadas
        if "ds_mun" not in col_map or "sg_uf" not in col_map:
            print(f"ERRO: Não foi possível mapear as colunas 'cidade' ou 'uf' para o ano {ano}. Pulando...")
            continue

        # Seleciona apenas as colunas mapeadas
        df_sel = df[list(col_map.values())].copy()
        df_sel.columns = list(col_map.keys())

        # Adiciona o ano e faz a limpeza
        df_sel["ano_atuacao"] = int(ano)
        df_sel = df_sel.dropna(subset=["ds_mun", "sg_uf"], how="any")
        df_sel = df_sel[~df_sel["ds_mun"].astype(str).str.contains("VARIAÇÃO|Obs|TOTAL", case=False, na=False)]
        
        if not df_sel.empty:
            lista_dataframes.append(df_sel)
            print(f"Dados de {ano} processados com sucesso. {len(df_sel)} registros adicionados.")
        else:
            print(f"AVISO: Nenhum registro válido encontrado para o ano {ano} após a limpeza.")

    # A concatenação e o return devem estar FORA do loop
    if not lista_dataframes:
        print("\nERRO FINAL: Nenhum dado foi coletado de nenhuma planilha. Retornando DataFrame vazio.")
        return pd.DataFrame()

    print("\nConcatenando todos os dados...")
    df_ia = pd.concat(lista_dataframes, ignore_index=True)
    return df_ia

#Dados da Divisão Territorial Brasileira - IBGE
def ler_dtb():
    """
    Baixa, extrai, trata e consolida os dados da Divisão Territorial Brasileira (DTB)
    do IBGE para os anos de 2020 a 2024.
    
    Retorna:
        pandas.DataFrame: Um único DataFrame contendo os dados de todos os anos.
                          Retorna um DataFrame vazio se nenhum dado for carregado.
    """
    # 2. Organização dos Dados: URLs e Caminhos (versão corrigida por você)
    urls_e_arquivos = [
        {"ano": 2020, "url": "https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/divisao_territorial/2020/DTB_2020_v2.zip", "caminho_interno_zip": "RELATORIO_DTB_BRASIL_MUNICIPIO.xls"},
        {"ano": 2021, "url": "https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/divisao_territorial/2021/DTB_2021.zip", "caminho_interno_zip": "RELATORIO_DTB_BRASIL_MUNICIPIO.xls"},
        {"ano": 2022, "url": "https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/divisao_territorial/2022/DTB_2022.zip", "caminho_interno_zip": "RELATORIO_DTB_BRASIL_MUNICIPIO.xls"},
        {"ano": 2023, "url": "https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/divisao_territorial/2023/DTB_2023.zip", "caminho_interno_zip": "DTB_2023/RELATORIO_DTB_BRASIL_MUNICIPIO.xls"},
        {"ano": 2024, "url": "https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/divisao_territorial/2024/DTB_2024.zip", "caminho_interno_zip": "RELATORIO_DTB_BRASIL_2024_MUNICIPIOS.xls"}
    ]

    # Lista para guardar os dataframes de cada ano
    lista_dfs = []

    print("Iniciando a automação de download, leitura e tratamento dos arquivos do IBGE...")

    for info in urls_e_arquivos:
        ano = info["ano"]
        url = info["url"]
        caminho_arquivo = info["caminho_interno_zip"]
        
        print(f"\n--- Processando dados para o ano de {ano} ---")
        
        try:
            # Lógica de definição (skiprows, usecols)
            colunas_para_usar = ['UF', 'Nome_UF', 'Nome Região Geográfica Imediata', 'Código Município Completo', 'Nome_Município']
            skip = 6 if ano in [2024, 2023, 2022] else 0
            
            # Download e Leitura
            response = requests.get(url)
            response.raise_for_status()

            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                with z.open(caminho_arquivo) as arquivo_excel:
                    print(f"Lendo e tratando o arquivo '{caminho_arquivo}'...")
                    df = pd.read_excel(arquivo_excel, skiprows=skip, usecols=colunas_para_usar)
                    
                    # Tratamento e Limpeza
                    df.columns = ['id_uf', 'ds_uf', 'ds_rgi', 'id_mundv', 'ds_mun']
                    df = df.drop_duplicates(subset=['id_mundv'])
                    df['ds_formatada'] = (df['ds_mun'].str.upper()
                                                     .str.replace("[-.!?'`()]", "", regex=True)
                                                     .str.replace("- MIXING CENTER", "", regex=False)
                                                     .str.strip()
                                                     .str.replace(" ", "", regex=False))
                    df['ano'] = ano
                    
                    # Adiciona o dataframe tratado à lista
                    lista_dfs.append(df)
                    print(f"Dados de {ano} processados com sucesso!")

        except Exception as e:
            print(f"Ocorreu um ERRO ao processar o ano {ano}: {e}")


    if not lista_dfs:
        print("\nNenhum dado foi carregado. Retornando DataFrame vazio.")
        return pd.DataFrame()
    
    print("\n--- Processo finalizado! Consolidando todos os dados... ---")
    df_dtb = pd.concat(lista_dfs, ignore_index=True)
    
    return df_dtb

#Nota média de Português e Matemática do SAEB (INEP)
def pt_mt_saeb():

    print("Iniciando Módulo: Extração da média de Português e Matemática do SAEB (INEP)")

    url_zip = 'https://download.inep.gov.br/ideb/resultados/divulgacao_anos_iniciais_municipios_2023.zip'
    caminho_completo_no_zip = 'divulgacao_anos_iniciais_municipios_2023/divulgacao_anos_iniciais_municipios_2023.xlsx'
    # Colunas: Código do Município, Nome do Município, Nota Média Padronizada
    colunas_para_usar = [1, 2, 103]
    linhas_a_pular = 9
    valores_na = ['-', '--']
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    
    print(f"\nIniciando download do arquivo ZIP do SAEB de: {url_zip}")
    try:
        response = session.get(url_zip, timeout=30)
        response.raise_for_status()
        print("Download concluído com sucesso.")

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            with z.open(caminho_completo_no_zip) as arquivo_excel:
                print("Lendo e transformando dados da planilha...")
                df_raw = pd.read_excel(
                    arquivo_excel, 
                    skiprows=linhas_a_pular, 
                    usecols=colunas_para_usar, 
                    na_values=valores_na,
                    names=['Codigo_Municipio', 'Nome_Municipio', 'Nota_SAEB'] 
                )
                print("Leitura de dados brutos concluída.")

                # --- ETAPA DE AGREGAÇÃO DENTRO DA FUNÇÃO ---
                print("Agregando dados por município...")
                df_agregado = df_raw.groupby(['Codigo_Municipio', 'Nome_Municipio']).agg(
                    Nota_Media_SAEB=('Nota_SAEB', 'mean')
                ).reset_index()
                print("Agregação concluída com sucesso!")
                
                return df_agregado

    except requests.exceptions.RequestException as e:
        print(f"ERRO: Falha no download do arquivo após múltiplas tentativas. {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"ERRO: Ocorreu um erro inesperado {e}")
        return pd.DataFrame()
    

#Taxa de aprovação do IDEB (INEP)
def aprov_ideb():
    print("Iniciando Módulo: Extração e Agregação de Dados do IDEB (INEP)")

    url_zip = 'https://download.inep.gov.br/ideb/resultados/divulgacao_anos_iniciais_municipios_2023.zip'
    caminho_completo_no_zip = 'divulgacao_anos_iniciais_municipios_2023/divulgacao_anos_iniciais_municipios_2023.xlsx'
    
    colunas_para_usar = [1, 2, 67]
    linhas_a_pular = 9
    valores_na = ['-', '--']
    
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    
    print(f"\nIniciando download do arquivo ZIP do IDEB de: {url_zip}")
    try:
        response = session.get(url_zip, timeout=30)
        response.raise_for_status()
        print("Download concluído com sucesso.")

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            with z.open(caminho_completo_no_zip) as arquivo_excel:
                print("Lendo dados da planilha...")
                df_ideb = pd.read_excel(
                    arquivo_excel, 
                    skiprows=linhas_a_pular, 
                    usecols=colunas_para_usar, 
                    na_values=valores_na
                )
                print("Leitura de dados concluída. Iniciando agregação...")

                # --- ETAPA DE AGREGAÇÃO INTEGRADA ---
                
                # 1. Renomear as colunas para facilitar o manuseio
                df_ideb.columns = ['cod_municipio', 'nome_municipio', 'taxa_aprovacao']

                # 2. Garantir que a coluna de taxa de aprovação seja numérica
                df_ideb['taxa_aprovacao'] = pd.to_numeric(df_ideb['taxa_aprovacao'], errors='coerce')

                # 3. Remover linhas onde a taxa de aprovação seja nula (NaN)
                df_ideb.dropna(subset=['taxa_aprovacao'], inplace=True)

                # 4. Agrupar por código e nome do município e calcular a média
                df_agregado = df_ideb.groupby(['cod_municipio', 'nome_municipio'])['taxa_aprovacao'].mean()

                # 5. Transformar de volta em DataFrame, arredondar e retornar
                df_agregado = df_agregado.reset_index()
                df_agregado['taxa_aprovacao'] = df_agregado['taxa_aprovacao'].round(2)
                
                print("Agregação por município concluída com sucesso!")
                return df_agregado
                
    except requests.exceptions.RequestException as e:
        print(f"ERRO: Falha no download do arquivo após múltiplas tentativas. {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"ERRO: Ocorreu um erro inesperado (IDEB). {e}")
        return pd.DataFrame()
    

#Índice de Qualidade da Infraestrutura Escolar (IQIE) - Censo Escolar (INEP)
def gerar_indice_infraestrutura_municipal():
    """
    Realiza o processo completo de download, extração, pré-processamento de dados
    do Censo Escolar e cálculo do Índice de Qualidade da Infraestrutura Escolar (IQIE)
    para cada município do Brasil.
    Returns:
        pd.DataFrame: Um DataFrame contendo três colunas:
                      - 'Código do Município' (CO_MUNICIPIO)
                      - 'Nome do Município' (NO_MUNICIPIO)
                      - 'IQIE' (o índice calculado)
                      O DataFrame é retornado ordenado do maior para o menor IQIE.
                      Retorna um DataFrame vazio em caso de falha no download.
    """
    # --- 1. CONFIGURAÇÃO ---
    URL_DADOS = 'https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2024.zip'
    NOME_PASTA_PRINCIPAL_ZIP = 'microdados_censo_escolar_2024'
    NOME_ARQUIVO_CSV = 'microdados_ed_basica_2024.csv'
    CAMINHO_DENTRO_DO_ZIP = f'{NOME_PASTA_PRINCIPAL_ZIP}/dados/{NOME_ARQUIVO_CSV}'

    # Colunas necessárias para a análise, otimizando o uso de memória
    COLUNAS_PARA_CARREGAR = [
        'SG_UF', 'NO_MUNICIPIO', 'CO_MUNICIPIO', 'CO_ENTIDADE',
        'IN_AGUA_INEXISTENTE', 'IN_ENERGIA_INEXISTENTE', 'IN_ESGOTO_INEXISTENTE',
        'IN_TRATAMENTO_LIXO_INEXISTENTE', 'IN_BANHEIRO', 'IN_BIBLIOTECA',
        'IN_LABORATORIO_CIENCIAS', 'IN_LABORATORIO_INFORMATICA',
        'IN_QUADRA_ESPORTES', 'IN_ACESSIBILIDADE_INEXISTENTE',
        'QT_SALAS_UTILIZA_CLIMATIZADAS', 'QT_SALAS_UTILIZADAS', 'IN_BANDA_LARGA'
    ]
    MAX_TENTATIVAS = 3
    DELAY_SEGUNDOS = 10

    # --- 2. DOWNLOAD E EXTRAÇÃO DOS DADOS ---
    df_escolas = None
    for tentativa in range(MAX_TENTATIVAS):
        try:
            print(f"\n--- Tentativa {tentativa + 1} de {MAX_TENTATIVAS} ---")
            print(f"Baixando dados de: {URL_DADOS}")
            response = requests.get(URL_DADOS, stream=True, timeout=300)
            response.raise_for_status()  
            print("Download concluído. Processando arquivo CSV em memória...")

            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                with z.open(CAMINHO_DENTRO_DO_ZIP) as csv_file:
                    df_escolas = pd.read_csv(
                        csv_file, sep=';', encoding='latin-1',
                        usecols=COLUNAS_PARA_CARREGAR, low_memory=False
                    )
            print(f"Dados de {len(df_escolas)} escolas carregados com sucesso.")
            break  
        except requests.exceptions.RequestException as e:
            print(f"ERRO DE CONEXÃO na tentativa {tentativa + 1}: {e}")
            if tentativa + 1 < MAX_TENTATIVAS:
                print(f"Aguardando {DELAY_SEGUNDOS} segundos para tentar novamente...")
                time.sleep(DELAY_SEGUNDOS)
            else:
                print("Número máximo de tentativas atingido. O download falhou.")
                return pd.DataFrame()  # Retorna DataFrame vazio em caso de falha

    if df_escolas is None or not isinstance(df_escolas, pd.DataFrame) or df_escolas.empty:
        return pd.DataFrame()

    # --- 3. PRÉ-PROCESSAMENTO (NÍVEL ESCOLA) ---
    print("\nIniciando pré-processamento dos indicadores das escolas...")
    # Inverte colunas de "inexistência" para "existência" (1 = Sim, 0 = Não)
    mapa_negativos = {
        'IN_AGUA_INEXISTENTE': 'AGUA_EXISTENTE',
        'IN_ENERGIA_INEXISTENTE': 'ENERGIA_EXISTENTE',
        'IN_ESGOTO_INEXISTENTE': 'ESGOTO_EXISTENTE',
        'IN_TRATAMENTO_LIXO_INEXISTENTE': 'LIXO_TRATADO_EXISTENTE',
        'IN_ACESSIBILIDADE_INEXISTENTE': 'ACESSIBILIDADE_EXISTENTE'
    }
    for col_original, col_nova in mapa_negativos.items():
        # Converte 0 para 1, 1 para 0, e mantém outros valores (como NaN) como estão
        df_escolas[col_nova] = np.select(
            [df_escolas[col_original] == 0, df_escolas[col_original] == 1],
            [1, 0],
            default=np.nan
        )

    # Renomeia colunas que já são positivas para maior clareza
    mapa_positivos = {
        'IN_BANHEIRO': 'BANHEIRO_EXISTENTE', 'IN_BIBLIOTECA': 'BIBLIOTECA_EXISTENTE',
        'IN_LABORATORIO_CIENCIAS': 'LAB_CIENCIAS_EXISTENTE', 'IN_LABORATORIO_INFORMATICA': 'LAB_INFORMATICA_EXISTENTE',
        'IN_QUADRA_ESPORTES': 'QUADRA_ESPORTES_EXISTENTE', 'IN_BANDA_LARGA': 'BANDA_LARGA_EXISTENTE'
    }
    df_escolas.rename(columns=mapa_positivos, inplace=True)

    # --- 4. CÁLCULO DO IQIE (NÍVEL MUNICIPAL) ---
    print("Agregando dados por município para calcular o IQIE...")
    indicadores_binarios = list(mapa_negativos.values()) + list(mapa_positivos.values())

    agregacao = {col: 'mean' for col in indicadores_binarios}
    agregacao.update({
        'QT_SALAS_UTILIZA_CLIMATIZADAS': 'sum',
        'QT_SALAS_UTILIZADAS': 'sum',
        'CO_ENTIDADE': 'count'  # Usado para contar o número de escolas
    })
    
    df_municipal = df_escolas.groupby(
        ['SG_UF', 'CO_MUNICIPIO', 'NO_MUNICIPIO']
    ).agg(agregacao).reset_index()

    # Cálculo da Taxa de Climatização de forma segura (evitando divisão por zero)
    df_municipal['TX_CLIMATIZACAO'] = 0.0
    salas_utilizadas_validas = df_municipal['QT_SALAS_UTILIZADAS'] > 0
    df_municipal.loc[salas_utilizadas_validas, 'TX_CLIMATIZACAO'] = \
        df_municipal['QT_SALAS_UTILIZA_CLIMATIZADAS'] / df_municipal['QT_SALAS_UTILIZADAS']
    
    # Garante que a taxa não ultrapasse 100% e preenche NaNs com 0
    df_municipal['TX_CLIMATIZACAO'] = df_municipal['TX_CLIMATIZACAO'].clip(upper=1).fillna(0)

    # Cálculo do IQIE: média de todos os indicadores percentuais + taxa de climatização
    colunas_para_iqie = indicadores_binarios + ['TX_CLIMATIZACAO']
    df_municipal['IQIE'] = df_municipal[colunas_para_iqie].mean(axis=1)

    # --- 5. FORMATAÇÃO DO RESULTADO FINAL ---
    print("Cálculo do IQIE Municipal concluído com sucesso.")
    
    df_resultado = df_municipal[['CO_MUNICIPIO', 'NO_MUNICIPIO', 'IQIE']]
    df_resultado = df_resultado.rename(columns={
        'CO_MUNICIPIO': 'Código do Município',
        'NO_MUNICIPIO': 'Nome do Município'
    })
    return df_resultado


#Indicador de Nível Socioeconômico (INSE) - SAEB (INEP)
def processar_inse():
    """
    Faz o download e processa dados socioeconômicos do INEP.
    Tenta novamente a conexão em caso de falha.

    Returns:
        pandas.DataFrame: DataFrame com a média do INSE por município.
    """
    url = 'https://download.inep.gov.br/informacoes_estatisticas/indicadores_educacionais/2021/nivel_socioeconomico/INSE_2021_municipios.xlsx'
    tentativas = 3
    for i in range(tentativas):
        try:
            print(f"Tentativa {i + 1} de {tentativas} para acessar a URL...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            print("Conexão bem-sucedida!")
            
            # Carrega a planilha correta do arquivo Excel
            df = pd.read_excel(response.content, sheet_name='INSE_MUN_2021')
            
            # Limpeza e conversão de dados
            df['MEDIA_INSE'] = pd.to_numeric(df['MEDIA_INSE'], errors='coerce')
            df.dropna(subset=['MEDIA_INSE'], inplace=True)
            
            # Agrega pela média, incluindo agora o NOME do município
            df_socio = df.groupby(['CO_MUNICIPIO', 'NO_MUNICIPIO'])['MEDIA_INSE'].mean().reset_index()
            
            return df_socio

        except requests.exceptions.RequestException as e:
            print(f"Falha na conexão: {e}")
            if i < tentativas - 1:
                print("Aguardando 5 segundos antes de tentar novamente...")
                time.sleep(5)
            else:
                print("Todas as tentativas de conexão falharam.")
                return None
            
def extrair_afd():
    """
    Baixa e processa dados de formação de docentes. Agrega os dados por município
    para calcular a média percentual de formação adequada, garantindo um único
    registro por município.

    Returns:
        Um DataFrame do Pandas com código, nome e a média do percentual de
        formação adequada por município, devidamente agregado.
    """
    url = "https://download.inep.gov.br/informacoes_estatisticas/indicadores_educacionais/2024/AFD_2024_MUNICIPIOS.zip"
    for tentativa in range(2):
        try:
            print("Tentando baixar o arquivo...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            print("Download concluído com sucesso!")

            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                caminho_arquivo = 'AFD_2024_MUNICIPIOS/AFD_MUNICIPIOS_2024.xlsx'
                with z.open(caminho_arquivo) as f:
                    # Carrega o arquivo excel
                    df = pd.read_excel(f, header=7)

                    # Seleciona as colunas de interesse pelo seu índice
                    df_temp = df.iloc[:, [3, 4, 7, 12]].copy()
                    df_temp.columns = [
                        'cod_municipio',
                        'nome_municipio',
                        'perc_infantil',
                        'perc_fundamental'
                    ]

                    # Converte colunas para numérico, tratando erros
                    df_temp['perc_infantil'] = pd.to_numeric(df_temp['perc_infantil'], errors='coerce')
                    df_temp['perc_fundamental'] = pd.to_numeric(df_temp['perc_fundamental'], errors='coerce')

                    # Calcula a média por linha (ainda com duplicatas)
                    df_temp['media_percentual'] = df_temp[['perc_infantil', 'perc_fundamental']].mean(axis=1)

                    # >>> ETAPA DE AGREGAÇÃO ADICIONADA <<<
                    # Agrupa pelo código e nome do município e calcula a média final
                    afd_agregado = df_temp.groupby(
                        ['cod_municipio', 'nome_municipio']
                    )['media_percentual'].mean().reset_index()

                    # Renomeia a coluna da média para o nome final
                    afd_agregado.rename(columns={'media_percentual': 'media_percentual_formacao_adequada'}, inplace=True)
                    
                    return afd_agregado

        except requests.exceptions.RequestException as e:
            print(f"Erro ao baixar o arquivo: {e}")
            if tentativa == 0:
                print("Tentando novamente...")
            else:
                print("Não foi possível baixar o arquivo após 2 tentativas.")
                return pd.DataFrame()

if __name__ == "__main__":
    # --- Execução da Nota média de Português e Matemática do SAEB (INEP) ---
    df_saeb_mt_pt = pt_mt_saeb()
    print("\n\n--- Resultado: Nota média de Português e Matemática do SAEB Por Município (10 primeiras linhas)---\n\n")
    print(df_saeb_mt_pt.head(10))

    # --- Execução da Taxa de aprovação IDEB (INEP) ---
    df_taxa_aprov = aprov_ideb()

    print("\n\n--- Taxa de Aprovação Média do IDEB por Município (10 primeiras linhas) ---\n\n")
    print(df_taxa_aprov.head(10))
    print("-" * 60)
    print(f"Total de municípios com dados consolidados: {len(df_taxa_aprov)}")

    # --- Execução do Cálculo do Índice de Qualidade da Infraestrutura Escolar (IQIE) - Censo escolar (INEP)---
    df_iqie = gerar_indice_infraestrutura_municipal()
    print("\n\n ÍNDICE DE QUALIDADE DA INFRAESTRUTURA ESCOLAR, calculado por meio do Censo Escolar (INEP)")

    print("\n 10 primeiras Linhas")
    print(df_iqie.head(10)) 

    # -- Execução do índice de Situação Socioeconômica (ISNE)---
    df_socioeconomicos = processar_inse()
    print("\nIndice de Situação Socioeconômica (INSE) - SAEB (10 primeiras linhas)")
    print('10 primeiras linhas')
    if df_socioeconomicos is not None:
        print(df_socioeconomicos.head(10))
    else:
        print("Nenhum dado socioeconômico foi retornado.")

    # -- Execuão da Adequação da Formação Docente (AFD) - INEP ---
    df_afd = extrair_afd()
    if df_afd is not None and not df_afd.empty:
        print("\n Adequação da Formação Docente - AFD (INEP) (10 primerias linhas) ")
        print(df_afd.head(10))
    else:
        print("\nNenhum dado foi carregado ou o DataFrame está vazio.")

    # --- Execução dos Dados do Instituto Alpargatas (IA) ---
    df_ia = ler_ia()
    print("\n\n--- Dados do Instituto Alpargatas (IA) ---\n\n")
    print(df_ia.info())

    # --- Execução dos Dados da Divisão Territorial Brasileira - IBGE ---
    df_dtb = ler_dtb()
    print("\n\n--- Dados da Divisão Territorial Brasileira (DTB) - IBGE")
    print(df_dtb.info())
          