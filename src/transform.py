from os import path
from extract import ler_dtb
from pandas import read_excel, concat
import pandas as pd
from pathlib import Path


data_dir = Path(__file__).parent.parent / 'data'


#Leitura dados IA 2020-2024 
# obs: colocar o caminho do arquivo do seu computador
file_path = data_dir / 'Projetos_de_Atuac807a771o_-_IA_-_2020_a_2025.xlsx'
anos_atuacao = ['2020', '2021', '2022', '2023', '2024']
lista_dataframes = []

for ano in anos_atuacao:
    df = pd.read_excel(file_path, sheet_name=ano, skiprows=5)

    col_map = {}
    for col in df.columns:
        col_norm = col.strip().lower().replace("\n", " ").replace("  ", " ")
        if "cidade" in col_norm:
            col_map["ds_mun"] = col
        elif col_norm in ["uf", "estado"]:
            col_map["sg_uf"] = col
        elif "projeto" in col_norm and "nº" in col_norm:
            col_map["nprojetos"] = col
        elif "institui" in col_norm:
            col_map["ninstituicoes"] = col
        elif "beneficiado" in col_norm:
            col_map["nbeneficiados"] = col

    if "nprojetos" not in col_map:
        proj_cols = [c for c in df.columns if "projeto" in c.lower()]
        if proj_cols:
            col_map["nprojetos"] = proj_cols[-1]

    if "ninstituicoes" not in col_map:
        inst_cols = [c for c in df.columns if "institui" in c.lower()]
        if inst_cols:
            col_map["ninstituicoes"] = inst_cols[-1]

    if "nbeneficiados" not in col_map:
        ben_cols = [c for c in df.columns if "beneficiado" in c.lower()]
        if ben_cols:
            col_map["nbeneficiados"] = ben_cols[-1]

    df_sel = df[[
        col_map["ds_mun"],
        col_map["sg_uf"],
        col_map["nprojetos"],
        col_map["ninstituicoes"],
        col_map["nbeneficiados"]
    ]].copy()

    df_sel.columns = ['ds_mun', 'sg_uf', 'nprojetos', 'ninstituicoes', 'nbeneficiados']
    df_sel["ano_atuacao"] = int(ano)


    df_sel = df_sel.dropna(subset=["ds_mun", "sg_uf"], how="any")
    df_sel = df_sel[~df_sel["ds_mun"].astype(str).str.contains("VARIAÇÃO|Obs|TOTAL", case=False, na=False)]

    lista_dataframes.append(df_sel)

dataia = pd.concat(lista_dataframes, ignore_index=True)

print('dataia' , dataia)

#lendo DTB de 2020-2024
dtb_dict = {ano: ler_dtb(ano) for ano in range(2020, 2025)}
df_dtb = pd.concat(dtb_dict.values(), ignore_index=True)

def formatar_nome(df, coluna, novo_nome="ds_formatada"):
    df[novo_nome] = (df[coluna].str.upper()
                       .str.replace("[-.!?'`()]", "", regex=True)
                       .str.replace("- MIXING CENTER", "")
                       .str.strip()
                       .str.replace(" ", ""))
                       
    return df

df_dtb = formatar_nome(df=df_dtb, coluna='ds_mun')
print('IBGE \n', df_dtb)

dataia= formatar_nome(df=dataia, coluna='ds_mun')
dataia['ds_uf'] = dataia['sg_uf'].map({"PB": "Paraíba", "PE": "Pernambuco",
                                   "MG": "Minas Gerais", "SP": "São Paulo"})
print("IA head \n", dataia.head())
print("IA value_counts \n", dataia.ds_uf.value_counts())

data_m = dataia.merge(df_dtb, how='inner', on=['ds_formatada', 'ds_uf'],
                      suffixes=['_ia','_dtb'], indicator='tipo_merge')
print('\nHEAD\n',data_m.head())
print('\nTIPO MERGE', data_m['tipo_merge'].value_counts)

#investigando os que estão no IA mas não no DTB
x = data_m.query("tipo_merge=='left_only'")
print(x.head())

#IDEB
lista_ideb = [f'VL_OBSERVADO_{x}' for x in range(2005,2025, 2)]
nome_ideb = [f'ideb_{x}' for x in range(2005,2025, 2)]
caminho_ideb = data_dir / 'divulgacao_anos_iniciais_municipios_2023.xlsx'

ideb = read_excel(caminho_ideb,
                  skiprows=9, usecols=['CO_MUNICIPIO', 'REDE'] + lista_ideb,
                  na_values=['-', '--'])
ideb.columns= ['id_mundv','rede'] + nome_ideb
print(ideb.head())
print(ideb.info())

data_final = data_m.merge(ideb, how='left')
print('\n DATA FINAL', data_final)

#Tratamento outliers