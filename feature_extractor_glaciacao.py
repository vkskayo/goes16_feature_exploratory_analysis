import os
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
from osgeo import osr, gdal

def get_reprojection(file_name, extent):
    var = 'CMI'
    img = gdal.Open(f'NETCDF:{file_name}.nc:' + var)
    metadata = img.GetMetadata()
    scale = float(metadata.get(var + '#scale_factor'))
    offset = float(metadata.get(var + '#add_offset'))
    undef = float(metadata.get(var + '#_FillValue'))

    ds = img.ReadAsArray(0, 0, img.RasterXSize, img.RasterYSize).astype(float)
    ds = (ds * scale + offset) - 273.15

    source_prj = osr.SpatialReference()
    source_prj.ImportFromProj4(img.GetProjectionRef())

    target_prj = osr.SpatialReference()
    target_prj.ImportFromProj4("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")

    GeoT = img.GetGeoTransform()
    driver = gdal.GetDriverByName('MEM')
    raw = driver.Create('raw', ds.shape[0], ds.shape[1], 1, gdal.GDT_Float32)
    raw.SetGeoTransform(GeoT)
    raw.GetRasterBand(1).WriteArray(ds)

    options = gdal.WarpOptions(
        format='netCDF',
        srcSRS=source_prj,
        dstSRS=target_prj,
        outputBounds=(extent[0], extent[3], extent[2], extent[1]),
        outputBoundsSRS=target_prj,
        outputType=gdal.GDT_Float32,
        srcNodata=undef,
        dstNodata='nan',
        xRes=0.02,
        yRes=0.02,
        resampleAlg=gdal.GRA_NearestNeighbour
    )

    gdal.Warp(f'{file_name}_ret.nc', raw, options=options)
    file = Dataset(f'{file_name}_ret.nc')
    data = file.variables['Band1'][:]
    return data

def process_day(channel1_folder, channel2_folder, extent):
    channel1_files = sorted(os.listdir(channel1_folder))
    channel2_files = sorted(os.listdir(channel2_folder))

    for ch1_file, ch2_file in zip(channel1_files, channel2_files):
        file_ch1 = os.path.join(channel1_folder, ch1_file)
        file_ch2 = os.path.join(channel2_folder, ch2_file)
        
        print(f'Processing {ch1_file} and {ch2_file}')
        
        data_ch1 = get_reprojection(file_ch1, extent)
        data_ch2 = get_reprojection(file_ch2, extent)

        # Calcula a diferença entre os dois canais
        data_diff = data_ch1 - data_ch2

        # Salva ou plota o resultado da diferença
        plt.figure(figsize=(8, 6))
        plt.imshow(data_diff, extent=[extent[0], extent[2], extent[1], extent[3]], cmap='gray_r')
        plt.title(f'Difference: {ch1_file} vs {ch2_file}')
        plt.colorbar(label='Temperature Difference (°C)')
        plt.savefig(f'diff_{ch1_file[:-3]}.png')
        plt.close()

# Definir pastas dos arquivos NetCDF
channel1_folder = 'path/to/atmospheric_window_channel'
channel2_folder = 'path/to/water_absorption_channel'
extent = [-45, -25, -40, -20]  # Definir os limites de longitude/latitude

# Processar os arquivos e calcular as diferenças
process_day(channel1_folder, channel2_folder, extent)
