import os
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from osgeo import gdal, osr
import cartopy.crs as ccrs


def calculate_derivative(data1, data2):
    return data2 - data1

def process_vertical_movement(channel_folder, extent):
    files = sorted(os.listdir(channel_folder))

    for i in range(len(files) - 3):  
        file_t0 = os.path.join(channel_folder, files[i])
        file_t30 = os.path.join(channel_folder, files[i + 3])  

        print(f'Processing {files[i]}, {files[i+3]}')

        data_t0 = get_reprojection(file_t0, extent)
        data_t30 = get_reprojection(file_t30, extent)

        # Calculate the temperature tendency (derivative) for 15 and 30 minutes
        tendency_30min = (data_t0 - data_t30) / 20

        
        upward_movement_30min = tendency_30min < -8  # Values less than -8K
      
        # Plot and save results
        plt.figure(figsize=(10, 8))

        plt.subplot(1, 2, 2)
        plt.imshow(upward_movement_30min, extent=[extent[0], extent[2], extent[1], extent[3]], cmap='gray_r')
        plt.title(f'Upward Movement (30min): {files[i]} to {files[i+3]}')
        plt.colorbar(label='Flux Ascendente')

        plt.savefig(f'upward_movement_{files[i][:-3]}.png')
        plt.close()

# Definir pasta de arquivos NetCDF do canal da janela atmosférica
channel_folder = 'path/to/atmospheric_window_channel'
extent = [-45, -25, -40, -20]  # Definir os limites de longitude/latitude

# Processar os arquivos e calcular a derivada temporal
process_vertical_movement(channel_folder, extent)
