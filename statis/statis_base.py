# -*- encoding: utf-8 -*-
'''
Created on 2024/09/11 11:21:55

@author: BOJUN WANG
'''
#%%
import numpy as np
from scipy import stats


def stat_func_epe(data: np.ndarray):
    '''
    极端降水频次统计，如果区域内 50% 以上的格点降水超过 50mm/h 记为一次事件
    :param data:
    :return:
    '''
    data_unique = np.sort(np.unique(data))[::-1]
    data_counts = (~np.isnan(data)).sum()
    epes = 0
    for item in data_unique:
        if np.isnan(item):
            continue
        item_prop = (data >= item).sum() / data_counts
        if item_prop >= 0.5:
            epes = item
            break
    return epes


def stat_func_wd(data: np.ndarray):
    '''
    
    :param data:
    :return:
    '''
    data_1d = data.flatten()
    data_1d = data_1d[~np.isnan(data_1d)]
    if len(data_1d) == 0:
        return None
    
    data_1d = data_1d.astype('int')
    
    return stats.mode(data_1d)[0]


#%%
def stat_func_pre_24(data: np.ndarray):
    '''
    24h降水 格点统计
    :param data:
    :return: <0.1mm, 0.1-10mm, 10-25mm, 25-50mm, 50-100mm, 100-250mm, >=250mm
    '''
    pre_24_level0 = (data < 0.1) | (np.isnan(data))  # 无降水
    pre_24_level1 = (data >= 0.1) & (data < 10.0)  # 小雨
    pre_24_level2 = (data >= 10.0) & (data < 25.0)  # 中雨
    pre_24_level3 = (data >= 25.0) & (data < 50.0)  # 大雨
    pre_24_level4 = (data >= 50.0) & (data < 100.0)  # 暴雨
    pre_24_level5 = (data >= 100.0) & (data < 250.0)  # 大暴雨
    pre_24_level6 = (data >= 250.0)  # 特大暴雨
    
    return np.sum(pre_24_level0), np.sum(pre_24_level1), np.sum(pre_24_level2), \
        np.sum(pre_24_level3), np.sum(pre_24_level4), np.sum(pre_24_level5), np.sum(pre_24_level6)


def stat_func_pre_3(data: np.ndarray):
    '''
    3h降水 格点统计
    :param data:
    :return: <0.1mm, 0.1-1mm, 1-3mm, 3-10mm, 10-20mm, 20-50mm, >=50mm
    '''
    pre_3_level0 = (data < 0.1) | (np.isnan(data))  # 无降水
    pre_3_level1 = (data >= 0.1) & (data < 1.0)  # 小雨
    pre_3_level2 = (data >= 1.0) & (data < 3.0)  # 中雨
    pre_3_level3 = (data >= 3.0) & (data < 10.0)  # 大雨
    pre_3_level4 = (data >= 10.0) & (data < 20.0)  # 暴雨
    pre_3_level5 = (data >= 20.0) & (data < 50.0)  # 大暴雨
    pre_3_level6 = (data >= 50.0)  # 特大暴雨
    
    return np.sum(pre_3_level0), np.sum(pre_3_level1), np.sum(pre_3_level2), \
        np.sum(pre_3_level3), np.sum(pre_3_level4), np.sum(pre_3_level5), np.sum(pre_3_level6)


def stat_func_rain_24(data: np.ndarray):
    '''
    24h降水 格点统计
    :param data:
    :return: <0.1mm, 0.1-10mm, 10-25mm, 25-50mm, 50-100mm, 100-250mm, >=250mm
    '''
    rain_24_level0 = (data < 0.1) | (np.isnan(data))  # 无降水
    rain_24_level1 = (data >= 0.1) & (data < 10.0)  # 小雨
    rain_24_level2 = (data >= 10.0) & (data < 25.0)  # 中雨
    rain_24_level3 = (data >= 25.0) & (data < 50.0)  # 大雨
    rain_24_level4 = (data >= 50.0) & (data < 100.0)  # 暴雨
    rain_24_level5 = (data >= 100.0) & (data < 250.0)  # 大暴雨
    rain_24_level6 = (data >= 250.0)  # 特大暴雨
    
    return np.sum(rain_24_level0), np.sum(rain_24_level1), np.sum(rain_24_level2), \
        np.sum(rain_24_level3), np.sum(rain_24_level4), np.sum(rain_24_level5), np.sum(rain_24_level6)


def stat_func_rain_3(data: np.ndarray):
    '''
    3h降水 格点统计
    :param data:
    :return: <0.1mm, 0.1-1mm, 1-3mm, 3-10mm, 10-20mm, 20-50mm, >=50mm
    '''
    rain_3_level0 = (data < 0.1) | (np.isnan(data))  # 无降水
    rain_3_level1 = (data >= 0.1) & (data < 1.0)  # 小雨
    rain_3_level2 = (data >= 1.0) & (data < 3.0)  # 中雨
    rain_3_level3 = (data >= 3.0) & (data < 10.0)  # 大雨
    rain_3_level4 = (data >= 10.0) & (data < 20.0)  # 暴雨
    rain_3_level5 = (data >= 20.0) & (data < 50.0)  # 大暴雨
    rain_3_level6 = (data >= 50.0)  # 特大暴雨
    
    return np.sum(rain_3_level0), np.sum(rain_3_level1), np.sum(rain_3_level2), \
        np.sum(rain_3_level3), np.sum(rain_3_level4), np.sum(rain_3_level5), np.sum(rain_3_level6)


def stat_func_snow_24(data: np.ndarray):
    '''
    24h降雪 格点统计
    :param data:
    :return: <0.01mm, 0.01-2.5mm, 2.5-5mm, 5-10mm, 10-20mm, 20-30mm, >=30mm
    '''
    snow_24_level0 = (data <  0.01) | (np.isnan(data)) # 无降雪
    snow_24_level1 = (data >= 0.01) & (data < 2.5) # 小雪
    snow_24_level2 = (data >= 2.5)  & (data < 5.0) # 中雪
    snow_24_level3 = (data >= 5.0)  & (data < 10.0) # 大雪
    snow_24_level4 = (data >= 10.0) & (data < 20.0) # 暴雪
    snow_24_level5 = (data >= 20.0) & (data < 30.0) # 大暴雪
    snow_24_level6 = (data >= 30.0) # 特大暴雪
    
    return np.sum(snow_24_level0), np.sum(snow_24_level1), np.sum(snow_24_level2), \
        np.sum(snow_24_level3), np.sum(snow_24_level4), np.sum(snow_24_level5), np.sum(snow_24_level6)


def stat_func_snow_3(data: np.ndarray):
    '''
    3h降雪 格点统计
    :param data:
    :return: <0.01mm, 0.01-0.5mm, 0.5-1mm, 1-2mm, 2-4mm, 4-8mm, 8-12mm, >=12mm
    '''
    snow_3_level0 = (data <  0.01) | (np.isnan(data)) # 无降雪
    snow_3_level1 = (data >= 0.01) & (data < 1.0) # 小雪
    snow_3_level2 = (data >= 1.0) & (data < 2.0) # 中雪
    snow_3_level3 = (data >= 2.0) & (data < 4.0) # 大雪
    snow_3_level4 = (data >= 4.0) & (data < 8.0) # 暴雪
    snow_3_level5 = (data >= 8.0) & (data < 12.0) # 大暴雪
    snow_3_level6 = (data >= 12.0) # 特大暴雪
    
    return np.sum(snow_3_level0), np.sum(snow_3_level1), np.sum(snow_3_level2), \
        np.sum(snow_3_level3), np.sum(snow_3_level4), np.sum(snow_3_level5), np.sum(snow_3_level6)


def stat_func_sleet_24(data: np.ndarray):
    '''
    24h雨夹雪 格点统计
    :param data:
    :return: <0.01mm, 0.01-10mm, 10-25mm, >=25mm
    '''
    sleet_24_level0 = (data <  0.01) | (np.isnan(data)) # 无雨夹雪
    sleet_24_level1 = (data >= 0.01) & (data < 10.0) # 小雨夹雪
    sleet_24_level2 = (data >= 10.0) & (data < 25.0) # 中雨夹雪 
    sleet_24_level3 = (data >= 25.0) # 大雨夹雪
    return np.sum(sleet_24_level0), np.sum(sleet_24_level1), np.sum(sleet_24_level2), np.sum(sleet_24_level3)


def stat_func_sleet_3(data: np.ndarray):
    '''
    3h雨夹雪 格点统计
    :param data:
    :return: <0.01mm, 0.01-3mm, 3-10mm, >=10mm
    '''
    sleet_3_level0 = (data <  0.01) | (np.isnan(data)) # 无雨夹雪
    sleet_3_level1 = (data >= 0.01) & (data < 3.0) # 小雨夹雪
    sleet_3_level2 = (data >= 3.0) & (data < 10.0) # 中雨夹雪 
    sleet_3_level3 = (data >= 10.0) # 大雨夹雪
    return np.sum(sleet_3_level0), np.sum(sleet_3_level1), np.sum(sleet_3_level2), np.sum(sleet_3_level3)


def stat_func_cape(data: np.ndarray):
    '''
    位能 格点统计
    :param data:
    :return: 200-800, >=800
    '''
    cape_low_risk  = (data >= 200) & (data < 800) # 低雷电风险
    cape_high_risk = (data >= 800)  # 高雷电风险
    return np.sum(cape_low_risk), np.sum(cape_high_risk)


def stat_func_wins(data: np.ndarray):
    '''
    风速 格点统计
    :param data:
    :return: <0.3, 0.3-1.6, 1.6-3.4, 3.4-5.5, 5.5-8.0, 8.0-10.8, 10.8-13.9, 13.9-17.2, 17.2-20.8, >=20.8
    '''
    wins_level_0 = (data < 0.3) | (np.isnan(data))  # 无风
    wins_level_1 = (data >= 0.3) & (data < 1.6)  # 1级风
    wins_level_2 = (data >= 1.6) & (data < 3.4)  # 2级风
    wins_level_3 = (data >= 3.4) & (data < 5.5)  # 3级风
    wins_level_4 = (data >= 5.5) & (data < 8.0)  # 4级风
    wins_level_5 = (data >= 8.0) & (data < 10.8)  # 5级风
    wins_level_6 = (data >= 10.8) & (data < 13.9)  # 6级风
    wins_level_7 = (data >= 13.9) & (data < 17.2)  # 7级风
    wins_level_8 = (data >= 17.2) & (data < 20.8)  # 8级风
    wins_level_9 = (data >= 20.8)  # 9级风
    return np.sum(wins_level_0), np.sum(wins_level_1), np.sum(wins_level_2), np.sum(wins_level_3), \
        np.sum(wins_level_4), np.sum(wins_level_5), np.sum(wins_level_6), \
                np.sum(wins_level_7), np.sum(wins_level_8), np.sum(wins_level_9)


def stat_func_storm(data: np.ndarray):
    '''
    雷电 格点统计
    :param data:
    :return: <40, 40-70, >=70
    '''
    storm_low_risk = (data < 40)  # 低雷电风险
    storm_mid_risk = (data >= 40) & (data < 70) # 中雷电风险
    storm_high_risk = (data >= 70)  # 高雷电风险
    return np.sum(storm_low_risk), np.sum(storm_mid_risk), np.sum(storm_high_risk)

