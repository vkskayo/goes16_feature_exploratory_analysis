# Download data from aws
#-----------------------------------------------------------------------------------------------------------
# Required modules
import os                                # Miscellaneous operating system interfaces
import numpy as np                       # Import the Numpy package
from botocore import UNSIGNED            # boto3 config
from botocore.config import Config       # boto3 config                       
from datetime import timedelta, date, datetime           # Basic Dates and time types
import sys
import argparse
from typing import List
import time
import pickle
import logging
from netCDF4 import Dataset 
from retrieve_goes16_cmi_for_extent import retrieve_data
from feature_extractor_profundidade_nuvens import calcular_diferenca_canais
from feature_extractor_glaciacao import calcular_diferenca_triespectral
from log import relatorio_features

def main(argv):
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Retrieve GOES16's data for (user-provided) band, variable, and date range.")
    
    # Add command line arguments for the exact day and the feature to be computed
    parser.add_argument("--date", type=str, required=True, nargs='+', help="Choose days to extract the feature (format: YYYY-MM-DD)")
    parser.add_argument("--feature", type=str, required=True, choices=["profundidade_nuvem", "fluxo_ascendente", "tamanho_particula", "glaciacao_topo_nuvem"],
 help="Feature requested")
  
    vars = ['CMI']
   
    args = parser.parse_args()
    days = args.date
    #end_date = start_date
    feature = args.feature

    yyyymmdd = [data.replace("-", "") for data in days]

    if feature == 'profundidade_nuvem':
        bands = ['9', '13']
    elif feature == 'fluxo_ascendente':
        bands = ['13']
    elif feature == 'tamanho_particula':
        bands = ['7']
    elif feature == 'glaciacao_topo_nuvem':
        bands = ['11', '14', '15']
    else:
        print("Não é uma feature válida")
        return

    ''' Download necessary data to compute the features '''
    retrieve_data(days, vars, bands)

    ''' Compute the feature(s) '''

    if feature == 'profundidade_nuvem':

        for day in yyyymmdd:
            calcular_diferenca_canais('9', '13', day, 'data/goes16', 'features/')
            relatorio_features('features/profundidade_das_nuvens/', 'relatorio_profundidade_nuvens')

    elif feature == 'fluxo_ascendente':

        for day in yyyymmdd:
            pass

    elif feature == 'tamanho_particula':

        for day in yyyymmdd:
            pass

    elif feature == 'glaciacao_topo_nuvem':

        for day in yyyymmdd:
            calcular_diferenca_triespectral('11', '14', '15', day, 'data/goes16', 'features/')
            relatorio_features('features/glaciacao_topo_nuvem/', 'relatorio_glaciacao_topo_nuvens')

    else:
        print("Não é uma feature válida")
        return

if __name__ == "__main__":
    ### Examples:
    # python src/python retrieve_goes16_cmi_for_extent.py --date_ini "2024-02-08" --date_end "2024-02-08" --vars CMI --bands 9 13


    fmt = "[%(levelname)s] %(funcName)s():%(lineno)i: %(message)s"
    logging.basicConfig(level=logging.INFO, format = fmt)

    start_time = time.time()  # Record the start time

    main(sys.argv)
   
    end_time = time.time()  # Record the end time
    duration = (end_time - start_time) / 60  # Calculate duration in minutes
    
    print(f"Script duration: {duration:.2f} minutes") 