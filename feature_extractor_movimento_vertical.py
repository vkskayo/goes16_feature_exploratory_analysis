import os
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from osgeo import gdal, osr
import netCDF4 as nc

def process_vertical_movement(canal, yyyymmdd, input_path, output_path):
    # Caminho da pasta de saída
    output_dir = os.path.join(output_path, 'fluxo_ascendente', yyyymmdd)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    files = sorted([f for f in os.listdir(input_path) if f.endswith('.nc') and f'band{canal}' in f and yyyymmdd in f])

    for i in range(len(files) - 3):  
        file_t0 = os.path.join(input_path, files[i])
        file_t30 = os.path.join(input_path, files[i + 3])

        timestamp_t0 = files[i][:12]  # Extraindo a estampa de tempo do nome do arquivo
        timestamp_t30 = files[i+3][:12]  # Extraindo a estampa de tempo do nome do arquivo

        timestamp = f'{timestamp_t0}_{timestamp_t30}'

        print(f'Processing {files[i]}, {files[i+3]}')

        t0_nc = nc.Dataset(file_t0)
        t30_nc = nc.Dataset(file_t30)
            
        # Supor que o dado está na mesma variável em ambos os canais (ajustar conforme necessário)
        var_name = 'Band1'  # Substituir pelo nome real da variável se diferente
        data_t0 = t0_nc.variables[var_name][:]
        data_t30 = t30_nc.variables[var_name][:]
        
        # Calculate the temperature tendency (derivative) for 30 minutes
        tendency_30min = (data_t30 - data_t0) / 30

    # Definir o nome do arquivo de saída
        output_file = os.path.join(output_dir, f'fluxo_ascendente_{timestamp}.nc')
        
        # Criar um novo arquivo NetCDF para salvar a diferença
        with nc.Dataset(output_file, 'w', format='NETCDF4') as new_nc:
            # Definir dimensões (assumindo que ambas são idênticas nos dois arquivos)
            for dim_name, dim in t0_nc.dimensions.items():
                new_nc.createDimension(dim_name, len(dim) if not dim.isunlimited() else None)
            
            # Criar variáveis (usando as mesmas variáveis do arquivo original)
            for var_name, var in t0_nc.variables.items():
                new_var = new_nc.createVariable(var_name, var.datatype, var.dimensions)
                if var_name == 'Band1':
                    new_var[:] = tendency_30min
                else:
                    new_var[:] = var[:]
            
            # Copiar atributos globais
            new_nc.setncatts({k: t0_nc.getncattr(k) for k in t0_nc.ncattrs()})
        print(f'Derivada calculada e salva em: {output_file}')    
        t0_nc.close()
        t30_nc.close()
         




