import os
import numpy as np
from netCDF4 import Dataset


def relatorio_features(diretorio_features, arquivo_saida):

    # Caminho para o diretório principal que contém as subpastas
    diretorio_principal = diretorio_features

    # Caminho para o arquivo de saída
    arquivo_saida = arquivo_saida

    # Abrir o arquivo de saída para escrever os resultados
    with open(arquivo_saida, 'w') as arquivo_txt:
        
        # Iterar sobre todas as pastas no diretório principal
        for pasta in os.listdir(diretorio_principal):
            caminho_pasta = os.path.join(diretorio_principal, pasta)
            
            # Verificar se é um diretório
            if os.path.isdir(caminho_pasta):
                print(f"\nProcessando a pasta: {pasta}\n")
                
                # Inicializar variáveis globais para armazenar o mínimo e o máximo globais
                minimo_global = np.inf  # Começa com infinito positivo
                maximo_global = -np.inf  # Começa com infinito negativo

                # Listar todos os arquivos NetCDF na pasta
                arquivos_netcdf = [f for f in os.listdir(caminho_pasta) if f.endswith('.nc')]

                # Iterar sobre cada arquivo NetCDF na pasta
                for arquivo in arquivos_netcdf:
                    caminho_arquivo = os.path.join(caminho_pasta, arquivo)
                    
                    # Abrir o arquivo NetCDF
                    with Dataset(caminho_arquivo, 'r') as dataset:
                        # Verificar se a variável 'Band1' está presente
                        if 'Band1' in dataset.variables:
                            data_band1 = dataset.variables['Band1'][:]
                            
                            # Verificar se os dados são um array NumPy
                            if isinstance(data_band1, np.ndarray):
                                # Calcular o mínimo e máximo desse arquivo
                                minimo_local = np.min(data_band1)
                                maximo_local = np.max(data_band1)
                                
                                # Atualizar os valores globais
                                minimo_global = min(minimo_global, minimo_local)
                                maximo_global = max(maximo_global, maximo_local)
                            else:
                                print(f"Os dados em 'Band1' no arquivo {arquivo} não são um array NumPy.")
                        else:
                            print(f"A variável 'Band1' não está presente no arquivo {arquivo}.")

                # Escrever os resultados da pasta no arquivo de saída
                arquivo_txt.write(f"Pasta: {pasta}\n")
                arquivo_txt.write(f"Valor mínimo global: {minimo_global}\n")
                arquivo_txt.write(f"Valor máximo global: {maximo_global}\n")
                arquivo_txt.write("\n")  # Linha em branco para separar pastas

                # Mostrar o resultado para cada pasta
                print(f"Resultado da pasta {pasta}:")
                print(f" - Valor mínimo global: {minimo_global}")
                print(f" - Valor máximo global: {maximo_global}\n")

    print(f"Resumo salvo em {arquivo_saida}.")

