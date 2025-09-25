# generate_simulated_data.py (VERSÃO 2 - CORRIGIDA)

import pandas as pd
import numpy as np
import os
import iqe # Continua usando o iqe.py, mas agora apenas para obter a lista de municípios para a predição final

def gerar_dados_sinteticos(num_amostras=1000):
    """
    Gera um DataFrame com dados SINTÉTICOS para treinar o modelo de forma robusta.
    Em vez de usar apenas os poucos municípios reais, cria muitos exemplos fictícios.
    """
    print(f"-> Gerando {num_amostras} amostras sintéticas para um treinamento robusto...")
    np.random.seed(42)

    # Criar distribuições realistas para os indicadores
    iqe_anterior = np.random.uniform(1, 9.5, num_amostras)
    nota_saeb = iqe_anterior * np.random.uniform(0.9, 1.1, num_amostras)
    taxa_aprovacao = 80 + (iqe_anterior * 2) + np.random.normal(0, 2, num_amostras)
    iqie_infra = iqe_anterior / 10 * np.random.uniform(0.8, 1.2, num_amostras)
    inse_socio = iqe_anterior / 2 * np.random.uniform(0.9, 1.1, num_amostras)
    formacao_docente = 60 + (iqe_anterior * 3) + np.random.normal(0, 5, num_amostras)
    valor_investido = np.random.uniform(20000, 250000, num_amostras)

    dados = {
        'cod_municipio': range(100000, 100000 + num_amostras), # Códigos fictícios
        'nome_municipio_anterior': [f"Sintético_{i}" for i in range(num_amostras)],
        'iqe_anterior': iqe_anterior,
        'nota_saeb_anterior': nota_saeb,
        'taxa_aprovacao_anterior': taxa_aprovacao.clip(50, 100),
        'iqie_infraestrutura_anterior': iqie_infra.clip(0, 1),
        'inse_socioeconomico_anterior': inse_socio.clip(1, 6),
        'formacao_docente_anterior': formacao_docente.clip(30, 100),
        'valor_investido': valor_investido
    }
    df_sintetico = pd.DataFrame(dados)

    # Lógica de simulação do resultado (igual à anterior)
    fator_melhoria = (10 - df_sintetico['iqe_anterior']) / 10
    impacto_investimento = (df_sintetico['valor_investido'] / 100000) * fator_melhoria * np.random.uniform(0.8, 1.2, size=num_amostras)
    flutuacao_natural = np.random.normal(0, 0.1, size=num_amostras)
    df_sintetico['iqe_recente'] = df_sintetico['iqe_anterior'] + impacto_investimento + flutuacao_natural
    df_sintetico['iqe_recente'] = df_sintetico['iqe_recente'].clip(1, 10)

    print("-> Geração de dados sintéticos concluída.")
    return df_sintetico


# Bloco Principal
if __name__ == "__main__":
    print("--- INICIANDO GERAÇÃO DE DADOS HISTÓRICOS SIMULADOS (V2) ---")
    
    df_treino_sintetico = gerar_dados_sinteticos(num_amostras=1000)

    # Criar o diretório 'data' se ele não existir
    if not os.path.exists('data'):
        os.makedirs('data')
        print("-> Diretório 'data/' criado.")

    caminho_arquivo = 'data/dados_historicos.csv'
    df_treino_sintetico.to_csv(caminho_arquivo, index=False)

    print(f"\n--- SUCESSO! ---")
    print(f"Arquivo '{caminho_arquivo}' com {len(df_treino_sintetico)} registros sintéticos foi criado.")
    print("\nAmostra dos dados de TREINO gerados:")
    print(df_treino_sintetico.head())