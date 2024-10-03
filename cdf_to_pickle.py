import os
import pickle
from netCDF4 import Dataset

def netcdf_para_pickle(input_dir, output_dir, variable_name='Band1'):
    """
    Converte todos os arquivos NetCDF em um diretório para arquivos Pickle, mantendo o mesmo nome dos arquivos.

    :param input_dir: Caminho para o diretório com arquivos NetCDF.
    :param output_dir: Caminho para o diretório onde os arquivos Pickle serão salvos.
    :param variable_name: Nome da variável a ser extraída dos arquivos NetCDF. Padrão é 'Band1'.
    """
    # Verificar se o diretório de saída existe, senão criá-lo
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Listar todos os arquivos NetCDF no diretório de entrada
    netcdf_files = [f for f in os.listdir(input_dir) if f.endswith('.nc')]
    
    # Iterar sobre todos os arquivos NetCDF e convertê-los para Pickle
    for netcdf_file in netcdf_files:
        file_name = os.path.join(input_dir, netcdf_file)
        full_disk_ds = Dataset(file_name, 'r')
        
        # Dicionário para armazenar a variável extraída
        dict_indices = {}
        if variable_name in full_disk_ds.variables:
            data = full_disk_ds.variables[variable_name][:]
            dict_indices[variable_name] = data
        
        # Criar o nome do arquivo Pickle correspondente
        pkl_file_name = os.path.join(output_dir, netcdf_file.replace('.nc', '.pkl'))
        
        # Abrir o arquivo Pickle para escrita
        with open(pkl_file_name, 'wb') as pkl_file:
            pickle.dump(dict_indices, pkl_file)
        
        print(f'Created pickle file: {pkl_file_name}')
        
        # Fechar o dataset NetCDF
        full_disk_ds.close()

# Exemplo de uso
input_dir = 'Scripts/goes16/profundidade_das_nuvens'
output_dir = 'Scripts/goes16/pickle'
netcdf_para_pickle(input_dir, output_dir, variable_name='Band1')
