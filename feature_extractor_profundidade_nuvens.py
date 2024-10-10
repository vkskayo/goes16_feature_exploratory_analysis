import os
from netCDF4 import Dataset
import os
import netCDF4 as nc


def calcular_diferenca_canais(canal1, canal2, yyyymmdd, input_path, output_path):
    """Calcula a diferença entre dois canais de arquivos NetCDF para uma data específica e salva em uma pasta chamada 'profundidade_das_nuvens'."""
    
    # Caminhos completos para os canais
    #canal1_full_path = f'{data_path}/{canal1_path}'
   # canal2_full_path = f'{data_path}/{canal2_path}'
    
    # Caminho da pasta de saída
    output_dir = os.path.join(output_path, 'profundidade_das_nuvens', yyyymmdd)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Listar arquivos NetCDF nos dois canais
    canal1_files = [f for f in os.listdir(input_path) if f.endswith('.nc') and f'band{canal1}' in f and yyyymmdd in f]
    canal2_files = [f for f in os.listdir(input_path) if f.endswith('.nc') and f'band{canal2}' in f and yyyymmdd in f]
 
    # Iterar sobre os arquivos do canal 1 e encontrar o correspondente no canal 2
    for file1 in canal1_files:
        # Procurar arquivo correspondente no canal 2 com a mesma estampa de tempo
        timestamp = file1[:12]  # Extraindo a estampa de tempo do nome do arquivo
        file2 = next((f for f in canal2_files if timestamp in f), None)
        
        if file2:
            # Abrir os arquivos NetCDF dos dois canais
            canal1_nc = nc.Dataset(os.path.join(input_path, file1))
            canal2_nc = nc.Dataset(os.path.join(input_path, file2))
            
            # Supor que o dado está na mesma variável em ambos os canais (ajustar conforme necessário)
            var_name = 'Band1'  # Substituir pelo nome real da variável se diferente
            data1 = canal1_nc.variables[var_name][:]
            data2 = canal2_nc.variables[var_name][:]
            
            # Calcular a diferença entre os dois canais
            diff_data = data1 - data2
            
            # Definir o nome do arquivo de saída
            output_file = os.path.join(output_dir, f'profundidade_nuvem_{timestamp}.nc')
            
            # Criar um novo arquivo NetCDF para salvar a diferença
            with nc.Dataset(output_file, 'w', format='NETCDF4') as new_nc:
                # Definir dimensões (assumindo que ambas são idênticas nos dois arquivos)
                for dim_name, dim in canal1_nc.dimensions.items():
                    new_nc.createDimension(dim_name, len(dim) if not dim.isunlimited() else None)
                
                # Criar variáveis (usando as mesmas variáveis do arquivo original)
                for var_name, var in canal1_nc.variables.items():
                    new_var = new_nc.createVariable(var_name, var.datatype, var.dimensions)
                    if var_name == 'Band1':
                        new_var[:] = diff_data
                    else:
                        new_var[:] = var[:]
                
                # Copiar atributos globais
                new_nc.setncatts({k: canal1_nc.getncattr(k) for k in canal1_nc.ncattrs()})
            
            # Fechar os arquivos NetCDF lidos
            canal1_nc.close()
            canal2_nc.close()
            
            print(f'Diferença calculada e salva em: {output_file}')
        else:
            print(f'Arquivo correspondente não encontrado para: {file1}')

