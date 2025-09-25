# investment_model.py

import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import iqe # Importa seu script para obter os dados atuais

def carregar_dados_historicos():
    """
    Função para carregar e preparar os dados históricos.
    !! ATENÇÃO: Você precisará criar este arquivo 'dados_historicos.csv' !!
    Ele deve conter os dados de investimento e os IQEs de dois períodos.
    """
    try:
        # Exemplo de como o arquivo 'dados_historicos.csv' deve ser:
        # cod_municipio, nome_municipio, iqe_anterior, nota_saeb_anterior, ..., valor_investido, iqe_recente
        df_hist = pd.read_csv('data/dados_historicos.csv')
        print("-> Dados históricos carregados com sucesso.")
        return df_hist
    except FileNotFoundError:
        print("ERRO: Arquivo 'dados_historicos.csv' não encontrado.")
        print("Crie este arquivo com os dados históricos de investimento e IQE para treinar o modelo.")
        return None

def engenharia_de_atributos(df):
    """
    Cria a variável alvo (delta_iqe) e seleciona as features.
    """
    # 1. Calcular a variável alvo
    df['delta_iqe'] = df['iqe_recente'] - df['iqe_anterior']
    
    # 2. Definir as variáveis preditivas (features)
    features = [
        'iqe_anterior',
        'nota_saeb_anterior',
        'taxa_aprovacao_anterior',
        'iqie_infraestrutura_anterior',
        'inse_socioeconomico_anterior',
        'formacao_docente_anterior',
        'valor_investido'
    ]
    
    # Garante que as colunas 'delta_iqe' e as features existam
    colunas_necessarias = ['delta_iqe'] + features
    if not all(col in df.columns for col in colunas_necessarias):
        print("ERRO: O DataFrame histórico não contém todas as colunas necessárias.")
        return None, None
        
    X = df[features]
    y = df['delta_iqe']
    
    print("-> Engenharia de atributos concluída. Variável alvo 'delta_iqe' criada.")
    return X, y

def treinar_modelo_preditivo(X, y):
    """
    Treina um modelo LightGBM para prever o delta_iqe.
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("\n--- FASE: TREINANDO O MODELO PREDITIVO ---")
    model = lgb.LGBMRegressor(random_state=42)
    model.fit(X_train, y_train)
    
    # Avalia o modelo
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred) #type: ignore
    print(f"-> Modelo treinado com sucesso. Mean Absolute Error no set de teste: {mae:.4f}")
    
    return model

def gerar_recomendacoes_investimento(model, df_dados_atuais, investimento_simulado=100000):
    """
    Usa o modelo treinado para prever o impacto de um investimento simulado
    nos municípios com dados atuais.
    """
    print(f"\n--- FASE: GERANDO RECOMENDAÇÕES PARA UM INVESTIMENTO DE R$ {investimento_simulado:.2f} ---")
    
    # Prepara o DataFrame atual para a predição
    df_pred = df_dados_atuais.copy()
    
    # Renomeia colunas atuais para corresponder às features do modelo
    df_pred.rename(columns={
        'IQE': 'iqe_anterior',
        'nota_saeb': 'nota_saeb_anterior',
        'taxa_aprovacao': 'taxa_aprovacao_anterior',
        'iqie_infraestrutura': 'iqie_infraestrutura_anterior',
        'inse_socioeconomico': 'inse_socioeconomico_anterior',
        'formacao_docente': 'formacao_docente_anterior'
    }, inplace=True)
    
    # Adiciona a coluna do investimento simulado
    df_pred['valor_investido'] = investimento_simulado
    
    # Seleciona as mesmas features usadas no treino
    features_modelo = model.feature_name_
    X_atual = df_pred[features_modelo]
    
    # Faz a predição do aumento do IQE
    df_pred['delta_iqe_predito'] = model.predict(X_atual)
    
    # Calcula o "Impacto por Real"
    df_pred['impacto_por_real'] = df_pred['delta_iqe_predito'] / df_pred['valor_investido']
    
    # Prepara o resultado final
    df_resultado = df_pred[[
        'cod_municipio',
        'nome_municipio',
        'ds_uf',
        'iqe_anterior',
        'delta_iqe_predito'
    ]].sort_values(by='delta_iqe_predito', ascending=False).reset_index(drop=True)
    
    df_resultado.rename(columns={'iqe_anterior': 'IQE_Atual', 'delta_iqe_predito': 'Melhoria_Estimada_IQE'}, inplace=True)
    
    return df_resultado

# Bloco de Execução Principal
if __name__ == "__main__":
    # 1. Carregar dados históricos para treino
    df_historico = carregar_dados_historicos()
    
    if df_historico is not None:
        # 2. Preparar dados para o modelo
        X, y = engenharia_de_atributos(df_historico)
        
        if X is not None:
            # 3. Treinar o modelo
            modelo = treinar_modelo_preditivo(X, y)
            
            # 4. Carregar os dados atuais (executando a lógica do iqe.py)
            print("\n--- FASE: CARREGANDO DADOS ATUAIS DOS MUNICÍPIOS ---")
            df_atual_completo = iqe.calcular_iqe()
            
            if not df_atual_completo.empty:
                # 5. Gerar e exibir as recomendações
                df_recomendacoes = gerar_recomendacoes_investimento(modelo, df_atual_completo)
                
                print("\n\n--- RANKING DE PRIORIZAÇÃO DE INVESTIMENTO ---")
                print("Municípios ordenados pelo maior potencial de melhoria do IQE com um investimento padrão:")
                print(df_recomendacoes)