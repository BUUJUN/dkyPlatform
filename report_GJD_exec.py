# -*- encoding: utf-8 -*-
'''
Created on 2024/09/12 09:08:25

@author: BOJUN WANG
'''
#%%
import os
import datetime
import pandas as pd

from configs import convert_time, print_exec_info
from statis import statis_basic
from read import Reader_GJD
from configs import shape_prov, shape_city, shape_sta
from configs import get_output_path, report_type_mapping
from model import GetSession
from model import WinterForecastProductInfo
from model import session_merge_from_df, session_extract_data

# 运行逻辑
# 每天 08CST 运行，使用前一天 12Z（20CST） 发报的数据
import argparse
time_now = convert_time(datetime.datetime.utcnow(), zone='utc2bj')
time_exec = pd.to_datetime(time_now.date()) + pd.Timedelta(hours=8)

parser = argparse.ArgumentParser(description='报告主程序')
parser.add_argument('--time', '-t', type=lambda s: pd.to_datetime(s, format='%Y%m%d%H'), help='设置执行时间 (北京时), 输入格式为`yyyymmddhh`, 默认是当天 08 时', default=time_exec)
parser.add_argument('--length', '-l', type=int, help='手动执行设置统计时长 (小时)', default=24)
parser.add_argument('--interval', '-i', type=int, help='手动执行设置统计间隔 (小时)', default=3)
args = parser.parse_args()
# args = parser.parse_args([])

exec_time = args.time
exec_length = args.length
exec_interval = args.interval

fore_start_utc = (time_exec + pd.Timedelta(days=-1)).replace(hour=12)
# fore_start_utc = pd.to_datetime('2023-11-27 T12:00:00')

print(f"执行时间: {exec_time}\t数据起报时间: {fore_start_utc}\t长度: {exec_length}\t间隔: {exec_interval}")

#%%
def statis_main(start, length, interval):
    
    end = start + pd.Timedelta(hours=length)
    print_exec_info(start, end, interval)
    
    reader = Reader_GJD(start, end, interval)
    
    if reader.files_group == 0:
        print('[ERROR] No data found to run in statis!!!')
        return None
    
    # 基础信息
    report_start = reader.time_start
    report_end = reader.time_end
    report_startstr = report_start.strftime('%Y%m%d%H')
    report_endstr = report_end.strftime('%Y%m%d%H')
    # report_length = reader.time_length
    report_interval = reader.interval
    report_type_str = reader.report_type
    report_type = report_type_mapping.get(report_type_str, -1)
    
    # lon = reader.lon
    # lat = reader.lat
    
    # 数据读入
    fileinfos_list = reader.extract_infos
    tp_list = reader.extract_data('tp', method='sum', to_tiff=True)
    t2m_list = reader.extract_data('t2m', method='mean', to_tiff=True)
    # tmax_list = reader.extract_data('t2m', method='max', to_tiff=True)
    # tmin_list = reader.extract_data('t2m', method='min', to_tiff=True)
    ws10_list = reader.extract_data('ws10', method='mean', to_tiff=True)
    r2m_list = reader.extract_data('r2m', method='mean', to_tiff=True)
    
    # 新建对话
    session = GetSession()
    df_list = []
    
    session_merge_kwargs_region = dict(
        cols = ['PAC', 'region_level', 'valid_time_start', 'cycle_time', 'valid_timestr'] +\
            ['pre_max', 'pre_mean'] + [f'pre_level_{i}' for i in range(0, 7)] + \
            ['wins_max', 'wins_mean', 'wins_min'] + [f'wins_level_{i}' for i in range(0, 10)] + \
            ['temp_max', 'temp_mean', 'temp_min'] + ['rh_max', 'rh_mean', 'rh_min'], 
        
        keys = ['region_id', 'region_level', 'data_time', 'forecast_cycle', 'forecast_timestr'] + \
            ['pre_max', 'pre_avg'] + [f'pre_level_{i}' for i in range(0, 7)] + \
            ['wins_max', 'wins_avg', 'wins_min'] + [f'wins_level_{i}' for i in range(0, 10)] + \
            ['temp_max', 'temp_avg', 'temp_min'] + ['rh_max', 'rh_avg', 'rh_min'], 
        
        data_id     = 3,
        create_time = time_now.date(),
        update_time = time_now, 
        forecast_type = report_type,
        forecast_step = report_interval, 
        report_time  = start, 
    )
    
    
    for i in range(len(fileinfos_list)):
        
        if tp_list[i]['tiff_path'] is None:
            continue
        
        files_count = fileinfos_list[i]['files_count']
        
        if files_count == 0:
            continue
        
        fb_timestr = fileinfos_list[i]['time_fb'].strftime('%Y%m%d%H')
        yb_startstr = fileinfos_list[i]['time_yb_start'].strftime('%Y%m%d%H')
        yb_stopstr = fileinfos_list[i]['time_yb_stop'].strftime('%Y%m%d%H')
        yb_rangestr = f"{yb_startstr}_{yb_stopstr}"
        
        statis_args = dict(
            pre_tif = tp_list[i]['tiff_path'], 
            wins_tif = ws10_list[i]['tiff_path'], 
            temp_tif = t2m_list[i]['tiff_path'],
            # tmax_tif = tmax_list[i]['tiff_path'],
            # tmin_tif = tmin_list[i]['tiff_path'],
            tmax_tif = None,
            tmin_tif = None,
            rh_tif = r2m_list[i]['tiff_path'], 
            report_type = report_type,
            report_interval = report_interval,
            report_time_start = report_start,
            report_time_end = report_end,
            cycle_time = fileinfos_list[i]['time_fb'],
            cycle_timestr = fb_timestr,
            valid_time_start = fileinfos_list[i]['time_yb_start'],
            valid_time_end = fileinfos_list[i]['time_yb_stop'],
            valid_timestr = yb_rangestr
        )
        
        # 统计省级矢量
        print(f'发报时间:{fb_timestr} \t预报时间:{yb_startstr}-{yb_stopstr} \tShapeFile:{shape_prov}')
        df_prov = statis_basic(region_shpfile=shape_prov, region_level=1, region_keys=['NAME', 'PAC'], **statis_args)
        
        # 统计地市矢量
        print(f'发报时间:{fb_timestr} \t预报时间:{yb_startstr}-{yb_stopstr} \tShapeFile:{shape_city}')
        df_city = statis_basic(region_shpfile=shape_city, region_level=2, region_keys=['NAME', 'PAC'], **statis_args)
        
        df_list.extend([df_prov, df_city])
        
        # 入库
        print("入库中 ... ")
        session_merge_from_df(session, WinterForecastProductInfo, df_prov, **session_merge_kwargs_region)
        session_merge_from_df(session, WinterForecastProductInfo, df_city, **session_merge_kwargs_region)
        
    session.close()
    
    df_list = [df for df in df_list if df is not None]
    
    if len(df_list) == 0:
        print('[ERROR] No data found to run in statis!!!')
        return None
    
    # 合并结果
    df_combined = pd.concat(df_list, axis=0, ignore_index=True)
    df_combined = df_combined.fillna(0)
    
    df_outpath = get_output_path(reader.dsname, report_type_str, report_startstr)
    df_combined.to_csv(os.path.join(df_outpath, f'{report_startstr}-{report_endstr}.csv'), index=False)
    
    return df_combined
    
#%%
if __name__ == '__main__':
    
    statis_main(start=fore_start_utc, length=exec_length, interval=exec_interval)
    
    # # 短临
    # df_res_imm = statis_main(start=args.time_start, length=24, interval=3)
    # # 短期
    # df_res_sht = statis_main(start=args.time_start, length=72, interval=24)
    # # 中期
    # df_res_med = statis_main(start=args.time_start, length=168, interval=24)
    
    print("FINISHED! 程序执行完毕")
    
#%%