# -*- encoding: utf-8 -*-
'''
Created on 2024/09/13 09:33:37

@author: BOJUN WANG
'''
import os
import datetime
import pandas as pd
import numpy as np
from typing import Union
from .un_config import output_prefix

def get_forecast_type(length, interval):
    if (interval == 3) & (length <= 24):
        forecast_type = 'imminent'
    elif (interval == 24) & (length <= 24):
        forecast_type = 'imminent'
    elif (interval == 24) & (length <= 72):
        forecast_type = 'short-term'
    elif (interval == 24) & (length > 72):
        forecast_type = 'medium-term'
    else:
        print("没有匹配到合适的 `forecasr_type` ")
        return 'other'
    
    return forecast_type


def get_time_type(time_type:str):
    time_type = time_type.lower()
    if time_type in ['hour', 'h']:
        return 'h'
    elif time_type in ['day', 'd']:
        return 'd'
    elif time_type in ['month', 'm']:
        return 'MS'
    elif time_type in ['quarter', 'q']:
        return 'QS'
    elif time_type in ['year', 'y']:
        return 'YS'
    else:
        print("没有匹配到合适的 `statis_type` ")
        return 'd'

def check_time_info(
    time_start      :Union[datetime.datetime, pd.Timestamp], 
    time_length     :int, 
    time_interval   :int, 
    time_period     :str):
    
    # 判断长度是否大于等于间隔
    if time_length<time_interval:
        print("[ERROR] 输入时间错误: 时间跨度应大于等于 `interval`")
        return None
    
    # time_range [ start, end )
    time_range = pd.date_range(start=time_start, periods=(time_length//time_interval)+1, freq=time_period)
    
    if time_start < time_range[0]:
        time_range_start = pd.date_range(end=time_start,periods=1,freq=time_period)
        time_range = time_range_start.append(time_range)
    
    time_range = time_range[:time_length+1]
    
    time_start = time_range[0]
    time_end = time_range[-1]
    
    time_delta = time_end - time_start
    time_length_hour = int(time_delta.days*24 + time_delta.seconds//3600)
    
    return dict(
        time_start=time_start, time_end=time_end, 
        time_range=time_range, time_length=time_length, time_interval=time_interval)


def get_output_filename(var, start, stop, filetype, fbtime=None):
    
    try: start = pd.to_datetime(start).strftime('%Y%m%d%H')
    except: pass
    
    try: stop = pd.to_datetime(stop).strftime('%Y%m%d%H')
    except: pass
    
    try: fbtime = pd.to_datetime(fbtime).strftime('%Y%m%d%H')
    except: pass
    
    # filename = output_filename_fmt\
    #     .format(var=var, start=start, stop=stop, filetype=filetype)
    
    kwargs = [fbtime, var, start, stop]
    kwargs = [k for k in kwargs if k is not None]
    filename = '_'.join(kwargs) + '.' + filetype
    
    return filename

def get_output_path(dsname, report_type, time_start, var=None):
    try: 
        time_start = time_start.strftime("%Y%m%d%H")
    except:
        pass
    
    kwargs = [dsname, report_type, time_start, var]
    kwargs = [k for k in kwargs if k is not None]
    kwargs = [str(k) for k in kwargs if k is not None]
    
    output_path = os.path.join(output_prefix, *kwargs)
    os.makedirs(output_path, exist_ok=True)
    return output_path


def convert_time(time, zone=None, fmt=None):
    if not fmt is None:
        time = pd.to_datetime(str(time), format=fmt)
    else:
        time = pd.to_datetime(time)
    
    if zone == 'utc2bj':
        time = time + pd.Timedelta(hours=8)
    if zone == 'bj2utc':
        time = time - pd.Timedelta(hours=8)

    return time


def print_ndarray_info(array: np.ndarray):
    print("———————— Ndarray Infos ————————")
    print(f"Shape: {array.shape}")
    print(f"Min: {np.nanmin(array)}")
    print(f"Max: {np.nanmax(array)}")
    print(f"Mean: {np.nanmean(array)}")
    print(f"Std: {np.nanstd(array)}")
    
    return None

def print_exec_info(time_start, time_end, interval:int):
    time_start_str = pd.to_datetime(time_start).strftime('%Y-%m-%dT%H')
    time_end_str = pd.to_datetime(time_end).strftime('%Y-%m-%dT%H')
    time_delta = pd.to_datetime(time_end) - pd.to_datetime(time_start)
    time_length = int(time_delta.days * 24 + time_delta.seconds / 3600)
    
    print(
        80 * '—' + '\n',
        f"开始时间:{time_start_str}, 结束时间:{time_end_str},", 
        f"时间跨度:{time_length:03d}小时, 间隔:{interval:02d}小时", 
        '\n' + 80 * '—'
    )
    
    return None