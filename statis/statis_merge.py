# -*- encoding: utf-8 -*-
'''
Created on 2024/09/11 15:37:27

@author: BOJUN WANG
'''
#%%
import pandas as pd
from .statis_core import *
from .statis_base import *


def statis_obs(
    time_start, time_end, period,
    region_shpfile, region_level, region_keys,
    tp_tif=None, epe_tif=None, sp_tif=None, t2m_tif=None, tmax_tif=None,
    tmin_tif=None, r2m_tif=None, ws10_tif=None, wd10_tif=None, **kwargs):
    '''

    :param time_start:
    :param time_end:
    :param period:
    :param region_shpfile:
    :param region_level:
    :param region_keys:
    :param tp_tif:
    :param epe_tif:
    :param sp_tif:
    :param t2m_tif:
    :param tmax_tif:
    :param tmin_tif:
    :param r2m_tif:
    :param ws10_tif:
    :param wd10_tif:
    :return:
    '''
    
    # [{"region":.., "var_mean":.., "var_max":.., "area":.., }, ...]
    res_tp = general_statis(tp_tif, region_shpfile, 'tp', region_keys)
    res_epe = epe_statis(epe_tif, region_shpfile, region_keys, stat_func_epe)
    res_sp = general_statis(sp_tif, region_shpfile, 'sp', region_keys)
    res_t2m = general_statis(t2m_tif, region_shpfile, 't2m', region_keys)
    res_tmax = general_statis(tmax_tif, region_shpfile, 'tmax', region_keys)
    res_tmin = general_statis(tmin_tif, region_shpfile, 'tmin', region_keys)
    res_r2m = general_statis(r2m_tif, region_shpfile, 'r2m', region_keys)
    res_ws10 = general_statis(ws10_tif, region_shpfile, 'ws10', region_keys)
    res_wd10 = wd_statis(wd10_tif, region_shpfile, region_keys, stat_func_wd)
    
    stat_res = [res_tp, res_epe, res_sp, res_t2m, res_tmax, res_tmin, res_r2m, res_ws10, res_wd10]
    stat_res = [x for x in stat_res if x is not None]
    
    if len(stat_res)==0:
        return None
    
    stat_res = [pd.DataFrame(res) for res in stat_res]
    
    stat_df = stat_res[0]
    for i in range(len(stat_res)):
        if i==0:
            continue
        else:
            stat_df_add = stat_res[i]
            stat_df_add_cols = [col for col in stat_df_add if (col in region_keys) or (col not in stat_df.columns)]
            stat_df = pd.merge(stat_df, stat_df_add.loc[:, stat_df_add_cols], how='inner', on=region_keys)
    
    stat_df['time_start'] = time_start
    stat_df['time_end'] = time_end
    stat_df['period'] = period
    stat_df['region_shpfile'] = region_shpfile
    stat_df['region_level'] = region_level
    
    for key, val in zip(kwargs.keys(), kwargs.values()):
        print(f"Add: \tstat_df['{key}'] = '{val}'")
        stat_df[key] = val
    
    return stat_df


#%%
def statis_basic(
    valid_time_start,valid_time_end,cycle_time,
    report_time_start,report_time_end,report_interval,report_type,
    region_shpfile,region_level,region_keys,
    pre_tif=None,wins_tif=None,temp_tif=None,tmax_tif=None,tmin_tif=None,rh_tif=None, **kwargs):
    '''
    
    :param valid_time_start:
    :param valid_time_end:
    :param cycle_time:
    :param report_time_start:
    :param report_time_end:
    :param report_interval:
    :param report_type:
    :param region_shpfile:
    :param region_level:
    :param region_keys:
    :param pre_tif:
    :param wins_tif:
    :param temp_tif:
    :param tmax_tif:
    :param tmin_tif:
    :param rh_tif:
    :return:
    '''
    if report_interval == 3:
        pre_func = stat_func_pre_3
        
    else:
        pre_func = stat_func_pre_24
    
    # [{"region":.., "var_mean":.., "var_max":.., "area":.., }, ...]
    pre_stat_res = pre_statis(pre_tif, region_shpfile, key_cols=region_keys, pre_func=pre_func)
    wins_stat_res = wins_statis(wins_tif, region_shpfile, key_cols=region_keys)
    temp_stat_res = temp_statis(temp_tif, region_shpfile, key_cols=region_keys)
    tmax_stat_res = tmax_statis(tmax_tif, region_shpfile, key_cols=region_keys)
    tmin_stat_res = tmin_statis(tmin_tif, region_shpfile, key_cols=region_keys)
    rh_stat_res = rh_statis(rh_tif, region_shpfile, key_cols=region_keys)
    
    stat_res = [pre_stat_res, temp_stat_res, tmax_stat_res, tmin_stat_res, rh_stat_res, wins_stat_res]
    stat_res = [x for x in stat_res if x is not None]
    
    if len(stat_res) == 0:
        return None
    
    stat_res = [pd.DataFrame(res) for res in stat_res]
    stat_df = pd.DataFrame()
    
    stat_df = stat_res[0]
    for i in range(len(stat_res)):
        if i == 0:
            continue
        else:
            stat_df_add = stat_res[i]
            stat_df_add_cols = [col for col in stat_df_add if (col in region_keys) or (col not in stat_df.columns)]
            stat_df = pd.merge(stat_df, stat_df_add.loc[:, stat_df_add_cols], how='inner', on=region_keys)
    
    stat_df['report_type'] = report_type
    stat_df['region_level'] = region_level
    stat_df['report_interval'] = report_interval
    stat_df['cycle_time'] = cycle_time
    stat_df['report_time_start'] = report_time_start
    stat_df['report_time_end'] = report_time_end
    stat_df['valid_time_start'] = valid_time_start
    stat_df['valid_time_end'] = valid_time_end
    
    for key, val in zip(kwargs.keys(), kwargs.values()):
        print(f"Add: \tstat_df['{key}'] = '{val}'")
        stat_df[key] = val
    
    return stat_df


def statis_winter(
    valid_time_start,valid_time_end,cycle_time,
    report_time_start,report_time_end,report_interval,report_type,
    region_shpfile,region_level,region_keys,
    rain_tif=None,wins_tif=None,cape_tif=None,snow_tif=None,sleet_tif=None,
    temp_tif=None,tmax_tif=None,tmin_tif=None,rh_tif=None,storm_tif=None,):
    '''
    
    :param valid_time_start:
    :param valid_time_end:
    :param cycle_time:
    :param report_time_start:
    :param report_time_end:
    :param report_interval:
    :param report_type:
    :param region_shpfile:
    :param region_level:
    :param region_keys:
    :param rain_tif:
    :param wins_tif:
    :param cape_tif:
    :param snow_tif:
    :param sleet_tif:
    :param temp_tif:
    :param tmax_tif:
    :param tmin_tif:
    :param rh_tif:
    :param storm_tif:
    :return:
    '''
    if report_interval == 3:
        rain_func = stat_func_rain_3
        snow_func = stat_func_snow_3
        sleet_func = stat_func_sleet_3
    else:
        rain_func = stat_func_rain_24
        snow_func = stat_func_snow_24
        sleet_func = stat_func_sleet_24
    
    rain_stat_res = rain_statis(rain_tif, region_shpfile, region_keys, rain_func)
    snow_stat_res = snow_statis(snow_tif, region_shpfile, region_keys, snow_func)
    sleet_stat_res = sleet_statis(sleet_tif, region_shpfile, region_keys, sleet_func)
    cape_stat_res = cape_statis(cape_tif, region_shpfile, region_keys)
    wins_stat_res = wins_statis(wins_tif, region_shpfile, region_keys)
    temp_stat_res = temp_statis(temp_tif, region_shpfile, region_keys)
    tmax_stat_res = tmax_statis(tmax_tif, region_shpfile, region_keys)
    tmin_stat_res = tmin_statis(tmin_tif, region_shpfile, region_keys)
    rh_stat_res = rh_statis(rh_tif, region_shpfile, region_keys)
    storm_stat_res = storm_statis(storm_tif, region_shpfile, region_keys)
    
    stat_res = [
        rain_stat_res, snow_stat_res, sleet_stat_res, 
        cape_stat_res, wins_stat_res, temp_stat_res, 
        tmax_stat_res, tmin_stat_res, rh_stat_res, storm_stat_res,
    ]
    stat_res = [x for x in stat_res if x is not None]
    
    if len(stat_res)==0:
        return None
    
    stat_res = [pd.DataFrame(res) for res in stat_res]
    stat_df = pd.DataFrame()
    
    stat_df = stat_res[0]
    for i in range(len(stat_res)):
        if i==0:
            continue
        else:
            stat_df_add = stat_res[i]
            stat_df_add_cols = [col for col in stat_df_add if (col in region_keys) or (col not in stat_df.columns)]
            stat_df = pd.merge(stat_df, stat_df_add.loc[:, stat_df_add_cols], how='inner', on=region_keys)
    
    stat_df['report_type'] = report_type
    stat_df['region_level'] = region_level
    stat_df['report_interval'] = report_interval
    stat_df['cycle_time'] = cycle_time
    stat_df['report_time_start'] = report_time_start
    stat_df['report_time_end'] = report_time_end
    stat_df['valid_time_start'] = valid_time_start
    stat_df['valid_time_end'] = valid_time_end
    
    return stat_df

