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
from warn import warn_merge
from read import Reader_5km, Reader_1km
from configs import shape_prov, shape_city, shape_sta, get_output_path
from configs import device_type_mapping, period_mapping, var_type_mapping
from configs import get_time_type
from model import GetSession
from model import WarnDeviceTable, WarnRegionTable
from model import session_merge_from_df, session_extract_data

# 运行逻辑
# 逐小时运行，如果 分钟 < 30, 则运行上一小时
import argparse
time_now = convert_time(datetime.datetime.utcnow(), zone='utc2bj')
if time_now.minute < 30:
    time_now = time_now - pd.Timedelta(hours=1)
time_exec = time_now.replace(minute=0, second=0, microsecond=0)
# time_exec = pd.to_datetime('2023-11-27 T00:00:00')
parser = argparse.ArgumentParser(description='实况告警主程序')
parser.add_argument('--time', '-t', type=lambda s: pd.to_datetime(s, format='%Y%m%d%H'), help='设置使用的实况数据的时间, 输入格式为`yyyymmddhh`, 默认是当前时间', default=time_exec)
args = parser.parse_args()
# args = parser.parse_args([])

exec_start = args.time
exec_length = 1
exec_interval = 1
exec_period = 'hour'

print(f"执行时间: {exec_start}")

#%%
def warn_exec(start, length, interval, ttype):
    
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
    tmax_list = reader.extract_data('t2m', method='max', to_tiff=True)
    tmin_list = reader.extract_data('t2m', method='min', to_tiff=True)
    ws10_list = reader.extract_data('ws10', method='mean', to_tiff=True)
    
    # 新建对话
    session = GetSession()
    df_list = []
    
    session_merge_kwargs_region = dict(
        cols = ['PAC', 'region_level', 'time_start', 'type', 'value', 'level'],
        keys = ['region_id', 'region_level', 'data_time', 'type', 'value', 'level'],
        create_time = time_now, 
        update_time = time_now, 
        data_id = 1, )
    
    session_merge_kwargs_device = dict(
        cols = ['PAC', 'NAME', 'device_type', 'time_start', 'LON', 'LAT', 'type', 'value', 'level'],
        keys = ['device_id', 'device_name', 'device_type', 'data_time', 'lon', 'lat', 'type', 'value', 'level'],
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
            tmax_tif    = tmax_list[i]['tiff_path'], 
            tmin_tif    = tmin_list[i]['tiff_path'],
            ws10_tif    = ws10_list[i]['tiff_path'], 
        )
        
        # 统计省级矢量
        print(f'时间:{startstr}-{stopstr} \tShapeFile:{shape_prov}')
        df_prov = warn_merge(region_shpfile=shape_prov, region_level=1, region_keys=['NAME', 'PAC'], **statis_args)
        df_prov['type'] = df_prov['varname'].map(var_type_mapping)
        
        # 统计地市矢量
        print(f'时间:{startstr}-{stopstr} \tShapeFile:{shape_city}')
        df_city = warn_merge(region_shpfile=shape_city, region_level=2, region_keys=['NAME', 'PAC'], **statis_args)
        df_city['type'] = df_city['varname'].map(var_type_mapping)
        
        # 统计站点矢量
        print(f'时间:{startstr}-{stopstr} \tShapeFile:{shape_sta}')
        df_sta = warn_merge(region_shpfile=shape_sta, region_level=3, region_keys=['NAME', 'PAC', 'LAT', 'LON', 'TYPE'], **statis_args)
        df_sta['type'] = df_sta['varname'].map(var_type_mapping)
        df_sta['device_type'] = df_sta['TYPE'].map(device_type_mapping)
        
        df_list.extend([df_prov, df_city, df_sta])
        
        # 入库
        print("入库中 ... ")
        session_merge_from_df(session, WarnRegionTable, df_prov, **session_merge_kwargs_region)
        session_merge_from_df(session, WarnRegionTable, df_city, **session_merge_kwargs_region)
        session_merge_from_df(session, WarnDeviceTable, df_sta, **session_merge_kwargs_device)
    
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

if __name__=='__main__':
    # 小时
    warn_exec(exec_start, exec_length, exec_interval, exec_period)
    
    print("FINISHED! 程序执行完毕")

#%%