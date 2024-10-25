# -*- encoding: utf-8 -*-
'''
Created on 2024/09/20 09:34:07

@author: BOJUN WANG
'''
#%%
import os
import datetime
import pandas as pd

from configs import convert_time, print_exec_info
from statis import statis_obs
from read import Reader_5km, Reader_1km
from configs import shape_prov, shape_city, shape_sta, get_output_path, device_type_mapping, period_mapping
from configs import get_time_type
from model import GetSession
from model import StatRegionTable, StatDeviceTable
from model import session_merge_from_df, session_extract_data

import argparse

# 运行逻辑
# 每天 01CST 运行，使用前一天 00-23 的实况数据
time_now = convert_time(datetime.datetime.utcnow(), zone='utc2bj')
if time_now.hour < 1:
    time_now = time_now+pd.Timedelta(days=-1)
time_exec = pd.to_datetime(time_now.date())+pd.Timedelta(days=-1)
# time_exec = pd.to_datetime('2023-11-27 T00:00:00')
parser = argparse.ArgumentParser(description='实况统计主程序')
parser.add_argument(
    '--time', '-t', type=lambda s: pd.to_datetime(s, format='%Y%m%d%H'),
    help='设置统计开始时间, 输入格式为`yyyymmddhh`, 默认是当前时间前一天 00 时 (CST)', default=time_exec)
parser.add_argument('--period', '-p', type=str, help='设置统计时间粒度 (时长、间隔的单位) [hour, day, month, quarter, year]', default='day')
parser.add_argument('--length', '-l', type=int, help='设置统计时长', default=24)
parser.add_argument('--interval', '-i', type=int, help='设置统计间隔', default=24)
args = parser.parse_args()
# args = parser.parse_args([])

exec_start = args.time
exec_period = args.period
exec_length = args.length
exec_interval = args.interval
print(f"执行时间: {exec_start}\t颗粒度: {exec_period}\t长度: {exec_length}\t间隔: {exec_interval}")

#%%
def statis_from_file(start, length, interval, ttype):
    
    # reader = Reader_1km(start, length, interval, ttype)
    reader = Reader_5km(start, length, interval, ttype)
    
    # 基础信息
    report_start = reader.time_start
    report_end = reader.time_end
    report_startstr = report_start.strftime('%Y%m%d%H')
    report_endstr = report_end.strftime('%Y%m%d%H')
    report_length = reader.time_length
    report_interval = reader.time_interval
    report_period = period_mapping.get(reader.time_period, -1)
    
    # 数据读入
    tp_list = reader.extract_data('tp', method='sum', to_tiff=True)
    epe_list = reader.extract_data('epe', method='sum', to_tiff=True)
    t2m_list = reader.extract_data('t2m', method='mean', to_tiff=True)
    tmax_list = reader.extract_data('t2m', method='max', to_tiff=True)
    tmin_list = reader.extract_data('t2m', method='min', to_tiff=True)
    ws10_list = reader.extract_data('ws10', method='mean', to_tiff=True)
    wd10_list = reader.extract_data('wd10', method='most', to_tiff=True)
    r2m_list = reader.extract_data('r2m', method='mean', to_tiff=True)
    sp_list = reader.extract_data('sp', method='mean', to_tiff=True)
    
    # 新建对话
    session = GetSession()
    df_list = []
    
    session_merge_kwargs_region = dict(
        cols = ['PAC', 'region_level', 'time_start', 'period', 't2m_mean', 'tmax_mean', 'tmin_mean', 
                'tp_mean', 'epes', 'ws10_mean', 'wd_most', 'r2m_mean', 'sp_mean'],
        keys = ['region_id', 'region_level', 'data_time', 'period', 'avg_temp', 'max_temp', 'min_temp', 'precipitation', 
                'extreme_prec', 'wind_speed', 'wind_direction', 'relative_humidity', 'pressure'],
        create_time = time_now, 
        update_time = time_now, 
        data_id = 1, )
    
    session_merge_kwargs_device = dict(
        cols = ['PAC', 'NAME', 'device_type', 'time_start', 'period', 'LON', 'LAT', 't2m_mean', 'tmax_mean', 'tmin_mean', 
                'tp_mean', 'epes', 'ws10_mean', 'wd_most', 'r2m_mean', 'sp_mean'],
        keys = ['device_id', 'device_name', 'device_type', 'data_time', 'period', 'lon', 'lat', 'avg_temp', 'max_temp', 'min_temp', 'precipitation', 
                'extreme_prec', 'wind_speed', 'wind_direction', 'relative_humidity', 'pressure'],
        create_time = time_now, 
        update_time = time_now, 
        data_id = 1, )
    
    for i in range(len(tp_list)):
        
        if tp_list[i]['tiff_path'] is None:
            continue
        
        startstr = tp_list[i]['time_start'].strftime('%Y%m%d%H')
        stopstr = tp_list[i]['time_stop'].strftime('%Y%m%d%H')
        
        statis_args = dict(
            time_start  = tp_list[i]['time_start'], 
            time_end    = tp_list[i]['time_stop'], 
            period      = report_period,
            tp_tif      = tp_list[i]['tiff_path'], 
            epe_tif     = epe_list[i]['tiff_path'], 
            sp_tif      = sp_list[i]['tiff_path'],
            t2m_tif     = t2m_list[i]['tiff_path'], 
            tmax_tif    = tmax_list[i]['tiff_path'], 
            tmin_tif    = tmin_list[i]['tiff_path'],
            r2m_tif     = r2m_list[i]['tiff_path'], 
            ws10_tif    = ws10_list[i]['tiff_path'], 
            wd10_tif    = wd10_list[i]['tiff_path'],
        )
        
        # 统计省级矢量
        print(f'时间:{startstr}-{stopstr} \tShapeFile:{shape_prov}')
        df_prov = statis_obs(region_shpfile=shape_prov, region_level=1, region_keys=['NAME', 'PAC'], **statis_args)
        
        # 统计地市矢量
        print(f'时间:{startstr}-{stopstr} \tShapeFile:{shape_city}')
        df_city = statis_obs(region_shpfile=shape_city, region_level=2, region_keys=['NAME', 'PAC'], **statis_args)
        
        # 统计站点矢量
        print(f'时间:{startstr}-{stopstr} \tShapeFile:{shape_sta}')
        df_sta = statis_obs(region_shpfile=shape_sta, region_level=3, region_keys=['NAME', 'PAC', 'LAT', 'LON', 'TYPE'], **statis_args)
        df_sta['device_type'] = df_sta['TYPE'].map(device_type_mapping)
        
        df_list.extend([df_prov, df_city, df_sta])
        
        # 入库
        print("入库中 ... ")
        session_merge_from_df(session, StatRegionTable, df_prov, **session_merge_kwargs_region)
        session_merge_from_df(session, StatRegionTable, df_city, **session_merge_kwargs_region)
        session_merge_from_df(session, StatDeviceTable, df_sta, **session_merge_kwargs_device)
    
    session.close()
    
    df_list = [df for df in df_list if df is not None]
    if len(df_list)==0:
        print('[ERROR] No data found to run in statis!!!')
        return None
    # # 合并结果
    df_combined = pd.concat(df_list, axis=0, ignore_index=True)
    df_outpath = get_output_path(reader.dsname, None, report_startstr)
    df_combined.to_csv(os.path.join(df_outpath, f'{report_startstr}-{report_endstr}.csv'), index=False)
    
    return df_combined


def statis_from_table(start, length, interval, ttype):
    
    report_period = period_mapping.get(f'{interval}{get_time_type(ttype)}', -1)
    
    query_region_list = session_extract_data(StatRegionTable, start, length, interval, ttype)
    query_device_list = session_extract_data(StatDeviceTable, start, length, interval, ttype)
    
    session = GetSession()
    
    for df_region in query_region_list:
        # 预处理
        df_region = df_region.drop(columns=['create_time', 'update_time'], errors='ignore')
        df_group = df_region.groupby(['region_id', 'data_id'])
        df_group_tstart = df_group.data_time.min()
        df_group_mean = df_group.mean(numeric_only=True)
        df_group_mean['data_time'] = df_group_tstart
        df_group_mean['period'] = report_period
        df_group_mean['create_time'] = time_now
        df_group_mean['update_time'] = time_now
        df_group_mean.reset_index(drop=False, inplace=True)
        # 入库
        print("入库中 ... ")
        session_merge_from_df(session, StatRegionTable, df_group_mean)
    
    for df_device in query_device_list:
        # 预处理
        df_device = df_device.drop(columns=['create_time', 'update_time'], errors='ignore')
        df_group = df_device.groupby(['device_id', 'device_name', 'device_type', 'data_id'])
        df_group_tstart = df_group.data_time.min()
        df_group_mean = df_group.mean(numeric_only=True)
        df_group_mean['data_time'] = df_group_tstart
        df_group_mean['period'] = report_period
        df_group_mean['create_time'] = time_now
        df_group_mean['update_time'] = time_now
        df_group_mean.reset_index(drop=False, inplace=True)
        # 入库
        print("入库中 ... ")
        session_merge_from_df(session, StatDeviceTable, df_group_mean)
    
    session.close()
    
    return None

def statis_main(start, length, interval, ttype):
    
    if ttype == 'day':
        res = statis_from_file(start, length, interval, 'day')
    elif ttype in ['month', 'year', 'quarter']:
        res = statis_from_table(start, length, interval, ttype)
    else:
        print('[ERROR] Invalid time type!')
        return None
    
    return res

if __name__=='__main__':
    
    statis_main(exec_start, exec_length, exec_interval, exec_period)
    
    # # 天
    # statis_main(exec_start, 1, 1, 'day')
    
    # 月
    if exec_start.day == 1:
        statis_main(exec_start+pd.Timedelta(days=-1), 1, 1, 'month')
    
    # 季度
    if (exec_start.month in [4, 7, 9, 1]) and (exec_start.day == 1):
        statis_main(exec_start+pd.Timedelta(days=-1), 1, 1, 'quarter')
    
    # 年
    if (exec_start.month == 1) and (exec_start.day == 1):
        statis_main(exec_start+pd.Timedelta(days=-1), 1, 1, 'year')
    
    print("FINISHED! 程序执行完毕")

#%%