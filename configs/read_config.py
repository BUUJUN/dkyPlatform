# -*- encoding: utf-8 -*-
'''
Created on 2024/09/12 09:23:51

@author: BOJUN WANG
'''
#%%
import os

from .un_config import input_directory_GJD, input_directory_5km, input_directory_1km

#%%


file_info = {
    'GJD':{
        # 'file_root': '/mnt/wxdata/GX_data/XNYZX-BJ/GJD',
        'file_root': input_directory_GJD,
        'file_folder': '{time_fb}',
        'file_name': r'GJD_{time_fb}_{time_yb}:00:00.nc',
        'file_folder_re': r'^(\d{10})$',
        'file_name_re': r'^GJD_(\d{10})_(\d{8}_\d{2}):00:00\.nc$',
        'time_fmts': {
            'time_fb': r'%Y%m%d%H',
            'time_yb': r'%Y%m%d_%H',
        },
        'fcst_start_hours': [0, 12],
        'fcst_length': 168,
        'fcst_interval': 1,
    },
    '5km':{
        # 'file_root': '/mnt/wxdata/GX_data',
        'file_root': input_directory_5km,
        'file_folder': '5KM_NC_{var}/{year}/{ym}/{ymd}',
        'file_name': '5KM_{var}_{ymdh}.nc',
        'file_folder_re': r'^5KM_NC_(\w+)\/\d{4}\/\d{6}\/(\d{8})$',
        'file_name_re': r'^5KM_(\w+)_(\d{10})\.nc$',
        'time_fmts': {
            'year': r'%Y',
            'ym':   r'%Y%m',
            'ymd':  r'%Y%m%d',
            'ymdh': r'%Y%m%d%H',
        },
        'file_name_var': {
            'lon': 'TMP',
            'lat': 'TMP',
            'ws10': 'WIN',
            'u10': 'WIU',
            'v10': 'WIV',
            'tp': 'PRE',
            't2m': 'TMP',
            'r2m': 'RH',
            'd2m': 'DPT',
            'sp': 'PRS',
        },
        'file_interval': 1
    },
    '1km':{
        # 'file_root': '/mnt/wxdata/GX_data',
        'file_root': input_directory_1km,
        'file_folder': '1KM_NC_{var}/{year}/{ym}/{ymd}',
        'file_name': '1KM_{var}_{ymdh}.nc',
        'file_folder_re': r'^5KM_NC_(\w+)\/\d{4}\/\d{6}\/(\d{8})$',
        'file_name_re': r'^5KM_(\w+)_(\d{10})\.nc$',
        'time_fmts': {
            'year': r'%Y',
            'ym':   r'%Y%m',
            'ymd':  r'%Y%m%d',
            'ymdh': r'%Y%m%d%H',
        },
        'file_name_var': {
            'lon': 'TMP',
            'lat': 'TMP',
            'ws10': 'WIN',
            'u10': 'WIU',
            'v10': 'WIV',
            'tp': 'PRE',
            't2m': 'TMP',
            'r2m': 'RH',
            'd2m': 'DPT',
            'sp': 'PRS',
        },
        'file_interval': 1
    },
}

data_info = {
    'GJD': {
        'renames': {
            'lon': 'LON',
            'lat': 'LAT',
            'ws10': 'WS',
            'fg10': 'GUST',
            'tp': 'TP',
            't2m': 'T2',
            'r2m': 'RH',
            'sp': 'PRESSURE'
        },
    },
    '5km': {
        'renames': {
            'lon': 'lon',
            'lat': 'lat',
            'ws10': 'WIN',
            'u10': 'WIU',
            'v10': 'WIV',
            'tp': 'PRE',
            't2m': 'TMP',
            'r2m': 'RH',
            'd2m': 'DPT',
            'sp': 'PRS',
        },
    },
    '1km': {
        'renames': {
            'lon': 'lon',
            'lat': 'lat',
            'ws10': 'WIN',
            'u10': 'WIU',
            'v10': 'WIV',
            'tp': 'PRE',
            't2m': 'TEM',
            'r2m': 'RH',
            'd2m': 'DPT',
            'sp': 'PRS',
        },
    },
}
