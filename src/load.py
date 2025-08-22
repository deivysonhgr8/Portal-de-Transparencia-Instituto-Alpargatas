import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from transform import data_final
from matplotlib.backends.backend_pdf import PdfPages

if 'ds_mun' not in data_final.columns:
    if 'ds_mun_ia' in data_final.columns:
        data_final = data_final.rename(columns={'ds_mun_ia': 'ds_mun'})
    elif 'ds_mun_dtb' in data_final.columns:
        data_final = data_final.rename(columns={'ds_mun_dtb': 'ds_mun'})

ideb_cols = [col for col in data_final.columns if col.startswith('ideb_')]
anos_ideb = list(range(2005, 2025, 2))

pdf_path = "relatorio_ideb.pdf"
pdf = PdfPages(pdf_path)


ideb_media_mun = data_final.groupby('ds_mun')[ideb_cols].mean().reset_index()
ideb_long_mun = ideb_media_mun.melt(
    id_vars='ds_mun',
    value_vars=ideb_cols,
    var_name='Ano',
    value_name='IDEB'
)
ideb_long_mun['Ano'] = ideb_long_mun['Ano'].str.replace('ideb_', '').astype(int)
ideb_long_mun = ideb_long_mun[ideb_long_mun['Ano'].isin(anos_ideb)]

for municipio, dados in ideb_long_mun.groupby('ds_mun'):
    plt.figure(figsize=(8, 5))
    sns.lineplot(data=dados, x='Ano', y='IDEB', marker='o')
    plt.title(f'Evolução do IDEB - {municipio}', fontsize=14)
    plt.ylabel('IDEB Médio')
    plt.xlabel('Ano')
    plt.xticks(anos_ideb)
    
    plt.axvspan(2020, anos_ideb[-1], color='yellow', alpha=0.2, label='Após atuação Instituto')
    
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    pdf.savefig()
    plt.close()


ideb_media_uf = data_final.groupby('ds_uf')[ideb_cols].mean().reset_index()
ideb_long_uf = ideb_media_uf.melt(
    id_vars='ds_uf',
    value_vars=ideb_cols,
    var_name='Ano',
    value_name='IDEB'
)
ideb_long_uf['Ano'] = ideb_long_uf['Ano'].str.replace('ideb_', '').astype(int)
ideb_long_uf = ideb_long_uf[ideb_long_uf['Ano'].isin(anos_ideb)]
ideb_long_uf = ideb_long_uf.sort_values(by=['ds_uf', 'Ano'])

plt.figure(figsize=(12, 6))
sns.lineplot(data=ideb_long_uf, x='Ano', y='IDEB', hue='ds_uf', marker='o')
plt.title('Evolução do IDEB Médio por UF (anos iniciais)', fontsize=14)
plt.ylabel('IDEB Médio')
plt.xlabel('Ano')
plt.xticks(anos_ideb)

# Sombreia a área a partir de 2020
plt.axvspan(2020, anos_ideb[-1], color='yellow', alpha=0.2, label='Após atuação Instituto')

plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()
pdf.savefig()
plt.close()

pdf.close()
print(f" Relatório completo salvo em: {pdf_path}")
