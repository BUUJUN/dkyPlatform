# -*- encoding: utf-8 -*-
'''
Created on 2024/10/24 09:36:46

@author: BOJUN WANG
'''
#%%
import pandas as pd
import numpy as np
from scipy import stats

# 定义温度等级划分
def classify_higtemp(temp):
    if temp >= 40:
        return 3
    elif 37 <= temp < 40:
        return 2
    elif 35 <= temp < 37:
        return 1
    else:
        return None  # 不统计35以下的温度

# 定义温度等级划分
def classify_lowtemp(temp):
    if 4 < temp <= 6:
        return 1
    elif 2 < temp <= 4:
        return 2
    elif 1 < temp <= 2:
        return 3
    elif 0 < temp <= 1:
        return 4
    elif -1 < temp <= 0:
        return 5
    elif -3 < temp <= -1:
        return 6
    elif -5 < temp <= -3:
        return 7
    elif -7 < temp <= -5:
        return 8
    elif temp <= -7:
        return 9
    else:
        return None

def classify_wins(wins):
    if 8.0 <= wins < 10.8:
        return 1
    elif 10.8 <= wins < 13.9:
        return 2
    elif 13.9 <= wins < 17.2:
        return 3
    elif 17.2 <= wins < 20.8:
        return 4
    elif 20.8 <= wins < 24.5:
        return 5
    elif 24.5 <= wins < 28.5:
        return 6
    elif 28.5 <= wins < 32.7:
        return 7
    elif 32.7 <= wins < 37:
        return 8
    elif wins >= 37:
        return 9
    else:
        return None

def classify_prec(prec):
    if 4 <= prec < 8:
        return 1
    elif 8 <= prec < 20:
        return 2
    elif 20 <= prec < 50:
        return 3
    elif prec >= 50:
        return 4
    else:
        return None

#%%
def warn_func_higtemp(data: pd.DataFrame, varname: str):
    '''
    高温统计 告警
    :param data:
    :return: 35~37, 37~40, >40
    '''
    # 应用分类函数
    data['level'] = data[varname].apply(classify_higtemp)
    # 只保留有效的温度数据
    return data[data['level'].notnull()]


def warn_func_lowtemp(data: pd.DataFrame, varname: str):
    '''
    低温统计 告警
    :param data:
    :return: 
    '''
    # 应用分类函数
    data['level'] = data[varname].apply(classify_lowtemp)
    # 只保留有效的温度数据
    return data[data['level'].notnull()]


def warn_func_wins(data: pd.DataFrame, varname: str):
    '''
    大风统计 告警
    :param data:
    :return: 
    '''
    # 应用分类函数
    data['level'] = data[varname].apply(classify_wins)
    # 只保留有效的温度数据
    return data[data['level'].notnull()]


def warn_func_prec(data: pd.DataFrame, varname: str):
    '''
    降水统计 告警
    :param data:
    :return: 
    '''
    # 应用分类函数
    data['level'] = data[varname].apply(classify_prec)
    # 只保留有效的温度数据
    return data[data['level'].notnull()]

