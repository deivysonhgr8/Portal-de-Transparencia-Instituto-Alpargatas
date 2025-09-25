import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from factor_analyzer import FactorAnalyzer
from factor_analyzer import calculate_bartlett_sphericity, calculate_kmo
import transform

def calcular_iqe():
    """
    Executa a análise fatorial, calcula o IQE e cria um índice final 
    em uma escala de 1 a 10. Retorna um DataFrame completo para visualização.
    """
    print("--- FASE 1: CARREGANDO DADOS CONSOLIDADOS ---")
    df_base = transform.criar_base_de_analise_completa()
    if df_base.empty: return pd.DataFrame()

    print("\n--- FASE 2: PREPARANDO DADOS PARA ANÁLISE FATORIAL ---")
    variaveis_analise = ['nota_saeb', 'taxa_aprovacao', 'iqie_infraestrutura', 'inse_socioeconomico', 'formacao_docente']
    df_analise = df_base.dropna(subset=variaveis_analise).copy()
    if len(df_analise) < 10: return pd.DataFrame()
    
    df_valores = df_analise[variaveis_analise]
    scaler = StandardScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df_valores), columns=variaveis_analise)
    print("-> Variáveis padronizadas com sucesso (Z-Score).")

    print("\n--- FASE 3: EXECUTANDO ANÁLISE FATORIAL E EXIBINDO PESOS ---")
    fa = FactorAnalyzer(n_factors=1)
    fa.fit(df_scaled)
    cargas_fatoriais = pd.DataFrame(fa.loadings_, index=variaveis_analise, columns=['Carga_Fatorial'])
    cargas_ao_quadrado = cargas_fatoriais['Carga_Fatorial'] ** 2
    soma_cargas_ao_quadrado = cargas_ao_quadrado.sum()
    pesos = cargas_ao_quadrado / soma_cargas_ao_quadrado
    pesos_df = pesos.to_frame(name='Peso')
    pesos_df['Peso (%)'] = (pesos_df['Peso'] * 100).map('{:.2f}%'.format)
    print("\nPesos calculados para cada variável:")
    print(pesos_df.sort_values(by='Peso', ascending=False))

    print("\n--- FASE 4: CALCULANDO E NORMALIZANDO O IQE ---")
    df_analise['IQE_original'] = np.dot(df_scaled, pesos)
    df_analise.sort_values(by='IQE_original', ascending=False, inplace=True)
    df_analise.reset_index(drop=True, inplace=True)
    
    min_iqe = df_analise['IQE_original'].min()
    max_iqe = df_analise['IQE_original'].max()
    iqe_0a1 = (df_analise['IQE_original'] - min_iqe) / (max_iqe - min_iqe)
    df_analise['IQE'] = (iqe_0a1 * 9) + 1
    print("-> Coluna 'IQE' final criada na escala de 1 a 10.")
    
    # Retorna o DataFrame completo com as colunas originais e o IQE calculado
    return df_analise

# Bloco de execução principal (para rodar o iqe.py sozinho e gerar o CSV)
if __name__ == "__main__":
    df_iqe = calcular_iqe()
    # Define as colunas para o resultado final limpo
    colunas_resultado = ['cod_municipio', 'nome_municipio', 'ds_uf', 'IQE']
    df_para_exibir_e_salvar = df_iqe[colunas_resultado]
    # --- MUDANÇA APLICADA AQUI ---
        # Adiciona o print do DataFrame final no console
    print("\n\n--- RESULTADO FINAL: ÍNDICE DE QUALIDADE DA EDUCAÇÃO (IQE) ---")
    print(f"O IQE foi calculado para {len(df_para_exibir_e_salvar)} municípios.")
    print(df_para_exibir_e_salvar)
