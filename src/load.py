from transform import data_final
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Selecionar colunas ideb
ideb_cols = [col for col in data_final.columns if col.startswith('ideb_')]

# Calcular média por UF e ano
ideb_media = data_final.groupby('ds_uf')[ideb_cols].mean().reset_index()

# Converter de wide para long
ideb_long = ideb_media.melt(id_vars='ds_uf', 
                            value_vars=ideb_cols,
                            var_name='Ano', 
                            value_name='IDEB')

# Ajustar a coluna "Ano" para ser numérica
ideb_long['Ano'] = ideb_long['Ano'].str.replace('ideb_', '').astype(int)

# Criar gráfico de linhas
plt.figure(figsize=(12, 6))
sns.lineplot(data=ideb_long, x='Ano', y='IDEB', hue='ds_uf', marker='o')

plt.title('Evolução do IDEB Médio por UF (anos iniciais)', fontsize=14)
plt.ylabel('IDEB Médio')
plt.xlabel('Ano')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()
