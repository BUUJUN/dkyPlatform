# -*- encoding: utf-8 -*-
'''
Created on 2024/09/11 13:53:51

@author: BOJUN WANG
'''
#%%
import numpy as np
from osgeo import gdal
from rasterstats import zonal_stats

from .statis_base import *
from .src import Convert_Coor, Convert_Coor_with_SHP

def general_statis(tiffsrc, shpsrc, varname:str, key_cols:list[str]):
    
    if tiffsrc is None:
        print(f'[WARNING] 数据不存在')
        return None
    
    tar_tif = f'/vsimem/{varname}_tiff.tif'
    tar_shp = f'/vsimem/{varname}_shp.shp'
    
    Convert_Coor(tiffsrc, tar_tif)
    Convert_Coor_with_SHP(shpsrc, tar_shp)
    try:
        dataset: gdal.Dataset = gdal.Open(tar_tif)
        geotrans = dataset.GetGeoTransform()
        res_x = abs(geotrans[1])
        res_y = abs(geotrans[5])
        pixel_area = res_x * res_y / (1000 * 1000)
        result_statis = zonal_stats(tar_shp, tar_tif, geojson_out=True, nodata=np.nan)
        
        statis_list = []
        for st in result_statis:
            item_stats = dict()
            propert = st['properties']
            sum_count = propert['count']
            # 收集全部信息
            for col in key_cols:
                try:
                    item_stats[col] = propert[col]
                except Exception as e:
                    item_stats[col] = None
                    print(f"[ERROR]: {e}")
            
            item_stats[f'{varname}_mean'] = np.round(propert['mean'], 4)
            item_stats[f'{varname}_max'] = np.round(propert['max'], 4)
            item_stats[f'{varname}_min'] = np.round(propert['min'], 4)
            item_stats['area'] = sum_count * pixel_area
            
            statis_list.append(item_stats)
        return statis_list
    
    except Exception as e:
        print("[ERROR] Error occured in `statis_core.py general_statis`: ", e)
        return None
    
    finally: del dataset


def epe_statis(tiffsrc, shpsrc, key_cols:list[str], epe_func=None):
    
    if epe_func is None:
        epe_func = stat_func_epe
    
    if tiffsrc is None:
        print(f'[WARNING] 数据不存在')
        return None
    
    tar_tif = '/vsimem/epe_tiff.tif'
    tar_shp = '/vsimem/epe_shp.shp'
    Convert_Coor(tiffsrc, tar_tif)
    Convert_Coor_with_SHP(shpsrc, tar_shp)
    try:
        dataset: gdal.Dataset = gdal.Open(tar_tif)
        geotrans = dataset.GetGeoTransform()
        res_x = abs(geotrans[1])
        res_y = abs(geotrans[5])
        pixel_area = res_x * res_y / (1000 * 1000)
        result_statis = zonal_stats(tar_shp, tar_tif, add_stats={'epes_count': epe_func}, geojson_out=True)
        statis_list = []
        for st in result_statis:
            item_stats = dict()
            propert = st['properties']
            sum_count = propert['count']
            # 收集全部信息
            for col in key_cols:
                try:
                    item_stats[col] = propert[col]
                except Exception as e:
                    item_stats[col] = None
                    print(f"[ERROR]: {e}")
            item_stats['epes_max'] = propert['max']
            item_stats['epes'] = propert['epes_count']
            item_stats['area'] = sum_count * pixel_area
            statis_list.append(item_stats)
        return statis_list
    
    except Exception as e:
        print("[ERROR] Error occured in `statis_core.py epe_statis`: ", e)
        return None
    
    finally: del dataset


def wd_statis(tiffsrc, shpsrc, key_cols:list[str], wd_func=None):
    
    if wd_func is None:
        wd_func = stat_func_wd
    
    if tiffsrc is None:
        print(f'[WARNING] 数据不存在')
        return None
    
    tar_tif = '/vsimem/wd_tiff.tif'
    tar_shp = '/vsimem/wd_shp.shp'
    Convert_Coor(tiffsrc, tar_tif)
    Convert_Coor_with_SHP(shpsrc, tar_shp)
    try:
        dataset: gdal.Dataset = gdal.Open(tar_tif)
        geotrans = dataset.GetGeoTransform()
        res_x = abs(geotrans[1])
        res_y = abs(geotrans[5])
        pixel_area = res_x * res_y / (1000 * 1000)
        result_statis = zonal_stats(tar_shp, tar_tif, add_stats={'wd_most': wd_func}, geojson_out=True)
        statis_list = []
        for st in result_statis:
            item_stats = dict()
            propert = st['properties']
            sum_count = propert['count']
            # 收集全部信息
            for col in key_cols:
                try:
                    item_stats[col] = propert[col]
                except Exception as e:
                    item_stats[col] = None
                    print(f"[ERROR]: {e}")
            item_stats['wd_most'] = propert['wd_most']
            item_stats['area'] = sum_count * pixel_area
            statis_list.append(item_stats)
        return statis_list
    
    except Exception as e:
        print("[ERROR] Error occured in `statis_core.py wd_statis`: ", e)
        return None
    
    finally: del dataset


#%%
def pre_statis(tiffsrc, shpsrc, key_cols:list[str], pre_func=None):
    
    if pre_func is None:
        pre_func = stat_func_pre_24
    
    if tiffsrc is None:
        print(f'[WARNING] 数据不存在')
        return None
    
    tar_tif = '/vsimem/pre_tiff.tif'
    tar_shp = '/vsimem/pre_shp.shp'
    Convert_Coor(tiffsrc, tar_tif)
    Convert_Coor_with_SHP(shpsrc, tar_shp)
    try:
        dataset: gdal.Dataset = gdal.Open(tar_tif)
        geotrans = dataset.GetGeoTransform()
        res_x = abs(geotrans[1])
        res_y = abs(geotrans[5])
        pixel_area = res_x * res_y / (1000 * 1000)
        result_statis = zonal_stats(tar_shp, tar_tif, add_stats={'levels_count': pre_func}, geojson_out=True, nodata=np.nan)
        
        statis_list = []
        for st in result_statis:
            item_stats = dict()
            propert = st['properties']
            levels_count = propert['levels_count']
            sum_count = propert['count']
            
            # 收集全部信息
            for col in key_cols:
                try:
                    item_stats[col] = propert[col]
                except Exception as e:
                    item_stats[col] = None
                    print(f"[ERROR]: {e}")
            item_stats['pre_mean'] = propert['mean']
            item_stats['pre_max'] = propert['max']
            item_stats['area'] = sum_count * pixel_area
            
            for i in range(len(levels_count)):
                item_stats[f'pre_level_{i}'] = levels_count[i] / sum_count  # leveli 占比
            
            statis_list.append(item_stats)
        return statis_list
    
    except Exception as e:
        print("[ERROR] Error occured in `statis_core.py pre_statis`: ", e)
        return None
    
    finally: del dataset


def rain_statis(tiffsrc, shpsrc, key_cols:list[str], rain_func=None):
    
    if rain_func is None:
        rain_func = stat_func_rain_24
    
    if tiffsrc is None:
        print(f'[WARNING] 数据不存在')
        return None
    
    tar_tif = '/vsimem/rain_tiff.tif'
    tar_shp = '/vsimem/rain_shp.shp'
    Convert_Coor(tiffsrc, tar_tif)
    Convert_Coor_with_SHP(shpsrc, tar_shp)
    try:
        dataset: gdal.Dataset = gdal.Open(tar_tif)
        geotrans = dataset.GetGeoTransform()
        res_x = abs(geotrans[1])
        res_y = abs(geotrans[5])
        pixel_area = res_x * res_y / (1000 * 1000)
        result_statis = zonal_stats(tar_shp, tar_tif, add_stats={'levels_count': rain_func}, geojson_out=True, nodata=np.nan)
        
        statis_list = []
        for st in result_statis:
            item_stats = dict()
            propert = st['properties']
            levels_count = propert['levels_count']
            sum_count = propert['count']
            
            # 收集全部信息
            for col in key_cols:
                try:
                    item_stats[col] = propert[col]
                except Exception as e:
                    item_stats[col] = None
                    print(f"[ERROR]: {e}")
            item_stats['rain_mean'] = propert['mean']
            item_stats['rain_max'] = propert['max']
            item_stats['area'] = sum_count * pixel_area
            
            for i in range(len(levels_count)):
                item_stats[f'rain_level_{i}'] = levels_count[i] / sum_count  # leveli 占比
            
            statis_list.append(item_stats)
        return statis_list
    
    except Exception as e:
        print("[ERROR] Error occured in `statis_core.py rain_statis`: ", e)
        return None
    
    finally: del dataset


def snow_statis(tiffsrc, shpsrc, key_cols:list[str], snow_func=None):
    
    if snow_func is None:
        snow_func = stat_func_snow_24
    
    if tiffsrc is None:
        print(f'[WARNING] 数据不存在')
        return None
    
    tar_tif = '/vsimem/snow_tiff.tif'
    tar_shp = '/vsimem/snow_shp.shp'
    Convert_Coor(tiffsrc, tar_tif)
    Convert_Coor_with_SHP(shpsrc, tar_shp)
    try:
        dataset: gdal.Dataset = gdal.Open(tar_tif)
        geotrans = dataset.GetGeoTransform()
        res_x = abs(geotrans[1])
        res_y = abs(geotrans[5])
        pixel_area = res_x * res_y / (1000 * 1000)
        result_statis = zonal_stats(tar_shp, tar_tif, add_stats={'levels_count': snow_func}, geojson_out=True, nodata=np.nan)
        
        statis_list = []
        for st in result_statis:
            item_stats = dict()
            propert = st['properties']
            levels_count = propert['levels_count']
            sum_count = propert['count']
            
            # 收集全部信息
            for col in key_cols:
                try:
                    item_stats[col] = propert[col]
                except Exception as e:
                    item_stats[col] = None
                    print(f"[ERROR]: {e}")
            item_stats['snow_mean'] = propert['mean']
            item_stats['snow_max'] = propert['max']
            item_stats['area'] = sum_count * pixel_area
            
            for i in range(len(levels_count)):
                item_stats[f'snow_level_{i}'] = levels_count[i] / sum_count  # leveli 占比
            
            statis_list.append(item_stats)
        return statis_list
    
    except Exception as e:
        print("Error occured in `statis_core.py snow_statis`: ", e)
        return None
    
    finally: del dataset


def sleet_statis(tiffsrc, shpsrc, key_cols:list[str], sleet_func=None):
    
    if sleet_func is None:
        sleet_func = stat_func_sleet_24
    
    if tiffsrc is None:
        print(f'[WARNING] 数据不存在')
        return None
    
    tar_tif = '/vsimem/sleet_tiff.tif'
    tar_shp = '/vsimem/sleet_shp.shp'
    Convert_Coor(tiffsrc, tar_tif)
    Convert_Coor_with_SHP(shpsrc, tar_shp)
    try:
        dataset: gdal.Dataset = gdal.Open(tar_tif)
        geotrans = dataset.GetGeoTransform()
        res_x = abs(geotrans[1])
        res_y = abs(geotrans[5])
        pixel_area = res_x * res_y / (1000 * 1000)
        result_statis = zonal_stats(tar_shp, tar_tif, add_stats={'levels_count': sleet_func}, geojson_out=True, nodata=np.nan)
        
        statis_list = []
        for st in result_statis:
            item_stats = dict()
            propert = st['properties']
            levels_count = propert['levels_count']
            sum_count = propert['count']
            
            # 收集全部信息
            for col in key_cols:
                try:
                    item_stats[col] = propert[col]
                except Exception as e:
                    item_stats[col] = None
                    print(f"[ERROR]: {e}")
            item_stats['sleet_mean'] = propert['mean']
            item_stats['sleet_max'] = propert['max']
            item_stats['area'] = sum_count * pixel_area
            
            for i in range(len(levels_count)):
                item_stats[f'sleet_level_{i}'] = levels_count[i] / sum_count  # leveli 占比
            
            statis_list.append(item_stats)
        return statis_list
    
    except Exception as e:
        print("Error occured in `statis_core.py sleet_statis`: ", e)
        return None
    
    finally: del dataset


def wins_statis(tiffsrc, shpsrc, key_cols:list[str], wins_func=None):
    
    if wins_func is None:
        wins_func = stat_func_wins
    
    if tiffsrc is None:
        print(f'[WARNING] 数据不存在')
        return None
    
    tar_tif = '/vsimem/wins_tiff.tif'
    tar_shp = '/vsimem/wins_shp.shp'
    Convert_Coor(tiffsrc, tar_tif)
    Convert_Coor_with_SHP(shpsrc, tar_shp)
    try:
        dataset: gdal.Dataset = gdal.Open(tar_tif)
        geotrans = dataset.GetGeoTransform()
        res_x = abs(geotrans[1])
        res_y = abs(geotrans[5])
        pixel_area = res_x * res_y / (1000 * 1000)
        result_statis = zonal_stats(tar_shp, tar_tif, add_stats={'levels_count': wins_func}, geojson_out=True, nodata=np.nan)
        
        statis_list = []
        for st in result_statis:
            item_stats = dict()
            propert = st['properties']
            levels_count = propert['levels_count']
            sum_count = propert['count']
            
            # 收集全部信息
            for col in key_cols:
                try:
                    item_stats[col] = propert[col]
                except Exception as e:
                    item_stats[col] = None
                    print(f"[ERROR]: {e}")
            item_stats['wins_mean'] = propert['mean']
            item_stats['wins_max'] = propert['max']
            item_stats['wins_min'] = propert['min']
            item_stats['area'] = sum_count * pixel_area
            
            for i in range(len(levels_count)):
                item_stats[f'wins_level_{i}'] = levels_count[i] / sum_count  # leveli 占比
            
            statis_list.append(item_stats)
        return statis_list
    
    except Exception as e:
        print("Error occured in `statis_core.py wins_statis`: ", e)
        return None
    
    finally: del dataset


def cape_statis(tiffsrc, shpsrc, key_cols:list[str], cape_func=None):
    
    if cape_func is None:
        cape_func = stat_func_cape
    
    if tiffsrc is None:
        print(f'[WARNING] 数据不存在')
        return None
    
    tar_tif = '/vsimem/cape_tiff.tif'
    tar_shp = '/vsimem/cape_shp.shp'
    Convert_Coor(tiffsrc, tar_tif)
    Convert_Coor_with_SHP(shpsrc, tar_shp)
    try:
        dataset: gdal.Dataset = gdal.Open(tar_tif)
        geotrans = dataset.GetGeoTransform()
        res_x = abs(geotrans[1])
        res_y = abs(geotrans[5])
        pixel_area = res_x * res_y / (1000 * 1000)
        result_statis = zonal_stats(tar_shp, tar_tif, add_stats={'levels_count': cape_func}, geojson_out=True, nodata=np.nan)
        
        statis_list = []
        for st in result_statis:
            item_stats = dict()
            propert = st['properties']
            levels_count = propert['levels_count']
            sum_count = propert['count']
            
            # 收集全部信息
            for col in key_cols:
                try:
                    item_stats[col] = propert[col]
                except Exception as e:
                    item_stats[col] = None
                    print(f"[ERROR]: {e}")
            item_stats['cape_mean'] = propert['mean']
            item_stats['cape_max'] = propert['max']
            item_stats['area'] = sum_count * pixel_area
            
            item_stats['cape_low_risk_prop'] = levels_count[0] / sum_count  # level0 占比
            item_stats['cape_high_risk_prop'] = levels_count[1] / sum_count  # level1 占比
            
            statis_list.append(item_stats)
        return statis_list
    
    except Exception as e:
        print("Error occured in `statis_core.py cape_statis`: ", e)
        return None
    
    finally: del dataset


def storm_statis(tiffsrc, shpsrc, key_cols:list[str], storm_func=None):
    
    if storm_func is None:
        storm_func = stat_func_storm
    
    if tiffsrc is None:
        print(f'[WARNING] 数据不存在')
        return None
    
    tar_tif = '/vsimem/storm_tiff.tif'
    tar_shp = '/vsimem/storm_shp.shp'
    Convert_Coor(tiffsrc, tar_tif)
    Convert_Coor_with_SHP(shpsrc, tar_shp)
    try:
        dataset: gdal.Dataset = gdal.Open(tar_tif)
        geotrans = dataset.GetGeoTransform()
        res_x = abs(geotrans[1])
        res_y = abs(geotrans[5])
        pixel_area = res_x * res_y / (1000 * 1000)
        result_statis = zonal_stats(tar_shp, tar_tif, add_stats={'levels_count': storm_func}, geojson_out=True, nodata=np.nan)
        
        statis_list = []
        for st in result_statis:
            item_stats = dict()
            propert = st['properties']
            levels_count = propert['levels_count']
            sum_count = propert['count']
            
            # 收集全部信息
            for col in key_cols:
                try:
                    item_stats[col] = propert[col]
                except Exception as e:
                    item_stats[col] = None
                    print(f"[ERROR]: {e}")
            # item_stats['storm_mean'] = propert['mean']
            # item_stats['storm_max'] = propert['max']
            item_stats['area'] = sum_count * pixel_area
            
            item_stats['storm_low_risk_prop'] = levels_count[0] / sum_count  # level0 占比
            item_stats['storm_mid_risk_prop'] = levels_count[1] / sum_count  # level1 占比
            item_stats['storm_high_risk_prop'] = levels_count[2] / sum_count  # level1 占比
            
            statis_list.append(item_stats)
        return statis_list
    
    except Exception as e:
        print("Error occured in `statis_core.py storm_statis`: ", e)
        return None
    
    finally: del dataset


def temp_statis(tiffsrc, shpsrc, key_cols:list[str]):
    return general_statis(tiffsrc, shpsrc, varname='temp', key_cols=key_cols)


def tmin_statis(tiffsrc, shpsrc, key_cols:list[str]):
    return general_statis(tiffsrc, shpsrc, varname='tmin', key_cols=key_cols)


def tmax_statis(tiffsrc, shpsrc, key_cols:list[str]):
    return general_statis(tiffsrc, shpsrc, varname='tmax', key_cols=key_cols)


def rh_statis(tiffsrc, shpsrc, key_cols:list[str]):
    return general_statis(tiffsrc, shpsrc, varname='rh', key_cols=key_cols)

