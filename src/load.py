import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from transform import data_final
import os

# ========================
# Configurações
# ========================
output_dir = "graficos_municipios"
os.makedirs(output_dir, exist_ok=True)

# Garantir que 'ds_mun' exista priorizando Instituto Alpargatas
if 'ds_mun' not in data_final.columns:
    if 'ds_mun_ia' in data_final.columns:
        data_final = data_final.rename(columns={'ds_mun_ia': 'ds_mun'})
    elif 'ds_mun_dtb' in data_final.columns:
        data_final = data_final.rename(columns={'ds_mun_dtb': 'ds_mun'})

# Selecionar colunas IDEB
ideb_cols = [col for col in data_final.columns if col.startswith('ideb_')]

# Calcular média por município
ideb_media = data_final.groupby('ds_mun')[ideb_cols].mean().reset_index()

# Converter de wide para long
ideb_long = ideb_media.melt(
    id_vars='ds_mun',
    value_vars=ideb_cols,
    var_name='Ano',
    value_name='IDEB'
)

# Ajustar a coluna "Ano" para ser numérica
ideb_long['Ano'] = ideb_long['Ano'].str.replace('ideb_', '').astype(int)

# Lista oficial de anos IDEB (bianuais)
anos_ideb = list(range(2005, 2026, 2))
ideb_long = ideb_long[ideb_long['Ano'].isin(anos_ideb)]

# Criar gráfico separado para cada município
for municipio, dados in ideb_long.groupby('ds_mun'):
    plt.figure(figsize=(8, 5))
    sns.lineplot(data=dados, x='Ano', y='IDEB', marker='o')
    plt.title(f'Evolução do IDEB - {municipio}', fontsize=14)
    plt.ylabel('IDEB Médio')
    plt.xlabel('Ano')
    plt.xticks(anos_ideb)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    
    # Salvar gráfico
    nome_arquivo = os.path.join(output_dir, f"{municipio.replace('/', '_')}.png")
    plt.savefig(nome_arquivo)
    plt.close()

print(f" Gráficos salvos na pasta: {output_dir}")


# Selecionar colunas ideb
ideb_cols = [col for col in data_final.columns if col.startswith('ideb_')]

# Calcular média por UF e ano
ideb_media = data_final.groupby('ds_uf')[ideb_cols].mean().reset_index()

# Converter de wide para long
ideb_long = ideb_media.melt(
    id_vars='ds_uf',
    value_vars=ideb_cols,
    var_name='Ano',
    value_name='IDEB'
)

# Ajustar a coluna "Ano" para ser numérica
ideb_long['Ano'] = ideb_long['Ano'].str.replace('ideb_', '').astype(int)

# Lista oficial de anos IDEB (bianuais)
anos_ideb = list(range(2005, 2026, 2))

# Filtrar somente esses anos
ideb_long = ideb_long[ideb_long['Ano'].isin(anos_ideb)]

# Ordenar corretamente
ideb_long = ideb_long.sort_values(by=['ds_uf', 'Ano'])

# Criar gráfico de linhas
plt.figure(figsize=(12, 6))
sns.lineplot(data=ideb_long, x='Ano', y='IDEB', hue='ds_uf', marker='o')

plt.title('Evolução do IDEB Médio por UF (anos iniciais)', fontsize=14)
plt.ylabel('IDEB Médio')
plt.xlabel('Ano')
plt.xticks(anos_ideb)
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()
