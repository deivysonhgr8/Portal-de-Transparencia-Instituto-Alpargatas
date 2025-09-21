import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import iqe # Importa o script que calcula o IQE

def plotar_grafico_barras_iqe(df):
    """
    Gera um gráfico de barras com o IQE de cada município.
    """
    if df.empty:
        print("DataFrame vazio, não é possível gerar o gráfico de barras.")
        return

    print("\n-> Gerando gráfico de barras do IQE por município...")
    
    df_sorted = df.sort_values(by='IQE', ascending=False)
    
    plt.figure(figsize=(12, 8))
    sns.barplot(x='IQE', y='nome_municipio', data=df_sorted, palette='viridis', orient='h')
    
    plt.title('Índice de Qualidade da Educação (IQE) por Município', fontsize=16)
    plt.xlabel('IQE (Escala de 1 a 10)', fontsize=12)
    plt.ylabel('Município', fontsize=12)
    plt.xlim(0, 10.5) # Define o limite do eixo x para ir de 0 a 10
    plt.tight_layout()
    
    for index, value in enumerate(df_sorted['IQE']):
        plt.text(value + 0.1, index, f'{value:.2f}', va='center')
        
    plt.show()

def plotar_graficos_dispersao(df):
    """
    Gera gráficos de dispersão para cada variável vs. o IQE final.
    """
    if df.empty: return
        
    print("\n-> Gerando gráficos de dispersão (Variável vs. IQE)...")
    
    variaveis = ['nota_saeb', 'taxa_aprovacao', 'iqie_infraestrutura', 'inse_socioeconomico', 'formacao_docente']
    
    for var in variaveis:
        plt.figure(figsize=(8, 6))
        sns.regplot(x=var, y='IQE', data=df, scatter_kws={'alpha':0.6}, line_kws={"color": "red"})
        
        plt.title(f'Relação entre {var.replace("_", " ").title()} e o IQE Final', fontsize=14)
        plt.xlabel(f'Valor da Variável ({var.replace("_", " ").title()})', fontsize=12)
        plt.ylabel('IQE (Escala de 1 a 10)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()

# Bloco de Execução Principal do script de Load/Visualização
if __name__ == "__main__":
    print("--- INICIANDO ROTINA DE LOAD E VISUALIZAÇÃO ---")
    
    # 1. Executa o iqe.py e carrega o DataFrame completo
    df_completo = iqe.calcular_iqe()
    
    if not df_completo.empty:
        # 2. Gera os gráficos a partir do DataFrame carregado
        plotar_grafico_barras_iqe(df_completo)
        plotar_graficos_dispersao(df_completo)
        print("\n--- ROTINA DE VISUALIZAÇÃO FINALIZADA ---")
    else:
        print("\n--- ROTINA DE VISUALIZAÇÃO ENCERRADA (DADOS INSUFICIENTES) ---")