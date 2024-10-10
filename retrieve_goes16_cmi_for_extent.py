# Download data from aws
#-----------------------------------------------------------------------------------------------------------
# Required modules
import os                                # Miscellaneous operating system interfaces
import numpy as np                       # Import the Numpy package
from botocore import UNSIGNED            # boto3 config
from botocore.config import Config       # boto3 config                       
from datetime import timedelta, date, datetime           # Basic Dates and time types
from osgeo import osr                    # Python bindings for GDAL
from osgeo import gdal                   # Python bindings for GDAL
import sys
import argparse
from typing import List
import time
import pickle
import logging
from netCDF4 import Dataset 
from goes16_utils import download_CMI


def save_extent_data(full_disk_filename, yyyymmddhhmn, variable_names, extent, dest_path, band):
    datetimeAgain = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M')
    formatted_date = datetimeAgain.strftime('%Y-%m-%d')

  
    for var in variable_names:
   
        # Open the file
        img = gdal.Open(f'NETCDF:{full_disk_filename}:' + var)

        # Read the header metadata
        metadata = img.GetMetadata()
        scale = float(metadata.get(var + '#scale_factor'))
        offset = float(metadata.get(var + '#add_offset'))
        undef = float(metadata.get(var + '#_FillValue'))
        dtime = metadata.get('NC_GLOBAL#time_coverage_start')

        # Load the data
        ds = img.ReadAsArray(0, 0, img.RasterXSize, img.RasterYSize).astype(float)

        # Apply the scale and offset
        ds = (ds * scale + offset)

        # Apply NaN's where the quality flag is greater than 1
        # ds[ds_dqf > 1] = np.nan

        # Read the original file projection and configure the output projection
        source_prj = osr.SpatialReference()
        source_prj.ImportFromProj4(img.GetProjectionRef())

        target_prj = osr.SpatialReference()
        target_prj.ImportFromProj4("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")

        # Reproject the data
        GeoT = img.GetGeoTransform()
        driver = gdal.GetDriverByName('MEM')
        raw = driver.Create('raw', ds.shape[0], ds.shape[1], 1, gdal.GDT_Float32)
        raw.SetGeoTransform(GeoT)
        raw.GetRasterBand(1).WriteArray(ds)

        # Define the parameters of the output file  
        options = gdal.WarpOptions(format = 'netCDF', 
                srcSRS = source_prj, 
                dstSRS = target_prj,
                outputBounds = (extent[0], extent[3], extent[2], extent[1]), 
                outputBoundsSRS = target_prj, 
                outputType = gdal.GDT_Float32, 
                srcNodata = undef, 
                dstNodata = 'nan', 
                resampleAlg = gdal.GRA_NearestNeighbour)
        
        img = None  # Close file

        # Write the reprojected file on disk
        filename_reprojected = f'{dest_path}/{yyyymmddhhmn}band{band}_{var}.nc'
        gdal.Warp(filename_reprojected, raw, options=options)


def download_data_for_a_day(extent: List[float], 
                            dest_path: str,
                            yyyymmdd: str, 
                            variable_names: List[str], 
                            bands:List[str],
                            temporal_resolution: int = 10,
                            remove_full_disk_file: bool = True):
    """
    Downloads values of a specific variable from a specific product and for a specific day from GOES-16 satellite.
    These values are downloaded only for the locations (lat/lon) of a list of stations of interest. 
    These downloaded values are appended (as new rows) to the provided DataFrame. 
    Each row will have the following columns: (timestamp, station_id, variable names's value)

    Args:
    - df (pandas.DataFrame): DataFrame to which downloaded values for stations of interest will be appended as a new column.
    - yyyymmdd (str): Date in 'YYYYMMDD' format specifying the day for which data will be downloaded.
    - stations_of_interest (dict): Dictionary containing stations of interest with their IDs as keys
                                   and their corresponding latitude and longitude coordinates as values.
    - product_name (str): The name of the GOES-16 product from which data will be downloaded.
    - variable_name (str): The specific variable to be retrieved from the product.
    """

    # Directory to temporarily store each downloaded full disk file.
    TEMP_DIR  = "data/goes16"

    # Initial time and date
    yyyy = datetime.strptime(yyyymmdd, '%Y%m%d').strftime('%Y')
    mm = datetime.strptime(yyyymmdd, '%Y%m%d').strftime('%m')
    dd = datetime.strptime(yyyymmdd, '%Y%m%d').strftime('%d')

    hour_ini = 0
    date_ini = datetime(int(yyyy),int(mm),int(dd),hour_ini,0)
    date_end = datetime(int(yyyy),int(mm),int(dd),hour_ini,0) + timedelta(hours=23)

    time_step = date_ini
  
    while (time_step <= date_end):
        # Date structure
        yyyymmddhhmn = datetime.strptime(str(time_step), '%Y-%m-%d %H:%M:%S').strftime('%Y%m%d%H%M')

        logging.info(f'-Getting data for {yyyymmddhhmn}...')

        for band in bands:

            # Verifica se o arquivo já existe
            if os.path.exists(f'{TEMP_DIR}/{yyyymmddhhmn}band{band}_CMI.nc'):
                print("O arquivo já existe. Pulando download...")
                continue
            else:
                print("O arquivo não existe.")

            # Download the full disk file from the Amazon cloud.
            file_name = download_CMI(yyyymmddhhmn, band, TEMP_DIR)

            if file_name != -1:
                try:
                    full_disk_filename = f'{TEMP_DIR}/{file_name}.nc'

                    save_extent_data(full_disk_filename, yyyymmddhhmn, variable_names, extent, dest_path, band)

                    if remove_full_disk_file:
                        try:
                            os.remove(full_disk_filename)  # Use os.remove() to delete the file
                        except FileNotFoundError:
                            logging.info(f"Error: File '{full_disk_filename}' not found.")
                        except PermissionError:
                            logging.info(f"Error: Permission denied to remove file '{full_disk_filename}'.")
                        except Exception as e:
                            logging.info(f"An error occurred: {e}")
                except Exception as e:
                    logging.info(f"An error occurred: {e}")

        # Increment to get the next full disk observation.
        time_step = time_step + timedelta(minutes=temporal_resolution)

def retrieve_data(days, vars, bands):
    
    for day in days:

        # TODO - change to cmd line args
        extent = [-43.890602827150, -23.1339033365138, -43.0483514573222, -22.64972474827293]
        dest_path = "data/goes16"

        # Convert start_date and end_date to datetime objects
        from datetime import datetime
        day_datetime = datetime.strptime(day, '%Y-%m-%d')
  

        folder_path = f'data/goes16'

        # Verifica se a pasta existe
        if not os.path.exists(folder_path):
            # Se não existir, cria a pasta
            os.makedirs(folder_path)
            print(f'Pasta criada: {folder_path}')
        else:
            print(f'A pasta já existe: {folder_path}')

        if day_datetime.month not in [6, 7, 8]:
            yyyymmdd = day_datetime.strftime('%Y%m%d')
            df = download_data_for_a_day(extent, dest_path, yyyymmdd,vars, bands)
       
