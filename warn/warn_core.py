# -*- encoding: utf-8 -*-
'''
Created on 2024/10/24 10:03:34

@author: BOJUN WANG
'''
#%%
import numpy as np
from osgeo import gdal
from rasterstats import zonal_stats

from .warn_base import *
from .src import Convert_Coor, Convert_Coor_with_SHP

def general_warn(tiffsrc, shpsrc, varname:str, warn_func, key_cols:list[str]):
    
    if tiffsrc is None:
        print(f'[WARNING] 数据不存在')
        return None
    
    tar_tif = f'/vsimem/{varname}_tiff.tif'
    tar_shp = f'/vsimem/{varname}_shp.shp'
    
    Convert_Coor(tiffsrc, tar_tif)
    Convert_Coor_with_SHP(shpsrc, tar_shp)
    try:
        result_statis = zonal_stats(tar_shp, tar_tif, geojson_out=True, nodata=np.nan)
        
        statis_list = []
        for st in result_statis:
            item_stats = dict()
            propert = st['properties']
            # 收集全部信息
            for col in key_cols:
                try:
                    item_stats[col] = propert[col]
                except Exception as e:
                    item_stats[col] = None
                    print(f"[ERROR]: {e}")
            
            item_stats['value'] = np.round(propert['mean'], 4)
            # item_stats[f'{varname}_max'] = np.round(propert['max'], 4)
            # item_stats[f'{varname}_min'] = np.round(propert['min'], 4)
            item_stats['level'] = warn_func(propert['mean'])
            item_stats['varname']  = varname
            
            if item_stats['level'] is None:
                continue
            
            statis_list.append(item_stats)
        
        if len(statis_list) == 0:
            return None
        
        return statis_list
    
    except Exception as e:
        print("[ERROR] Error occured in `warn_core.py general_statis`: ", e)
        return None
    
    
def warn_merge(
    time_start, time_end, period,
    region_shpfile, region_level, region_keys,
    tp_tif=None, tmax_tif=None, tmin_tif=None, ws10_tif=None, **kwargs):
    '''

    :param time_start:
    :param time_end:
    :param period:
    :param region_shpfile:
    :param region_level:
    :param region_keys:
    :param tp_tif:
    :param tmax_tif:
    :param tmin_tif:
    :param ws10_tif:
    :return:
    '''
    
    # [{"region":.., "var_mean":.., "var_level":.., }, ...]
    res_tp   = general_warn(tp_tif, region_shpfile,   'tp', classify_prec, region_keys)
    res_tmax = general_warn(tmax_tif, region_shpfile, 'tmax', classify_higtemp, region_keys)
    res_tmin = general_warn(tmin_tif, region_shpfile, 'tmin', classify_lowtemp, region_keys)
    res_ws10 = general_warn(ws10_tif, region_shpfile, 'ws10', classify_wins, region_keys)
    
    stat_res = [res_tp, res_tmax, res_tmin, res_ws10]
    stat_res = [x for x in stat_res if x is not None]
    
    if len(stat_res)==0:
        return None
    
    stat_res = [pd.DataFrame(res) for res in stat_res]
    
    stat_df = pd.concat(stat_res, axis=0)
    
    stat_df['time_start'] = time_start
    stat_df['time_end'] = time_end
    stat_df['period'] = period
    stat_df['region_shpfile'] = region_shpfile
    stat_df['region_level'] = region_level
    
    for key, val in zip(kwargs.keys(), kwargs.values()):
        print(f"Add: \tstat_df['{key}'] = '{val}'")
        stat_df[key] = val
    
    return stat_df