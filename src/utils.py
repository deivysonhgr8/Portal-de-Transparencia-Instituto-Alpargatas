from pandas import read_excel
from os import path

#leitura de dados de divisão geográfica do brasil - munícipios

def getdtb(file:str):
    data_dir = r'C:\Users\Deivyson Henrique\Desktop\projeto alpargatas\ia_cdn\data'
    file = path.join(data_dir, r'RELATORIO_DTB_BRASIL_2024_MUNICIPIOS.xls')
    print('lendo o arquivo', file)

    data = read_excel(file, skiprows=6, nrows=100, usecols= ['UF', 'Nome_UF', 'Nome Região Geográfica Imediata', 'Código Município Completo',
                                                  'Nome_Município'])
    data.columns = ['id_uf', 'nome_uf', 'rgi', 'id_mun', 'nome_municipio']

    #garantir a unicidade de municípios

    data = data.drop_duplicates(subset=['id_mun'])

    print ('\n INSPEÇÃO DAS PRIMEIRAS LINHAS \n\n', (data.head(5)))
    print ('\n INSPEÇÃO DAS ÚLTIMAS LINHAS \n\n', (data.tail(5)))
    print('\n INFO \n\n', (data.info()))

    return data

getdtb(r'RELATORIO_DTB_BRASIL_2024_MUNICIPIOS.xls')
#teste
