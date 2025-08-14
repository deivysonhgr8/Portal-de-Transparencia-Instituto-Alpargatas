import pandas as pd
from os import path

data_dir = r'C:\Users\Deivyson Henrique\Desktop\projeto alpargatas\ia_cdn_main\data'

def ler_dtb(ano):
    """Lê e formata dados DTB para um determinado ano."""
    # Ajusta o nome do arquivo
    if ano == 2024:
        file_name = 'RELATORIO_DTB_BRASIL_2024_MUNICIPIOS.xls'
        skip = 6
    elif ano in [2023, 2022, 2021, 2020]:
        file_name = f'RELATORIO_DTB_BRASIL_MUNICIPIO_{ano}.xls'
        skip = 6 if ano in [2023, 2022] else 0
    else:
        raise ValueError("Ano inválido.")

    file_path = path.join(data_dir, file_name)
    print(f"\nLendo o arquivo: {file_path}")
    df = pd.read_excel(file_path,
                       skiprows=skip,
                       usecols=['UF', 'Nome_UF', 'Nome Região Geográfica Imediata',
                                'Código Município Completo', 'Nome_Município'])

    df.columns = ['id_uf', 'ds_uf', 'ds_rgi', 'id_mundv', 'ds_mun']
    df = df.drop_duplicates(subset=['id_mundv'])

    # Formatação do nome
    df['ds_formatada'] = (df['ds_mun'].str.upper()
                                         .str.replace("[-.!?'`()]", "", regex=True)
                                         .str.replace("- MIXING CENTER", "", regex=False)
                                         .str.strip()
                                         .str.replace(" ", "", regex=False))
    df['ano'] = ano
    return df